import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction, RegisterEventHandler, ExecuteProcess
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

    use_sim_time = LaunchConfiguration('use_sim_time')

    # --- Include robot_state_publisher (RSP) ---
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': 'false',
            'use_ros2_control': 'true',
            'sim_mode': 'false'
        }.items()
    )

    # --- Joystick ---
    joystick = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'joystick.launch.py'
            )
        ]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    # --- Twist mux ---
    twist_mux_params = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'twist_mux.yaml'
    )

    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params, {'use_sim_time': False}],
        remappings=[('/cmd_vel_out', '/cmd_vel_out_unstamped')]
    )

    # --- Twist to TwistStamped ---
    twist_stamp = Node(
        package="twist_to_twiststamped",
        executable="twist_to_twiststamped_node",
        parameters=[{
            'input_topic': '/cmd_vel_out_unstamped',
            'output_topic': '/ack_cont/reference',
            'frame_id': 'base_link'
        }]
    )

    # --- ros2_control_node (Controller Manager) ---
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
        output="screen"
    )


    # --- Spawners ---
    ack_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ack_cont", "--controller-manager-timeout", "60"],
        output="screen"
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad", "--controller-manager-timeout", "60"],
        output="screen"
    )

    # Spawn controllers *after* controller_manager starts
    # Increased delay from 2.0 to 5.0 seconds to ensure controller_manager is fully initialized
    delayed_spawners = TimerAction(
        period=1.0,
        actions=[joint_broad_spawner]
    )
    

    ack_drive_spawner_event = RegisterEventHandler(
    
        event_handler=OnProcessStart(
            target_action=joint_broad_spawner,
            on_start=[
                TimerAction(period=1.0, actions=[ack_drive_spawner])
            ]
        )
    )

    

    controller_manager_cmd = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'controller_manager', 'ros2_control_node',
        ],
        output='screen'
    )


    ros2_control_node = RegisterEventHandler(
    
        event_handler=OnProcessStart(
            target_action=ack_drive_spawner,
            on_start=[
                TimerAction(period=1.0, actions=[controller_manager_cmd])
            ]
        )
    )

    return LaunchDescription([
        use_sim_time_arg,
        rsp,
        joystick,
        twist_mux,
        twist_stamp,
        controller_manager,
        delayed_spawners,
        ack_drive_spawner_event,
        ros2_control_node,
    ])
