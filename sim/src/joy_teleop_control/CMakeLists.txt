cmake_minimum_required(VERSION 3.8)
project(joy_teleop_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(arduino_comms REQUIRED)

include_directories(include)

add_executable(joy_teleop_control src/joy_listener.cpp)
ament_target_dependencies(joy_teleop_control rclcpp sensor_msgs arduino_comms)

install(TARGETS
  joy_teleop_control
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
