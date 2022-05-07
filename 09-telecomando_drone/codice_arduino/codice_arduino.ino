/*
FUNZIONE DEI TASTI DEL TELECOMANDO

Pulsanti:
  - CENTRALE: ferma i motori (b)
Joystick di destra:
- ruotare su se stesso

Joystick di sinistra:
- movimento del drone (AVANTI, DIETRO, SINISTRA, DESTRA)

In entrambi i casi i pulsanti dei joystick non sono implementati

POTENZIOMETRO:
- Seleziona il valore da 1000 a 2000

*/

//includo le librerie
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

//---------------------------------------

//Definizione ed istanza per la comunicazione con il drone

/*Creo un'istanza della "radio" passandogli il numero dei pin collegati a CE e CSN del modulo*/
RF24 radio(11, 10);
/*definizione indirizzo sul quale stabilire la comunicazione*/
const byte indirizzo[5] = {0,0,0,0,0};
//---------------------------------------

//Definisco le dimensioni del display
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
//---------------------------------------

//Definisco le variabile dei due joystick
#define JOYSTICK_SX_X A2
#define JOYSTICK_DX_X A0
#define JOYSTICK_SX_Y A3
#define JOYSTICK_DX_Y A1
#define JOYSTICK_SX_BUTTON 40
#define JOYSTICK_DX_BUTTON 42
//---------------------------------------

//Definisco le variabili dei pulsanti
#define BUTTON_SX 23
#define BUTTON_DX 37
#define BUTTON_UP 49
#define BUTTON_DOWN 22
#define BUTTON_CENTRE 36
//--------------------------------------- 

//Definisco la varabile del potenziometro
#define POTENZIOMETRO A4
//---------------------------------------

//Dichiaro le variabili globali per inviare il messaggio al drone
bool comunicazione_abilitata = false;
int valore_potenziometro = 1000;
String comando_drone = "b";
String testo = "";
String joystick_sx = "";
String joystick_dx = "";
String string_to_send = "";
//---------------------------------------

// Creo istanza del display
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT);
//---------------------------------------

/*INIZIO DEL SETUP*/
void setup() {
  //Inizializzo la seriale
  Serial.begin(9600);
  //---------------------------------------

  //Inizializzo la radio
  radio.begin();
  /*
     La radio può lavorare a diverse potenze: RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH e RF24_PA_MAX
     Che corrispondono a: -18dBm, -12dBm,-6dBM, e 0dBm
  */
  
  /*Setto la potenza della radio a LOW*/
  radio.setPALevel(RF24_PA_MIN);

  /*Apro un canale di comunicazione sull'indirizzo specificato (sarà lo stesso per il ricevitore)*/
  radio.openWritingPipe(indirizzo);

  /*Richiamando questo metodo sto impostando la radio come trasmettitore*/
  radio.stopListening();
  //---------------------------------------

  //Inizializzo i pulsanti
  pinMode(BUTTON_SX, INPUT_PULLUP);
  pinMode(BUTTON_DX, INPUT_PULLUP);
  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
  pinMode(BUTTON_CENTRE, INPUT_PULLUP);
  //---------------------------------------

  //Inizializzo i joystick
  pinMode(JOYSTICK_SX_BUTTON, INPUT_PULLUP);
  pinMode(JOYSTICK_DX_BUTTON, INPUT_PULLUP);
  //---------------------------------------
  
  //Inizializzo il display all'indirizzo 0x3C
  if (!display.begin( SSD1306_SWITCHCAPVCC, 0x3C)) {
    /*
      Se non sono riuscito ad inizializzare il display
      creo un loop infinito ed impedisco al programma di andare avanti
    */
    Serial.println("errore");
    while (true);
  }
  // Pulisco il buffer
  display.clearDisplay();
  // Applico la pulizia al display
  display.display();
  //I due passaggi qui sopra evitano di mostrare il logo adafruit all'avvio
  //---------------------------------------
}

/*INIZIO VOID LOOP*/
void loop(){

  //Ripulisco il buffer
  display.clearDisplay();
    getDataJoystick();
    getDataPotenziometro();
    pulsantePremuto();
  if (!comunicazione_abilitata){
    valore_potenziometro = 1000;
    comando_drone = "b";
  }
  
  string_to_send = comando_drone + "-" + (String)valore_potenziometro;
  int len= string_to_send.length();
  char input_da_inviare[len] = "";
  for(int i=0; i<len; i++){
    input_da_inviare[i] = string_to_send[i];
    Serial.println(input_da_inviare[i]);
  }
  radio.stopListening();
  radio.write(&input_da_inviare, sizeof(input_da_inviare)); 
  stampaTesto("-.-.-.-.-.-.-.-.-.-.-", 0, 40);
  stampaTesto(string_to_send, 50, 50);
  delay(200);
  
}

/*INIZIO FUNZIONI*/

//Funzione che controlla i pulsanti premuti e li stampa sul monitor
void pulsantePremuto(){
  String testo_precedente = testo;
  testo = "";
  if(!digitalRead(BUTTON_SX)){
    testo = "sx";
  }
  if(!digitalRead(BUTTON_DX)){
    testo = "dx";
  }
  if(!digitalRead(BUTTON_UP)){
    testo = "u";
  }
  if(!digitalRead(BUTTON_DOWN)){
    testo = "d";
  }
  if(!digitalRead(BUTTON_CENTRE)){
    comunicazione_abilitata = !comunicazione_abilitata;
    comando_drone = "b";
    testo = "c";
  }
  if(!digitalRead(JOYSTICK_SX_BUTTON)){
    testo = "js";
  }
  if(!digitalRead(JOYSTICK_DX_BUTTON)){
    testo = "jd";
  }
  stampaTesto("pulsante: "+testo, 0, 0);
  
  return;
}
//---------------------------------------

//Funzione che stampa il testo sul monitor
void stampaTesto(String testo, int coord_x, int coord_y) {

  display.setCursor(coord_x, coord_y);

  //Setto il colore del testo a "bianco"
  display.setTextColor( WHITE);

  //Setto dimensione del testo
  display.setTextSize(1);

  //Stampo una scritta
  display.println(testo);

  //La mando in stampa
  display.display();

}
//---------------------------------------

void getDataJoystick(){
  int coord_x_sx = analogRead(JOYSTICK_SX_X);
  int coord_y_sx = analogRead(JOYSTICK_SX_Y);
  int coord_x_dx = analogRead(JOYSTICK_DX_X);
  int coord_y_dx = analogRead(JOYSTICK_DX_Y);

  //AVANTI: (0:500) INDIETRO: (800:550) 
  //SINISTRA: (500:1023) DESTRA: (500:0)
  // CENTRO: (500:500)
  joystick_dx = getDirectionJoystick(coord_x_dx, coord_y_dx); 
  stampaTesto("JD: "+joystick_dx, 0, 10);

  comando_drone = joystick_dx;
  
  joystick_sx = getDirectionJoystick(coord_x_sx, coord_y_sx); 
  stampaTesto("JS: "+joystick_sx, 0, 20);
  if (joystick_sx != "a"){
    comando_drone = joystick_sx;
  }
  return;
}

String getDirectionJoystick(int coord_x, int coord_y){
  String direction = "a";
  if(isLeft(coord_x, coord_y)){
    direction = "l";
  }
  if(isRight(coord_x, coord_y)){
    direction = "r";
  }
  if(isUp(coord_x, coord_y)){
    direction = "u";
  }
  if(isDown(coord_x, coord_y)){
    direction = "d";
  }
  return direction;
}

bool isLeft(int coord_x, int coord_y){
  return ((coord_x > 250 && coord_x < 600)&&(coord_y > 750));
}

bool isRight(int coord_x, int coord_y){
  return ((coord_x > 250 && coord_x < 600)&&(coord_y < 250));
}

bool isUp(int coord_x, int coord_y){
  return ((coord_x<=250)&&(coord_y>=250 && coord_y <=750));
}

bool isDown(int coord_x, int coord_y){
  return ((coord_x >=600) && (coord_y>=250 && coord_y <=750));
}

void getDataPotenziometro(){
  valore_potenziometro = map(analogRead(POTENZIOMETRO), 0, 1023, 100, 200);
  valore_potenziometro = valore_potenziometro*10;
  stampaTesto("Potenza: "+ (String) valore_potenziometro, 0, 30);
}
