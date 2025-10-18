#include <Arduino.h>

#include <commands.h>
#include <motor_driver.h>


#define BAUDRATE 57600


/* Command parsing variables */

// A pair of varibles to help parse serial commands (thanks Fergs)
int arg = 0;
int index = 0;

// Variable to hold an input character
char chr;

// Variable to hold the current single-character command
char cmd;

// Character arrays to hold the first and second arguments
char argv1[ARG_MAX_LEN];
char argv2[ARG_MAX_LEN];

// The arguments converted to doubles
double arg1;
double arg2;


// Run command based on currently parsed command:
void runCommand();

void resetCommand();

// Error parsing command, send back an error over serial
void errorCommand();

// Go through buffer, parse and run commands as needed
void processBuffer();

void setup() {
  Serial.begin(BAUDRATE);
  pinMode(LED_BUILTIN, OUTPUT);
  resetCommand();
}

void loop() {
  processBuffer();
}

void runCommand() {
  switch (cmd) {
  case SET_MOTOR_PWM:
    //TODO
  case SET_DRIVE_VEL:
    //TODO
  case SET_TURNING_POS:
    //TODO
  case GET_ENCODER:
    //TODO
  case TEST_BLINK_ON:
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("test on");
    Serial.println(String(arg1, 5));
    Serial.println(String(arg2, 5));
    break;
  case TEST_BLINK_OFF:
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("test off");
    break;
  default:
    errorCommand();
  }
}

void resetCommand() {
  arg = 0;
  index = 0;
  cmd = '\0';
  memset(argv1, 0, sizeof(argv1));
  memset(argv2, 0, sizeof(argv2));
  arg1 = 0;
  arg2 = 0;
}

void errorCommand() {
  Serial.print(ERROR_RES);
  Serial.print(NEW_COMMAND);
  resetCommand();
}

void processBuffer() {
  while (Serial.available() > 0) {
    chr = Serial.read();

    if (chr == NEW_COMMAND) {
      if (arg == 1) argv1[index] = '\0';
      else if (arg == 2) argv2[index] = '\0';
      arg1 = atof(argv1);
      arg2 = atof(argv2);
      if (cmd != '\0') runCommand();
      resetCommand();
    }

    else if (chr == NEW_ARG) {
      if (arg == 0) arg++;
      else if (arg == 1) {
        argv1[index] = '\0';
        arg++;
        index = 0;
      }
    }

    else {
      if (arg == 0) {
        if (cmd != '\0') errorCommand();
        else cmd = chr;
      } else if (arg == 1) {
        argv1[index] = chr;
        index++;
      } else if (arg == 2) {
        argv2[index] = chr;
        index++;
      }

      if (index == ARG_MAX_LEN) errorCommand();
    }
  }
}