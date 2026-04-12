#include <Wire.h>
#include <Preferences.h>

Preferences prefs;

void setup() {
  Serial.begin(115200);  

  Wire.begin();
  Wire.setClock(400000);

  Wire.beginTransmission(0x68);
  Wire.write(0x6b);
  Wire.write(0x0);
  Wire.endTransmission(true);
}

void loop() {
  Wire.beginTransmission(0x68);
  Wire.write(0x47);
  Wire.endTransmission(false);
  Wire.requestFrom((uint16_t)0x68,(uint8_t)2,true);

  int16_t GyZH = Wire.read();  
  int16_t GyZL = Wire.read();
  int16_t GyZ = GyZH <<8 |GyZL;

  static int32_t GyZSum = 0;
  static int16_t GyZOff = 0;
  static int cnt_sample = 1000;
  if(cnt_sample > 0) {
    GyZSum += GyZ;
    cnt_sample --;
    if(cnt_sample ==0) {            
      GyZOff = (GyZSum+500) / 1000;

      Serial.print("GyZSum: ");
      Serial.print(GyZSum);
      Serial.print(", GyZOff: ");
      Serial.println(GyZOff);

      saveGyZOff(GyZOff);

      delay(3000);
    }
    delay(1);

    return;    
  }

  int16_t GyZCalib = GyZ - GyZOff;
  const float GYROXYZ_TO_DEGREES_PER_SEC = 131.;
  double GyZR = GyZCalib/GYROXYZ_TO_DEGREES_PER_SEC;

  static unsigned long t_prev = 0;
  unsigned long t_now = micros();
  double dt = (t_now - t_prev)/1000000.0;
  t_prev = t_now;

  static double time = 0.0;
  time += dt;

  static double gyAngleZ = 0.0;
  gyAngleZ += GyZR*dt;

  static int cnt_loop = 0;
  cnt_loop++;
  if (cnt_loop % 1000 == 0) {
    Serial.print("gyZOffset = ");
    Serial.print(GyZOff);
    Serial.print(", gyAngleZ = ");
    Serial.print(gyAngleZ, 3);
    Serial.print(" degs, time = ");
    Serial.println(time, 6);

    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');  // 개행까지 읽기
      int16_t newOffset = input.toInt();          // 문자열 → double
      if (newOffset != 0 || input.startsWith("0")) { 
        GyZOff = newOffset;
        Serial.print("GyZ offset updated: ");
        Serial.println(GyZOff, 3);

        saveGyZOff(GyZOff);
        
        time=0;
        gyAngleZ=0;
      }
    }
  }

}

void saveGyZOff(int16_t& GyZOff) {
  // NVS 시작
  prefs.begin("imu", false); // 읽기 쓰기 모드

  // NVS에 저장
  prefs.putInt("GyZOff", GyZOff);
  Serial.print("GyZOff saved: ");
  Serial.println(GyZOff);
  
  prefs.end();
}