import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command, LaunchConfiguration

def generate_launch_description():
    package_name = 'robo_courier'

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    # --- Generate robot_description from xacro ---
    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        'description',
        'robot.urdf.xacro'
    )

    robot_description = Command([
        'xacro ', xacro_file,
        ' use_ros2_control:=true',
        ' sim_mode:=false'
    ])

    # --- Controller Manager (The ONLY one you need) ---
    # We use output='both' so you can see if the C++ code crashes
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {'robot_description': robot_description},
            os.path.join(
                get_package_share_directory(package_name),
                'config',
                'my_controllers.yaml'
            ),
            {'use_sim_time': False}
        ],
        output="both", 
    )

    # --- Spawners ---
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
        output="screen"
    )

    ack_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ack_cont"],
        output="screen"
    )

    # --- CRITICAL FIX: The Delay ---
    # On a Pi, the Controller Manager takes time to open Serial ports and load plugins.
    # We wait 10 seconds before letting the spawners run.
    # If this feels too long later, you can reduce it to 5 or 7.
    delayed_controller_manager_spawner = TimerAction(
        period=10.0,
        actions=[
            joint_broad_spawner,
            ack_drive_spawner
        ]
    )

    # --- Other Nodes (RSP, Joystick, etc) ---
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true', 'sim_mode': 'false'}.items()
    )

    joystick = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory(package_name), 'launch', 'joystick.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    twist_mux_params = os.path.join(get_package_share_directory(package_name), 'config', 'twist_mux.yaml')
    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params, {'use_sim_time': False}],
        remappings=[('/cmd_vel_out', '/cmd_vel_out_unstamped')]
    )

    twist_stamp = Node(
        package="twist_to_twiststamped",
        executable="twist_to_twiststamped_node",
        parameters=[{'input_topic': '/cmd_vel_out_unstamped', 'output_topic': '/ack_cont/reference', 'frame_id': 'base_link'}]
    )

    return LaunchDescription([
        use_sim_time_arg,
        rsp,
        joystick,
        twist_mux,
        twist_stamp,
        controller_manager,
        delayed_controller_manager_spawner
    ])