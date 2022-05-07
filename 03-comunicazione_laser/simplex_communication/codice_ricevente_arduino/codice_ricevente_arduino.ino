#define pin_sensore_fotoresistenza A4
#define time_segnale_lungo 100
#define time_segnale_corto_approssimato 65
#define time_pausa_tra_segnali 50
#define segnale_analogico_HIGH 700

void setup() {
  Serial.begin(9600);
  Serial.println("stringa acquisita:");
}

long t_zero;

long ch = 0;


void loop() {
    //Per 6 volte chiamo la funzione acquisizione_stringa_binario
    for(int i = 0; i < 6; i++){
      acquisizione_stringa_binario();
    }
   
  //Chiama la funzione conversione e lo stampa
    char carattere;
    carattere = conversione();
    Serial.print(carattere);
    ch = 0;

  }
//Calcola per quanti millisecondi il laser è acceso
void acquisizione_stringa_binario(){
  while(analogRead(pin_sensore_fotoresistenza)<segnale_analogico_HIGH){}


    t_zero=millis();
    while(analogRead(pin_sensore_fotoresistenza)>segnale_analogico_HIGH){}
    if((millis()-t_zero)>time_segnale_corto_approssimato){
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
