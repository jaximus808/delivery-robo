cmake_minimum_required(VERSION 3.5)
project(ackdrive_arduino)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()


if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra)
endif()

find_package(ament_cmake REQUIRED)
find_package(serial REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(controller_manager REQUIRED)
find_package(rclcpp REQUIRED)
find_package(pluginlib REQUIRED)






add_library(ackdrive_arduino SHARED src/ackdrive_arduino.cpp src/wheel.cpp src/arduino_comms.cpp)

target_include_directories(
  ackdrive_arduino
  PRIVATE
  include
)
ament_target_dependencies(
  ackdrive_arduino
  hardware_interface
  controller_manager
  serial
  rclcpp
  pluginlib
)

pluginlib_export_plugin_description_file(hardware_interface robot_hardware.xml)


ament_package()

