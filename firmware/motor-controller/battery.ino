// Battery Voltage Monitor with I2C LCD
// Reads battery voltage through voltage divider (2x 10K resistors)
// Displays on 16x2 LCD and alerts if voltage is low

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize LCD (address, columns, rows)
LiquidCrystal_I2C lcd(I2C_ADDR, 16, 2);

unsigned long lastUpdate = 0;

void batteryUpdate() {
  // Update display at regular intervals
  if (millis() - lastUpdate >= UPDATE_INTERVAL) {
    lastUpdate = millis();
    
    float voltage = readVoltage();
    displayVoltage(voltage);
    checkLowBattery(voltage);
  }
}

void batteryInit() {
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  
  // Initialize LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Display startup message
  lcd.setCursor(0, 0);
  lcd.print("Battery Monitor");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");
  delay(2000);
  lcd.clear();
}

// Read voltage with averaging for stability
float readVoltage() {
  long sum = 0;
  
  // Take multiple samples and average
  for (int i = 0; i < SAMPLES; i++) {
    sum += analogRead(ANALOG_PIN);
    delay(SAMPLE_DELAY);
  }
  
  float average = sum / (float)SAMPLES;
  
  // Convert to voltage
  // Arduino ADC: 0-1023 represents 0-5V
  // Multiply by divider ratio to get actual battery voltage
  float voltage = (average * 5.0 / 1023.0) * VOLTAGE_DIVIDER;
  
  return voltage;
}

// Display voltage on LCD
void displayVoltage(float voltage) {
  lcd.setCursor(0, 0);
  lcd.print("Battery Voltage:");
  
  lcd.setCursor(0, 1);
  lcd.print("   ");  // Clear previous value
  lcd.setCursor(0, 1);
  if(((voltage/Battery_MAX)*100) > 1){
    lcd.print(100);
    lcd.print(" %    ");
  }else{
    lcd.print((voltage/Battery_MAX)*100, 2);  // Show 2 decimal places
    lcd.print(" %    ");    // Extra spaces to clear old characters
  }
  // Show battery status high,med,low
  lcd.setCursor(10, 1);
  if ((voltage/Battery_MAX) >= HIGH_VOLTAGE) { //Above or at 0.7
    lcd.print("HIGH");
  } else if ((voltage/Battery_MAX)>= MED_VOLTAGE) { //Above or at 0.35
    lcd.print("MEDIUM");
  } else if ((voltage/Battery_MAX) < MED_VOLTAGE){ //Below 0.35
    lcd.print("LOW!");
  }
}

// Check for low battery and activate LED warning
void checkLowBattery(float voltage) {
  if (voltage < MED_VOLTAGE) {
    // Blink LED for critical battery
    digitalWrite(LED_PIN, (millis() / 250) % 2);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
}

// Optional: Calibration function
// Call this if your readings are off
float calibrateVoltage(float rawVoltage) {
  // Measure actual voltage with multimeter
  // Adjust this multiplier if readings are consistently off
  const float CALIBRATION_FACTOR = 1.0;  // Adjust as needed
  return rawVoltage * CALIBRATION_FACTOR;
}
