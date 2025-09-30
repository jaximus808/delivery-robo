# WashU Robo Courier 

This robot's goal is to be able to navigate washu with an ackerman steering while carrying a load

### Reference

to run robot body

> ros2 launch robo_courier rsp.launch.py

to run joint rotations

> ros2 run joint_state_publisher_gui joint_state_publisher_gui 

rviz

> rviz2

make sure to change frame to base link, and add tf topic

## NEW UPDATED RUN with ackerman

### launch sim

ros2 launch robo_courier launch_sim.launch.py 

### launch keyboard

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true --remap /cmd_vel:=/ack_cont/reference

stamped

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap /cmd_vel:=/ack_cont/reference_unstamped


### dev notes

configs for control is in my_controllers.yaml, we use ros2_control.yaml for future reference plz dont troll this i spent so much time