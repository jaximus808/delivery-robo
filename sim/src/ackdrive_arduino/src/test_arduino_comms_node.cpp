#include "ackdrive_arduino/arduino_comms.h"
#include <rclcpp/rclcpp.hpp>

class TestNode : public rclcpp::Node {
public:
  TestNode() : Node("arduino_test") {
    comms_.setup("/dev/ttyUSB0", 57600, 1000);
    timer_ = create_wall_timer(std::chrono::seconds(1),
      [this]() {
        int left, right;
        comms_.readEncoderValues(left, right);
        RCLCPP_INFO(get_logger(), "Encoders: %d, %d", left, right);
        comms_.setMotorValues(100, 100);
      });
  }
private:
  ArduinoComms comms_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TestNode>());
  rclcpp::shutdown();
  return 0;
}
