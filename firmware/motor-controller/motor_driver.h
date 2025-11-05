// Motor pins
#define DRIVE_MOTOR_IN1 2
#define DRIVE_MOTOR_IN2 3
#define DRIVE_MOTOR_PWM 5
#define TURN_SERVO 10

#define KP_V 2
#define KI_V 5
#define KD_V 1
#define KP_T 2
#define KI_T 5
#define KD_T 1


void setMotorPWM(int motor, int pwm);

void setDriveVel(double speed);

void setTurnAngle(double angle);

void motorInit();

void motorUpdate();