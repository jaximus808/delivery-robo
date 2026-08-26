import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
   ublox_dir = get_package_share_directory('ublox_dgnss')

   gps_main_node = IncludeLaunchDescription(
       PythonLaunchDescriptionSource(
           os.path.join(ublox_dir, 'launch', 'ublox_rover_hpposllh_navsatfix.launch.py')
       )
   )

   gps_ntrip_node = IncludeLaunchDescription(
       PythonLaunchDescriptionSource(
           os.path.join(ublox_dir, 'launch', 'ntrip_client.launch.py')
       ),
       launch_arguments={
           'use_https': 'false',
           'host':'168.166.125.30',
           'port': '2101',
           'mountpoint':'RTX_RTCM34',
           'username':'/WashUroboticsDelivery2026',
           'password':'$DeliveryWU197?'
       }.items()
   )

   imu_node = Node(
       package='imu_package',
       executable='imu_publisher',
       name='imu_publisher',
       respawn=True,
       respawn_delay=3.0,
       output='screen'
   )

   # RTK lat/lon -> map-frame meters (datum generated from map/georef.yaml;
   # edit that file + run map/tools/update_georef.py to move the datum)
   bringup_dir = get_package_share_directory('my_bringup')
   gps_to_map_node = Node(
       package='my_bringup',
       executable='gps_to_map',
       name='gps_to_map',
       parameters=[os.path.join(bringup_dir, 'config', 'gps_datum.yaml')],
       respawn=True,
       respawn_delay=3.0,
       output='screen'
   )

   return LaunchDescription([gps_main_node, gps_ntrip_node, imu_node, gps_to_map_node])
