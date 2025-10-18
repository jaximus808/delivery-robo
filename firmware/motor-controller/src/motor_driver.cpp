#include <Arduino.h>

void setMotorPWM(int motor, int pwm) {
    analogWrite(motor, pwm);
}