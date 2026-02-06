#include "defs.hpp"

byte control_flags = 0x7f;
bool stop_flag = true;

byte param_len_table[] = {
  0,0, // stop has no params
  2,1, // DC motor int16/int8
  2,1, // Brushless 1 int16/int8
  2,1, // Brushless 2 int16/int8
  2,1, // Wrist 1 int16/int8
  2,1, // Wrist 2 int16/int8
  2,1, // Wrist 3 int16/int8
  1,1  // Claw int8/int8
};
byte cf_pos_table[] = {
  7,6,5,4,3,2,1,0
};
char* wrist_messages[] = {"WR1: ","WR2: ","WR3: "};
char* dcm_messages[] = {"stop", "right", "left"};

void setup() {
  setPinModes();
  analogWrite(PIN_DCM_R, 0);
  analogWrite(PIN_DCM_L, 0);
  SERVO_BRUSHLESS_1.write(90);
  SERVO_BRUSHLESS_2.write(90);
  SERVO_R.write(88);
  SERVO_L.write(92);
  Serial.begin(9600);
}

// handles a command over serial
void handleCommand() {
  int cmd_id = Serial.read();
  // for (int i = 0; i <= 5; i ++) { // attempt to read command id
  //   if (i == 5) {
  //     return;
  //   }
  //   if (Serial.available()) {
  //     cmd_id = Serial.read();
  //     break;
  //   }
  //   delay(1);
  // }
  int plt_index = (cmd_id<<1)+(control_flags&(1<<cf_pos_table[cmd_id])>0);
  byte buf[2];
  if (param_len_table[plt_index] == 0) {
    goto no_params;
  }
  // for (int i = 0; i <= 5; i ++) { // attempt to read command params
  //   if (i == 5) {
  //     return;
  //   }
  //   if (Serial.available() >= param_len_table[plt_index]) {
  //     break;
  //   }
  //   delay(1);
  // }
  Serial.readBytes(buf, param_len_table[plt_index]);
  no_params:
  switch (cmd_id) {
    case 0:{
      stop_flag = true;
      Serial.println("STOPPING");
      setDCM(0);
      break;
    }
    case 1:{
      Serial.print("DCM: ");
      Serial.println(dcm_messages[buf[0]]);
      setDCM((int)buf[0]);
      break;
    }
    case 2:case 3:{
      if (cmd_id == 2)
        Serial.print("BL1: ");
      else
        Serial.print("BL2: ");
      int v = (int)(*((char*)buf));
      Serial.println(v, DEC);
      (cmd_id==2?SERVO_BRUSHLESS_1:SERVO_BRUSHLESS_2).write(90+v);
      break;
    }
    case 4:case 5:case 6:{
      Serial.print(wrist_messages[cmd_id-4]);
      int v = (int)map((long)buf[0], 0, 255, -750, 750);
      Serial.println(v, DEC);
      if (cmd_id==4) setW1(v);
      else if (cmd_id==5) setW2(v);
      else setW3(v);
      break;
    }
    case 7:{
      Serial.print("CLAW: ");
      int v = (int)(*((char*)buf));
      Serial.println(v);
      moveClaw(v);
      break;
    }
  }
}

// reads incoming serial communication and handles it
void readSerial() {
  while (Serial.available() >= 2) {
    switch (Serial.read()) {
      case (0x99):{
        control_flags = (byte)Serial.read();
        break;
      }
      case (0x55):{
        handleCommand();
        break;
      }
    }
  }
}

void loop() {
  readSerial();
}
