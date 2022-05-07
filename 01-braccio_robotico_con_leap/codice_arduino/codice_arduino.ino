#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SERVOMIN  150 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // this is the 'maximum' pulse length count (out of 4096)
#define MIN_ANGLE 0
#define MAX_ANGLE 180

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

String stringa = ""; //variable to store incoming data from JAVA 
char carattere;
int motore = 0;
int angolo = 0;

void setup() {  
  Serial.begin(115200);

  pwm.begin();
  pwm.setPWMFreq(60);
  delay(10);
}

void loop() {
  if(Serial.available()>0){ //if data has been written to the Serial stream
    carattere=Serial.read();
  
    if(carattere != '#') stringa += carattere;
    else{

      Serial.println(stringa);

      motore = splitString(stringa,':',0).toInt();
      angolo = splitString(stringa,':',1).toInt();

      pwm.setPWM(motore, 0, map(angolo, MIN_ANGLE, MAX_ANGLE, SERVOMIN, SERVOMAX));

      stringa = "";
    }
    
  }
}


String splitString(String str, char sep, int index)
{
 int found = 0;
 int strIdx[] = { 0, -1 };
 int maxIdx = str.length() - 1;

 for (int i = 0; i <= maxIdx && found <= index; i++)
 {
    if (str.charAt(i) == sep || i == maxIdx)
    {
      found++;
      strIdx[0] = strIdx[1] + 1;
      strIdx[1] = (i == maxIdx) ? i+1 : i;
    }
 }
 return found > index ? str.substring(strIdx[0], strIdx[1]) : "";
}
