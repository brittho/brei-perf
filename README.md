# brei-perf
Standalone ROS2 control loops, spatiotemporal state estimation evaluation frameworks, and runtime performance benchmarks for Brei™.

> **Scope:** ROS2 control loops, performance monitors, and spatiotemporal state estimation benchmarks from the Brei runtime stack.

## Prerequisites

1. **Ubuntu 24.04 Node:**
   - ROS 2 Jazzy (Native installation)
2. **macOS Node:**
   - ROS 2 Jazzy installed via Pixi/RoboStack

> **Note:** Detailed setup instructions will be added in a future update. For now, this guide assumes you have a working ROS 2 environment with nodes capable of communicating across your network for the subsequent steps.

## ROS 2 and System Bringup

> **Note:** Ensure both machines are connected to the same local network.

### 1. macOS (subscriber node)
```bash
cd ros2_jazzy_ws
pixi shell -e jazzy
source ros2_ws/install/local_setup.sh
ros2 run py_imgpubsub img_subscriber
```
### 2. Ubuntu (publisher node)
Source ROS 2 core and local workspace
```bash
source /opt/ros/jazzy/setup.bash
source ~/brei_ws/ros2_ws/install/local_setup.bash
```
Configure libcamera and GStreamer plugin paths
```bash
export LIBCAMERA_IPA_MODULE_PATH=/usr/local/lib/aarch64-linux-gnu/libcamera
export GST_PLUGIN_PATH=/usr/local/lib/aarch64-linux-gnu/gstreamer-1.0:$GST_PLUGIN_PATH
```
Run the publisher
```bash
ros2 run py_imgpubsub img_publisher
```
Open your web browser and navigate to the IP address displayed in the subscriber node terminal (e.g., `http://<ip_address>:8080`).
