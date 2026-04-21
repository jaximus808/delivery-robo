# IMU Covariance Estimator — Documentation

## Overview

This document explains the `imu_covariance_estimator` utility node in `imu_package`. It subscribes to live IMU data, measures how the sensor behaves over time, and computes covariance matrices that can be copied back into the IMU publisher node.

Unlike the IMU publisher, this node is not part of the robot's normal runtime behavior. It is a calibration and analysis tool that helps produce more realistic covariance values for downstream estimation and sensor fusion.

---

## Background and Motivation

### Why Estimate Covariance?

ROS2 IMU messages include covariance matrices for orientation, angular velocity, and linear acceleration. These values describe how uncertain the measurements are.

If the covariance is too small, downstream filters may trust the IMU too much. If it is too large, they may ignore useful motion information. This node exists to derive those values from real sensor data instead of guessing them by hand.

### What This Node Does

The estimator:

- Subscribes to a live `sensor_msgs/Imu` topic
- Ignores an initial warmup period so the sensor can settle
- Collects a configurable number of samples
- Computes covariance matrices from the captured data
- Prints the results to the console
- Writes the results to a text file for later copy-paste into the publisher node

---

## Package Structure

This utility lives in the same Python package as the IMU publisher:

```
ros2_ws/src/imu_package/
├── package.xml
├── setup.py
└── imu_package/
    ├── imu_node.py
    └── imu_covariance_estimator.py
```

The executable is registered in `setup.py` as:

```python
'console_scripts': [
    'imu_publisher = imu_package.imu_node:main',
    'imu_covariance_estimator = imu_package.imu_covariance_estimator:main',
],
```

That means it can be launched with:

```bash
ros2 run imu_package imu_covariance_estimator
```

---

## The Node: `imu_covariance_estimator.py`

### Imports

```python
import argparse
from typing import List

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from sensor_msgs.msg import Imu
```

- **`argparse`** is used for command-line arguments.
- **`numpy`** provides the matrix and statistics operations.
- **`rclpy`** and **`Node`** provide the ROS2 runtime.
- **`QoSProfile`** and **`ReliabilityPolicy`** configure subscription behavior.
- **`sensor_msgs.msg.Imu`** is the topic message type.

---

### Quaternion Conversion Helper

```python
def quaternion_to_rpy(x: float, y: float, z: float, w: float) -> np.ndarray:
    """Convert quaternion to roll, pitch, yaw in radians."""
```

The helper converts a quaternion to roll, pitch, and yaw values. The estimator stores orientation samples in this form because covariance over Euler-like angles is easier to inspect and reason about than raw quaternions.

The function uses standard trigonometric formulas and returns a NumPy array of three values in radians.

---

### Node Initialization (`__init__`)

```python
super().__init__('imu_covariance_estimator')
self.topic = topic
self.warmup_samples = warmup_samples
self.target_samples = target_samples
self.min_variance = min_variance
```

The node is named `imu_covariance_estimator` and stores the runtime configuration passed in from the command line.

```python
self.messages_seen = 0
self.orientation_samples: List[np.ndarray] = []
self.angular_velocity_samples: List[np.ndarray] = []
self.linear_accel_samples: List[np.ndarray] = []
self.finished = False
```

These fields track progress and accumulate the sample arrays used for covariance estimation.

```python
qos = QoSProfile(depth=200)
qos.reliability = ReliabilityPolicy.BEST_EFFORT
```

The subscription uses a best-effort QoS profile. That is a good match for live sensor data where the newest sample matters more than guaranteed delivery of every sample.

```python
self.subscription = self.create_subscription(
    Imu,
    self.topic,
    self.imu_callback,
    qos,
)
```

The node subscribes to the chosen IMU topic, which defaults to `imu/data`.

```python
self.get_logger().info(
    f"Listening on '{self.topic}'. "
    f"Warmup: {self.warmup_samples} samples, capture: {self.target_samples} samples."
)
```

This logs the active configuration so the calibration run is easy to track.

---

### IMU Callback (`imu_callback`)

The callback runs for every incoming IMU message until the estimator finishes.

```python
if self.finished:
    return
```

Once enough samples have been collected, extra messages are ignored.

```python
self.messages_seen += 1
if self.messages_seen <= self.warmup_samples:
    if self.messages_seen % max(1, self.warmup_samples // 5) == 0:
        self.get_logger().info(f"Warmup {self.messages_seen}/{self.warmup_samples}...")
    return
```

The initial messages are treated as warmup. This gives the sensor time to stabilize before recording data for covariance estimation.

```python
qx = msg.orientation.x
qy = msg.orientation.y
qz = msg.orientation.z
qw = msg.orientation.w
qnorm = np.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
if qnorm > 1e-9:
    self.orientation_samples.append(quaternion_to_rpy(qx / qnorm, qy / qnorm, qz / qnorm, qw / qnorm))
```

The quaternion is normalized before conversion and then stored as roll, pitch, and yaw samples.

```python
self.angular_velocity_samples.append(
    np.array([msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z], dtype=np.float64)
)
self.linear_accel_samples.append(
    np.array(
        [msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z],
        dtype=np.float64,
    )
)
```

The angular velocity and linear acceleration data are appended as numeric vectors.

```python
captured = len(self.linear_accel_samples)
if captured % max(1, self.target_samples // 10) == 0:
    self.get_logger().info(f"Captured {captured}/{self.target_samples} samples...")
```

The node logs progress periodically so long calibration runs remain visible.

```python
if captured >= self.target_samples:
    self.finished = True
    self.report_and_shutdown()
```

Once the requested number of samples has been gathered, the node computes and reports the covariance results.

---

### Covariance Computation

```python
def _covariance_from_samples(self, values: List[np.ndarray], unwrap_angles: bool = False) -> np.ndarray:
```

This helper turns a list of sample vectors into a covariance matrix.

```python
if len(values) < 2:
    raise RuntimeError('Need at least 2 samples to compute covariance.')
```

At least two samples are required for covariance.

```python
data = np.vstack(values)
if unwrap_angles:
    data = np.unwrap(data, axis=0)

cov = np.cov(data, rowvar=False, ddof=1)
```

The samples are stacked into a matrix and passed to NumPy's covariance computation. Angle data is unwrapped first so wraparound at $2\pi$ does not create artificial jumps.

```python
for i in range(3):
    if cov[i, i] < self.min_variance:
        cov[i, i] = self.min_variance
```

A minimum diagonal variance floor is enforced so the resulting covariance matrices stay usable by downstream estimators and do not become singular.

---

### Reporting Results

```python
def report_and_shutdown(self) -> None:
```

This method generates the final covariance values and shuts the node down.

```python
orientation_cov = self._covariance_from_samples(self.orientation_samples, unwrap_angles=True)
angular_cov = self._covariance_from_samples(self.angular_velocity_samples)
linear_cov = self._covariance_from_samples(self.linear_accel_samples)
```

Covariance is computed separately for orientation, angular velocity, and linear acceleration.

```python
orientation_flat = self._flatten_row_major(orientation_cov)
angular_flat = self._flatten_row_major(angular_cov)
linear_flat = self._flatten_row_major(linear_cov)
```

The matrices are flattened into row-major arrays because ROS message fields expect a flat list of nine values.

```python
self.get_logger().info('=== Estimated IMU Covariances ===')
self.get_logger().info(f'orientation_covariance: {orientation_flat}')
self.get_logger().info(f'angular_velocity_covariance: {angular_flat}')
self.get_logger().info(f'linear_acceleration_covariance: {linear_flat}')
```

The computed values are printed so they can be copied directly into the IMU publisher.

```python
with open("imu_covariance_results.txt", "w") as file:
    file.write(f'orientation_covariance: {orientation_flat}')
    file.write(f'angular_velocity_covariance: {angular_flat}')
    file.write(f'linear_acceleration_covariance: {linear_flat}')
```

A text file is written for later review. The file is intended as a convenience artifact from a calibration run.

```python
rclpy.shutdown()
```

The node shuts down after the results are emitted.

---

### Command-Line Arguments

```python
def parse_args() -> argparse.Namespace:
```

The utility is configured from the command line rather than ROS parameters.

Supported arguments:

- `--topic` selects the IMU topic to subscribe to
- `--warmup-samples` controls how many initial messages to ignore
- `--samples` sets how many messages to use for covariance estimation
- `--min-variance` sets the minimum allowed diagonal variance

Example:

```bash
ros2 run imu_package imu_covariance_estimator -- --topic imu/data --warmup-samples 200 --samples 2000
```

---

### Shutdown and Entry Point

```python
def main() -> None:
```

The entry point validates the arguments, initializes ROS2, creates the estimator node, and spins until enough data has been collected or the user interrupts the process.

The `finally` block shuts ROS2 down cleanly and destroys the node.

---

## Full Data Flow

```
Live IMU Publisher
     |
     | ROS2 topic: imu/data
     v
imu_covariance_estimator (ROS2, Python)
  - Ignores warmup samples
  - Collects live IMU measurements
  - Computes covariance matrices
  - Prints and writes results
     |
     | copy/paste into IMU publisher node
     v
Updated covariance arrays in imu_node.py
```

---

## How to Build and Run

### Build the package

```bash
cd ~/delivery-robo/ros2_ws
colcon build --packages-select imu_package
source install/setup.bash
```

### Run the estimator

```bash
ros2 run imu_package imu_covariance_estimator
```

### Run with custom settings

```bash
ros2 run imu_package imu_covariance_estimator -- --topic imu/data --warmup-samples 100 --samples 1000 --min-variance 1e-9
```

### Review the output

After the run completes, check the terminal output and the generated `imu_covariance_results.txt` file. The values can be copied into the covariance arrays in the IMU publisher.

---

## Common Issues

| Problem | Likely Cause | Fix |
|---|---|---|
| The node never finishes | Not enough IMU messages are arriving | Confirm the IMU publisher is running and the topic name is correct |
| Covariance values look too small | The sensor was not given enough warmup or the robot was too still | Increase the warmup or capture motion in a more representative configuration |
| Quaternion values behave oddly | Orientation samples wrap around at $2\pi$ | Keep angle unwrapping enabled and verify the sensor frame alignment |
| The output file is not created | The node was interrupted before completion | Let the estimator finish or re-run it from the start |

---

## Dependencies Summary

| Dependency | Where Declared | Purpose |
|---|---|---|
| `rclpy` | `package.xml` | ROS2 Python client library |
| `sensor_msgs` | `package.xml` | Provides the `Imu` message type |
| `numpy` | `setup.py` | Matrix and covariance calculations |
| `argparse` | Python standard library | Command-line argument parsing |
