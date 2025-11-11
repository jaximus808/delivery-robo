#include "PID_v1.h"

#include "motor_driver.h"
#include "encoder_driver.h"


double vel_input, vel_output, vel_target;
double turn_input, turn_output, turn_target;

PID vel_control(&vel_input, &vel_output, &vel_target, KP_V, KI_V, KD_V, DIRECT);
PID turn_control(&turn_input, &turn_output, &turn_target, KP_T, KI_T, KD_T, DIRECT);


void setMotorPWM(int motor, int pwm) {
    // Reverse direction and pwm if negative
    int dir = HIGH;
    if (pwm < 0) {
        pwm = -pwm;
        dir = LOW;
    }

    // Set motor direction
    if (motor == DRIVE_MOTOR) {
        digitalWrite(DRIVE_MOTOR_IN1, dir);
        digitalWrite(DRIVE_MOTOR_IN2, abs(dir-1)); // opposite of dir
    } else if (motor == TURN_MOTOR) {
        digitalWrite(TURN_MOTOR_IN1, HIGH);
        digitalWrite(TURN_MOTOR_IN2, abs(dir-1));
    }

    // Write pwm
    analogWrite(motor, pwm);
}

void setDriveVel(double speed) {
    vel_target = speed;
}

void setTurnAngle(double angle) {
    turn_target = angle;
}

void motorInit() {
    pinMode(DRIVE_MOTOR_IN1, OUTPUT);
    pinMode(DRIVE_MOTOR_IN2, OUTPUT);
    // digitalWrite(DRIVE_MOTOR_PWM, HIGH);
    digitalWrite(TURN_SERVO, LOW);  // Ensure LOW before attach
    delay(100);
    turnServo.attach(TURN_SERVO);
    turnServo.write(90); 
    // pinMode(TURN_MOTOR_PWM, OUTPUT);
    // pinMode(TURN_MOTOR_IN1, OUTPUT);
    // pinMode(TURN_MOTOR_IN2, OUTPUT);
    // Serial.println("REAEDY!");
}

void motorUpdate() {
    vel_input = getDriveVel();
    vel_control.Compute();
    setMotorPWM(DRIVE_MOTOR, vel_output);

    turn_input = getTurnAngle();
    turn_control.Compute();
    setMotorPWM(TURN_MOTOR, turn_output);
}