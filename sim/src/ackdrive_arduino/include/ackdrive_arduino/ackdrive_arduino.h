#ifndef ACKDRIVE_ARDUINO_H
#define ACKDRIVE_ARDUINO_H

#include "rclcpp/rclcpp.hpp"
#include <cstring>
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "arduino_comms.h"
#include "config.h"
#include "wheel.h"

using hardware_interface::CallbackReturn;
using hardware_interface::return_type;

namespace ackdrive_arduino  // ADD THIS!
{
class AckDriveArduino : public hardware_interface::SystemInterface {
public:
    AckDriveArduino();
    
    CallbackReturn on_init(const hardware_interface::HardwareInfo & info) override;
    
    std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
    
    std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;
    
    CallbackReturn on_activate(const rclcpp_lifecycle::State & previous_state) override;
    
    CallbackReturn on_deactivate(const rclcpp_lifecycle::State & previous_state) override;
    
    return_type read(const rclcpp::Time & time, const rclcpp::Duration & period) override;
    
    return_type write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
    Config cfg_;
    ArduinoComms arduino_;
    
    // Four separate joints
    Wheel left_steer_;          // left_wheel_hinge
    Wheel right_steer_;         // right_wheel_hinge
    Wheel left_rear_wheel_;     // left_rear_wheel_joint
    Wheel right_rear_wheel_;    // right_rear_wheel_joint
    
    rclcpp::Logger logger_;
    std::chrono::time_point<std::chrono::system_clock> time_;
};
}
#endif // ACKDRIVE_ARDUINO_REAL_ROBOT_H