import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError

# Selected by deployment/robot_config.yaml (via startup.sh), or by hand:
#   ros2 launch my_bringup master_launch.py mode:=teleop
#   ros2 launch my_bringup master_launch.py mode:=autonomous

def generate_launch_description():
   mode = LaunchConfiguration('mode')
   mode_arg = DeclareLaunchArgument(
      'mode',
      default_value='teleop',
      choices=['teleop', 'autonomous'],
      description='teleop = wired joystick control; autonomous = sensor stack (GPS/NTRIP/IMU)',
   )
   is_teleop = IfCondition(PythonExpression(["'", mode, "' == 'teleop'"]))
   is_autonomous = IfCondition(PythonExpression(["'", mode, "' == 'autonomous'"]))

   # --- teleop: wired joystick (verified working on the Pi, keep as-is) -----
   joy_node = Node(
      package='joy',
      executable='joy_node',
      name='joy_node',
      respawn=True,
      respawn_delay=3.0,
      output='screen',
      condition=is_teleop,
   )

   control_node = Node(
      package='joystick_control',
      executable='joystick_node',
      name='control_node',
      respawn=True,
      respawn_delay=3.0,
      output='screen',
      condition=is_teleop,
   )

   # --- autonomous: sensor stack ------------------------------------------
   # Resolved at load time, so guard it: teleop must still work on a Pi
   # where ublox_dgnss isn't built.
   try:
      ublox_dir = get_package_share_directory('ublox_dgnss')
   except PackageNotFoundError:
      ublox_dir = None
      print('[master_launch] ublox_dgnss not found; autonomous mode has no GPS/NTRIP nodes')

   gps_main_node = IncludeLaunchDescription(
       PythonLaunchDescriptionSource(
           os.path.join(ublox_dir or '', 'launch', 'ublox_rover_hpposllh_navsatfix.launch.py')
       ),
       condition=is_autonomous,
   )

   gps_ntrip_node = IncludeLaunchDescription(
       PythonLaunchDescriptionSource(
           os.path.join(ublox_dir or '', 'launch', 'ntrip_client.launch.py')
       ),
       launch_arguments={
           'use_https': 'false',
           'host':'168.166.125.30',
           'port': '2101',
           'mountpoint':'RTX_RTCM34',
           'username':'/WashUroboticsDelivery2026',
           'password':'$DeliveryWU197?'
       }.items(),
       condition=is_autonomous,
   )

   imu_node = Node(
       package='imu_package',
       executable='imu_publisher',
       name='imu_publisher',
       respawn=True,
       respawn_delay=3.0,
       output='screen',
       condition=is_autonomous,
   )

   autonomous_nodes = [imu_node]
   if ublox_dir is not None:
      autonomous_nodes += [gps_main_node, gps_ntrip_node]

   return LaunchDescription([
        mode_arg,
        joy_node, 
        control_node, 
        *autonomous_nodes
    ])
