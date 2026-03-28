#include <SPI.h>
#include <AS5047P.h>

// CS pin 9, SPI speed default from library header (can pass a custom speed)
AS5047P as5047p(9);

void setup() {
  Serial.begin(115200);
  // Initialize SPI via library and verify connectivity
  if (!as5047p.initSPI()) {
    Serial.println("AS5047P init failed. Check wiring and power.");
    while (true) { delay(1000); }
  }
}

void loop() {
  // Read 14-bit angle (degrees) with DAE compensation
  float deg = as5047p.readAngleDegree(true);
  Serial.print("Angle (deg): ");
  Serial.println(deg, 3);

  // Read magnitude
  uint16_t mag = as5047p.readMagnitude();
  Serial.print("Magnitude: ");
  Serial.println(mag);

  delay(500);
}
