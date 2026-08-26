# Deployment — the robot Pi

The robot's compute is a Raspberry Pi, hostname `raspi`, user `delivery`,
running **ROS 2 Jazzy** installed natively at `/opt/ros/jazzy`. The repo is
cloned at `~/delivery-robo`.

## Connecting

```sh
ssh delivery@raspi.local     # mDNS; use the IP if .local doesn't resolve
```

(Ask a team member for the password / current WiFi. The Pi joins WiFi via
`wpa_supplicant.conf` in the home directory.)

## What runs at boot

`deployment/startup.sh`, run as a systemd service (`robot.service`). On every
start it:

1. `git fetch` + fast-forward to `origin/main` (20 s timeout — skipped when
   offline, refused if someone edited files directly on the Pi so local
   changes are never clobbered);
2. rebuilds `ros2_ws` with colcon **only if** the repo moved or there is no
   install yet (build failure falls back to the previous install);
3. launches the sensor stack: `ros2 launch my_bringup master_launch.py`
   (RTK GPS + NTRIP, IMU, gps_to_map).

So the normal deploy flow is: **merge to `main`, then reboot the robot** (or
`sudo systemctl restart robot.service`). No hand-building on the Pi.

Note: only the *sensor* stack starts at boot. The drive stack
(`launch_real_robot.launch.py` in `sim/`, ros2_control + joystick) is still
launched manually.

## Installing / re-wiring the service on the Pi

```sh
cd ~/delivery-robo && git pull
chmod +x deployment/startup.sh
sudo cp deployment/robot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now robot.service
```

Checking on it:

```sh
systemctl status robot.service          # running? enabled?
systemctl is-enabled robot.service      # "enabled" = starts on boot
journalctl -u robot.service -f          # live logs (launch output goes here)
```

## History

The script that was found running on the Pi (uncommitted, ~/startup.sh)
was:

```bash
#!/bin/bash
source /opt/ros/jazzy/setup.bash
source ~/delivery-robo/ros2_ws/install/setup.bash
ros2 launch my_bringup master_launch.py
# ros2 run joystick_control joystick_node &
#ros2 run joy joy_node &
```

`deployment/startup.sh` supersedes it (same launch, plus pull-and-rebuild).
When switching to the service, remove the old wiring for `~/startup.sh` so it
doesn't start twice.

## Pi setup notes (not yet automated)

Things the Pi needs that no script installs yet — verify when reimaging:

- pip: `adafruit-circuitpython-bno08x` (+ Blinka `board`/`busio`) for the IMU;
  `pyserial` for the encoder node
- apt/ROS: `ublox_dgnss` (+ ntrip client), `twist_mux`, `ros2_control` stack
- user groups: `dialout` (serial), `i2c`
- the `serial` package must be built with
  `colcon build --packages-select serial --cmake-args -DCMAKE_POSITION_INDEPENDENT_CODE=ON`
- `rplidar_sdk` is checked out at `~/rplidar_sdk` (lidar not yet wired into
  any launch)
- stray copies exist in the home dir (`~/relivery-robo-old`, a loose
  `~/build`/`~/install`) — do not source those by accident
