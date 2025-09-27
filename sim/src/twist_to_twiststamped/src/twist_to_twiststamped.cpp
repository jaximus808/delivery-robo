#include "twist_to_twiststamped/twist_to_twiststamped.hpp"

TwistToTwistStampedNode::TwistToTwistStampedNode() : Node("twist_to_twiststamped") {
    // Declare parameters
    this->declare_parameter<std::string>("input_topic", "/cmd_vel");
    this->declare_parameter<std::string>("output_topic", "/cmd_vel_stamped");
    this->declare_parameter<std::string>("frame_id", "base_link");

    // Get parameters
    std::string input_topic = this->get_parameter("input_topic").as_string();
    std::string output_topic = this->get_parameter("output_topic").as_string();
    frame_id_ = this->get_parameter("frame_id").as_string();

    // Subscriber and Publisher
    twist_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
        input_topic, 10,
        std::bind(&TwistToTwistStampedNode::twistCallback, this, std::placeholders::_1));

    twist_stamped_pub_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(output_topic, 10);

    RCLCPP_INFO(this->get_logger(), "Node initialized. Subscribing to '%s' and publishing to '%s'.",
                input_topic.c_str(), output_topic.c_str());
}

void TwistToTwistStampedNode::twistCallback(const geometry_msgs::msg::Twist::SharedPtr twist_msg) {
    // Create and publish TwistStamped message
    auto twist_stamped_msg = geometry_msgs::msg::TwistStamped();
    twist_stamped_msg.header.stamp = this->get_clock()->now();
    twist_stamped_msg.header.frame_id = frame_id_;
    twist_stamped_msg.twist = *twist_msg;

    twist_stamped_pub_->publish(twist_stamped_msg);
}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<TwistToTwistStampedNode>());
    rclcpp::shutdown();
    return 0;
}
