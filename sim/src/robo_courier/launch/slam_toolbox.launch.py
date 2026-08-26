
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('robo_courier')
    params_file = os.path.join(pkg_share, 'config', 'slam_toolbox_params.yaml')
    rviz_config = os.path.join(pkg_share, 'config', 'map_view.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz = LaunchConfiguration('rviz')

    slam_node = Node(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
    )

    # Same config as map_server.launch.py: slam_toolbox publishes its live
    # occupancy grid on /map, which lands in the "Base Map" display.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        # OGRE renders via GLX; on Wayland Qt must run through XWayland or
        # rviz aborts with "Invalid parentWindowHandle".
        additional_env={'QT_QPA_PLATFORM': 'xcb'},
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Launch RViz with the map view config'),
        slam_node,
        rviz_node,
    ])
