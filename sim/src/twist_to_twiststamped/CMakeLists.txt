cmake_minimum_required(VERSION 3.8)
project(twist_to_twiststamped)

# Find required dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

# Include header files
include_directories(include)

# Add the executable
add_executable(twist_to_twiststamped_node src/twist_to_twiststamped.cpp)

# Link dependencies
ament_target_dependencies(twist_to_twiststamped_node
  rclcpp
  geometry_msgs
)

# Specify include directories for the executable
target_include_directories(twist_to_twiststamped_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# Install the executable
install(TARGETS
  twist_to_twiststamped_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install the include directory
install(
  DIRECTORY include/
  DESTINATION include
)

# Export the package
ament_package()