#include "encoder_driver.h"


static volatile long encoderValue = 0;    // the current click count
unsigned long lastReportTime = 0;  // the last time data was reported to the Pi
const int reportInterval = 20;     // Report the count every 20 milliseconds
volatile int8_t lastEncoded = 0;

long getEncoder() {
  noInterrupts();      // prevent updateEncoder() from modifying value mid-read
  long encoderValueSteady = encoderValue;
  interrupts();
  return encoderValueSteady;
}

void encoderInit() {

  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);

  //Serial.begin(115200);

  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), updateEncoder, CHANGE);
}
//void loop() {

 // if (millis() - lastReportTime >= reportInterval) {

    //long encoderValueSteady;
    //noInterrupts();
    //encoderValueSteady = encoderValue;
    //interrupts();

    //String myString = String(encoderValueSteady);

   // Serial.println("*" + encoderValueSteady + "*");
   // lastReportTime = millis();
  //}
  //if (Serial.available() > 0) {  // checks if the Pi sent a command
   // char command = Serial.read();
    //if (command == 'r') {  // checks for the specific command "r" meaining "reset"
      //encoderValue = 0;    // Reset the count
    //}
  //}
//}

void updateEncoder() {

  int MSB = digitalRead(ENCODER_CLK);
  int LSB = digitalRead(ENCODER_DT);

  int encoded = (MSB << 1) | LSB;

  int sum = (lastEncoded << 2) | encoded;

  if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) {
    encoderValue++;
  }
  if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) {
    encoderValue--;
  }
  lastEncoded = encoded;
}

void resetEncoder() {
  noInterrupts();
  encoderValue = 0;
  interrupts();
}