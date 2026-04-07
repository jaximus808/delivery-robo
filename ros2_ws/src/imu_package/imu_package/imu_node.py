import board
import busio
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR
from adafruit_bno08x import BNO_REPORT_ACCELEROMETER
from adafruit_bno08x.i2c import BNO08X_I2C
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node')
        self.publisher_ = self.create_publisher(Imu, 'imu/data', 10)

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info("IMU node has started publishing!!!!!!!")

        REPORT_INTERVAL = 100000
        i2c = busio.I2C(board.SCL, board.SDA)
        self.bno = BNO08X_I2C(i2c)

        self.bno.enable_feature(BNO_REPORT_ACCELEROMETER, REPORT_INTERVAL)
        self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR, REPORT_INTERVAL)


    def timer_callback(self):
        msg = Imu()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        quat_i, quat_j, quat_k, quat_real = self.bno.quaternion
        accel_x, accel_y, accel_z = self.bno.acceleration
        
        msg.orientation.w = quat_real

        msg.linear_acceleration.x = accel_x
        msg.linear_acceleration.y = accel_y
        msg.linear_acceleration.z = accel_z

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
