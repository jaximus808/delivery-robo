#ifndef ACKDRIVE_ARDUINO_REAL_ROBOT_H
#define ACKDRIVE_ARDUINO_REAL_ROBOT_H

#include <string>

struct Config {
  std::string left_steer_joint = "left_steer_joint";
  std::string right_steer_joint = "right_steer_joint";
  std::string left_rear_wheel_joint = "left_rear_wheel_joint";
  std::string right_rear_wheel_joint = "right_rear_wheel_joint";
  float loop_rate = 30;
  std::string device = "/dev/ttyUSB0";
  int baud_rate = 57600;
  int timeout = 1000;
  int enc_counts_per_rev = 1920;
};

#endif // ACKDRIVE_ARDUINO_REAL_ROBOT_H
