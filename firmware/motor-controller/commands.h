#ifndef COMMANDS_H
#define COMMANDS_H

#define ARG_MAX_LEN 16       // max chars in an argument
#define NEW_COMMAND '\r'     // matches ArduinoComms termination
#define NEW_ARG ' '          // argument separator
#define ERROR_RES 'X'        // error response

// Motor control
#define SET_DRIVE_PWM 'm'    // "m val1 val2"
#define SET_DRIVE_VEL 'v'    // "v val"
#define SET_TURN_ANGLE 'r'   // "r val"
#define SET_PID 'u'          // "u kp:kd:ki:ko"

// Sensors / testing
#define GET_ENCODER 'e'
#define TEST_BLINK_ON 'o'
#define TEST_BLINK_OFF 'f'

#endif
