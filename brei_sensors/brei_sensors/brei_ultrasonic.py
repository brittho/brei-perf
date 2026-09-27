import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
import lgpio
import time

class BreiUltrasonic(Node):
    def __init__(self):
        super().__init__('brei_ultrasonic')
        
        # Publisher for ultrasonic range data
        self.range_pub = self.create_publisher(Range, 'ultrasonic/range', 10)
        
        # Timer loop running at 10 Hz
        self.timer = self.create_timer(0.1, self.timer_callback)

        # Pin mapping (Default PiDog GPIO pins)
        self.TRIG = 23
        self.ECHO = 24

        try:
            # Open main GPIO chip handle (gpiochip4 on Pi 5, gpiochip0 on Pi 4)
            # lgpio.chip_open(0) auto-selects primary chip on most setups
            self.chip = lgpio.gpiochip_open(0)
            
            # Set up pins
            lgpio.gpio_claim_output(self.chip, self.TRIG)
            lgpio.gpio_claim_input(self.chip, self.ECHO)
            
            # Set TRIG low initially
            lgpio.gpio_write(self.chip, self.TRIG, 0)
            time.sleep(0.1)
            
            self.get_logger().info('Ultrasonic node initialized via lgpio (GPIO 23/24).')
        except Exception as e:
            self.get_logger().error(f'Failed to initialize GPIO chip via lgpio: {e}')
            self.chip = None

    def timer_callback(self):
        if self.chip is None:
            return

        # Emit 10us trigger pulse
        lgpio.gpio_write(self.chip, self.TRIG, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(self.chip, self.TRIG, 0)

        pulse_start = time.time()
        pulse_end = time.time()
        timeout = time.time() + 0.04  # 40ms timeout (~6.8 meters max)

        # Wait for ECHO pin to go HIGH
        while lgpio.gpio_read(self.chip, self.ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                return

        # Wait for ECHO pin to go LOW
        while lgpio.gpio_read(self.chip, self.ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                return

        # Calculate duration and distance in meters
        pulse_duration = pulse_end - pulse_start
        distance_m = (pulse_duration * 343.0) / 2.0

        # Construct ROS 2 Range Message
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'ultrasonic_link'
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.26  # ~15 degrees
        msg.min_range = 0.02      # 2 cm
        msg.max_range = 4.0       # 4 meters
        msg.range = float(distance_m)

        self.range_pub.publish(msg)

    def destroy_node(self):
        if hasattr(self, 'chip') and self.chip is not None:
            lgpio.gpiochip_close(self.chip)
            self.get_logger().info('GPIO resources closed cleanly.')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BreiUltrasonic()
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