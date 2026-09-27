import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from pidog.sh3001 import Sh3001
import os

class BreiImu(Node):
    def __init__(self):
        super().__init__('brei_imu')

        self.imu_pub = self.create_publisher(Imu, 'imu/data_raw', 10)
        self.timer = self.create_timer(0.02, self.timer_callback) # 50 Hz

        # Load PiDog config path for calibration offsets
        user = os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()
        user_home = os.popen(f'getent passwd {user} | cut -d: -f 6').readline().strip()
        config_file = f'{user_home}/.config/pidog/pidog.conf'

        try:
            self.imu = Sh3001(db=config_file)
            self.get_logger().info('SH3001 IMU successfully initialized via pidog library.')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize SH3001 IMU: {e}')
            self.imu = None

    def timer_callback(self):
        if self.imu is None:
            return

        data = self.imu._sh3001_getimudata()
        if data is False or data is None:
            self.get_logger().warn('IMU data read error.')
            return

        acc_data, gyro_data = data  # [ax, ay, az], [gx, gy, gz]

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        # Convert raw LSB to m/s^2 (Standard SH3001 16384 LSB/g)
        ACCEL_SCALE = 16384.0 / 9.80665
        msg.linear_acceleration.x = float(acc_data[0]) / ACCEL_SCALE
        msg.linear_acceleration.y = float(acc_data[1]) / ACCEL_SCALE
        msg.linear_acceleration.z = float(acc_data[2]) / ACCEL_SCALE

        # Convert raw LSB to rad/s (Standard SH3001 131 LSB/deg/s)
        GYRO_SCALE = 131.0 * (180.0 / 3.1415926535)
        msg.angular_velocity.x = float(gyro_data[0]) / GYRO_SCALE
        msg.angular_velocity.y = float(gyro_data[1]) / GYRO_SCALE
        msg.angular_velocity.z = float(gyro_data[2]) / GYRO_SCALE

        msg.orientation_covariance[0] = -1.0 # Un-fused raw IMU data

        self.imu_pub.publish(msg)

    def destroy_node(self):
        self.get_logger().info('SH3001 IMU node shutdown.')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BreiImu()
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
