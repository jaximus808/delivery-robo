// Define the pins connected to the encoder's outputs
#define ENCODER_CLK 2  // Channel A (connects to interrupt pin)
#define ENCODER_DT 3   // Channel B (connects to interrupt pin)

volatile long encoderValue = 0;  // the current click count
unsigned long lastReportTime = 0; // the last time data was reported to the Pi
const int reportInterval = 20; // Report the count every 20 milliseconds
//long previousValue = 0;          // the old click count
//long lastReportedValue = 0;
//unsigned long previousTime = 0;  // the last time snapshot taken
//const int sampleTime = 50;       // setting a sample time interval to 50 milliseconds (will be used to calculate velocity)

void setup() {
  // Set encoder pins as inputs with internal pull-up resistors
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);

  // Initialize Serial Monitor
  Serial.begin(115200); // setting baud rate

  // Attach interrupts to the encoder pins
  // Call the 'updateEncoder' function whenever a change is detected
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_DT), updateEncoder, CHANGE);
}

void loop() {
  //unsigned long currentTime = millis();

// Check the time to determine whether to report data to the Pi
  if (millis() - lastReportTime >= reportInterval) {
    Serial.println(encoderValue);
    lastReportTime = millis();
  }

  if (Serial.available() > 0) { // checks if the Pi sent a command
    char command = Serial.read();
    if (command == 'r') { // checks for the specific command "r" meaining "reset"
      encoderValue = 0; // Reset the count
    }
  }
}

//Initial distance/velocity calculations, not needed for the Arduino because the Pi will be doing the work

  //if (encoderValue != lastReportedValue) {
    //Serial.println(encoderValue);
   // lastReportedValue = encoderValue;
  //}

  //if (currentTime - previousTime >= sampleTime) {  // the calculation only runs when a minimum of 50 milliseconds have elapsed
    //long positionChange = encoderValue - previousValue;
   // float currentVelocity = positionChange * 1000 / (currentTime - previousTime);  //the *1000 converts from counts/millisecond to counts/second
    // print to Serial Monitor
  //  Serial.print("Velocity: ");
   // Serial.print(velocity);
   // Serial.println(" counts per second");
    //  previousValue = encoderValue;
   // previousTime = currentTime;
 // }
//}

//This function is called whenever an interrupt occurs
void updateEncoder() {
  // Read the current state of the two pins
  int clkState = digitalRead(ENCODER_CLK);
  int dtState = digitalRead(ENCODER_DT);

  // Determine direction based on the state of the other pin
  if (clkState != dtState) {
    encoderValue++;  // Clockwise
  } else {
    encoderValue--;  // Counter-clockwise
  }
}