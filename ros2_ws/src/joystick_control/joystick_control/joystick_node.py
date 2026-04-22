import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import serial
import time

class JoystickNode(Node):
    def __init__(self):
        super().__init__('joystick_node')
        
        # Declare parameters
        self.declare_parameter('device', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 57600)
        self.declare_parameter('timeout', 1.0)
        self.declare_parameter('verbose', False)
        
        self.device = self.get_parameter('device').get_parameter_value().string_value
        self.baud_rate = self.get_parameter('baud_rate').get_parameter_value().integer_value
        self.timeout = self.get_parameter('timeout').get_parameter_value().double_value
        self.verbose = self.get_parameter('verbose').get_parameter_value().bool_value
        
        # Constants
        self.MAX_PWM = 220.0
        self.MAX_STEER = 45.0
        self.STEER_ORIGIN = 45.0
        
        # Initialize Serial
        try:
            self.ser = serial.Serial(self.device, self.baud_rate, timeout=self.timeout)
            self.get_logger().info(f"Opened serial port: {self.device} at {self.baud_rate}")
        except Exception as e:
            self.get_logger().error(f"Failed to open serial port {self.device}: {e}")
            self.ser = None

        # Subscription
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
        
        self.get_logger().info("Joystick control node (Python) started.")

    def joy_callback(self, msg):
        # Example axes mapping from C++ code:
        # steer = axes[2] (left stick X in their code)
        # throttle = axes[1] (left stick Y)
        
        # Checking if axes are available
        if len(msg.axes) < 3:
            return

        steer = msg.axes[2]
        throttle = msg.axes[1]
        
        # Original C++ node also reads a button, though it doesn't use it.
        # Button 9 is typically "Start" or "Options" on many controllers, but it's labeled "A" in the comment.
        if len(msg.buttons) > 9:
            a_button = msg.buttons[9]
        
        pwm = throttle * self.MAX_PWM
        servo_angle = self.STEER_ORIGIN + steer * self.MAX_STEER
        
        if self.verbose:
            self.get_logger().info(f"Throttle: {throttle:.2f} | Steer: {steer:.2f}")
            self.get_logger().info(f"PWM: {pwm:.2f} | Angle: {servo_angle:.2f}")

        if self.ser and self.ser.is_open:
            command = f"m {pwm:.2f} {servo_angle:.2f}\r"
            try:
                self.ser.write(command.encode())
            except Exception as e:
                self.get_logger().error(f"Error writing to serial: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = JoystickNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
