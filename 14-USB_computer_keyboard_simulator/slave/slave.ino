#include <Wire.h>

//ARDUINO SLAVE

void setup() {
  delay(1000);
  Serial.begin(115200);
  delay(1000);
  // Start the I2C Bus as Slave on address 9
  Wire.begin(9);
  Wire.onRequest(requestEvent); 
  delay(1000);
  pinMode(11, OUTPUT);
}

void requestEvent(){
  if(Serial.available() != 0){
    char input = Serial.read();
    byte input_byte = (int)input;
    Wire.write(input_byte);
  }
}

void loop() {
  Wire.onRequest(requestEvent); 
}
