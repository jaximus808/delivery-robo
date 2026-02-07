#!/usr/bin/env python3

"""Relay Ackermann controller odom and TF topics to globally expected names."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from rclpy.parameter import Parameter

from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage


class AckermannOdomBridge(Node):
    """Republish controller-scoped odom and TF topics under the conventional names."""

    def __init__(self) -> None:
        super().__init__("ackermann_odom_bridge")

        # Parameters make the bridge reusable if names change later.
        self.declare_parameter("input_odom_topic", "/ack_cont/odometry")
        self.declare_parameter("output_odom_topic", "/odom")
        self.declare_parameter("input_tf_topic", "/ack_cont/tf_odometry")
        self.declare_parameter("output_tf_topic", "/tf")
        if not self.has_parameter("use_sim_time"):
            self.declare_parameter("use_sim_time", True)

        input_odom = self.get_parameter("input_odom_topic").value
        output_odom = self.get_parameter("output_odom_topic").value
        input_tf = self.get_parameter("input_tf_topic").value
        output_tf = self.get_parameter("output_tf_topic").value
        use_sim_time = self.get_parameter("use_sim_time").value
        self.set_parameters([Parameter("use_sim_time", value=use_sim_time)])

        odom_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            durability=DurabilityPolicy.VOLATILE,
        )
        tf_sub_qos = QoSProfile(
            depth=100,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            durability=DurabilityPolicy.VOLATILE,
        )
        # Publish transforms reliably so RViz (which prefers RELIABLE) can subscribe without warnings.
        tf_pub_qos = QoSProfile(
            depth=100,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            durability=DurabilityPolicy.VOLATILE,
        )

        self._odom_pub = self.create_publisher(Odometry, output_odom, odom_qos)
        self._tf_pub = self.create_publisher(TFMessage, output_tf, tf_pub_qos)

        self.create_subscription(Odometry, input_odom, self._on_odom, odom_qos)
        self.create_subscription(TFMessage, input_tf, self._on_tf, tf_sub_qos)

        self.get_logger().info(
            f"Bridging odom from {input_odom} -> {output_odom} and TF from {input_tf} -> {output_tf}"
        )

    def _on_odom(self, msg: Odometry) -> None:
        self._odom_pub.publish(msg)

    def _on_tf(self, msg: TFMessage) -> None:
        self._tf_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = AckermannOdomBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
