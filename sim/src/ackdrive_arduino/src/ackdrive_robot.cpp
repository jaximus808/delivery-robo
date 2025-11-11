#include <memory>
#include <chrono>
#include <thread>

#include "rclcpp/rclcpp.hpp"
#include "hardware_interface/resource_manager.hpp"
#include "controller_manager/controller_manager.hpp"
#include "ackdrive_arduino/ackdrive_arduino.h"

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    auto executor = std::make_shared<rclcpp::executors::MultiThreadedExecutor>();
    auto node = std::make_shared<rclcpp::Node>("ackdrive_robot");

    // Get parameters with defaults
    node->declare_parameter<std::string>("left_steer_joint", "left_wheel_hinge");
    node->declare_parameter<std::string>("right_steer_joint", "right_wheel_hinge");
    node->declare_parameter<std::string>("left_rear_wheel_joint", "left_rear_wheel_joint");
    node->declare_parameter<std::string>("right_rear_wheel_joint", "right_rear_wheel_joint");
    node->declare_parameter<int>("baud_rate", 57600);
    node->declare_parameter<std::string>("device", "/dev/ttyUSB0");
    node->declare_parameter<int>("enc_counts_per_rev", 3436);
    node->declare_parameter<int>("timeout", 1000);
    node->declare_parameter<double>("robot_loop_rate", 50.0);

    std::string left_steer_joint = node->get_parameter("left_steer_joint").as_string();
    std::string right_steer_joint = node->get_parameter("right_steer_joint").as_string();
    std::string left_rear_wheel_joint = node->get_parameter("left_rear_wheel_joint").as_string();
    std::string right_rear_wheel_joint = node->get_parameter("right_rear_wheel_joint").as_string();
    int baud_rate = node->get_parameter("baud_rate").as_int();
    std::string device = node->get_parameter("device").as_string();
    int enc_counts_per_rev = node->get_parameter("enc_counts_per_rev").as_int();
    int timeout = node->get_parameter("timeout").as_int();
    double loop_rate = node->get_parameter("robot_loop_rate").as_double();

    RCLCPP_INFO(node->get_logger(), "Starting Ackermann Drive Robot Node");
    RCLCPP_INFO(node->get_logger(), "Left Steer Joint: %s", left_steer_joint.c_str());
    RCLCPP_INFO(node->get_logger(), "Right Steer Joint: %s", right_steer_joint.c_str());
    RCLCPP_INFO(node->get_logger(), "Left Rear Wheel: %s", left_rear_wheel_joint.c_str());
    RCLCPP_INFO(node->get_logger(), "Right Rear Wheel: %s", right_rear_wheel_joint.c_str());
    RCLCPP_INFO(node->get_logger(), "Device: %s", device.c_str());
    RCLCPP_INFO(node->get_logger(), "Baud Rate: %d", baud_rate);
    RCLCPP_INFO(node->get_logger(), "Loop Rate: %.2f Hz", loop_rate);

    // Create hardware interface
    auto hardware = std::make_shared<AckDriveArduino>();
    
    // Build HardwareInfo structure
    hardware_interface::HardwareInfo info;
    info.name = "AckDriveArduino";
    info.type = "system";
    
    // Add hardware parameters
    info.hardware_parameters["left_steer_joint"] = left_steer_joint;
    info.hardware_parameters["right_steer_joint"] = right_steer_joint;
    info.hardware_parameters["left_rear_wheel_joint"] = left_rear_wheel_joint;
    info.hardware_parameters["right_rear_wheel_joint"] = right_rear_wheel_joint;
    info.hardware_parameters["loop_rate"] = std::to_string(loop_rate);
    info.hardware_parameters["device"] = device;
    info.hardware_parameters["baud_rate"] = std::to_string(baud_rate);
    info.hardware_parameters["timeout"] = std::to_string(timeout);
    info.hardware_parameters["enc_counts_per_rev"] = std::to_string(enc_counts_per_rev);

    // Initialize hardware
    if (hardware->on_init(info) != hardware_interface::CallbackReturn::SUCCESS)
    {
        RCLCPP_ERROR(node->get_logger(), "Failed to initialize hardware interface");
        return 1;
    }

    // Activate hardware
    rclcpp_lifecycle::State state;
    if (hardware->on_activate(state) != hardware_interface::CallbackReturn::SUCCESS)
    {
        RCLCPP_ERROR(node->get_logger(), "Failed to activate hardware interface");
        return 1;
    }

    // Create controller manager
    auto controller_manager = std::make_shared<controller_manager::ControllerManager>(
        executor, "_controller_manager");

    executor->add_node(controller_manager);

    // Main control loop
    auto prev_time = node->now();
    rclcpp::Rate rate(loop_rate);

    RCLCPP_INFO(node->get_logger(), "Starting main control loop...");

    while (rclcpp::ok())
    {
        auto current_time = node->now();
        auto period = current_time - prev_time;

        // Read from hardware
        hardware->read(current_time, period);

        // Update controllers
        controller_manager->update(current_time, period);

        // Write to hardware
        hardware->write(current_time, period);

        prev_time = current_time;

        // Spin executor
        executor->spin_some();
        
        rate.sleep();
    }

    // Deactivate hardware before shutdown
    hardware->on_deactivate(state);

    rclcpp::shutdown();
    return 0;
}