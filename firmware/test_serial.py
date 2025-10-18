# Script to test serial connection with arduino

import serial
import time

PORT = "/dev/ttyUSB0"   # change if needed (e.g., COM3 on Windows)
BAUD = 57600            # must match Serial.begin() on Arduino

# open the serial connection
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # give the Arduino time to reset

print(f"Connected to {PORT} at {BAUD} baud.")
print("Type commands to send to Arduino. Type 'exit' to quit.")

try:
    while True:
        cmd = input(">>> ")  # user input
        if cmd.lower() in ("exit", "quit"):
            break
        ser.write((cmd + "").encode())  # send to Arduino

        time.sleep(0.1)  # short delay for response
        while ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(f"< {line}")

except KeyboardInterrupt:
    pass
finally:
    ser.close()
    print("Serial connection closed.")