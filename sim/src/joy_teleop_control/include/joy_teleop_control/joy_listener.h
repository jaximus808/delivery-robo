#ifndef JOYSTICK_TELEOP__JOY_LISTENER_HPP_
#define JOYSTICK_TELEOP__JOY_LISTENER_HPP_

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "arduino_comms/arduino_comms.h"
#include "config.h"

const double MAX_PWM = 220.0;
const double MAX_STEER = 45.0;
const double STEER_ORIGIN = 90.0;

class JoyListener : public rclcpp::Node
{
public:
    JoyListener();

private:
    void joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg);

    rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr joy_sub_;
    ArduinoComms arduino_;
    Config cfg_;
    bool verbose_;
};

#endif // JOYSTICK_TELEOP__JOY_LISTENER_HPP_
