// Define motor driver pins
#define IN1 4
#define IN2 5
#define ENA 9 // PWM pin for speed control

void setup() {
  // Set motor driver pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
}

void loop() {
  // Set motor A direction to forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  // Set speed to 50%
  analogWrite(ENA, 127);
  delay(1000); // Run for 2 seconds
  analogWrite(ENA, 60);
  delay(1000);

  // Set motor A direction to reverse
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  // Set speed to 50%
  analogWrite(ENA, 60);
  delay(1000); // Run for 2 seconds
  analogWrite(ENA, 200);
  delay(1000);

  // Stop motor A
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  delay(1000); // Stop for 1 second
}
