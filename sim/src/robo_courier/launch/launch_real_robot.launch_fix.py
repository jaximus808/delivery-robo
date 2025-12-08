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

    # --- Controller Manager (The ONLY one) ---
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
        output="both", # Changed to 'both' to see C++ crashes
    )

    # --- Spawners ---
    # Spawn Joint Broadcaster first
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad", "--controller-manager-timeout", "60"],
        output="screen"
    )

    # Spawn Ackermann Controller AFTER Joint Broadcaster
    ack_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ack_cont", "--controller-manager-timeout", "60"],
        output="screen"
    )

    # Delay start of spawners to let Controller Manager spin up
    delayed_joint_broad_spawner = TimerAction(
        period=3.0, 
        actions=[joint_broad_spawner]
    )

    # Start Ackermann spawner after Joint Broadcaster finishes
    ack_drive_spawner_event = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=joint_broad_spawner,
            on_start=[ack_drive_spawner]
        )
    )

    # --- RSP, Joystick, Twist Mux, etc... ---
    # (Kept these as they were)
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
        delayed_joint_broad_spawner,
        ack_drive_spawner_event
    ])