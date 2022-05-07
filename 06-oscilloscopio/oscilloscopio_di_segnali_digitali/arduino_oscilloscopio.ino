#define PIN_SIGNAL 4

void setup() {
  pinMode(PIN_SIGNAL, INPUT);
  Serial.begin(9600);
}
int tempo_iniziale=0;
void loop() {
  int valore=0;
  int tempo_valore=0;
//Se il segnale è HIGH allora valore è 1 e calcolo il tempo in cui è rimasto alto
  if(digitalRead(PIN_SIGNAL)==HIGH){
    valore=1;
    tempo_iniziale = millis();
    while(digitalRead(PIN_SIGNAL)==HIGH){}
    tempo_valore=millis()-tempo_iniziale;
    Serial.println(tempo_valore);
    Serial.println(valore);
//Se il segnale è LOW allora valore è 0 e calcolo il tempo in cui è rimasto basso
  }else if(digitalRead(PIN_SIGNAL)==LOW){
    valore=0;
    tempo_iniziale = millis();
    while(digitalRead(PIN_SIGNAL)==LOW){}
    tempo_valore=millis()-tempo_iniziale;
    Serial.println(tempo_valore);
    Serial.println(valore);
    
  }

}
