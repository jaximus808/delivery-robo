// Define the pins connected to the encoder's outputs
#define ENCODER_CLK 2  // Channel A (connects to interrupt pin)
#define ENCODER_DT 3   // Channel B (connects to interrupt pin)

volatile long encoderValue = 0;  // the current click count
unsigned long lastReportTime = 0; // the last time data was reported to the Pi
const int reportInterval = 20; // Report the count every 20 milliseconds
volatile int8_t lastEncoded = 0;

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

    // make a copy of encoderValue without volatility
long encoderValueSteady;
    noInterrupts();
    encoderValueSteady = encoderValue;
    interrupts();

    // Convert non-volatile encoderValue to a string
    String myString = String(encoderValueSteady);

    Serial.println("*" + encoderValueSteady + "*");
    lastReportTime = millis();
  }

  if (Serial.available() > 0) { // checks if the Pi sent a command
    char command = Serial.read();
    if (command == 'r') { // checks for the specific command "r" meaining "reset"
      encoderValue = 0; // Reset the count
    }
  }
}

//This function is called whenever an interrupt occurs
//void updateEncoder() {
  // Read the current state of the two pins
  //int clkState = digitalRead(ENCODER_CLK);
  //int dtState = digitalRead(ENCODER_DT);

  // Determine direction based on the state of the other pin
 // if (clkState != dtState) {
 //   encoderValue++;  // Clockwise
 // } else {
  //  encoderValue--;  // Counter-clockwise
  //}
//}

// This function is called whenever an interrupt occurs
void updateEncoder() {
  // Read the current state of the two pins
  int MSB = digitalRead(ENCODER_CLK); // Channel A
  int LSB = digitalRead(ENCODER_DT); // Channel B

  // Convert the two-bit state to a single number (0, 1, 2, or 3)
  int encoded = (MSB << 1) | LSB; 

  // Combine the previous state and new state into a 4-bit number
  // (Bits 3 & 2 are old state, Bits 1 & 0 are new state)
  int sum = (lastEncoded << 2) | encoded;
  // Use a state-table to determine direction
  // This looks complex, but it's just a fast way to check valid transitions
  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) {
    encoderValue++; // Clockwise
  }
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) {
    encoderValue--; // Counter-clockwise
  }

  // Store the new state as the "last" state for the next interrupt
  lastEncoded = encoded; 
}