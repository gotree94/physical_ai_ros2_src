#include <micro_ros_arduino.h>
#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>
#include <geometry_msgs/msg/twist.h>
#include <std_msgs/msg/string.h>
#include <math.h>

rcl_subscription_t twist_sub;
geometry_msgs__msg__Twist twist_msg;

rcl_allocator_t allocator;
rclc_support_t support;
rcl_node_t node;
rclc_executor_t executor;

rcl_publisher_t heartbeat_pub;
std_msgs__msg__String heartbeat_msg;

unsigned long last_heartbeat = 0;
unsigned long heartbeat_cnt = 0;
const char *text = "hello from esp32";
char heartbeat_text[50];

// 로봇 파라미터
const float TRACK_WIDTH = 0.145f; // 바퀴 간 거리 (m)
const float WHEEL_RADIUS = 0.065f/2; // 바퀴 반지름 (m)

void twist_callback(const void *msgin) {
  const geometry_msgs__msg__Twist *msg = (const geometry_msgs__msg__Twist *)msgin;

  float v = msg->linear.x;   // 선속도
  float w = msg->angular.z;  // 각속도
  
  Serial.printf("v:%.3f(m/s), w:%.3f(rad/s)\n", v, w);

  // 속도 계산
  float left_speed = v - w * TRACK_WIDTH / 2.0f;
  float right_speed = v + w * TRACK_WIDTH / 2.0f;

  // RPM 값으로 변환
  int left_rpm = (int)(left_speed / (TWO_PI * WHEEL_RADIUS) * 60 + 0.5);
  int right_rpm = (int)(right_speed / (TWO_PI * WHEEL_RADIUS) * 60 + 0.5);
  
  Serial.printf("left_rpm:%d, right_rpm:%d\n", left_rpm, right_rpm);
}

void setup() {
	Serial.begin(115200);
	delay(1000);
	// Wi-Fi micro-ROS 연결
	// set_microros_wifi_transports("swiftgo", "swiftgo14", "192.168.35.37", 8888);
	set_microros_wifi_transports("swiftgo", "swiftgo14", "192.168.35.67", 8888);
	
	delay(2000);

	allocator = rcl_get_default_allocator();

	rclc_support_init(&support, 0, NULL, &allocator);
	rclc_node_init_default(&node, "esp32_twist_sub_node", "", &support);

	rclc_subscription_init_default(
		&twist_sub,
		&node,
		ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist),
		"cmd_vel"
	);

	rclc_publisher_init_default(
		&heartbeat_pub,
		&node,
		ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),
		"esp32/heartbeat"
	);

	// 메시지 버퍼 준비
	heartbeat_msg.data.data = (char *)malloc(50);
	heartbeat_msg.data.capacity = 50;
	heartbeat_msg.data.size = 0;

	rclc_executor_init(&executor, &support.context, 1, &allocator);
	rclc_executor_add_subscription(&executor, &twist_sub, &twist_msg, &twist_callback, ON_NEW_DATA);  
}

void loop() {
	rclc_executor_spin_some(&executor, RCL_MS_TO_NS(50)); 

	// 1초마다 heartbeat 보내기
	if (millis() - last_heartbeat > 1000) {
		heartbeat_cnt++;
		sprintf(heartbeat_text, "%s - %d", text, heartbeat_cnt);
		strcpy(heartbeat_msg.data.data, heartbeat_text);
		heartbeat_msg.data.size = strlen(heartbeat_text);

		rcl_publish(&heartbeat_pub, &heartbeat_msg, NULL);

		last_heartbeat = millis();
	}

	delay(10);
}