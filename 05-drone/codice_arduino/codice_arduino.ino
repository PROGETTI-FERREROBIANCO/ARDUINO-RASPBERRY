/***********************************************************
                          DRONE

Programma realizzato da Isabella Bianco e Gabriele Ferrero
per un progetto di telecomunicazioni.

+ POSIZIONE DEI MOTORI:

        1   2
        
        3   4

- Per andare AVANTI bisogna diminuire:        1 e 2  [la y è positiva]
- Per andare a DESTRA bisogna diminuire:      2 e 4  [la x è positiva]
- Per andare INDIETRO bisogna diminuire:      4 e 3  [la y è negativa]
- Per andare a SINISTRA bisogna diminuire:    3 e 1  [la x è negativa]
- Per RUOTARE su se stesso bisogna diminuire: 1 e 4 oppure 2 e 3
 
***********************************************************/

/*-- INCLUSIONE LIBRERIE --*/

#include <nRF24L01.h>
#include <RF24_config.h>
#include <RF24.h>
#include <MPU6050_tockn.h>
#include <Wire.h>
#include <SPI.h>
#include <Servo.h>
#include <PID_v1.h>

/*------------------------*/


/*-- DEFINIZIONE COSTANTI --*/

#define MIN_VELOCITA 1000
#define MAX_VELOCITA 2000
#define MAX_DIM 7
#define ABBASSA_MOTORE 10
#define NUM_MOTORI 4
#define VARIAZIONE_ANGOLO 20  

/*------------------------*/


/*-- CREAZIONE VARIABILI PER IL RICEVIMENTO ED INTERPRETAZIONE DEL MESSAGGIO --*/

/*
 * Formato del messaggio inviato: AZIONE_MOTORE;VALORE_AZIONE
 * 
 * Tipi di AZIONE_MOTORE: [a, b, c, d, e, f, g]
 * I quali corrisponderebbero a: [AVANTI, INDIETRO, DESTRA, SINISTRA, ROTAZIONE, FERMO, ALTEZZA]
 * 
 * Range di grandezza VALORE_AZIONE: [0, 1023]
 * 
 */

char stringa_ricevuta[MAX_DIM] = "";
int valore_azione;
char azione_motori;

/*------------------------*/

/*-- CREAZIONE VARIABILI PER GESTIRE I MOTORI DEL DRONE --*/

double throttle = 1000;
double offset_x = 0;
double offset_y = 0;

/*---X---*/
double Kp_x=2;
double Ki_x=5;
double Kd_x=1;
/*---Y---*/
double Kp_y=2;
double Ki_y=5;
double Kd_y=1;
///////////////////////////////////////////////

/*---X---*/
double desired_angle_x = 0; //This is the angle in which we whant the balance to stay steady
double measured_angle_x = 0;
/*---Y---*/
double desired_angle_y = 0; //This is the angle in which we whant the balance to stay steady
double measured_angle_y = 0;

/*------------------------*/

/*-- CREAZIONE OGGETTI --*/

/* Creazione oggetto giroscopio */
MPU6050 mpu6050(Wire);

/* Creazione oggetto antenna */
RF24 radio(7, 8); // CE, CSN
const byte indirizzo[5] = {0,0,0,0,0};

/* Creazione oggetto motori */
Servo motori[NUM_MOTORI];

/* Creazione oggetti PID */
PID PIDx(&measured_angle_x, &offset_x, &desired_angle_x, Kp_x, Ki_x, Kd_x, DIRECT);
PID PIDy(&measured_angle_y, &offset_y, &desired_angle_y, Kp_y, Ki_y, Kd_y, DIRECT);
/*------------------------*/

/////////////////////////////// INIZIO SETUP /////////////////////////////////////////
void setup() {

  /*-- INIZIALIZZAZIONE OGGETTI --*/
  
  /* Inizializzazione giroscopio */
  Serial.begin(9600);
  Wire.begin();
  mpu6050.begin();
  mpu6050.calcGyroOffsets(true);

  /* Inizializzazione PID */
  PIDx.SetMode(AUTOMATIC);
  PIDy.SetMode(AUTOMATIC);

  /* Inizializzazione antenna */
  radio.begin();
  radio.setPALevel(RF24_PA_MIN);  /*DA MODIFICARE PER AUMENTARE LA DISTANZA DI COMUNICAZIONE*/
  radio.openReadingPipe(1, indirizzo); 
  radio.startListening();

  /* Inizializzazione motori */
  motori[0].attach(3);
  motori[1].attach(5);
  motori[2].attach(6);
  motori[3].attach(10);

  /*------------------------*/

  /*-- SETTAGGIO RANGE MOTORI --*/

  delay(5000);
  
  settaggioRangeMotori();

  /*------------------------*/

  /* Delay per dividere l'esecuzione del SETUP dal LOOP */
  delay(5000);
}
/////////////////////////////// FINE SETUP /////////////////////////////////////////


/////////////////////////////// INIZIO LOOP /////////////////////////////////////////
void loop() {
  mpu6050.update();
  if(valore_azione == 'b'){
    for(int i=0; i<NUM_MOTORI; i++){
    motori[i].writeMicroseconds(MIN_VELOCITA);
    }
  }else{
    measured_angle_x = mpu6050.getAngleX();
    measured_angle_y = mpu6050.getAngleY();
    PIDx.Compute();
    PIDy.Compute();
    movimentoMotoriAsseX();
    movimentoMotoriAsseY();
  }
  
  if (radio.available()) {
      radio.read(&stringa_ricevuta, sizeof(stringa_ricevuta));
      Serial.println(stringa_ricevuta);
      memorizzaAzioneMotori();
      memorizzaValoreAzione();
      muoviMotori();
  }    
}
/////////////////////////////// FINE LOOP /////////////////////////////////////////

/*++++++++++ INIZIO FUNZIONE PER IL SETTAGGIO DEI MOTORI ++++++++++*/
void settaggioRangeMotori(){
  /*
   * 
   */
  for(int i=0; i<NUM_MOTORI; i++){
    motori[i].writeMicroseconds(MAX_VELOCITA);
  }
  delay(5000);
  for(int i=0; i<NUM_MOTORI; i++){
    motori[i].writeMicroseconds(MIN_VELOCITA);
  }
}
/*++++++++++ FINE FUNZIONE ++++++++++*/

/*++++++++++ INIZIO FUNZIONE PER LA MEMORIZZAZIONE DELLA AZIONE CHE DOVRANNO COMPIERE I MOTORI ++++++++++*/
void memorizzaAzioneMotori(){
  /*
   * 
   */
  azione_motori = stringa_ricevuta[0];
}
/*++++++++++ FINE FUNZIONE ++++++++++*/

/*++++++++++ INIZIO FUNZIONE PER LA MEMORIZZAZIONE DEL VALORE DELL'AZIONE ++++++++++*/
void memorizzaValoreAzione(){
  /*
   * 
   */
  valore_azione = atoi(&stringa_ricevuta[2]);  
  Serial.println(valore_azione);
}
/*++++++++++ FINE FUNZIONE ++++++++++*/

/*++++++++++ INIZIO FUNZIONE PER IL CALCOLO DEL MOVIMENTO DEI MOTORI ++++++++++*/
void muoviMotori(){
  /*
   * 
   */
  desired_angle_x = 0;
  desired_angle_y = 0;
    
  switch(azione_motori){
    case 'a':
      throttle = valore_azione;       
      break;
     case 'b': // caso in cui il drone viene spento [usare solo in casi di pericolo]   
      throttle = 1000;
      break;
     case 'u':
      throttle = valore_azione;  
      desired_angle_y += VARIAZIONE_ANGOLO;     
      break;
     case 'd':
      throttle = valore_azione;
      desired_angle_y -= VARIAZIONE_ANGOLO;             
      break;
     case 'l':
      throttle = valore_azione;
      desired_angle_x -= VARIAZIONE_ANGOLO;            
      break;
     case 'r':
      throttle = valore_azione;
      desired_angle_x += VARIAZIONE_ANGOLO;
      break;
  }
}
/*++++++++++ FINE FUNZIONE ++++++++++*/

/*++++++++++ INIZIO FUNZIONE PER IL MOVIMENTO DEI MOTORI ASSE X ++++++++++*/
void movimentoMotoriAsseX(){
  motori[0].writeMicroseconds(throttle - offset_x);
  motori[1].writeMicroseconds(throttle - offset_x);
  motori[2].writeMicroseconds(throttle + offset_x);
  motori[3].writeMicroseconds(throttle + offset_x);
}
/*++++++++++ FINE FUNZIONE ++++++++++*/

/*++++++++++ INIZIO FUNZIONE PER IL MOVIMENTO DEI MOTORI ASSE Y ++++++++++*/
void movimentoMotoriAsseY(){
  motori[0].writeMicroseconds(throttle - offset_y);
  motori[1].writeMicroseconds(throttle + offset_y);
  motori[2].writeMicroseconds(throttle - offset_y);
  motori[3].writeMicroseconds(throttle + offset_y);
}
/*++++++++++ FINE FUNZIONE ++++++++++*/
