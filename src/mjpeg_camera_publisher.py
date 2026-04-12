import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
import threading
import requests
import time

# --- 설정 변수 ---
STREAM_URL = "http://192.168.137.100/stream"
IMAGE_TOPIC = "/camera/image_raw" # 토픽 이름
INFO_TOPIC = "/camera/camera_info" # Image Topic 관례에 따라 /camera/image_raw의 info는 보통 /camera/camera_info로 발행
FRAME_ID = "camera_link" # 프레임 ID
VGA_WIDTH = 640
VGA_HEIGHT = 480
# 최종 출력 해상도: QVGA(320x240)를 90도 회전 -> 240x320
FINAL_WIDTH = 240 
FINAL_HEIGHT = 320
# ------------------

class MJPEGToImageRaw(Node):
    def __init__(self):
        super().__init__('mjpeg_to_image_raw_publisher')
        
        self.bridge = CvBridge()
        self.frame_id = FRAME_ID
        
        # Publishers
        self.image_publisher = self.create_publisher(Image, IMAGE_TOPIC, 50)
        self.info_publisher = self.create_publisher(CameraInfo, INFO_TOPIC, 50)
        
        self.stream_url = STREAM_URL
        self.bytes_data = b""
        self.latest_jpg = None

        # 변형된 해상도 (240x320)를 반영한 더미 CameraInfo 미리 생성
        self.camera_info_msg = self._create_transformed_camera_info(
            VGA_WIDTH, VGA_HEIGHT, FINAL_WIDTH, FINAL_HEIGHT) 

        self.get_logger().info(f"Connecting to MJPEG stream: {self.stream_url}")

        # 스트림 읽기용 Thread 시작
        self.stream_thread = threading.Thread(target=self._stream_reader, daemon=True)
        self.stream_thread.start()

        # ROS publish 타이머 (~30 FPS)
        self.timer = self.create_timer(0.03, self._publish_data) 

    def _create_transformed_camera_info(self, orig_w, orig_h, new_w, new_h):
        """
        VGA (640x480) 기본 K 행렬을 가정하고, QVGA 리사이즈 및 90도 회전을 적용하여
        최종 240x320 해상도에 맞는 CameraInfo를 계산하여 생성합니다.
        """
        msg = CameraInfo()
        msg.header.frame_id = self.frame_id
        msg.width = new_w
        msg.height = new_h
        
        # 1. VGA 원본 해상도 가정 (더미 값)
        # 비율: 500은 일반적인 웹캠의 가상 초점 거리
        fx_orig = 500.0
        fy_orig = 500.0
        cx_orig = orig_w / 2.0 # 320.0
        cy_orig = orig_h / 2.0 # 240.0
        
        # 2. QVGA 리사이즈 (배율 0.5) 적용
        scale = 320.0 / orig_w # 0.5
        fx_res = fx_orig * scale # 250.0
        fy_res = fy_orig * scale # 250.0
        cx_res = cx_orig * scale # 160.0
        cy_res = cy_orig * scale # 120.0
        
        # 3. 90도 시계방향 회전 적용
        # K_rot = [ fy_res, 0, new_w - cy_res ]
        #         [ 0,      fx_res, cx_res     ]
        #         [ 0,      0,      1          ]
        
        fx_rot = fy_res
        fy_rot = fx_res
        cx_rot = new_w - cy_res # 240 - 120 = 120.0 (새로운 중심점 X)
        cy_rot = cx_res # 160.0 (새로운 중심점 Y)

        # K 행렬 (내부 매개변수) 설정
        msg.k = [fx_rot, 0.0, cx_rot, 
                 0.0, fy_rot, cy_rot, 
                 0.0, 0.0, 1.0]
                 
        # P 행렬 (투영 행렬) 설정
        msg.p = [fx_rot, 0.0, cx_rot, 0.0, 
                 0.0, fy_rot, cy_rot, 0.0, 
                 0.0, 0.0, 1.0, 0.0]
        
        return msg

    def _stream_reader(self):
        """ 별도 쓰레드: MJPEG 스트림에서 JPEG 프레임을 추출 """
        while True:
            try:
                # ... (이전 코드의 스트림 연결 및 JPEG 파싱 로직) ...
                stream = requests.get(self.stream_url, stream=True, timeout=5)
                
                if stream.status_code != 200:
                    self.get_logger().error(f"HTTP error: {stream.status_code}")
                    time.sleep(1)
                    continue

                for chunk in stream.iter_content(chunk_size=4096):
                    if not chunk: break
                    self.bytes_data += chunk
                    start = self.bytes_data.find(b'\xff\xd8')
                    end = self.bytes_data.find(b'\xff\xd9')
                    if start != -1 and end != -1:
                        jpg = self.bytes_data[start:end+2]
                        self.bytes_data = self.bytes_data[end+2:]
                        if len(jpg) < 100: continue
                        self.latest_jpg = jpg
                        
            except Exception as e:
                self.get_logger().error(f"Stream error: {e}")
                time.sleep(1)
                continue

    def _publish_data(self):
        """ ROS2 Image와 CameraInfo를 동기화하여 publish """
        if self.latest_jpg is None:
            return

        try:
            # 1. JPEG 디코드 (Numpy -> OpenCV)
            np_arr = np.frombuffer(self.latest_jpg, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if cv_image is None:
                self.get_logger().warn("Could not decode JPEG image.")
                return

            # 2. VGA 640x480 -> QVGA 320x240 리사이즈
            resized_img = cv2.resize(cv_image, (320, 240), interpolation=cv2.INTER_LINEAR) 
            
            # 3. 시계방향 90도 회전 (최종 240x320)
            rotated_img = cv2.rotate(resized_img, cv2.ROTATE_90_CLOCKWISE)

            # 4. OpenCV -> ROS Image 메시지 변환
            img_msg = self.bridge.cv2_to_imgmsg(rotated_img, encoding="bgr8")
            current_time = self.get_clock().now().to_msg()
            img_msg.header.stamp = current_time
            img_msg.header.frame_id = self.frame_id
            
            # 5. Image 발행
            self.image_publisher.publish(img_msg)

            # 6. CameraInfo 발행 (동기화)
            info_msg = self.camera_info_msg
            info_msg.header.stamp = current_time # 이미지와 동일한 타임스탬프
            self.info_publisher.publish(info_msg)

        except Exception as e:
            self.get_logger().error(f"Processing/Publishing error: {e}")
            return


def main(args=None):
    rclpy.init(args=args)
    node = MJPEGToImageRaw()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()