#include "joy_teleop_control/joy_listener.h"

JoyListener::JoyListener()
    : Node("joy_listener")
{
    joy_sub_ = this->create_subscription<sensor_msgs::msg::Joy>(
        "joy",
        10,
        std::bind(&JoyListener::joy_callback, this, std::placeholders::_1)
    );
    arduino_.setup(cfg_.device, cfg_.baud_rate, cfg_.timeout);  

    RCLCPP_INFO(this->get_logger(), "Joystick teleop node started (header/cpp split).");
}

void JoyListener::joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg)
{
    // Example axes (you can remap however you want)
    double steer = msg->axes[2];     // left stick X
    double throttle = msg->axes[1];  // left stick Y

    bool a_button = msg->buttons[9];

    double pwm = throttle*MAX_PWM;

    double servo_angle = STEER_ORIGIN + steer*MAX_STEER;

    RCLCPP_INFO(this->get_logger(),
                "Throttle: %.2f | Steer: %.2f | A: %d",
                throttle, steer, a_button);


    RCLCPP_INFO(this->get_logger(),
                "PWM: %.2f | Angle: %.2f ",
                pwm, servo_angle);

    
    this->arduino_.setMotorValues(pwm, servo_angle);
    // TODO: Insert your serial write here
    // send_serial(steer, throttle);
}

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<JoyListener>());
    rclcpp::shutdown();
    return 0;
}
