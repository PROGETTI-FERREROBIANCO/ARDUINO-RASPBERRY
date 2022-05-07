"""
Creazione oscilloscopio con arduino
"""


#inclusione librerie
import turtle
from turtle import Screen, Turtle
from PIL import Image
import serial
import time
#----------------------------------


#avvio comunicazione seriale con la porta a cui è collegato l'arduino uno
arduino = serial.Serial('/dev/ttyACM0',9600)     
time.sleep(1)
#----------------------------------


#inizializzazione finestra di turtle
screen = turtle.Screen()
screen.title("GRAFICO")
screen.setworldcoordinates(-50, -50, 50, 50)
screen.bgpic("sfondo_oscilloscopio.gif")
screen.cv._rootwindow.resizable(False, False)   #blocco la ridimensione della finestra
#----------------------------------


#definizione variabili
condizione_while=True
x = 0
y = 0
#----------------------------------


#definizione funzione per settaggio parametri iniziali
def punto_iniziale():
    global x
    global y
    x=-48
    y=0
    screen.clearscreen()  #pulisco lo schermo
    screen.bgpic("sfondo_oscilloscopio.gif")  #settaggio immagine di sfondo
    turtle.penup()  #alzo la penna
    turtle.goto(x,y)   #muovo la penna al punto desiderato
    turtle.pendown()   #abbasso la penna
    turtle.color("red")  #imposto la penna di colore rosso
#----------------------------------


#definizione funzione per disegno grafico
def oscilloscopio(tempo_valore, valore):
    global x
    global y
    tempo_valore = int(tempo_valore)
    valore=int(valore)

    if(valore==1):   #se valore = 1 setto valore = 30
        valore=int(30)
    elif(valore==0 and x==-48 and y==0):   #se valore = 0 e ci troviamo all'inizio del grafico setto valore = 0
        valore=int(0)
    elif(valore==0 and y!=0):  # se valore = 0 e y != 0 setto valore = -30
        valore=int(-30)
    print("x: "+ str(x) + ", y: "+ str(y) + ", valore: "+ str(valore) + ", tempo_valore: "+ str(tempo_valore))
    y+=valore
    turtle.goto(x,y)   #vado alle coordinate x e y indicate
    x+=(tempo_valore/100)*5/4.5    #arrotondiamo il valore della x
    turtle.goto(x,y)   #vado alle coordinate x e y indicate
    if(x>50):   #se si va fuori dal grafico si resetta tutto
        punto_iniziale()
#----------------------------------


#definizione funzione per cambio valore della variabile f
def set_condizione_while():
    global condizione_while
    condizione_while=False
#----------------------------------


#definizione main
def main(): 
    valore = 0
    tempo_valore = 0

    global condizione_while
    condizione_while=True
    
    punto_iniziale()   #inizializzazione schermata

    while(condizione_while==True):
        turtle.listen()   #impostiamo il monitor in ascolto della premuta di qualche tasto
        turtle.onkey(set_condizione_while, "space")   #se si preme il tasto space eseguo la funzione set_condizione_while
        tempo_valore=int(arduino.readline())   #leggo i valori dalla seriale
        valore=int(arduino.readline())
        print(tempo_valore)
        print(valore)

        oscilloscopio(tempo_valore, valore)   #eseguo la funzione per disegnare il grafico
       
    screen.mainloop()   #lascio il monitor aperto anche dopo l'esecuzione
#----------------------------------

main()    #esecuzione main






