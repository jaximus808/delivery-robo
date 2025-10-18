#include <Arduino.h>
#include <PID_v1.h>

#include <motor_driver.h>
#include <encoder_driver.h>


double vel_input, vel_output, vel_target;
double turn_input, turn_output, turn_target;

PID vel_control(&vel_input, &vel_output, &vel_target, KP_V, KI_V, KD_V, DIRECT);
PID turn_control(&turn_input, &turn_output, &turn_target, KP_T, KI_T, KD_T, DIRECT);


void setMotorPWM(int motor, int pwm) {
    analogWrite(motor, pwm);
}

void setDriveVel(double speed) {
    vel_target = speed;
}

void setTurnAngle(double angle) {
    turn_target = angle;
}

void motorInit() {
    vel_input = getDriveVel();
    vel_target = vel_input;
    vel_control.SetMode(AUTOMATIC);

    turn_input = getTurnAngle();
    turn_target = turn_input;
    turn_control.SetMode(AUTOMATIC);
}

void motorUpdate() {
    vel_input = getDriveVel();
    vel_control.Compute();
    setMotorPWM(DRIVE_MOTOR, vel_output);

    turn_input = getTurnAngle();
    turn_control.Compute();
    setMotorPWM(TURN_MOTOR, turn_output);
}