#include "ackdrive_arduino/ackdrive_arduino.h"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
namespace ackdrive_arduino  // ADD THIS!
{

AckDriveArduino::AckDriveArduino()
    : logger_(rclcpp::get_logger("AckDriveArduino"))
{}

CallbackReturn AckDriveArduino::on_init(const hardware_interface::HardwareInfo & info) {
    if (hardware_interface::SystemInterface::on_init(info) != CallbackReturn::SUCCESS) {
      return CallbackReturn::ERROR;
    }

    RCLCPP_INFO(logger_, "Configuring...");

    time_ = std::chrono::system_clock::now();

    // Read parameters for all 4 joints
    cfg_.left_steer_joint = info_.hardware_parameters["left_steer_joint"];
    cfg_.right_steer_joint = info_.hardware_parameters["right_steer_joint"];
    cfg_.left_rear_wheel_joint = info_.hardware_parameters["left_rear_wheel_joint"];
    cfg_.right_rear_wheel_joint = info_.hardware_parameters["right_rear_wheel_joint"];
    
    cfg_.loop_rate = std::stof(info_.hardware_parameters["loop_rate"]);
    cfg_.device = info_.hardware_parameters["device"];
    cfg_.baud_rate = std::stoi(info_.hardware_parameters["baud_rate"]);
    cfg_.timeout = std::stoi(info_.hardware_parameters["timeout"]);
    cfg_.enc_counts_per_rev = std::stoi(info_.hardware_parameters["enc_counts_per_rev"]);

    // Set up all 4 wheels
    left_steer_.setup(cfg_.left_steer_joint, cfg_.enc_counts_per_rev);
    right_steer_.setup(cfg_.right_steer_joint, cfg_.enc_counts_per_rev);
    left_rear_wheel_.setup(cfg_.left_rear_wheel_joint, cfg_.enc_counts_per_rev);
    right_rear_wheel_.setup(cfg_.right_rear_wheel_joint, cfg_.enc_counts_per_rev);

    // Set up the Arduino (when ready)
    arduino_.setup(cfg_.device, cfg_.baud_rate, cfg_.timeout);  

    RCLCPP_INFO(logger_, "Finished Configuration");

    return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> AckDriveArduino::export_state_interfaces()
{
    std::vector<hardware_interface::StateInterface> state_interfaces;

    // Left steering joint states
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        left_steer_.name, 
        hardware_interface::HW_IF_POSITION, 
        &left_steer_.pos));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        left_steer_.name, 
        hardware_interface::HW_IF_VELOCITY, 
        &left_steer_.vel));

    // Right steering joint states
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        right_steer_.name, 
        hardware_interface::HW_IF_POSITION, 
        &right_steer_.pos));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        right_steer_.name, 
        hardware_interface::HW_IF_VELOCITY, 
        &right_steer_.vel));

    // Left rear wheel states
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        left_rear_wheel_.name, 
        hardware_interface::HW_IF_POSITION, 
        &left_rear_wheel_.pos));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        left_rear_wheel_.name, 
        hardware_interface::HW_IF_VELOCITY, 
        &left_rear_wheel_.vel));

    // Right rear wheel states
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        right_rear_wheel_.name, 
        hardware_interface::HW_IF_POSITION, 
        &right_rear_wheel_.pos));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
        right_rear_wheel_.name, 
        hardware_interface::HW_IF_VELOCITY, 
        &right_rear_wheel_.vel));

    return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> AckDriveArduino::export_command_interfaces()
{
    std::vector<hardware_interface::CommandInterface> command_interfaces;

    // Left steering position command
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        left_steer_.name, 
        hardware_interface::HW_IF_POSITION, 
        &left_steer_.cmd));

    // Right steering position command
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        right_steer_.name, 
        hardware_interface::HW_IF_POSITION, 
        &right_steer_.cmd));

    // Left rear wheel velocity command
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        left_rear_wheel_.name, 
        hardware_interface::HW_IF_VELOCITY, 
        &left_rear_wheel_.cmd));

    // Right rear wheel velocity command
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
        right_rear_wheel_.name, 
        hardware_interface::HW_IF_VELOCITY, 
        &right_rear_wheel_.cmd));

    return command_interfaces;
}

CallbackReturn AckDriveArduino::on_activate(const rclcpp_lifecycle::State &state)
{
    RCLCPP_INFO(logger_, "Starting Controller...");

    // When Arduino is ready:
    // arduino_.sendEmptyMsg();
    // arduino_.setPidValues(30, 20, 0, 100);

    return CallbackReturn::SUCCESS;
}

CallbackReturn AckDriveArduino::on_deactivate(const rclcpp_lifecycle::State &state)
{
    RCLCPP_INFO(logger_, "Stopping Controller...");
    return CallbackReturn::SUCCESS;
}

return_type AckDriveArduino::read(const rclcpp::Time & time, const rclcpp::Duration & period)
{
    // Calculate time delta
    auto new_time = std::chrono::system_clock::now();
    std::chrono::duration<double> diff = new_time - time_;
    double deltaSeconds = diff.count();
    time_ = new_time;

    // When Arduino is ready:
    // if (!arduino_.connected())
    // {
    //     return return_type::ERROR;
    // }

    // Read encoder values for all 4 joints from Arduino
    // arduino_.readEncoderValues(left_steer_.enc, right_steer_.enc, 
    //                            left_rear_wheel_.enc, right_rear_wheel_.enc);

    // Update steering positions and velocities
    // double pos_prev = left_steer_.pos;
    // left_steer_.pos = left_steer_.calcEncAngle();
    // left_steer_.vel = (left_steer_.pos - pos_prev) / deltaSeconds;

    // pos_prev = right_steer_.pos;
    // right_steer_.pos = right_steer_.calcEncAngle();
    // right_steer_.vel = (right_steer_.pos - pos_prev) / deltaSeconds;

    // Update rear wheel positions and velocities
    // pos_prev = left_rear_wheel_.pos;
    // left_rear_wheel_.pos = left_rear_wheel_.calcEncAngle();
    // left_rear_wheel_.vel = (left_rear_wheel_.pos - pos_prev) / deltaSeconds;

    // pos_prev = right_rear_wheel_.pos;
    // right_rear_wheel_.pos = right_rear_wheel_.calcEncAngle();
    // right_rear_wheel_.vel = (right_rear_wheel_.pos - pos_prev) / deltaSeconds;

    return return_type::OK;
}

return_type AckDriveArduino::write(const rclcpp::Time & time, const rclcpp::Duration & period)
{
    const double WHEELBASE = 0.30;       // meters
    const double TRACK_WIDTH = 0.25;     // meters
    const double WHEEL_DIAMETER = 0.2032; // 8 inches in meters
    const double WHEEL_RADIUS = WHEEL_DIAMETER / 2.0;
    const double MAX_LINEAR_SPEED = 2.0;  // m/s (adjust based on your setup)
    const double MAX_ANGULAR_SPEED = MAX_LINEAR_SPEED / WHEEL_RADIUS; // rad/s

    double virtual_steering_angle = 0.0;
    
    if (std::abs(left_steer_.cmd) > 0.001 || std::abs(right_steer_.cmd) > 0.001) 
    {
        double inner_angle = (std::abs(left_steer_.cmd) > std::abs(right_steer_.cmd)) ? 
                             left_steer_.cmd : right_steer_.cmd;

        double tan_inner = std::tan(inner_angle);
        double R_center = WHEELBASE / tan_inner + (TRACK_WIDTH / 2.0) * (inner_angle / std::abs(inner_angle));
        virtual_steering_angle = std::atan2(WHEELBASE, R_center);
    }
    else
    {
        virtual_steering_angle = 0.0;
    }

    const double MIN_SERVO_ANGLE = 45.0;
    const double MAX_SERVO_ANGLE = 135.0;
    const double CENTER_SERVO_ANGLE = 90.0;
    const double MAX_STEERING_ANGLE = 0.52; // ~30 degrees in radians

    double servo_angle = CENTER_SERVO_ANGLE + 
                         (virtual_steering_angle / MAX_STEERING_ANGLE) * 
                         ((MAX_SERVO_ANGLE - MIN_SERVO_ANGLE) / 2.0);
    servo_angle = std::max(MIN_SERVO_ANGLE, std::min(MAX_SERVO_ANGLE, servo_angle));

    double avg_rear_velocity = (left_rear_wheel_.cmd + right_rear_wheel_.cmd) / 2.0;

    // === Convert angular velocity (rad/s) → PWM ===
    // PWM proportional to desired wheel linear speed
    double linear_speed = avg_rear_velocity * WHEEL_RADIUS; // m/s
    int pwm = static_cast<int>((linear_speed / MAX_LINEAR_SPEED) * 255.0);

    // Clamp to valid PWM range
    pwm = std::max(-255, std::min(255, pwm));

    RCLCPP_INFO(logger_, "=== Ackermann Steering Commands ===");
    RCLCPP_INFO(logger_, "Left Steering Angle:  %.4f rad (%.2f deg)", 
                left_steer_.cmd, left_steer_.cmd * 180.0 / M_PI);
    RCLCPP_INFO(logger_, "Right Steering Angle: %.4f rad (%.2f deg)", 
                right_steer_.cmd, right_steer_.cmd * 180.0 / M_PI);
    RCLCPP_INFO(logger_, "Virtual Center Angle: %.4f rad (%.2f deg)", 
                virtual_steering_angle, virtual_steering_angle * 180.0 / M_PI);
    RCLCPP_INFO(logger_, "---");
    RCLCPP_INFO(logger_, "Avg Rear Vel: %.4f rad/s | Linear: %.3f m/s | PWM: %d", 
                avg_rear_velocity, linear_speed, pwm);
    RCLCPP_INFO(logger_, "Servo Angle: %.2f deg", servo_angle);
    RCLCPP_INFO(logger_, "===================================");

    // Send to Arduino
    this->arduino_.setMotorValues(pwm, servo_angle);

    return return_type::OK;
}

}
#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
    ackdrive_arduino::AckDriveArduino, 
    hardware_interface::SystemInterface
)