cmake_minimum_required(VERSION 3.5)
project(arduino_comms)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(serial REQUIRED)

# Export headers and library
ament_export_include_directories(include)
ament_export_libraries(${PROJECT_NAME})
ament_export_dependencies(rclcpp serial)

# Build library
add_library(${PROJECT_NAME}
    src/arduino_comms.cpp
    include/arduino_comms/arduino_comms.h
)

set_target_properties(${PROJECT_NAME} PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Include dirs
target_include_directories(${PROJECT_NAME}
    PUBLIC
        include
)

# Use ament_target_dependencies to link + include
ament_target_dependencies(${PROJECT_NAME}
    rclcpp
    serial
)

# Install library
install(
  TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

# Install headers
install(
  DIRECTORY include/
  DESTINATION include
)

ament_package()
