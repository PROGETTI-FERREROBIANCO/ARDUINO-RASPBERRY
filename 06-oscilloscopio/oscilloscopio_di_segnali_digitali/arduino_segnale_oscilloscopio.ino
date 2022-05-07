//Questo programma crea un impulso elettrico

#define PIN_OUTPUT 34

void setup() {
  pinMode(PIN_OUTPUT, OUTPUT);

}

//Il pin 7 sta 1 secondo alto e 1 secondo basso
void loop() {
  digitalWrite(PIN_OUTPUT, HIGH);
  delay(1000);
  digitalWrite(PIN_OUTPUT, LOW);
  delay(1000);
}
