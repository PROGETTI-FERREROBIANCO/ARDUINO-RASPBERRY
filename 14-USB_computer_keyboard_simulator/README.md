
# USB computer keyboard simulator
This project makes it possible to use a computer, especially its keyboard, as an output device for another computer.

## Hardware
The hardware looks like this. There are two ports, appropriately labeled with the words *slave* for the computer whose keyboard you will use and *master* for the PC on which what has been typed will be written.
Inside there are an **Arduino Nano** and an **Arduino ProMicro** that take care of the communication between the *master* and the *slave*.

<img src="./photos/foto_01.jpeg" style="width:20%"></img>
<img src="./photos/foto_02.jpeg" style="width:20%"></img>

The **electrical circuit** is shown below:

<img src="./wiring_diagram.png" style="width:50%"></img>

## Software
The code that allows this device to work is shown below and inside the *master* and *slave* folders.

> **MASTER CODE**

```#include "Keyboard.h"
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
```
