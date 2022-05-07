#define PIN_SIGNAL A4
#define DELAY_SEGNALE 100

void setup() {
  Serial.begin(9600);
}

int valore = 0;

void loop() {
  valore = analogRead(PIN_SIGNAL);
  Serial.println(valore);
  delay(DELAY_SEGNALE);
    
}
