import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('robo_courier')
    default_map = os.path.join(pkg_share, 'maps', 'base_map.yaml')
    default_keepout = os.path.join(pkg_share, 'maps', 'keepout_draft.yaml')
    rviz_config = os.path.join(pkg_share, 'config', 'map_view.rviz')

    map_yaml = LaunchConfiguration('map')
    keepout_yaml = LaunchConfiguration('keepout')
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz = LaunchConfiguration('rviz')

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml,
            'topic_name': 'map',
            'frame_id': 'map',
            'use_sim_time': use_sim_time,
        }],
    )

    keepout_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='keepout_mask_server',
        output='screen',
        parameters=[{
            'yaml_filename': keepout_yaml,
            'topic_name': 'keepout_mask',
            'frame_id': 'map',
            'use_sim_time': use_sim_time,
        }],
    )

    # map_server is a lifecycle node; it publishes nothing until activated.
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server', 'keepout_mask_server'],
            'use_sim_time': use_sim_time,
        }],
    )

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
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the map yaml served on /map'),
        DeclareLaunchArgument('keepout', default_value=default_keepout,
                              description='Full path to the keepout mask yaml served on /keepout_mask'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Launch RViz with the map review config'),
        map_server,
        keepout_server,
        lifecycle_manager,
        rviz_node,
    ])
