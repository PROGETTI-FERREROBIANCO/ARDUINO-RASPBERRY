import PySimpleGUI as sg
import serial
import datetime
import random

arduino = serial.Serial('/dev/ttyUSB0',9600)
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.

val = 0
message = []
MESSAGE_SENT = 0
MESSAGE_RECEVEID = 1
SEND_DATA = "#"
TOTAL_MESSAGE = 10
message_justification = ["right", "left"]
message_background_color = ["blue", "green"]
send_message = True

def positiveVal(v):
    if( v - TOTAL_MESSAGE) < 0:
        return 0
    else: return v - TOTAL_MESSAGE

layout = [sg.Column(([(sg.Text(size=(65,1),border_width=2, font="Times", key=str(a)))] for a in range(TOTAL_MESSAGE))), sg.Slider(range=(positiveVal(len(message)), 0), default_value=0, size=(10, 10), orientation="v",  background_color="orange", trough_color="grey",enable_events=True, key="slider", disable_number_display=True)]
layout = [layout, [sg.Text('Testo da inviare: ', font="Times"), sg.InputText(), sg.Button('Invia', font="Times")] ]

# Create the Window
window = sg.Window('Window Title', layout)



def sendMessage(values):
    string_to_send = list(values[0])
    string_to_send.append("-")
    for element in string_to_send:
        arduino.write(element.encode())


def readMessage():
    global send_message
    complete_string = ""
    last_char = ""
    while last_char != '-' :
        complete_string += last_char
        last_char = arduino.read()
        last_char = str(last_char).replace("b'", "").split("\\")[0].split("'")[0]
        print(last_char)

        
    print(complete_string)
    message.append((MESSAGE_RECEVEID, complete_string))
    
    send_message = True
    #msg = arduino.readline()
    
    
def drawMessage(d_value):
    global window
    global layout
    if len(message) < TOTAL_MESSAGE:
        for a in range(len(message)):
            window[str(a)].update(message[a][1])
            window[str(a)].update(text_color=message_background_color[message[a][0]])
            #window[str(a)].update(justification=message_justification[message[a][0]])
    else:
        for a in range(TOTAL_MESSAGE):
            window[str(a)].update(message[a+d_value][1])
            window[str(a)].update(text_color=message_background_color[message[a+d_value][0]])
            #window[str(a)].update(justification=message_justification[message[a+d_value][0]])
    window["slider"].update(range=(positiveVal(len(message)), 0))

def main():
    global layout
    global window
    global val
    global send_message
    # Event Loop to process "events" and get the "values" of the inputs

    while True:
        """if send_message==False:
            readMessage()
            print("Messaggio letto!")"""

        
        event, values = window.read()        
        #drawMessage(len(message)-TOTAL_MESSAGE)
        #window.refresh()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        if event == "slider":
            val = int(values["slider"])
            window.Element("slider").Update(val)
            drawMessage(val)
        if event == "Invia" and send_message:
            sendMessage(values)
            send_message = False
            message.append((MESSAGE_SENT, values[0]))
            drawMessage(len(message)-TOTAL_MESSAGE)
            window.refresh()
            print("messaggio inviato!")
            if send_message==False:
                readMessage()
            print("Messaggio letto!")
            drawMessage(len(message)-TOTAL_MESSAGE)
            window.refresh()
                    

    window.Close()
    arduino.close()

if __name__ == "__main__":
    main()