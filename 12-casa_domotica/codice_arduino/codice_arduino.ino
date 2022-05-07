String dati = "";
char c;

void setup(){
  Serial.begin(9600);
}

void loop(){
  
  while(Serial.available()){
    c = Serial.read();
    if(c != '!'){
      if(c != '\r' && c != '\n'){
        dati += c;        
      }
    }else{

      // MESSAGGIO: IO#dato1#dato2!
      

      String IO = split(dati, '#', 0);
      
      if(IO == "INPUT"){
        String protocollo = split(dati, '#', 1);
        int valore = split(dati, '#', 2).toInt();


        float corrente;
        
        if(protocollo == "ANALOGICO"){
          int corr = analogRead(valore);
          corrente = map(corr, 0, 1023, 0, 5);
          
        }
        
        Serial.print(corrente);
        
        
      }else{
        int pin = split(dati, '#', 1).toInt();
        int stato = split(dati, '#', 2).toInt();
        pinMode(pin, OUTPUT);
        if (stato == 0){
          digitalWrite(pin, LOW);
        }else{
          digitalWrite(pin, HIGH);
        }
      }
      
      dati = "";

      Serial.print("-");

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
