#include "encoder_driver.h"


volatile long encoder_value = 0;

double getDriveVel() {
    return 0.0;
}

double getTurnAngle() {
    return 0.0;
}

long getEncoderCount() {
    noInterrupts();
    long encoder_value_steady = encoder_value;
    interrupts();
    return encoder_value_steady;
}

void encoderInit() {
    pinMode(DRIVE_ENCODER_A, INPUT_PULLUP);
    pinMode(DRIVE_ENCODER_B, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(DRIVE_ENCODER_A), updateEncoder, CHANGE);
    attachInterrupt(digitalPinToInterrupt(DRIVE_ENCODER_B), updateEncoder, CHANGE);
}

void updateEncoder() {
  // Read the current state of the two pins
  int clkState = digitalRead(DRIVE_ENCODER_A);
  int dtState = digitalRead(DRIVE_ENCODER_B);

  // Determine direction based on the state of the other pin
  if (clkState != dtState) {
    encoder_value++;  // Clockwise
  } else {
    encoder_value--;  // Counter-clockwise
  }
}