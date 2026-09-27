import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
import cv2
from cv_bridge import CvBridge

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('brei_imgpub')
        
        # Publishers required by image_proc (Published under /camera namespace)
        self.image_pub = self.create_publisher(Image, 'camera/image_raw', 10)
        self.info_pub = self.create_publisher(CameraInfo, 'camera/camera_info', 10)

        self.bridge = CvBridge()
        self.timer = self.create_timer(0.033, self.timer_callback) # ~30 FPS

        # GStreamer pipeline using libcamerasrc
        self.f_width, self.f_height = 640, 480
        pipeline = (
            "libcamerasrc ! "
            "video/x-raw,format=NV12,colorimetry=bt709 ! "
            "videoconvert ! "
            "videoscale ! "
            f"video/x-raw,width={self.f_width},height={self.f_height},format=BGR ! "
            "appsink drop=true max-buffers=1 emit-signals=true"
        )

        self.get_logger().info('Initializing Pi Camera 3 via libcamerasrc GStreamer...')
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().error('CRITICAL: Failed to open GStreamer pipeline!')

    def timer_callback(self):
        # Guard against uninitialized camera handle
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn('Hardware warning: Pipeline failed to grab frame.')
            return

        now = self.get_clock().now().to_msg()

        # 1. Publish Raw Image
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        img_msg.header.stamp = now
        img_msg.header.frame_id = 'camera_optical_frame'
        self.image_pub.publish(img_msg)

        # 2. Publish Camera Info Metadata
        info_msg = CameraInfo()
        info_msg.header.stamp = now
        info_msg.header.frame_id = 'camera_optical_frame'
        info_msg.width = self.f_width
        info_msg.height = self.f_height
        
        # Default intrinsic estimation (Focal length ~ width) until calibrated
        fx = float(self.f_width)
        fy = float(self.f_width)
        cx = float(self.f_width) / 2.0
        cy = float(self.f_height) / 2.0

        info_msg.k = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
        info_msg.p = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        
        self.info_pub.publish(info_msg)

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            self.get_logger().info('Camera GStreamer resource released safely.')
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
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