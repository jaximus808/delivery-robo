#ifndef TWIST_TO_TWISTSTAMPED_NODE_HPP_
#define TWIST_TO_TWISTSTAMPED_NODE_HPP_

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

class TwistToTwistStampedNode : public rclcpp::Node {
public:
    TwistToTwistStampedNode();
    ~TwistToTwistStampedNode() = default;

private:
    void twistCallback(const geometry_msgs::msg::Twist::SharedPtr twist_msg);

    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr twist_sub_;
    rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr twist_stamped_pub_;
    std::string frame_id_;
};

#endif  // TWIST_TO_TWISTSTAMPED_NODE_HPP_
