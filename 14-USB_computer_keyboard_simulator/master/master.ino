#include "Keyboard.h"
#include <Wire.h>

//ARDUINO MASTER

void setup() {
   Serial.begin(115200);
   Wire.begin();
   delay(1000);
   Keyboard.begin(); // initialize control over the keyboard:
}

void loop() {
  Wire.requestFrom(9,1);
  byte byte_received = Wire.read();
  if (byte_received != 255 && byte_received != 0){
    //Serial.println((char)byte_received);
    Keyboard.write((char)byte_received);
    
  }
}
