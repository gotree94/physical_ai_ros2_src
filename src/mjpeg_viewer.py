# pip install opencv-python requests numpy
import cv2
import requests
import numpy as np

STREAM_URL = "http://192.168.137.100/stream"

def mjpeg_subscriber(url):
	print(f"Connecting to MJPEG stream: {url}")

	# 스트림 연결
	stream = requests.get(url, stream=True)

	if stream.status_code != 200:
		print("Failed to connect:", stream.status_code)
		return

	# MJPEG 스트림은 boundary 형태로 계속 JPEG가 들어옴
	bytes_data = b""

	for chunk in stream.iter_content(chunk_size=4096):
		bytes_data += chunk
		# JPEG 시작 (\xff\xd8) ~ 끝 (\xff\xd9)을 찾음
		start = bytes_data.find(b'\xff\xd8')
		end = bytes_data.find(b'\xff\xd9')

		if start != -1 and end != -1:
			jpg = bytes_data[start:end+2]  
			bytes_data = bytes_data[end+2:]  

			if len(jpg) < 100:
				continue

			# 1. 바이트 데이터를 NumPy 배열로 변환
			try:
				np_arr = np.frombuffer(jpg, dtype=np.uint8)
			except Exception as e:
				# print(f"NumPy buffer conversion error: {e}")
				continue # 변환 실패 시 다음 조각으로 넘어감

			# 2. NumPy 배열을 OpenCV 이미지로 디코드
			img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

			if img is not None:
				# 3. VGA 640x480 -> QVGA 320x240
				resized_img = cv2.resize(img, (320, 240), interpolation=cv2.INTER_LINEAR)                
				# 4. 시계방향 90도 회전
				rotated_img = cv2.rotate(resized_img, cv2.ROTATE_90_CLOCKWISE)

				cv2.imshow("MJPEG Stream Viewer", rotated_img)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

	cv2.destroyAllWindows()


if __name__ == "__main__":
	mjpeg_subscriber(STREAM_URL)
 
# python mjpeg_viewer.py
# 창이 열리면 실시간 ESP32 카메라 화면이 표시됩니다.
# 화면에서 Q 키를 누르면 종료됩니다.
# MJPEG가 느려 보일 경우
# chunk_size 를 2048 또는 4096으로 증가