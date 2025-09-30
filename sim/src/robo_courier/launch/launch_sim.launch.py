import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # Replace with your package name
    package_name = 'robo_courier'

    # Include the robot_state_publisher launch file
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'use_ros2_control': 'true'
        }.items()
    )

    joystick = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'joystick.launch.py'
            )
        ]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    twist_mux_params = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'twist_mux.yaml'
    )
    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params, {'use_sim_time': True}],
        remappings=[('/cmd_vel_out', '/cmd_vel_out_unstamped')]
    )

    # temp twist to twist stamped
    twist_stamp = Node(
        package="twist_to_twiststamped",
        executable="twist_to_twiststamped_node",
        parameters=[{
            'input_topic': '/cmd_vel_out_unstamped',
            'output_topic': '/ack_cont/reference',
            'frame_id': 'base_link'
        }]
    )

    # Path to Gazebo parameters file
    gazebo_params_file = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'gazebo_params.yaml'
    )

    # Path to custom world file
    world_file = os.path.join(
        get_package_share_directory(package_name),
        'worlds',
        'apartmentswag.world'
    )

    # Include the Gazebo launch file with the world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        ]),
        launch_arguments={
            'world': world_file,
            "publish_rate": "400.0",
        }.items()
    )

    # Run the spawner node for the robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'my_bot'],
        output='screen'
    )

    ack_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ack_cont"],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    # Launch them all
    return LaunchDescription([
        rsp,
        joystick,
        twist_mux,
        twist_stamp,
        gazebo,
        spawn_entity,
        ack_drive_spawner,
        joint_broad_spawner,
    ])
