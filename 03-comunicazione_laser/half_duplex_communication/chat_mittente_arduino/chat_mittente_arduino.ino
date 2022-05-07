#define FOTOTRANSISTOR A1
#define LASER 8
#define TEMPO_SEGNALE_LUNGO 100
#define TEMPO_SEGNALE_CORTO 50
#define TEMPO_DI_PAUSA_TRA_SEGNALI 50
#define SEGNALE_ANALOGICO_HIGH 950
#define TEMPO_SEGNALE_CORTO_APPROSSIMATO 65

void setup() {
  pinMode(LASER, OUTPUT);
  Serial.begin(9600);
}

unsigned long t_zero;
long ch = 0;

void loop() {

  // INVIO
  while(!Serial.available()){}
  while(Serial.available()){
  char ch = Serial.read();
  if((ch=='\n') || (ch=='\r')){}
  else{process(ch);}
  }

  // RICEZIONE
  char carattere = '0';
  while(carattere != '-'){
    for(int i = 0; i < 6; i++){
        acquisizione_stringa_binario();
      }
     
    //Chiama la funzione conversione e lo stampa
    
    carattere = conversione();
    Serial.println(carattere);
    ch = 0;

  }
}

//Conversione dei vari caratteri in una sequenza di 6 segnali che possono essere lunghi o corti
void process(char ch){
    switch(ch){
      case '0':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      break;
      case '1':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      break;
      case '2':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      break;
      case '3':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      break;
      case '4':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      break;
      case '5':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      break;
      case '6':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      break;
      case '7':
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      break;
      case '8':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      break;
      case '9':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'a':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'b':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      break;
      case 'c':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      break;
      case 'd':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'e':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'f':
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      break;
      case 'g':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      break;
      case 'h':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'i':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'j':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      break;
      case 'k':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      break;
      case 'l':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'm':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'n':
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      break;
      case 'o':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      break;
      case 'p':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'q':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'r':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      break;
      case 's':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      break;
      case 't':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'u':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'v':
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      break;
      case 'w':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      break;
      case 'x':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      break;
      case 'y':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      break;
      case 'z':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      break;
      case '?':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      break;
      case '!':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      break;
      case ' ':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      break;
      case '.':
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleCorto();
      break;
      case ';':
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleLungo();
      break;
      case ',':
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      segnaleCorto();
      break;
      case '-':
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      break;
      case ':':
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      break;
      case '\'':
      segnaleCorto();
      segnaleLungo();
      segnaleCorto();
      segnaleCorto();
      segnaleLungo();
      segnaleLungo();
      break;
      default:
      break;
  }
}
//IL segnale lungo consiste nell'inviare un segnale di 100ms
void segnaleLungo(){
  digitalWrite(LASER, HIGH);
  delay(TEMPO_SEGNALE_LUNGO);
  digitalWrite(LASER, LOW);
  delay(TEMPO_DI_PAUSA_TRA_SEGNALI);
}
//IL segnale corto consiste nell'inviare un segnale di 50ms
void segnaleCorto(){
  digitalWrite(LASER, HIGH);
  delay(TEMPO_SEGNALE_CORTO);
  digitalWrite(LASER, LOW);
  delay(TEMPO_DI_PAUSA_TRA_SEGNALI);
}

//Calcola per quanti millisecondi il laser è acceso
void acquisizione_stringa_binario(){
  while(analogRead(FOTOTRANSISTOR)<SEGNALE_ANALOGICO_HIGH){}

  t_zero=millis();
  while(analogRead(FOTOTRANSISTOR)>SEGNALE_ANALOGICO_HIGH){}
  if((millis()-t_zero)>TEMPO_SEGNALE_CORTO_APPROSSIMATO){
    ch = ch*10 + 0;
  }else{
    ch = ch*10 + 1;
  }
}

//Converte il segnale in un carattere
char conversione(){
  char carattere;
  switch(ch){
     case 0:
        carattere = '0';
        break;
     case 1:
        carattere = '1';
        break;
     case 10:
        carattere = '2';
        break;
     case 11:
        carattere = '3';
        break;  
     case 100:
        carattere = '4';
        break;
     case 101:
        carattere = '5';
        break;
     case 110:
        carattere = '6';
        break;
     case 111:
        carattere = '7';
        break;
     case 1000:
        carattere = '8';
        break;
     case 1001:
        carattere = '9';
        break;
     case 1010:
        carattere = 'a';
        break;
     case 1011:
        carattere = 'b';
        break;
     case 1100:
        carattere = 'c';
        break;
     case 1101:
        carattere = 'd';
        break;
     case 1110:
        carattere = 'e';
        break;
     case 1111:
        carattere = 'f';
        break;
     case 10000:
        carattere = 'g';
        break;
     case 10001:
        carattere = 'h';
        break;
     case 10010:
        carattere = 'i';
        break;
     case 10011:
        carattere = 'j';
        break;
     case 10100:
        carattere = 'k';
        break;
     case 10101:
        carattere = 'l';
        break;
     case 10110:
        carattere = 'm';
        break;
     case 10111:
        carattere = 'n';
        break;
     case 11000:
        carattere = 'o';
        break;
     case 11001:
        carattere = 'p';
        break;
     case 11010:
        carattere = 'q';
        break;
     case 11011:
        carattere = 'r';
        break;
     case 11100:
        carattere = 's';
        break;
     case 11101:
        carattere = 't';
        break;
     case 11110:
        carattere = 'u';
        break;
     case 11111:
        carattere = 'v';
        break;
     case 100000:
        carattere = 'w';
        break;
     case 100001:
        carattere = 'x';
        break;
     case 100010:
        carattere = 'y';
        break;
     case 100011:
        carattere = 'z';
        break;
     case 100100:
        carattere = '?';
        break;
     case 100101:
        carattere = '!';
        break;
     case 100110:
        carattere = ' ';
        break;
     case 100111:
        carattere = '.';
        break;
     case 101000:
        carattere = ';';
        break;
     case 101001:
        carattere = ',';
        break;
     case 101010:
        carattere = '-';
        break;
     case 101011:
        carattere = ':';
        break;
     case 101100:
        carattere = '\'';
        break;
     default:
        carattere = '#';
        break;
  }
  return carattere;
}
