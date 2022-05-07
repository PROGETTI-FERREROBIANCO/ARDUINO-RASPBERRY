"""



   _____ _            _                    __  __      _                       _             _             _____             _____ _____  ____  ______ _____  _______     __
  / ____| |          (_)                  |  \/  |    | |                     | |           (_)           |  __ \     /\    / ____|  __ \|  _ \|  ____|  __ \|  __ \ \   / /
 | (___ | |_ __ _ _____  ___  _ __   ___  | \  / | ___| |_ ___  ___  _ __ ___ | | ___   __ _ _  ___ __ _  | |__) |   /  \  | (___ | |__) | |_) | |__  | |__) | |__) \ \_/ / 
  \___ \| __/ _` |_  / |/ _ \| '_ \ / _ \ | |\/| |/ _ \ __/ _ \/ _ \| '__/ _ \| |/ _ \ / _` | |/ __/ _` | |  _  /   / /\ \  \___ \|  ___/|  _ <|  __| |  _  /|  _  / \   /  
  ____) | || (_| |/ /| | (_) | | | |  __/ | |  | |  __/ ||  __/ (_) | | | (_) | | (_) | (_| | | (_| (_| | | | \ \  / ____ \ ____) | |    | |_) | |____| | \ \| | \ \  | |   
 |_____/ \__\__,_/___|_|\___/|_| |_|\___| |_|  |_|\___|\__\___|\___/|_|  \___/|_|\___/ \__, |_|\___\__,_| |_|  \_\/_/    \_\_____/|_|    |____/|______|_|  \_\_|  \_\ |_|   
                                                                                        __/ |                                                                               
                                                                                       |___/                                                                                



"""


""" _______________________INCLUSIONE LIBRERIE________________________"""

import threading
import serial
from time import sleep
import datetime
from pathlib import Path
from mega import Mega
import subprocess
import logzero
from flask import Flask, jsonify
from tensorflow import keras
from PIL import Image, ImageOps
import numpy as np
import smtplib 

""" //////////////////////////////////////////////////////////////// """


""" ______________________DEFINIZIONE COSTANTI______________________ """

#       DATI STAZIONE      #
id_stazione = 0
sensori = []
# ------------------------ #

#          DELAY           #
SECONDI_TRA_SCATTO_FOTO = 60*5
# ------------------------ #

#    PERCORSO CARTELLA     #
dir_path = str(Path(__file__).parent.resolve())
print(dir_path)
# ------------------------ #

#   ACCESSO ACCOUNT MEGA   #
email = "..."
password = "..."
# ------------------------ #

#      FILE PER ERRORI     #
file_info_error= logzero.setup_logger(name='file_info_error', logfile=f"{dir_path}/log/file_info_error.csv") 
# ------------------------ #

#         ARDUINO          #
try:
    arduino = serial.Serial('/dev/ttyUSB0',115200)
except:
    file_info_error.error("error arduino connection")
    
# ------------------------ #

#          SOCKET          #
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 80
# ------------------------ #

#     MACHINE LEARNING     #
#model = keras.models.load_model(f"{dir_path}/machine_learning")
# ------------------------ #

#           EMAIL          #
GMAILADDRESS = "..."
GMAILPASSWORD = "..."
MAILTO = "..."

fist_time_arduino_disconnected = False
# ------------------------ #

#          THREAD          #
scatta_foto = threading.Thread()
blocco_arduino = threading.Lock()
# ------------------------ #

""" //////////////////////////////////////////////////////////////// """

""" ____________________DEFINIZIONI ROUTE FLASK_____________________ """

app = Flask(__name__)

@app.route(f"/stazione-meteorologica/dato/sensori-attuali")
def datiSensoriAttuali():
    with blocco_arduino:
        return jsonify(letturaDatiSensori())

""" //////////////////////////////////////////////////////////////// """

""" _________________SPECIALIZZAZIONI CLASSI THREAD_________________ """

# THREAD PER LO SCATTO DELLA FOTO #

class ScattaFoto(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
     
    def run(self):

        while self.running:

            try:
                print("scatto foto")
                # SCATTA FOTO
                subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", f"{dir_path}/foto/foto.jpg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # MACHINE LEARNING SU FOTO
                nome_foto = getNomeFoto(machineLearning())

                # RINOMINAZIONE DELLA FOTO
                subprocess.run(["mv", f"{dir_path}/foto/foto.jpg", f"{dir_path}/foto/{nome_foto}"])
            except:
                file_info_error.error("photo capture error or machine learning error")


            try:
                # LOGIN A MEGA
                mega = Mega()
                m = mega.login(email, password)

                print("salvataggio dati su mega")
                # SALVATAGGIO FOTO SUL CLOUD
                folder = m.find('StazioneMeteorologica/foto', exclude_deleted=True)
                m.upload(f"{dir_path}/foto/{nome_foto}", folder[0])

                print("foto caricata ed ora la elimino")
                subprocess.call(f"rm {dir_path}/foto/'{nome_foto}'", shell=True)
                

            except:
                file_info_error.error("error upload mega")

            sleep(SECONDI_TRA_SCATTO_FOTO)

# ---------------------------------------------------------- #

""" //////////////////////////////////////////////////////////////// """

""" ________________________MACHINE LEARNING________________________ """


def machineLearning():

    """
    Funzione che serve per effettuare il machine learning sulla foto appena scattata.
    Restituisce una stringa contenente l'oggetto fotografato.
    """

    """
    try:
        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        # Replace this with the path to your image
        image = Image.open(f"{dir_path}/foto/foto.jpg")
        #resize the image to a 224x224 with the same strategy as in TM2:
        #resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        #turn the image into a numpy array
        image_array = np.asarray(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = model.predict(data)
        print(prediction)
        return prediction
    except:
        file_info_error.error("error machine learning")
        return "sconosciuto"

    """

    return "sconosciuto"

        
""" //////////////////////////////////////////////////////////////// """

# FUNZIONE PER OTTENERE IL NOME CHE DOVRANNO AVERE LE FOTO #

def getNomeFoto(oggetto_fotografato):
    data_ora_corrente = datetime.datetime.utcnow()
    data_ora_corrente = str(data_ora_corrente).replace(":", "-")  
    return f"{data_ora_corrente}_({oggetto_fotografato})_[{id_stazione}].jpg"

# ------------------------------------------------------- #


# FUNZIONE PER LA LETTURA DEI SENSORI #

def letturaDatiSensori():
    """
    Si occuperà arduino di leggere i vari sensori. Nel caso ci siano degli errori, il valore di quel sensore
    sarà 9999.9 oppure la stringa "9999.9".

    Se si presenta un errore con arduino verrà salvato il valore 8888.8
    """

    global arduino
    global fist_time_arduino_disconnected
    
    data_ora_corrente = datetime.datetime.utcnow()
    dati_sensori = {}
    dati_sensori["data_ora_stazione"] = f"{data_ora_corrente}" # salvo dentro il dizionario la data di acqusizione dei dati

    try:
        arduino.write("s".encode()) # dico all'arduino che può inviarmi i dati
        sleep(10)
        misurazioni = arduino.read_all().decode() # leggo i dati inviati dall'arduino
        misurazioni = misurazioni.split("#")

        for sensore in sensori:
            if sensore in misurazioni:
                i = misurazioni.index(sensore)

                dati_sensori[sensore] = float(misurazioni[i+1])
        
        fist_time_arduino_disconnected = False
    except:

        # GESTISCO EVENTUALI ERRORI DELL'ARDUINO

        if fist_time_arduino_disconnected == False:
            sendEmailForProblems("ARDUINO DISCONNESSO")
            arduino.close()
            fist_time_arduino_disconnected = True

        for sensore in sensori:
            dati_sensori[sensore] = 8888.8

        try:
            arduino = serial.Serial('/dev/ttyUSB0',115200)
        except:
            file_info_error.error("error arduino connection")


    return dati_sensori

# ------------------------------------------------------- #


def sendEmailForProblems(msg):
    """
    Funzione per mandare un email in caso di problemi
    """
    try:
        mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
        mailServer.starttls()
        mailServer.login(GMAILADDRESS , GMAILPASSWORD)
        mailServer.sendmail(GMAILADDRESS, MAILTO , msg)
        mailServer.quit()
    except:
        file_info_error.error("error send email")


""" //////////////////////////////////////////////////////////////// """

""" ------------------MAIN------------------ """

def main():

    # estrazione dati da file
    global sensori
    global id_stazione
    with open(f"{dir_path}/config_file.txt") as config_file_stazione:
        righe = config_file_stazione.readlines()
        # estrazione elenco_sensori e tipi_sensori
        sensori = righe[0].replace("\n","").split(",")

        id_stazione = int(righe[1].replace("\n",""))


    global scatta_foto
    scatta_foto = ScattaFoto()
    scatta_foto.start()

    app.run(host=SERVER_ADDRESS, port=SERVER_PORT)
    
""" --------------------------------------- """

if __name__ == "__main__":
    main()





    
