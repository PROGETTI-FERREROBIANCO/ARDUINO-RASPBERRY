//CODICE PER CONTROLLARE I FINECORSA

#include <stdio.h>
#include <stdlib.h>


/*
Z --> asse riferito alla posizione rispetto all'altezza
X --> asse riferito alla posizione rispetto destra e sinistra
Y --> asse riferito alla posizione rispetto avanti e indietro
*/
#define PIN_MAX_Z 22
#define PIN_MIN_Z 23
#define PIN_MAX_X 24
#define PIN_MIN_X 25
#define PIN_MAX_Y 26
#define PIN_MIN_Y 27


// QUESTO PIN DOVRÀ ESSERE COLLEGATO AD UN CONVERTITORE DI SEGNALE DA 5V A 3.3V
#define PIN_ERRORE 36

void setup(){
  pinMode(PIN_MAX_Z, INPUT_PULLUP);
  pinMode(PIN_MAX_Y, INPUT_PULLUP);
  pinMode(PIN_MAX_X, INPUT_PULLUP);
  pinMode(PIN_MIN_Z, INPUT_PULLUP);
  pinMode(PIN_MIN_Y, INPUT_PULLUP);
  pinMode(PIN_MIN_X, INPUT_PULLUP);
  pinMode(PIN_ERRORE, OUTPUT);
  digitalWrite(PIN_ERRORE, LOW);
  // VERRANNO ANCHE INSERITI DEI LED IN SERIE AGLI INGRESSI
  Serial.begin(9600);
}


unsigned long tempo_prima = 0;
unsigned long tempo_adesso = 0;

int sp1=1,sp2=1,sp3=1,sp4=1,sp5=1,sp6=1;
int s1=0,s2=0,s3=0,s4=0,s5=0,s6=0;

void loop(){
  s1=digitalRead(PIN_MAX_Z);
  s2=digitalRead(PIN_MAX_Y);
  s3=digitalRead(PIN_MAX_X);
  s4=digitalRead(PIN_MIN_Z);
  s5=digitalRead(PIN_MIN_Y);
  s6=digitalRead(PIN_MIN_X);


  
  if(sp1!=s1 || sp2!=s2 || sp3!=s3 || sp4!=s4 || sp5!=s5 || sp6!=s6){
    tempo_adesso = millis();
    if(tempo_adesso-tempo_prima > 70){
      if(s1==0){
        digitalWrite(PIN_ERRORE, HIGH);
        Serial.println(PIN_MAX_Z);
              
      }else if(s3==0){
        digitalWrite(PIN_ERRORE, HIGH);
        Serial.println(PIN_MAX_X);        
      }else if(s2==0){
        digitalWrite(PIN_ERRORE, HIGH);
        Serial.println(PIN_MAX_Y);
      }else if(s4==0){
        digitalWrite(PIN_ERRORE, HIGH);
        Serial.println(PIN_MIN_Z);        
      }else if(s5==0){
        digitalWrite(PIN_ERRORE, HIGH);
        Serial.println(PIN_MIN_Y);        
      }else if(s6==0){
        digitalWrite(PIN_ERRORE, HIGH);
        Serial.println(PIN_MIN_X);        
      }else{
        digitalWrite(PIN_ERRORE, LOW);
      }
    }
  }else{
        digitalWrite(PIN_ERRORE, LOW);
      }
  sp1=s1;
  sp2=s2;
  sp3=s3;
  sp4=s4;
  sp5=s5;
  sp6=s6;
  tempo_prima = tempo_adesso;
  delay(50);
}
