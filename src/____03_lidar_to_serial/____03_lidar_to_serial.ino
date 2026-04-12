#define LIDAR_SERIAL Serial1
#define LIDAR_BAUD 230400
#define UART_RX 16
#define UART_TX 17

void setup() {
  Serial.begin(LIDAR_BAUD);

  LIDAR_SERIAL.begin(LIDAR_BAUD, SERIAL_8N1, UART_RX, UART_TX);
}

void loop() {
  while (LIDAR_SERIAL.available()>0) {
    uint8_t byte = LIDAR_SERIAL.read();
    Serial.write(byte);
  }
}

// 1. LdsPointCloudViewer 다운로드 및 설치
//   https://github.com/ldrobotSensorTeam/ld_desktop_tool/releases
// 2. USB 데이터를 LdsPointCloudViewer로 전달 및 확인
