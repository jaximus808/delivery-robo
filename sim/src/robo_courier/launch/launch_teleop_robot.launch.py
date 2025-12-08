import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'robo_courier'

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

    # --- joy_teleop_control package ---
    joy_teleop = Node(
        package="joy_teleop_control",
        executable="joy_teleop_control",   # <-- rename if your exec name is different
        name="joy_teleop_control",
        output="screen",
        parameters=[{'use_sim_time': False}]
    )

    return LaunchDescription([
        joystick,
        joy_teleop,
    ])
