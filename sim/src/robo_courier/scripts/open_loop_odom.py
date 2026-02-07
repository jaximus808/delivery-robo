#!/usr/bin/env python3
"""Simple open-loop odometry integrator for simulation.

Integrates Twist commands (e.g. from the Ackermann controller reference) to
publish a nav_msgs/Odometry topic and the corresponding TF transform between
odom and base_link. Keeps SLAM happy even when the hardware stack does not
provide wheel-encoder based odometry yet.
"""

from math import cos, sin
from typing import Tuple

import rclpy
from rclpy.node import Node
from rclpy.time import Time

from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster


class OpenLoopOdomNode(Node):
    def __init__(self) -> None:
        super().__init__('open_loop_odom')
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', False)
        self.declare_parameter('input_topic', '/ack_cont/reference')
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('publish_tf', True)

        self.input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.odom_topic = self.get_parameter('odom_topic').get_parameter_value().string_value
        self.odom_frame = self.get_parameter('odom_frame').get_parameter_value().string_value
        self.base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        self.publish_tf = self.get_parameter('publish_tf').get_parameter_value().bool_value
        self.use_sim_time_param = self.get_parameter('use_sim_time').get_parameter_value().bool_value

        # Integrated pose state
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_time = None
        self.last_twist = Twist()

        self.odom_pub = self.create_publisher(Odometry, self.odom_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(TwistStamped, self.input_topic, self._twist_callback, 10)
        self.get_logger().info(
            f'Open-loop odometry active: {self.odom_frame} -> {self.base_frame} (input: {self.input_topic})'
        )

        # Keep publishing even when no new command arrives so TF stays alive.
        self.keep_alive_timer = self.create_timer(0.1, self._publish_keep_alive)

    def _twist_callback(self, msg: TwistStamped) -> None:
        if self.use_sim_time_param and not self.get_clock().ros_time_is_active:
            # Avoid mixing wall time and sim time before /clock is available.
            return

        now_time = self.get_clock().now()
        self._integrate_to(now_time)

        self.last_twist = msg.twist
        self._publish_state(now_time.to_msg(), self.last_twist)

    def _publish_keep_alive(self) -> None:
        if self.use_sim_time_param and not self.get_clock().ros_time_is_active:
            return

        now_time = self.get_clock().now()

        self._integrate_to(now_time)

        if self.last_time is None:
            self._publish_state(now_time.to_msg(), Twist())
            return

        self._publish_state(now_time.to_msg(), self.last_twist)

    def _publish_state(self, stamp, twist: Twist) -> None:
        quat = self._yaw_to_quaternion(self.theta)

        odom_msg = Odometry()
        odom_msg.header.stamp = stamp
        odom_msg.header.frame_id = self.odom_frame
        odom_msg.child_frame_id = self.base_frame
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.orientation.x = quat[0]
        odom_msg.pose.pose.orientation.y = quat[1]
        odom_msg.pose.pose.orientation.z = quat[2]
        odom_msg.pose.pose.orientation.w = quat[3]
        odom_msg.twist.twist = twist
        self.odom_pub.publish(odom_msg)

        if self.publish_tf:
            transform = TransformStamped()
            transform.header.stamp = stamp
            transform.header.frame_id = self.odom_frame
            transform.child_frame_id = self.base_frame
            transform.transform.translation.x = self.x
            transform.transform.translation.y = self.y
            transform.transform.translation.z = 0.0
            transform.transform.rotation.x = quat[0]
            transform.transform.rotation.y = quat[1]
            transform.transform.rotation.z = quat[2]
            transform.transform.rotation.w = quat[3]
            self.tf_broadcaster.sendTransform(transform)
    @staticmethod
    def _yaw_to_quaternion(yaw: float) -> Tuple[float, float, float, float]:
        half_yaw = yaw * 0.5
        return (0.0, 0.0, sin(half_yaw), cos(half_yaw))

    def _integrate_to(self, target_time: Time) -> None:
        """Advance the integrated pose up to the provided time using the last command."""
        if self.last_time is None:
            self.last_time = target_time
            return

        dt = target_time - self.last_time
        dt_s = dt.nanoseconds / 1e9

        if dt_s <= 0.0:
            self.last_time = target_time
            return

        v = self.last_twist.linear.x
        omega = self.last_twist.angular.z

        self.theta += omega * dt_s
        self.x += v * cos(self.theta) * dt_s
        self.y += v * sin(self.theta) * dt_s

        self.last_time = target_time


def main() -> None:
    rclpy.init()
    node = OpenLoopOdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
