// Encoder pins
#define DRIVE_ENCODER_A 2
#define DRIVE_ENCODER_B 3
#define TURN_ENCODER 0
#define ENCODER_CLK 2
#define ENCODER_DT 3

double getDriveVel();

double getTurnAngle();

long getEncoderCount();

void encoderInit();