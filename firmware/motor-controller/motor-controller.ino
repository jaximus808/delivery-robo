#include "commands.h"
#include "motor_driver.h"


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

// Reset command variables to parse a new command
void resetCommand();

// Error parsing command, send back an error over serial
void errorCommand();

// Go through buffer, parse and run commands as needed
void processBuffer();

void setup() {
  Serial.begin(BAUDRATE);
  // pinMode(LED_BUILTIN, OUTPUT);
  motorInit(); // initialize motors
  encoderInit(); //initialize encoder
}

void loop() {
  processBuffer();
  // motorUpdate(); // keep PID running
  Serial.println(getEncoder());
}

void runCommand() {
  switch (cmd) {
    case SET_DRIVE_PWM: // "m val1 val2"
      setDriveSpeed((int)arg1);
      setTurnAngle((int)arg2);
      Serial.print("Parsed - Vel: ");
      Serial.print((int)arg1);
      Serial.print(" | Angle: ");
      Serial.println((int)arg2);

      break;

    // case SET_DRIVE_VEL: // "v val"
    //   setDriveVel(arg1);
    //   break;

    // case SET_TURN_ANGLE: // "r val"
    //   setTurnAngle(arg1);
    //   break;

    case SET_PID: // "u kp:kd:ki:ko"
      // TODO: parse colon-delimited values and call setPidValues()
      break;

    case GET_ENCODER: // "e"
      Serial.print(getEncoder());
      break;

    case TEST_BLINK_ON: // "o"
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("test on");
      break;

    case TEST_BLINK_OFF: // "f"
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
    // New command/run command
    if (chr == NEW_COMMAND) {
      // Terminate arg array with null byte
      if (arg == 1) argv1[index] = '\0';
      else if (arg == 2) argv2[index] = '\0';
      // Convert arg array to double
      arg1 = atof(argv1);
      arg2 = atof(argv2);
      // Run command if a command is set
      if (cmd != '\0') runCommand();
      resetCommand();
    }
    // New arg
    else if (chr == NEW_ARG) {
      if (arg == 0) arg++;
      else if (arg == 1) {
        argv1[index] = '\0';
        arg++;
        index = 0;
      }
    }
    // Processing other characters
    else {
      if (arg == 0) {
        // Error if command is already set
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