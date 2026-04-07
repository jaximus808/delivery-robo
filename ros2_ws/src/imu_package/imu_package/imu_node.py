import board
import busio
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR, BNO_REPORT_ACCELEROMETER, BNO_REPORT_GYROSCOPE
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

        self.bno.enable_feature(BNO_REPORT_ACCELEROMETER)
        self.bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
        self.bno.enable_feature(BNO_REPORT_GYROSCOPE)


    def timer_callback(self):
        msg = Imu()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        quat_i, quat_j, quat_k, quat_real = self.bno.quaternion
        accel_x, accel_y, accel_z = self.bno.acceleration
        gyro_x, gyro_y, gyro_z = self.bno.gyro
        
        msg.orientation.x = quat_i
        msg.orientation.y = quat_j
        msg.orientation.z = quat_k
        msg.orientation.w = quat_real

        msg.linear_acceleration.x = accel_x
        msg.linear_acceleration.y = accel_y
        msg.linear_acceleration.z = accel_z

        msg.angular_velocity.x = gyro_x
        msg.angular_velocity.y = gyro_y
        msg.angular_velocity.z = gyro_z

        msg.orientation_covariance = [1.1912989969130138e-08, 7.458051230937461e-11, -7.714913773216416e-10, 7.458051230937461e-11, 4.578213663520167e-09, -6.144561660125438e-10, -7.714913773216416e-10, -6.144561660125438e-10, 7.026383185562511e-08]
        msg.angular_velocity_covariance = [1.5105170688371545e-06, -1.1745603636778752e-08, -1.9045815937753488e-07, -1.1745603636778752e-08, 4.2638258674014977e-07, -2.2517018702222813e-08, -1.9045815937753488e-07, -2.2517018702222813e-08, 1.0818464270587167e-06]
        msg.linear_acceleration_covariance = [3.525993954008387e-06, 1.2365802041646368e-08, 8.610262162331126e-08, 1.2365802041646368e-08, 2.0331439523472155e-05, -1.1739878728426825e-06, 8.610262162331126e-08, -1.1739878728426825e-06, 0.000130014958651195]

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
