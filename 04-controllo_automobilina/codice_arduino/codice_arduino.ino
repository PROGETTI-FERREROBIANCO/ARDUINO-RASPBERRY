#include <Servo.h>

#define PIN_VOLANTE 5
#define PIN_RUOTE 6

#define FERMO 90

#define MIN_STERZO -35
#define MAX_STERZO 60

Servo volante, ruote;

String dati = "";
String vel = "";
String ste = "";
char c;

int velocita;
int angolo_sterzo;

void setup(){
  Serial.begin(9600);
  volante.attach(PIN_VOLANTE);
  ruote.attach(PIN_RUOTE);
}

void loop(){
  
  while(Serial.available()){
    c = Serial.read();
    if(c != '!'){
      if(c != '\r' && c != '\n'){
        dati += c;        
      }
    }else{

      //Serial.println(dati);

      vel = split(dati, '#', 0);
      ste = split(dati, '#', 1);
      
      velocita = vel.toInt();
      angolo_sterzo = ste.toInt();

      //Serial.println(velocita);
      //Serial.println(angolo_sterzo);
      

      if(velocita >= 45 && velocita <= 55){
        ruote.write(FERMO);
      }else if(velocita < 45){
        ruote.write(50);
        ruote.write(7);
        ruote.write(map(velocita, 0, 100, 0, 180));
      }else if(velocita > 55){
        ruote.write(map(velocita, 0, 100, 0, 180));
      }

      if(angolo_sterzo < MIN_STERZO){ angolo_sterzo = MIN_STERZO;}
      else if(angolo_sterzo > MAX_STERZO){ angolo_sterzo = MAX_STERZO;}

      volante.write(map(angolo_sterzo, MIN_STERZO, MAX_STERZO, 65, 115));
      
      dati = "";

    }
  }

}

String split(String data, char separator, int index){
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";

}
