class DCMotor {
  int M1;
  int M2;

  void control(int value1, int value2) {
    digitalWrite(M1, value1);
    digitalWrite(M2, value2);
  }

public:
  DCMotor(int M1, int M2)
    :M1(M1),M2(M2) {}

  void begin() {
    pinMode(M1,OUTPUT);
    pinMode(M2,OUTPUT);    
  }

  void forward() {
    control(HIGH,LOW);
  }

  void reverse() {
    control(LOW,HIGH);
  }

  void stop() {
    control(LOW,LOW);
  }

  void brake() {
    control(HIGH,HIGH);
  }  
};

class Encoder {
  int C1;
  int C2;
  volatile long pos;
  portMUX_TYPE encMux;

  void IRAM_ATTR C1_ISR() {
    byte val1=digitalRead(C1);
    byte val2=digitalRead(C2);
    if(val1==val2) pos++;
    else pos--;
  }

  void IRAM_ATTR C2_ISR() {
    byte val1=digitalRead(C1);
    byte val2=digitalRead(C2);
    if(val1!=val2) pos++;
    else pos--;
  }

  static void IRAM_ATTR C1_ISR_static(void* arg) {
    Encoder* enc=static_cast<Encoder*>(arg);
    enc->C1_ISR();
  }

  static void IRAM_ATTR C2_ISR_static(void* arg) {
    Encoder* enc=static_cast<Encoder*>(arg);
    enc->C2_ISR();
  }

public:
  Encoder(int C1, int C2)
    : C1(C1),C2(C2), encMux(portMUX_INITIALIZER_UNLOCKED) {}

  void begin() {
    pinMode(C1, INPUT);
    pinMode(C2, INPUT);
    attachInterruptArg(C1, C1_ISR_static, this, CHANGE);
    attachInterruptArg(C2, C2_ISR_static, this, CHANGE);    
  }

  long getPos() {
    portENTER_CRITICAL(&encMux);
    long tmp_pos=pos;
    portEXIT_CRITICAL(&encMux);
    return tmp_pos;
  }
};

DCMotor dcFL(19,27);
DCMotor dcFR(26,25);
DCMotor dcRL(0,15);
DCMotor dcRR(23,12);

Encoder encFL(14, 4);
Encoder encFR(34,35);
Encoder encRL(13,18);
Encoder encRR(32,33);

void setup() {

  Serial.begin(115200);

  dcFL.begin();
  dcFR.begin();
  dcRL.begin();
  dcRR.begin();

  encFL.begin();
  encFR.begin();
  encRL.begin();
  encRR.begin();
}

void loop() {

  if(Serial.available()) {
    char input = Serial.read();
    if(input=='f') {  
      dcFL.forward();
      dcFR.forward();
      dcRL.forward();
      dcRR.forward();
    } else if(input=='r') {        
      dcFL.reverse();
      dcFR.reverse();
      dcRL.reverse();
      dcRR.reverse();
    } else if(input=='b') {
      dcFL.brake();
      dcFR.brake();
      dcRL.brake();
      dcRR.brake();
    } else if(input=='s') {
      dcFL.stop();
      dcFR.stop();
      dcRL.stop();
      dcRR.stop();
    } 
  }
  
  Serial.printf("%ld, %ld, %ld, %ld\n", 
    encFL.getPos(), 
    encFR.getPos(), 
    encRL.getPos(),
    encRR.getPos());
    
}
