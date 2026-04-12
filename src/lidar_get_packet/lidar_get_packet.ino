#define LIDAR_SERIAL Serial1
#define LIDAR_BAUD 230400
#define UART_RX 16
#define UART_TX 17

#define BUF_SIZE 64  // 블록 단위 읽기 버퍼 크기, LD14P 데이터 패킷 크기 - 47B

void setup() {
  Serial.begin(115200);
  LIDAR_SERIAL.begin(LIDAR_BAUD, SERIAL_8N1, UART_RX, UART_TX);
}

uint32_t cntByte = 0;
unsigned long lastPrintTime = 0;
unsigned long whileTimeAccum = 0;  // while문 수행 누적 시간
unsigned long whileStart = 0;
unsigned long whileEnd = 0;
unsigned long whileTimeAccum2 = 0;
unsigned long whileStart2 = 0;
unsigned long whileEnd2 = 0;

uint8_t buf[BUF_SIZE];

uint32_t correctCRCCheck=0;
uint32_t wrongVerLen=0;
uint32_t wrongCRCCheck=0; 

int parse_cnt=0;

void loop() {
  // while 문 시작 시간 기록
  whileStart = micros();

  // FIFO에 있는 바이트 수 확인
  size_t avail = LIDAR_SERIAL.available();
  while (avail > 0) {
    whileStart2 = micros();
    // 블록 단위로 읽을 수 있는 최대 바이트 수 계산
    size_t toRead = (avail > BUF_SIZE) ? BUF_SIZE : avail;

    // 한 번에 읽기
    size_t n = LIDAR_SERIAL.readBytes(buf, toRead);
    for(int i=0;i<n;i++) {
      uint8_t byte = buf[i];
      if(AnalysisOne(byte)) {
        Parse();
        parse_cnt++;  
      }
    } 

    // 수신 바이트 누적
    cntByte += n;

    // 남은 데이터 수 업데이트
    avail = LIDAR_SERIAL.available();
    whileEnd2 = micros();
    whileTimeAccum2 += (whileEnd2 - whileStart2);
  }

  // while 문 끝난 시간
  whileEnd = micros();
  whileTimeAccum += (whileEnd - whileStart);

  // 1초마다 출력
  unsigned long currentTime = millis();
  if (currentTime - lastPrintTime >= 1000) {
    Serial.print("Bytes per second: ");
    Serial.print(cntByte);
    Serial.print(" | Packets per second: ");
    Serial.print(cntByte/47.); // ld14P 패킷 사이즈 - 47B
    Serial.print(" | While time (us): ");
    Serial.print(whileTimeAccum);
    Serial.print(" | While2 time (us): ");
    Serial.println(whileTimeAccum2);

    cntByte = 0;
    whileTimeAccum = 0;  // 초기화
    whileTimeAccum2 = 0;  // 초기화
    lastPrintTime = currentTime;
  }
}

// 초당 바이트 수 : 15704
// 초당 패킷 수 : 334.13
// 초당 패킷 처리 시간 : 340 ms
// 패킷 처리 주기 : 1000/334.13 = 2.993ms
// 패킷 당 처리 시간 : 340/334.13 = 1.018ms
// 패킷 당 IDLE 시간 : 2.993 - 1.018 = 1.975ms
