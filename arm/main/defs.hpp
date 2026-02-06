#include "Arduino.h"
#include <Servo.h>

Servo SERVO_BRUSHLESS_1;
Servo SERVO_BRUSHLESS_2;
Servo SERVO_R;
Servo SERVO_L;

// dc motor
#define PIN_DCM_R 9
#define PIN_DCM_L 10
// brushless motors
#define PIN_BRUSHLESS_1 13
#define PIN_BRUSHLESS_2 4
// stepper motors
#define PIN_STEPPER_1_DIR 2
#define PIN_STEPPER_1_DUTY 3
#define PIN_STEPPER_2_DIR 5
#define PIN_STEPPER_2_DUTY 6
#define PIN_STEPPER_3_DIR 7
#define PIN_STEPPER_3_DUTY 8
// servos
#define PIN_SERVO_R 11
#define PIN_SERVO_L 12
// limit switches
#define PIN_JLIM_1 15
#define PIN_JLIM_2 16
#define PIN_JLIM_3 17
#define PIN_JLIM_4 18
#define PIN_JLIM_5 19
#define PIN_JLIM_6 20

#define MODE_DCM 0x40
#define MODE_BL1 0x20
#define MODE_BL2 0x10
#define MODE_WR1 0x80
#define MODE_WR2 0x04
#define MODE_WR3 0x02
#define MODE_CLW 0x01

#define clamp(v, minv, maxv) min(max(minv, v), maxv)

static uint16_t lockouts = 0;
//inline bool get_lockout

void setPinModes() {
  pinMode(PIN_DCM_R, OUTPUT);
  pinMode(PIN_DCM_L, OUTPUT);
  pinMode(PIN_STEPPER_1_DIR, OUTPUT);
  pinMode(PIN_STEPPER_1_DUTY, OUTPUT);
  pinMode(PIN_STEPPER_2_DIR, OUTPUT);
  pinMode(PIN_STEPPER_2_DUTY, OUTPUT);
  pinMode(PIN_STEPPER_3_DIR, OUTPUT);
  pinMode(PIN_STEPPER_3_DUTY, OUTPUT);
  pinMode(PIN_JLIM_1, INPUT);
  // pinMode(PIN_JLIM_1, OUTPUT);
  // digitalWrite(PIN_JLIM_1, HIGH);
  pinMode(PIN_JLIM_2, INPUT);
  pinMode(PIN_JLIM_3, INPUT);
  pinMode(PIN_JLIM_4, INPUT);
  pinMode(PIN_JLIM_5, INPUT);
  pinMode(PIN_JLIM_6, INPUT);
  SERVO_BRUSHLESS_1.attach(PIN_BRUSHLESS_1);
  SERVO_BRUSHLESS_2.attach(PIN_BRUSHLESS_2);
  SERVO_R.attach(PIN_SERVO_R);
  SERVO_L.attach(PIN_SERVO_L);
}

void setDCM(int v) {
  if (v == 2) {
    analogWrite(PIN_DCM_R, 0);
    analogWrite(PIN_DCM_L, 50);
  } else if (v == 1) {
    analogWrite(PIN_DCM_L, 0);
    analogWrite(PIN_DCM_R, 50);
  } else {
    analogWrite(PIN_DCM_L, 0);
    analogWrite(PIN_DCM_R, 0);
  }
}

// int clamp(int v, int minv, int maxv) {
//   return max(min(v, maxv), minv);
// }

static int claw_l_pos, claw_r_pos;
void clawL(int v) {
  SERVO_L.write(v);
  claw_l_pos = v;
}
void clawR (int v) {
  SERVO_R.write(v);
  claw_r_pos = v;
}
void setClaw(int v) {
  //
}
void moveClaw(int v) {
  clawL(clamp(claw_l_pos - v, 5, 88));
  clawR(clamp(claw_r_pos + v, 92, 175));
}

void setBL1(int v) {
  SERVO_BRUSHLESS_1.write(90+v);
}
void setBL2(int v) {
  SERVO_BRUSHLESS_2.write(90+v);
}

void setW(int dir, int duty, int v) {
  if (v < 0) {
    digitalWrite(dir, LOW);
  } else {
    digitalWrite(dir, HIGH);
  }
  analogWrite(duty, 250);
  delayMicroseconds(760 - abs(v));
  analogWrite(duty, 0);
}
#define setW1(v) setW(PIN_STEPPER_1_DIR, PIN_STEPPER_1_DUTY, v)
#define setW2(v) setW(PIN_STEPPER_2_DIR, PIN_STEPPER_2_DUTY, v)
#define setW3(v) setW(PIN_STEPPER_3_DIR, PIN_STEPPER_3_DUTY, v)
