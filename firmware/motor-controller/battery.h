// Configuration
#define I2C_ADDR          0x27    // Change to your LCD address (use I2C scanner)
#define ANALOG_PIN        A0      // Voltage divider input
#define LED_PIN           13      // Low battery warning LED
#define HIGH_VOLTAGE      .7
#define MED_VOLTAGE       .35    // Low battery threshold (volts)
#define VOLTAGE_DIVIDER   3.0     // Divider ratio (both resistors equal = 2.0)
#define SAMPLES           10      // Number of readings to average
#define SAMPLE_DELAY      10      // Delay between samples (ms)
#define UPDATE_INTERVAL   500     // Display update interval (ms)
#define Battery_MAX       12      // Total Battery Value (V)


void batteryInit();

float readVoltage();

void displayVoltage(float voltage);

void checkLowBattery(float voltage);

float calibrateVoltage(float rawVoltage);