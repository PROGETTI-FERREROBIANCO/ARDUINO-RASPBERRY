import pandas as pd
import socket as sck
import threading
from threading import Lock
from time import sleep
from flask import Flask, request, render_template, send_file, jsonify
from pathlib import Path
import websockets
import asyncio
import sqlite3
import datetime
import webbrowser as _webbrowser
import platform    
import subprocess  
import copy
import requests
import os
from ipaddress import ip_address

CARATTERI_PROTOCOLLO_RICEZIONE_INIZIO_TCP = "0200ff44001b00"
CARATTERI_PROTOCOLLO_RICEZIONE_INIZIO_UDP = "00000002001b0001"

CARATTERI_PROTOCOLLO_INVIO_INIZIO_TCP = "ff4444"
CARATTERI_PROTOCOLLO_INVIO_INIZIO_UDP = "000202"
CARATTERI_PROTOCOLLO_INVIO_META = "000200"
CARATTERI_PROTOCOLLO_INVIO_FINE = "00000000"
CARATTERI_CODIFICA_INVIO = "061b5b346c0d0a"

MESSAGGIO_RICHIESTA_INFORMAZIONI_UDP = "0000000000000000cba14100201e8b00"
MESSAGGIO_CONNESSIONE_UDP = "000404dd1902000000000000"
MESSAGGIO_CONNESSIONE_TCP = "000404b41702cb6000000000"
CARATTERE_INVIO_CODIFICATO_TCP = "ff44446a0002000d00000000"

CARATTERI_PROTOCOLLO_INIZIO_MONITOR = """
00 00 00 04 00 0a 00 a4 02 8c
02 a5 00 04 00 00 00 00 4d 6f 6e 69 74 6f 72 00 
00 00 00 00 00 00 00 00 00 07 4d 6f 6e 69 74 6f 
72 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 01 40 55 00""".replace(' ', '').replace('\n', '').replace("\r", "")

CARATTERI_PROTOCOLLO_META_MONITOR = "01ff9d7800"
CARATTERI_PROTOCOLLO_FINE_MONITOR = """
00 00 00 00 
02 8c 02 a5 00 00 00 00 00 00 00 00 00 06 00 08
02 86 ff ff 00 00 00 00 ff ff 00 01 00 05 ff ff
00 03 ff 44 00 00 00 00 00 00 00 00 00 00 00 00
00 00""".replace(' ', '').replace('\n', '').replace("\r", "")

CARATTERE_MONITOR_PRINCIPALE = "04ff0f"

TEMPO_MAX_TIMEOUT = 10 # tempo dopo il quale considero che l'utente si è sconnesso
MAX_LUNGHEZZA_NOME_FILE = 15
MAX_SECONDI_RISPOSTA_TCP = 1
MAX_SECONDI_RISPOSTA_UDP = 1
FINE_SCHEDA = "SCHEDAFINITA"

PORTA_INVIO_DATI_NETWORK_CONTROLLER = 1992
PORTA_RICEZIONE_DATI_ROBOT_NETWORK_CONTROLLER = 1993
PORTA_CONNESSIONE_INFO = 2002
PORTA_TERMINALE = 1999
PORTA_WEB_SERVER = 80

dir_path = str(Path(__file__).parent.resolve())
app = Flask(__name__)
nome_python = ""
indirizzo_ip = None
indirizzo_ip_ethernet = None
separatore = "\\" if platform.system().lower()=='windows' else '/'
lock_invio_messaggio_tcp = {}
lock_invo_messaggio_udp = {}
lock_cella = {}
lock_upload = {}
lock_upload_programma = {}
lock_recv_tcp = {}
lock_recv_udp = {}
lock_calibrazione = {}
lock_connetti = {}
lock_cambia_ip = {}
lock_upload_programma_celle = Lock()
lock_creazione_server_udp = Lock()
lock_next_free_port = Lock()

n_schede_fatte = {}
celle_disponibili = {}

prototipo_cella = {"connessione_cella":None, "connessione_cella_udp":None, "ultima_verifica":datetime.datetime.now(), "ws_shell":None, "porta_ws_shell":0, "ws_info":None, "porta_ws_info":0, "ws_shell_udp": None, "porta_ws_shell_udp": 0}
lista_celle = {}


@app.route("/", methods=['GET', 'POST'])
def index():
    global n_schede_fatte
    if request.method == "POST":
        if "comando" in request.form:
            comando = request.form["comando"]

            dati_csv = pd.read_csv(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}celle{separatore}dati.csv")
            celle = dati_csv["N-cella"].unique()

            if comando == "AVVIA":
                n_schede_fatte = {}
                if "valore" in request.form:
                    valore = request.form["valore"]
                    for id_cella in celle:
                        #print(id_cella)
                        risposta = requests.post(f"http://{indirizzo_ip}/cella?id_cella={id_cella}", data={"comando":"START", "valore":valore}).text
                        #print(risposta)
                        if risposta!="OK": return risposta
                else: return "Errore nella richiesta"

            elif comando == "STOP":
                n_schede_fatte = {}
                for id_cella in celle:
                    risposta = requests.post(f"http://{indirizzo_ip}/cella?id_cella={id_cella}", data={"comando":"STOP"}).text
                    if risposta!="OK": return risposta

            return "OK"
    
    
    return render_template("index.html", lista_celle_disponibili = celle_disponibili)


@app.route("/counter_schede_fatte", methods=['GET'])
def counter_schede_fatte():
    #print(n_schede_fatte)
    return jsonify(n_schede_fatte)

@app.route("/occupa", methods=['GET'])
def occupa():
    if "id_cella" in request.args and isInt(request.args["id_cella"]) and int(request.args["id_cella"]) in lista_celle:
        id_cella = int(request.args["id_cella"])
        lista_celle[id_cella]["ultima_verifica"] = datetime.datetime.now()

        if lista_celle[id_cella]["connessione_cella"] != None: return "OK"
        else: return "NO"
        
    return "parametri della richiesta errati"

@app.route("/stato_celle", methods=['GET'])
def stato_celle():
    stati = {}
    for id_cella in lista_celle:
        stati[id_cella] = (lista_celle[id_cella]["connessione_cella"] != None)
    return jsonify(stati)



@app.route("/upload_programma_celle", methods=['GET', 'POST'])
def upload_programma_celle():

        with lock_upload_programma_celle:
            f = request.files['fileupload']
            if f.filename == '': return "File non selezionato"
            
            f.save(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}celle{separatore}dati.csv")

            if os.stat(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}celle{separatore}dati.csv").st_size == 0: return "Il file caricato è vuoto"

            

            dati_contenuto = {}
            dati_csv = pd.read_csv(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}celle{separatore}dati.csv")
            
            dati_csv.columns = dati_csv.columns.str.replace(" ", "")
            dati_csv.columns= dati_csv.columns.str.lower()

            try:

                dati_csv = dati_csv[["n-cella", "n-pinza", "n-alimentatore", "center-x(mm)", "center-y(mm)", "rotation"]]

                #print(dati_csv.dtypes("N-alimentatore") == int)
                
                try:
                    dati_csv = dati_csv.astype(float)
                except: return "Tipi delle colonne non corrette"


                # verifica stato macchine
                celle = dati_csv["n-cella"].unique()
                for id_cella in celle:
                    try:
                        if lista_celle[id_cella]["connessione_cella"] == None: return f"Cella {id_cella} non attiva"
                    except: return f"Cella {id_cella} non attiva"

                # divisione dati da csv
                for dato_csv_np in dati_csv.values:
                    dato_csv = []
                    dato_csv.append(int(dato_csv_np[0]))
                    dato_csv.append(int(dato_csv_np[1]))
                    dato_csv.append(int(dato_csv_np[2]))
                    dato_csv.append(float(dato_csv_np[3]))
                    dato_csv.append(float(dato_csv_np[4]))
                    dato_csv.append(float(dato_csv_np[5]))

                    #print(dato_csv)

                    if dato_csv[0] in lista_celle:
                        if dato_csv[0] not in dati_contenuto: 
                            dati_contenuto[dato_csv[0]] = "N-pinza,N-alimentatore,Center-X(mm),Center-Y(mm),Rotation\n"
                            dati_contenuto[dato_csv[0]] += f"{dato_csv[1]},{dato_csv[2]},{dato_csv[3]},{dato_csv[4]},{dato_csv[5]}\n"
                        else: dati_contenuto[dato_csv[0]] += f"{dato_csv[1]},{dato_csv[2]},{dato_csv[3]},{dato_csv[4]},{dato_csv[5]}\n"
                    else: return f"Cella {dato_csv[0]} non esistente"


                # creazione file
                for id_cella,contenuto_file in dati_contenuto.items():
                    crea_cartella(f"{dir_path}{separatore}tftpserver{separatore}positions",f"cella{id_cella}")
                    with open(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}dati_upload_programma_celle.csv", "w") as f:
                        f.write(contenuto_file)

    
                # invio dei file alle macchine

                for id_cella in dati_contenuto:
                    files = {"fileupload": open(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}dati_upload_programma_celle.csv", "rb")}
                    risposta = requests.post(f"http://{indirizzo_ip}/upload_programma?id_cella={id_cella}", files=files).text
                    #print(f"Risposta:{risposta}")
                    if risposta != "OK": return risposta
            except: return "Problemi nell'elaborazione del file"


        return "OK"

@app.route("/upload_programma", methods=['GET', 'POST'])
def upload_programma():
    
        if "id_cella" in request.args and isInt(request.args["id_cella"]) and int(request.args["id_cella"]) in lista_celle:
            id_cella = int(request.args["id_cella"])
            with lock_upload_programma[id_cella]:
                if lista_celle[id_cella]["connessione_cella"]!=None and lista_celle[id_cella]["ws_shell"]!=None:
                    f = request.files['fileupload']
                    if f.filename == '': return "File non selezionato"
                    
                    
                    #lunghezza -2 perché è necessario aggingere p_
                    #if len(f.filename) > MAX_LUNGHEZZA_NOME_FILE-2: return f"Il nome del file è troppo lungo! Non deve superare i {MAX_LUNGHEZZA_NOME_FILE-2} caratteri compresa l'estensione."
                    crea_cartella(f"{dir_path}{separatore}tftpserver{separatore}upload",f"cella{id_cella}")
                    f.save(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}cella{id_cella}{separatore}{f.filename}")
                    
                    if os.stat(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}cella{id_cella}{separatore}{f.filename}").st_size == 0: return "Il file caricato è vuoto"
                    

                    dati_contenuto = ""
                    dati_csv = pd.read_csv(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}cella{id_cella}{separatore}{f.filename}")

                    dati_csv.columns = dati_csv.columns.str.replace(" ", "")
                    dati_csv.columns= dati_csv.columns.str.lower()

                    try:

                        dati_csv = dati_csv[["n-pinza", "n-alimentatore", "center-x(mm)", "center-y(mm)", "rotation"]]
                        
                        try:
                            dati_csv = dati_csv.astype(float)
                        except: return "Tipi delle colonne non corrette"


                        dati_csv.sort_values("n-pinza", inplace=True)

            
                        for dato_csv in dati_csv.values:
                            # query
                            con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
                            cur = con.cursor()
                            cur.execute("""SELECT id_tipo_pinza FROM pinze WHERE id_cella=? AND num_pos_in_cella=? AND stato='ON'""", [id_cella, dato_csv[0]])
                            output = cur.fetchall()
                            if(len(output) == 0): return  f" La pinza {int(dato_csv[0])} non è attiva o non è presente"
                            id_tipo_pinza = output[0][0]
                            

                            cur.execute("""SELECT id_tipo_alimentatore FROM alimentatori WHERE id_cella=? AND num_pos_in_cella=? AND stato='ON'""", [id_cella, dato_csv[1]])
                            output = cur.fetchall()
                            if(len(output) == 0): return  f" L'alimentatore {int(dato_csv[1])} non è attivo o non è presente"
                            id_tipo_alimentatore = output[0][0]

                            con.close()

                            if id_tipo_alimentatore != id_tipo_pinza: return " Incongruenza tra le tipologie delle pinze e degli alimentatori"


                            dati_contenuto += f"{dato_csv[0]}|{dato_csv[1]}|{dato_csv[2]}|{dato_csv[3]}|{dato_csv[4]}\n"

                    except: return "Errore nel file"

                    crea_cartella(f"{dir_path}{separatore}tftpserver{separatore}positions",f"cella{id_cella}")
                    with open(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}dati.txt", "w") as f:
                        f.write(dati_contenuto)

                    aggiungi_spazi_a_file(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}dati.txt")

                    files = {"fileupload": open(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}dati.txt", "rb")}
                    requests.post(f"http://{indirizzo_ip}/upload?id_cella={id_cella}", files=files)


                    return "OK"
                else:
                    return "Web socket shell chiuso"
        return render_template("index.html", lista_celle_disponibili = celle_disponibili)



@app.route("/calibrazione", methods=['GET', 'POST'])
def calibrazione():

    if "id_cella" in request.args and isInt(request.args["id_cella"]) and int(request.args["id_cella"]) in lista_celle:
        id_cella = int(request.args["id_cella"])
        with lock_calibrazione[id_cella]:
            if lista_celle[id_cella]["connessione_cella"]!=None and lista_celle[id_cella]["ws_shell"]!=None:
                if "comando" in request.args:
                    if request.args["comando"] == "pos":
                        lista_celle[id_cella]["connessione_cella"].send_messagge("load D:\\get_pos.v2")
                        output = get_info_from_comando(2, id_cella, "execute 4 get_pos.v2", "Program task 4 stopped at get_pos.v2, step 10")

                        output = output.split("\n")[0]

                        #print(output)

                        return jsonify(eval(output))

                    elif request.args["comando"] == "esegui_movimento":

                        if (all (k in request.form for k in ("x", "y", "z", "ya", "p", "r"))) and (isFloat(request.form["x"]) and isFloat(request.form["y"]) and isFloat(request.form["z"]) and isFloat(request.form["ya"]) and isFloat(request.form["p"]) and isFloat(request.form["r"])):
                            x = request.form["x"]
                            y = request.form["y"]
                            z = request.form["z"]
                            ya = request.form["ya"]
                            p = request.form["p"]
                            r = request.form["r"]

                            lista_celle[id_cella]["connessione_cella"].send_messagge("abort 0")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("kill 0")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("load D:\\mv_rob.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge(f"execute mv_rob.v2({x},{y},{z},{ya},{p},{r})")
                            return "OK"
                        return "Errore: richiesta mal formulata"


                    
                    elif request.args["comando"] == "prendi_pinza_cal":
                        con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
                        cur = con.cursor()
                        
                        
                        cur.execute("""SELECT pinze.num_pos_in_cella FROM pinze, tipi_componenti t_c WHERE pinze.id_cella = ? AND pinze.id_tipo_pinza = t_c.id AND t_c.nome = 'calibrazione' AND pinze.stato = 'ON'""", [id_cella])
                        output = cur.fetchall()
                        con.close()
                        if len(output) > 0:
                            output = output[0][0]
                            lista_celle[id_cella]["connessione_cella"].send_messagge("abort 0")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("kill 0")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("load D:\\main.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("execute main.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge(f"execute prendi_pinza.v2({output})")
                            return "OK"
                        return "Errore! Pinza non presente o mal configurata."
                    
                    elif request.args["comando"] == "posa_pinza_cal":
                        con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
                        cur = con.cursor()
                        
                        
                        cur.execute("""SELECT pinze.num_pos_in_cella FROM pinze, tipi_componenti t_c WHERE pinze.id_cella = ? AND pinze.id_tipo_pinza = t_c.id AND t_c.nome = 'calibrazione' AND pinze.stato = 'ON'""", [id_cella])
                        output = cur.fetchall()
                        con.close()
                        if len(output) > 0:
                            output = output[0][0]
                            lista_celle[id_cella]["connessione_cella"].send_messagge("abort 0")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("kill 0")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("load D:\\main.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("execute main.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge(f"execute lascia_pinza.v2({output})")
                            return "OK"
                        return "Errore! Pinza non presente o mal configurata."



                    elif request.args["comando"] == "download":
                        dati = {}

                        lista_pinze = [1,2,3,4,5,6,7,8,9,10]
                        lista_alimentatori = [1,2,3,4,5,6,7,8,9,10]
                        num_punti_specifici = 3

                        con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
                        cur = con.cursor()
                        
                        
                        cur.execute("""SELECT pinze.id_cella, pinze.id_tipo_pinza, pinze.num_pos_in_cella, pinze.funzione, pinze.h_alim, pinze.h_ins_comp, celle.nome, celle.descrizione, celle.num_pos_in_linea, posizioni.x, posizioni.y, posizioni.z, posizioni.yaw, posizioni.pitch, posizioni.roll, pinze.stato FROM pinze, celle, posizioni WHERE pinze.id_cella = celle.id AND pinze.id_posizione = posizioni.id AND celle.id = ?""", [id_cella])
                        output = cur.fetchall()
                        #print(output)
                        pinze = []
                        new_output = {}
                        for riga in output:
                            #print(len(riga))
                            pinze.append(riga[2])
                            new_output[riga[2]] = (riga[0], riga[1], riga[3], riga[4], riga[5], riga[6], riga[7], riga[8], riga[9], riga[10], riga[11], riga[12], riga[13], riga[14], riga[15])
                        for diff in list(set(lista_pinze) - set(pinze)):
                            new_output[diff] = ()
                        dati["pinze"] = new_output


                        cur.execute("""SELECT alimentatori.id_cella, alimentatori.id_tipo_alimentatore, alimentatori.num_pos_in_cella, alimentatori.funzione, celle.nome, celle.descrizione, celle.num_pos_in_linea, posizioni.x, posizioni.y, posizioni.z, posizioni.yaw, posizioni.pitch, posizioni.roll, alimentatori.stato FROM alimentatori, celle, posizioni WHERE alimentatori.id_cella = celle.id AND alimentatori.id_posizione = posizioni.id AND celle.id = ?""", [id_cella])
                        output = cur.fetchall()
                        alimentatori = []
                        new_output = {}
                        for riga in output:
                            alimentatori.append(riga[2])
                            new_output[riga[2]] = (riga[0], riga[1], riga[3], riga[4], riga[5], riga[6], riga[7], riga[8], riga[9], riga[10], riga[11], riga[12], riga[13])
                        for diff in list(set(lista_alimentatori) - set(alimentatori)):
                            new_output[diff] = ()
                        dati["alimentatori"] = new_output


                        cur.execute("""SELECT punti_specifici.id_cella, punti_specifici.nome, punti_specifici.descrizione, celle.nome, celle.descrizione, celle.num_pos_in_linea, posizioni.x, posizioni.y, posizioni.z, posizioni.yaw, posizioni.pitch, posizioni.roll FROM punti_specifici, celle, posizioni WHERE punti_specifici.id_cella = celle.id AND punti_specifici.id_posizione = posizioni.id AND celle.id = ?""", [id_cella])
                        output = cur.fetchall()
                        punti_specifici = 0
                        new_output = {}
                        for riga in output:
                            punti_specifici += 1
                            new_output[punti_specifici] = (riga[0], riga[1], riga[2], riga[3],riga[4], riga[5], riga[6], riga[7], riga[8], riga[9], riga[10], riga[11])
                        for diff in range(punti_specifici+1, num_punti_specifici+1):
                            new_output[diff] = ()
                        dati["punti_specifici"] = new_output


                        cur.execute("""SELECT * FROM tipi_componenti""")
                        dati["tipi_componenti"] = cur.fetchall()

                        con.close()

                        return jsonify(dati)
                    elif request.args["comando"] == "save":
                        dict_da_salvare = request.form["json"]

                        #print(dict_da_salvare)

                        dict_da_salvare = eval(dict_da_salvare)

                        errore = ""

                        try:
                            con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
                            cur = con.cursor()
                        except: return "Errore connessione al databse"
                        
                        try:
                            for n in range(1,11):
                                ris = dict_da_salvare[f"pinza_{n}"]
                                if len(ris) > 3:
                                    cur.execute("SELECT id_cella FROM pinze WHERE id_cella=? AND num_pos_in_cella=?", [ris["id_cella"],ris["num_pos_in_cella"]])
                                    if len(cur.fetchall()) > 0:
                                        cur.execute("INSERT INTO posizioni (x, y, z, yaw, pitch, roll) VALUES (?, ?, ?, ?, ?, ?)", [ris["x"],ris["y"],ris["z"],ris["yaw"],ris["pitch"],ris["roll"]])
                                        con.commit()
                                        cur.execute("SELECT id FROM posizioni ORDER BY id DESC LIMIT 1")
                                        id_pos = cur.fetchall()[0][0]
                                        cur.execute("UPDATE pinze SET id_posizione=?, id_tipo_pinza=?, funzione=?, h_ins_comp=?, h_alim=?, stato=? WHERE num_pos_in_cella=? AND id_cella=?", [id_pos, ris["id_tipo_pinza"], ris["funzione"], ris["h_ins_comp"], ris["h_alim"], ris["stato"], ris["num_pos_in_cella"], ris["id_cella"]])
                                        con.commit()
                                    else:
                                        cur.execute("INSERT INTO posizioni (x, y, z, yaw, pitch, roll) VALUES (?, ?, ?, ?, ?, ?)", [ris["x"],ris["y"],ris["z"],ris["yaw"],ris["pitch"],ris["roll"]])
                                        con.commit()
                                        cur.execute("SELECT id FROM posizioni ORDER BY id DESC LIMIT 1")
                                        id_pos = cur.fetchall()[0][0]
                                        cur.execute("INSERT INTO pinze (id_cella, id_posizione, id_tipo_pinza, num_pos_in_cella, funzione, h_ins_comp, h_alim, stato) VALUES (?,?,?,?,?,?,?,?)", [ris["id_cella"],id_pos,ris["id_tipo_pinza"],ris["num_pos_in_cella"],ris["funzione"],ris["h_ins_comp"],ris["h_alim"],ris["stato"]])
                                        con.commit()

                        except: errore += "Errore salvataggio pinze|"

                        try:
                            for n in range(1,11):
                                ris = dict_da_salvare[f"alimentatore_{n}"]
                                if len(ris) > 3:
                                    cur.execute("SELECT id_cella FROM alimentatori WHERE id_cella=? AND num_pos_in_cella=?", [ris["id_cella"],ris["num_pos_in_cella"]])
                                    if len(cur.fetchall()) > 0:
                                        cur.execute("INSERT INTO posizioni (x, y, z, yaw, pitch, roll) VALUES (?, ?, ?, ?, ?, ?)", [ris["x"],ris["y"],ris["z"],ris["yaw"],ris["pitch"],ris["roll"]])
                                        con.commit()
                                        cur.execute("SELECT id FROM posizioni ORDER BY id DESC LIMIT 1")
                                        id_pos = cur.fetchall()[0][0]
                                        cur.execute("UPDATE alimentatori SET id_posizione=?, id_tipo_alimentatore=?, funzione=?, stato=? WHERE num_pos_in_cella=? AND id_cella=?", [id_pos, ris["id_tipo_alimentatore"], ris["funzione"],ris["stato"], ris["num_pos_in_cella"], ris["id_cella"]])
                                        con.commit()
                                    else:
                                        cur.execute("INSERT INTO posizioni (x, y, z, yaw, pitch, roll) VALUES (?, ?, ?, ?, ?, ?)", [ris["x"],ris["y"],ris["z"],ris["yaw"],ris["pitch"],ris["roll"]])
                                        con.commit()
                                        cur.execute("SELECT id FROM posizioni ORDER BY id DESC LIMIT 1")
                                        id_pos = cur.fetchall()[0][0]
                                        cur.execute("INSERT INTO alimentatori (id_cella, id_posizione, id_tipo_alimentatore, num_pos_in_cella, funzione, stato) VALUES (?,?,?,?,?,?)", [ris["id_cella"],id_pos,ris["id_tipo_alimentatore"],ris["num_pos_in_cella"],ris["funzione"],ris["stato"]])
                                        con.commit()
                        except: errore += "Errore salvataggio alimentatori|"


                        try:
                            for n in range(1,4):
                                ris = dict_da_salvare[f"punto_specifico_{n}"]
                                #print(f"PUNTO SPECIFICIO.: {ris}")
                                
                                cur.execute("INSERT INTO posizioni (x, y, z, yaw, pitch, roll) VALUES (?, ?, ?, ?, ?, ?)", [ris["x"],ris["y"],ris["z"],ris["yaw"],ris["pitch"],ris["roll"]])
                                con.commit()
                                cur.execute("SELECT id FROM posizioni ORDER BY id DESC LIMIT 1")
                                id_pos = cur.fetchall()[0][0]
                                
                                cur.execute("SELECT id_cella FROM punti_specifici WHERE id_cella=? AND nome=?", [ris["id_cella"],ris["nome"]])
                                if len(cur.fetchall()) > 0:
                                    cur.execute("UPDATE punti_specifici SET id_posizione=?, descrizione=? WHERE id_cella=? AND nome=?", [id_pos,ris["descrizione"],ris["id_cella"],ris["nome"]])
                                    con.commit()
                                else:
                                    cur.execute("INSERT INTO punti_specifici (id_cella, id_posizione, nome, descrizione) VALUES (?,?,?,?)", [ris["id_cella"],id_pos,ris["nome"],ris["descrizione"]])
                                    con.commit()
                        except: errore += "Errore salvataggio punti_specifici"

                        if len(errore) != 0: 
                            con.close()
                            return errore

                        dati = ""
                        
                        cur.execute("""SELECT pinze.num_pos_in_cella, tipi_componenti.id, posizioni.x, posizioni.y, posizioni.z, posizioni.yaw, posizioni.pitch, posizioni.roll, pinze.h_alim, pinze.h_ins_comp FROM tipi_componenti, pinze, celle, posizioni WHERE pinze.id_cella = celle.id AND pinze.id_posizione = posizioni.id AND celle.id = ? AND tipi_componenti.id = pinze.id_tipo_pinza AND stato='ON' ORDER BY pinze.num_pos_in_cella ASC""", [id_cella])
                        output = cur.fetchall()
                        num_prec = 0
                        for riga in output:
                            for riga_mancante in range(num_prec+1, riga[0]):
                                dati += f"pinza_{riga_mancante}|null\n"
                            dati += f"pinza_{riga[0]}|{riga[1]}|{riga[2]}|{riga[3]}|{riga[4]}|{riga[5]}|{riga[6]}|{riga[7]}|{riga[8]}|{riga[9]}\n"
                            num_prec = riga[0]
                        for i in range(num_prec+1,11): dati += f"pinza_{i}|null\n"



                        cur.execute("""SELECT alimentatori.num_pos_in_cella, tipi_componenti.id, posizioni.x, posizioni.y, posizioni.z, posizioni.yaw, posizioni.pitch, posizioni.roll FROM tipi_componenti, alimentatori, celle, posizioni WHERE alimentatori.id_cella = celle.id AND alimentatori.id_posizione = posizioni.id AND celle.id = ? AND tipi_componenti.id = alimentatori.id_tipo_alimentatore AND stato='ON' ORDER BY alimentatori.num_pos_in_cella ASC""", [id_cella])
                        output = cur.fetchall()
                        num_prec = 0
                        for riga in output:
                            for riga_mancante in range(num_prec+1, riga[0]):
                                dati += f"alimentatore_{riga_mancante}|null\n"
                            dati += f"alimentatore_{riga[0]}|{riga[1]}|{riga[2]}|{riga[3]}|{riga[4]}|{riga[5]}|{riga[6]}|{riga[7]}\n"
                            num_prec = riga[0]
                        for i in range(num_prec+1,11): dati += f"alimentatore_{i}|null\n"


                        cur.execute("""SELECT punti_specifici.nome, posizioni.x, posizioni.y, posizioni.z, posizioni.yaw, posizioni.pitch, posizioni.roll FROM punti_specifici, celle, posizioni WHERE punti_specifici.id_cella = celle.id AND punti_specifici.id_posizione = posizioni.id AND celle.id = ?""", [id_cella])
                        output = cur.fetchall()
                        num_prec = 0
                        if len(output) == 3:
                            for riga in output:
                                dati += f"{riga[0]}|{riga[1]}|{riga[2]}|{riga[3]}|{riga[4]}|{riga[5]}|{riga[6]}\n"
                        else: return "Errore: mancano dei punti specifici"

                        con.close()

                        # print(dati)

                        crea_cartella(f"{dir_path}{separatore}tftpserver{separatore}positions",f"cella{id_cella}")
                        with open(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}posi.txt", "w") as f:
                            f.write(dati)

                        aggiungi_spazi_a_file(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}posi.txt")

                        files = {"fileupload": open(f"{dir_path}{separatore}tftpserver{separatore}positions{separatore}cella{id_cella}{separatore}posi.txt", "rb")}

                        return requests.post(f"http://{indirizzo_ip}/upload?id_cella={id_cella}", files=files).text



                else: return render_template("calibrazione.html", id_cella=id_cella)
            else: return render_template("errore_cella.html", errore = f'<p>Prima di accedere alla calibrazione devi connetterti alla cella.</p>', id_cella=id_cella, lista_celle_disponibili = celle_disponibili)

    return render_template("errore_cella.html", errore = f'<p>Sembra che qualcosa sia andato storto. <a href="/">Riprovare</a></p>', lista_celle_disponibili = celle_disponibili)



@app.route("/upload", methods=['GET', 'POST'])
def upload():
        if "id_cella" in request.args and isInt(request.args["id_cella"]) and int(request.args["id_cella"]) in lista_celle:
            id_cella = int(request.args["id_cella"])
        
            with lock_upload[id_cella]:
                if lista_celle[id_cella]["connessione_cella"]!=None and lista_celle[id_cella]["ws_shell"]!=None:
                    f = request.files['fileupload']
                    if f.filename == '':return "File non selezionato"
                    #lunghezza -2 perché è necessario aggingere p_
                    if len(f.filename) > MAX_LUNGHEZZA_NOME_FILE-2: return f"Il nome del file è troppo lungo! Non deve superare i {MAX_LUNGHEZZA_NOME_FILE-2} caratteri compresa l'estensione."
                    
                    crea_cartella(f"{dir_path}{separatore}tftpserver{separatore}upload",f"cella{id_cella}")
                    f.save(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}cella{id_cella}{separatore}{f.filename}")

                    if os.stat(f"{dir_path}{separatore}tftpserver{separatore}upload{separatore}cella{id_cella}{separatore}{f.filename}").st_size == 0: return "Il file caricato è vuoto"
                    
                    lista_celle[id_cella]["connessione_cella"].send_messagge(f"fdelete {f.filename}")
                    lista_celle[id_cella]["connessione_cella"].send_messagge(f"Y")
                    output = get_info_from_comando(3, id_cella, f"FCOPY {f.filename}=tftp>{indirizzo_ip_ethernet}:{separatore}upload{separatore}cella{id_cella}{separatore}{f.filename}","___FINE_COMANDO_RICHIESTO___","___FINE_COMANDO_RICHIESTO___")

                    if '*' != output and '.' != output:
                        return "Problema nel download del file. Vericare che sia esistente e riprovare."
                    return "OK"


                else: return "Web socket shell chiuso"
        return render_template("index.html", lista_celle_disponibili = celle_disponibili)

@app.route("/network_controller", methods=['GET', 'POST'])
def cambia_ip():
      if "id_cella" in request.args and isInt(request.args["id_cella"]) and int(request.args["id_cella"]) in lista_celle:
        id_cella = int(request.args["id_cella"])
        with lock_cambia_ip[id_cella]:
            if request.method == "GET":
                return render_template("cambia_ip.html",id_cella=id_cella)
                
            else:
                if "comando" in request.form:
                    comando = request.form["comando"]
                    if comando == "CAMBIA_IP":
                        if 'valore' in request.form and isIp(request.form["valore"].split("|")[0]) and isIp(request.form["valore"].split("|")[1]) and isIp(request.form["valore"].split("|")[2] and len(request.form["valore"].split("|")[3:]) == 4):
                            valore = request.form["valore"]
                            vecchio_ip = valore.split("|")[0]
                            nuovo_ip = valore.split("|")[1]
                            nuova_subnetmask = valore.split("|")[2]
                            flags = valore.split("|")[3:]

                            try:
                                stringa_da_inviare = ""
                                for pezzo_di_ip in vecchio_ip.split("."):
                                    numero = int(pezzo_di_ip)
                                    stringa_esadecimale =  hex(numero).replace("0x","")
                                    if len(stringa_esadecimale) < 2: stringa_esadecimale = "0"+stringa_esadecimale
                                    stringa_da_inviare += stringa_esadecimale
                                
                                for pezzo_di_subnetmask in nuova_subnetmask.split("."):
                                    numero = int(pezzo_di_subnetmask)
                                    stringa_esadecimale =  hex(numero).replace("0x","")
                                    if len(stringa_esadecimale) < 2: stringa_esadecimale = "0"+stringa_esadecimale
                                    stringa_da_inviare += stringa_esadecimale
                                
                                for pezzo_di_ip in nuovo_ip.split("."):
                                    numero = int(pezzo_di_ip)
                                    stringa_esadecimale =  hex(numero).replace("0x","")
                                    if len(stringa_esadecimale) < 2: stringa_esadecimale = "0"+stringa_esadecimale
                                    stringa_da_inviare += stringa_esadecimale

                                for flag in flags:
                                    if flag == "false":
                                        stringa_da_inviare += '00'
                                    elif flag == "true":
                                        stringa_da_inviare += '01'
                                    else: return "flag inviato non corretto"
                                        
                            
                                s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
                                s.sendto(bytes.fromhex(stringa_da_inviare), (vecchio_ip, PORTA_INVIO_DATI_NETWORK_CONTROLLER))
                                s.close()


                                try:
                                    con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
                                    cur = con.cursor()
                                    cur.execute("UPDATE celle SET indirizzo_ip=? WHERE id=?", [nuovo_ip,id_cella])
                                    con.commit()
                                    con.close()

                                    celle_disponibili[id_cella][0] = nuovo_ip

                                except: return "errore salvataggio su db (modificare manualmente)"

                                return "OK"

                            except: return "errore nell'invio del dato"

                        else: return "errore nella richiesta"
                    elif comando == "RICHIEDI_INFO":
                        errore_dati, dati = get_info_from_cella(id_cella=id_cella)
                        if errore_dati == "OK":
                            celle_disponibili[id_cella] = dati
                        #print({"stato":errore_dati, "dati":celle_disponibili})
                        return jsonify({"stato":errore_dati, "dati":celle_disponibili})
                        


@app.route("/cella", methods=['GET', 'POST'])
def cella():
    errore = None 
    if "id_cella" in request.args and isInt(request.args["id_cella"]) and int(request.args["id_cella"]) in lista_celle:
        id_cella = int(request.args["id_cella"])
        with lock_cella[id_cella]:
            if request.method == "GET":
                
                # verifico presenza utente per determinata cella
                if (datetime.datetime.now() - lista_celle[id_cella]["ultima_verifica"]).total_seconds() < TEMPO_MAX_TIMEOUT:
                    return render_template("errore_cella.html", errore = f'<p>Sembra che la cella {id_cella} sia già controllata da un altro utente. Riprova tra alcuni secondi, intanto torna alla <a href="/">home</a>.</p>', id_cella=id_cella, lista_celle_disponibili = celle_disponibili)
                
                """
                else:
                    if errore == None and lista_celle[id_cella]["connessione_cella"]!=None:
                        chiudi_cella(id_cella)
                        print("chiudi4")
                """
                pass
                 

            else:
                if "comando" in request.form:
                    comando = request.form["comando"]
                    #print(f"comando: {comando}")

                    if comando == "SHELL_TCP" and lista_celle[id_cella]["connessione_cella"]!=None:
                        #print(f'valore: {request.form["valore"]}')
                        lista_celle[id_cella]["connessione_cella"].send_messagge(request.form["valore"])
                        return "OK"
                    elif comando == "SHELL_UDP" and lista_celle[id_cella]["connessione_cella_udp"]!=None:
                        #print(f'valore: {request.form["valore"]}')
                        lista_celle[id_cella]["connessione_cella_udp"].send_messagge(request.form["valore"])
                        return "OK"
                    elif comando == "CONNETTI":
                        with lock_connetti[id_cella]:

                            if not isIp(request.form["indirizzo_ip"]) or not isInt(request.form["porta"]): errore = "Indirizzo ip e/o porta errata"
                            else:
                                if (datetime.datetime.now() - lista_celle[id_cella]["ultima_verifica"]).total_seconds() < TEMPO_MAX_TIMEOUT:
                                    return render_template("errore_cella.html", errore = f'<p>Sembra che la cella {id_cella} sia già controllata da un altro utente. Riprova tra alcuni secondi, intanto torna alla <a href="/">home</a>.</p>', id_cella=id_cella, lista_celle_disponibili = celle_disponibili)
                        
                                errore_connessione = None

                                for n_cella in lista_celle:
                                    if lista_celle[n_cella]["connessione_cella"] != None and lista_celle[n_cella]["connessione_cella"].indirizzo_ip == request.form["indirizzo_ip"]: errore_connessione = "Indirizzo IP già in uso"
                                if errore_connessione == None:
                                    if lista_celle[id_cella]["connessione_cella"] != None:
                                        chiudi_cella(id_cella)
                                    
                                    
                                    cella_udp = CellaUDP(id_cella, request.form["indirizzo_ip"], porta=int(request.form["porta"]))
                                    cella_udp.start()
                                    lista_celle[id_cella]["connessione_cella_udp"] = cella_udp

                                    #if apri_websocket_shell_udp(id_cella) == -1: return render_template("errore_cella.html", errore="<p>È stato riscontrato un problema software. Riavvia il web server.</p>", id_cella=id_cella, lista_celle_disponibili = celle_disponibili)
                                    #if apri_websocket_shell(id_cella) == -1: return render_template("errore_cella.html", errore="<p>È stato riscontrato un problema software. Riavvia il web server.</p>", id_cella=id_cella, lista_celle_disponibili = celle_disponibili)
                                    
                                    apri_websocket_shell_udp(id_cella)
                                    apri_websocket_shell(id_cella)
                                
                                else: errore = errore_connessione
                    elif comando == "DISCONNETTI":
                        chiudi_cella(id_cella)

                    elif comando == "DOWNLOAD" and lista_celle[id_cella]["connessione_cella"]!=None:
                        if "valore" not in request.form: return "errore nella richiesta"
                        nome_file = request.form["valore"]
                        if nome_file == "null" or nome_file=='': return "Nome file non valido!"

                        crea_cartella(f"{dir_path}{separatore}tftpserver{separatore}download",f"cella{id_cella}")
                        output = get_info_from_comando(0, id_cella, f"FCOPY tftp>{indirizzo_ip_ethernet}:{separatore}download{separatore}cella{id_cella}{separatore}{nome_file}={nome_file}","___FINE_COMANDO_RICHIESTO___","___FINE_COMANDO_RICHIESTO___")

                        if '*' != output and output != '.':
                            return "Problema nel download del file. Vericare che sia esistente e riprovare."

                        with open(f"{dir_path}{separatore}tftpserver{separatore}download{separatore}cella{id_cella}{separatore}{nome_file}", "a") as f:
                            f.write("___QUESTOÈUNDOWNLOAD___")
                        
                        
                        return send_file(f"{dir_path}{separatore}tftpserver{separatore}download{separatore}cella{id_cella}{separatore}{nome_file}", as_attachment=True)

                    
                    elif comando == "STOP_INFO" and lista_celle[id_cella]["connessione_cella"]!=None:
                        chiudi_websocket_info(id_cella)
                        return "OK"

                    elif comando == "START_INFO" and lista_celle[id_cella]["connessione_cella"]!=None:
                        chiudi_websocket_info(id_cella)
                        porta = apri_websocket_info(id_cella)
                        #if porta == -1: return render_template("errore_cella.html", errore="<p>È stato riscontrato un problema software. Riavvia il web server.</p>", id_cella=id_cella, lista_celle_disponibili = celle_disponibili)
                        return str(porta)
                    
                    elif comando == "STOP_SHELL" and lista_celle[id_cella]["connessione_cella"]!=None:
                        chiudi_websocket_shell(id_cella)
                        return "OK"

                    elif comando == "START_SHELL" and lista_celle[id_cella]["connessione_cella"]!=None:
                        chiudi_websocket_shell(id_cella)
                        porta = apri_websocket_shell(id_cella)
                        #if porta == -1: return render_template("errore_cella.html", errore="<p>È stato riscontrato un problema software. Riavvia il web server.</p>", id_cella=id_cella, lista_celle_disponibili = celle_disponibili)
                        return str(porta)
                        
                    elif comando == "START" and lista_celle[id_cella]["connessione_cella"]!=None:
                        if "valore" in request.form and isInt(request.form['valore']) and int(request.form['valore']) > 0:
                            lista_celle[id_cella]["connessione_cella"].send_messagge("load D:\\main.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge("execute def_var.v2")
                            lista_celle[id_cella]["connessione_cella"].send_messagge(f"execute avvia_prod.v2({request.form['valore']})")
                            return "OK"
                        else: return "Errore: parametro non corretto"

                    elif comando == "STOP" and lista_celle[id_cella]["connessione_cella"]!=None:      
                        lista_celle[id_cella]["connessione_cella"].send_messagge("abort 0")
                        lista_celle[id_cella]["connessione_cella"].send_messagge("kill 0")
                        lista_celle[id_cella]["connessione_cella"].send_messagge("signal -1")
                        return "OK"


            return render_template("cella.html", eConnesso=((lista_celle[id_cella]["connessione_cella"]!=None) or (lista_celle[id_cella]["connessione_cella_udp"]!=None)), errore=errore, id_cella=id_cella, indirizzo_ip=indirizzo_ip, porta=lista_celle[id_cella]["porta_ws_shell"], lista_celle_disponibili=celle_disponibili, porta_udp=lista_celle[id_cella]["porta_ws_shell_udp"])
                  

    else: return render_template("index.html", lista_celle_disponibili = celle_disponibili)


def isIp(string):
    try:
        ip_address(string)
        return True
    except:
        return False

def isInt(string):
    try:
        int(string)
        return True
    except:
        return False

def isFloat(string):
    try:
        float(string)
        return True
    except:
        return False

def crea_cartella(percorso, nome_cartella):
    # Path
    path_c = os.path.join(percorso, nome_cartella)
    if not os.path.exists(path_c):
        os.mkdir(path_c)



def get_info_from_comando(num_ouput, id_cella, comando, fine_comando_verifica, fine_comando=""):
    lista_celle[id_cella]["ws_shell"].output[num_ouput] = []
    lista_celle[id_cella]["ws_shell"].elimina_array[num_ouput] = False
    lista_celle[id_cella]["connessione_cella"].send_messagge(comando)
    lista_celle[id_cella]["connessione_cella"].send_messagge(fine_comando)
    output = ""
    while fine_comando_verifica not in output:
        # print(output)
        output = ''.join(lista_celle[id_cella]["ws_shell"].output[num_ouput])

    lista_celle[id_cella]["ws_shell"].elimina_array[num_ouput] = True

    output = output[:output.find(fine_comando_verifica)]
    output = output[output.find(comando)+len(comando)+2:]
    #print(output)
    
    return output   


def chiudi_cella(id_cella):
    try: lista_celle[id_cella]["connessione_cella_udp"].s.close()
    except: pass
    try:
        lista_celle[id_cella]["connessione_cella_udp"].running = False
        # lista_celle[id_cella]["connessione_cella"].join()
    except: pass


    try: lista_celle[id_cella]["connessione_cella"].s.close()
    except: pass
    try:
        lista_celle[id_cella]["connessione_cella"].running = False
        # lista_celle[id_cella]["connessione_cella"].join()
    except: pass
    
    chiudi_weboscket_shell_udp(id_cella)
    chiudi_websocket_shell(id_cella)
    chiudi_websocket_info(id_cella)

    lista_celle[id_cella]["connessione_cella"] = None
    lista_celle[id_cella]["connessione_cella_udp"] = None


def apri_websocket_shell(id_cella):
    porta = next_free_port()
    lista_celle[id_cella]["porta_ws_shell"] = porta
   # if porta == -1: return -1
    thread_websocket= WSTerminale(indirizzo_ip, porta, id_cella)
    thread_websocket.start()
    lista_celle[id_cella]["ws_shell"] = thread_websocket
    #sleep(2)
    return porta

def apri_websocket_info(id_cella):
    porta = next_free_port()
    lista_celle[id_cella]["porta_ws_info"] = porta
    #if porta == -1: return -1
    thread_websocket = WSInfo(indirizzo_ip, porta, id_cella, lista_celle[id_cella]["connessione_cella"].indirizzo_ip)
    thread_websocket.start()
    lista_celle[id_cella]["ws_info"] = thread_websocket
    #sleep(2)
    return porta


def apri_websocket_shell_udp(id_cella):
    porta = next_free_port()
    lista_celle[id_cella]["porta_ws_shell_udp"] = porta
    #if porta == -1: return -1
    thread_websocket = WSTerminaleUDP(indirizzo_ip, porta, id_cella)
    thread_websocket.start()
    lista_celle[id_cella]["ws_shell_udp"] = thread_websocket
    #sleep(2)
    return porta

def chiudi_weboscket_shell_udp(id_cella):
    try:
        lista_celle[id_cella]["ws_shell_udp"].running = False
        lista_celle[id_cella]["ws_shell_udp"].loop.stop()
        # lista_celle[id_cella]["ws_shell"].join()
    except: pass

    lista_celle[id_cella]["ws_shell_udp"] = None
    lista_celle[id_cella]["porta_ws_shell_udp"] = 0


def chiudi_websocket_shell(id_cella):
    try:
        lista_celle[id_cella]["ws_shell"].running = False
        lista_celle[id_cella]["ws_shell"].loop.stop()
        # lista_celle[id_cella]["ws_shell"].join()
    except: pass

    lista_celle[id_cella]["ws_shell"] = None
    lista_celle[id_cella]["porta_ws_shell"] = 0

def chiudi_websocket_info(id_cella):
    try:
        lista_celle[id_cella]["ws_info"].s.close()
    except: pass

    try:
        lista_celle[id_cella]["ws_info"].running = False
        lista_celle[id_cella]["ws_info"].loop.stop()
        # lista_celle[id_cella]["ws_info"].join()
    except: pass

    lista_celle[id_cella]["ws_info"] = None
    lista_celle[id_cella]["porta_ws_info"] = 0

def ping(host, n_tentativi = 3):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, str(n_tentativi), host]

    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0


def aggiungi_spazi_a_file(nome_file):
    contenuto_file_nuovo = ""
    with open(nome_file, "r") as file:
        contenuto = file.readlines()

        for riga in contenuto:
            riga = riga.replace("\r\n", "\n")
            aggiungispazi = False
            if len(riga) < 100: aggiungispazi = True
            n = 99
            ris = [riga[i:i+n] for i in range(0, len(riga), n)]
            for r in ris:
                if "\n" in r and aggiungispazi:
                    r = r.replace("\r", "").replace("\n", "")
                    aggiunta = " " * (100-2-len(r))
                    r = r + aggiunta + "\r\n"
                else: r = r.replace("\n", "\r\n")

                contenuto_file_nuovo += r
                #print(len(r))

    with open(nome_file, "w") as file:
        file.write(contenuto_file_nuovo)


def prepara_messaggio_ricezione_udp(stringa_byte):
    data = stringa_byte.hex()
    data = data.replace(" ", "")
    data = data.replace(CARATTERI_PROTOCOLLO_RICEZIONE_INIZIO_UDP, "")
    data = data.replace("5c", "5c5c")
    return bytes.fromhex(data).decode("unicode_escape")
    

def prepara_messaggio_ricezione_tcp(stringa_byte):
    # conversione da byte ad esadecimale
    messaggi = stringa_byte.hex()
    # elminazione spazi
    messaggi = messaggi.replace(" ", "")
    messaggio_finale = ""
    
    if (CARATTERI_PROTOCOLLO_INIZIO_MONITOR in messaggi) and (CARATTERI_PROTOCOLLO_FINE_MONITOR in messaggi):
        messaggio_monitor = messaggi[messaggi.find(CARATTERI_PROTOCOLLO_INIZIO_MONITOR): messaggi.find(CARATTERI_PROTOCOLLO_FINE_MONITOR)]
        messaggio_monitor = messaggio_monitor.replace(CARATTERI_PROTOCOLLO_INIZIO_MONITOR, '').replace(CARATTERI_PROTOCOLLO_FINE_MONITOR, '').replace(CARATTERI_PROTOCOLLO_META_MONITOR, '')
        #eliminiamo i primi 6 caratteri che sono randomici
        messaggio_monitor = messaggio_monitor[6:12]
        if messaggio_monitor == CARATTERE_MONITOR_PRINCIPALE: messaggio_finale = "\nMonitor terminale attivo\n"
        else: messaggio_finale = "\nQuesta funzione richiede un monitor non supportato. Premi CTRL C per continuare ad utilizzare il terminale.\n"
        messaggi = messaggi[(messaggi.find(CARATTERI_PROTOCOLLO_FINE_MONITOR)+len(CARATTERI_PROTOCOLLO_FINE_MONITOR)):]
    # eliminazione caratteri di protocollo
    for msg in messaggi.split(CARATTERI_PROTOCOLLO_RICEZIONE_INIZIO_TCP):
    # msg = msg.replace(CARATTERI_PROTOCOLLO_RICEZIONE_INIZIO, "")
        msg = msg.replace("5c", "5c5c") # risoluzione problema conversione del \
        if CARATTERI_CODIFICA_INVIO not in msg:
            messaggio = msg[2:]
        else: messaggio = msg.replace(CARATTERI_CODIFICA_INVIO, '0d0a')
        #indice_capo = messaggio.find('0d0a')
        """messaggio_senza_inizio_riga = ""
        while indice_capo != -1 and indice_capo != len(messaggio)-4:
            messaggio_senza_inizio_riga += messaggio[:indice_capo+4]
            messaggio = messaggio[indice_capo+6:]
            indice_capo = messaggio.find('0d0a')
        if messaggio_senza_inizio_riga == "": messaggio_senza_inizio_riga = messaggio"""
            
            # conversione da esadecimale a stringa
        messaggio_finale += bytes.fromhex(messaggio).decode("unicode_escape")
    # print(f"messaggio finale: {messaggio_finale}")
    return messaggio_finale


def prepara_messaggio_invio(carattere_stringa, caratteri_protocollo_inizio, num_carattere_di_controllo):
    # print(f"carattere: {carattere_stringa}")
    # conversione da stringa ad esadecimale
    carattere_esadecimale = hex(ord(carattere_stringa)).replace("0x", "")
    if len(carattere_esadecimale) < 2: carattere_esadecimale = "0"+carattere_esadecimale
    # conversione da stringa ad intero
    carattere_intero = ord(carattere_stringa)
    # calcolo carattere di controllo
    carattere_di_controllo_intero = num_carattere_di_controllo - carattere_intero  # 65 --> A , 54 --> 6
    if carattere_di_controllo_intero < 0: carattere_di_controllo_intero += 255
    # conversione da intero ad esadecimale
    carattere_di_controllo_esadecimale = hex(carattere_di_controllo_intero).replace("0x", "")
    if len(carattere_di_controllo_esadecimale) < 2: carattere_di_controllo_esadecimale = "0"+carattere_di_controllo_esadecimale
    # creazione messaggio
    dato = f"{caratteri_protocollo_inizio}{carattere_di_controllo_esadecimale}{CARATTERI_PROTOCOLLO_INVIO_META}{carattere_esadecimale}{CARATTERI_PROTOCOLLO_INVIO_FINE}"
    # conversione da stringa ad esadecimale
    # print(dato)
    #if carattere_stringa == '+': print(f"dato: {dato}")
    dato = bytes.fromhex(dato)
    return dato


def next_free_port():
    with lock_next_free_port:
        sleep(2)
        while True:
            try:
                with sck.socket() as sock:
                    sock.bind(('', 0))
                    porta = sock.getsockname()[1]
                    #print(porta)
                    if porta not in [PORTA_CONNESSIONE_INFO, PORTA_INVIO_DATI_NETWORK_CONTROLLER, PORTA_RICEZIONE_DATI_ROBOT_NETWORK_CONTROLLER, PORTA_TERMINALE, PORTA_WEB_SERVER]: return porta
            except: pass


def get_info_from_cella(id_cella, ind_ip=None):
    with lock_creazione_server_udp:

        s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        s.bind(('', PORTA_RICEZIONE_DATI_ROBOT_NETWORK_CONTROLLER))

        if ind_ip == None:
            _, addr = s.recvfrom(4096)
            ind_ip = addr[0]
 
        try:
            s.settimeout(2)

            s.sendto(bytes.fromhex(MESSAGGIO_RICHIESTA_INFORMAZIONI_UDP), (ind_ip,PORTA_INVIO_DATI_NETWORK_CONTROLLER))

            stringa_byte, addr = s.recvfrom(4096)
            
            data = stringa_byte.hex()
            data = data.replace(" ", "")

            ip = data[:8]
            sub = data[8:16]
            flags = data[-8:]
            flags = [flags[i:i+2] for i in range(0,len(flags),2)]


            stringa_ip = ""
            for p in [ip[i:i+2] for i in range(0,len(ip),2)]:
                stringa_ip += str(int(p,16))+"."
            ip = stringa_ip[:-1]


            stringa_sub = ""
            for p in [sub[i:i+2] for i in range(0,len(sub),2)]:
                stringa_sub += str(int(p,16))+"."
            sub = stringa_sub[:-1]

            for i, flag in enumerate(flags):
                if flag == "ff": flags[i] = 1
                elif flag == "00": flags[i] = 0
                else: flags[i] = 0

            s.close()

            con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
            cur = con.cursor()
            cur.execute("UPDATE celle SET indirizzo_ip=? WHERE id=?", [ip,id_cella])
            con.commit()
            con.close()

            return "OK", [ip,sub]+flags
        except: return f"<p>C'è stato un problema con il robot {id_cella}. Verificare che sia acceso e riprovare.</p>", []


def prRed(skk): print("\033[91m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m{}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m{}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m{}\033[00m" .format(skk))

class ControlloUtentiCollegati(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
    def run(self):
        while self.running:
            for id_cella in lista_celle:
                if lista_celle[id_cella]["connessione_cella"] != None and ping(lista_celle[id_cella]["connessione_cella"].indirizzo_ip,1) == False: 
                    chiudi_cella(id_cella)
                    print("CHIUSURA CELLA (spenta)")
                else:
                    with lock_connetti[id_cella]:
                        sleep(2) # da modificare il tempo se ci sono errori nella connessione
                        if (datetime.datetime.now() - lista_celle[id_cella]["ultima_verifica"]).total_seconds() < TEMPO_MAX_TIMEOUT: pass
                        else:
                            if lista_celle[id_cella]["connessione_cella"]!=None:
                                chiudi_cella(id_cella)
                                print("CHIUSURA CELLA (inattiva)")

            sleep(0.5)

class WebServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        app.run(port=PORTA_WEB_SERVER, host=indirizzo_ip)


class TFTPServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        comando = [nome_python, f'{dir_path}{separatore}tftpserver{separatore}SimpleTftpServer.py'] if platform.system().lower()=='windows' else ['sudo', nome_python, f'{dir_path}{separatore}tftpserver{separatore}SimpleTftpServer.py']
        subprocess.run(comando)
        prRed("Il server TFTP è stato chiuso. Nel caso il programma sia ancora in esecuzione riavviare il server.")

class Cella(threading.Thread):
    def __init__(self, id_cella, s, address, porta=PORTA_TERMINALE):
        threading.Thread.__init__(self)
        self.running = True
        self.id_cella = id_cella
        self.indirizzo_ip = address
        self.porta = porta
        self.s = s
        self.output = []
    def run(self):

        sleep(2)

        self.s.sendall(bytes.fromhex(MESSAGGIO_CONNESSIONE_TCP))

        while self.running:
            with lock_recv_tcp[self.id_cella]:
                try:
                    msg =  self.s.recv(4096)
                    self.output.append(prepara_messaggio_ricezione_tcp(msg))
                    #self.s.sendall(bytes.fromhex("ff ff ff ff"))
                except sck.error: pass
                except:
                    prRed("Errore nella codifica del messaggio di ricezione")

    def send_messagge(self, messagge, invio=True):
        #print(f"message: {messagge}")
        with lock_invio_messaggio_tcp[self.id_cella]:
            if len(messagge) > 0 and messagge[0] == '!':
                self.s.sendall(bytes.fromhex(messagge[1:]))
            else:
                for carattere in messagge:
                    with lock_recv_tcp[self.id_cella]:
                        self.s.setblocking(1)
                        self.s.settimeout(MAX_SECONDI_RISPOSTA_TCP)

                        msg = ""
                        while True:
                            try:
                                self.s.sendall(prepara_messaggio_invio(carattere, CARATTERI_PROTOCOLLO_INVIO_INIZIO_TCP, 119))
                                stringa_byte = self.s.recv(4096)
                                msg = prepara_messaggio_ricezione_tcp(stringa_byte)
                                break
                            except sck.error: 
                                pass
                            except: break


                        self.output.append(msg)

                        self.s.settimeout(None)
                        self.s.setblocking(0)    

                if invio:
                    self.s.sendall(bytes.fromhex(CARATTERE_INVIO_CODIFICATO_TCP)) # invio


class CellaUDP(threading.Thread):
    def __init__(self, id_cella, address, porta=PORTA_TERMINALE):
        threading.Thread.__init__(self)
        self.running = True
        self.id_cella = id_cella
        self.indirizzo_ip = address
        self.porta = porta
        self.s = None
        self.stringa_iniziale = None
        self.econnesso = False
        self.output = []
    def run(self):

        try:
            
            while True:
                try:
                    self.s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
                    self.s.bind((indirizzo_ip_ethernet, next_free_port()))
                    break
                except: pass

            self.s.settimeout(2)

            while True:
                try:
                    self.s.sendto(bytes.fromhex(MESSAGGIO_CONNESSIONE_UDP), (self.indirizzo_ip,self.porta))
                    stringa_byte, addr = self.s.recvfrom(4096)
                    break
                except: pass

            self.econnesso = True
           

            self.s.settimeout(None)
            self.s.setblocking(0)
            
            data = stringa_byte.hex()
            data = data.replace(" ", "")
            if data[30:32] == "01": 
                self.stringa_iniziale = data[:10]+'1f'+data[12:]


            while self.running:
                with lock_recv_udp[self.id_cella]:
                    if self.stringa_iniziale != None:
                        try: 
                            stringa_byte, addr = self.s.recvfrom(4096)
                            data = stringa_byte.hex()
                            data = data.replace(" ", "")
                        except: 
                            data = None
                    

                    if self.stringa_iniziale == None or data == self.stringa_iniziale:
                        self.s.close()

                        sleep(1)

                        try:
                            sck_terminale = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
                            sck_terminale.connect((self.indirizzo_ip, self.porta)) # tupla --> indirizzo ip, porta
                            sleep(1)
                            sck_terminale.setblocking(0)

                            cella = Cella(id_cella=self.id_cella, s=sck_terminale, address=self.indirizzo_ip, porta=self.porta)
                            cella.start()
                            lista_celle[self.id_cella]["connessione_cella"] = cella
                        except:
                            try: lista_celle[self.id_cella]["connessione_cella"].s.close()
                            except: pass
                            try:
                                lista_celle[self.id_cella]["connessione_cella"].running = False
                                # lista_celle[id_cella]["connessione_cella"].join()
                            except: pass
                            lista_celle[self.id_cella]["connessione_cella"] = None


                        self.output.append("CHIUSURAWBSOCKETUDP")

                        break 
                    else:
                        if data != None: 
                            data = data.replace(CARATTERI_PROTOCOLLO_RICEZIONE_INIZIO_UDP, "")
                            data = data.replace("5c", "5c5c")
                            self.output.append(bytes.fromhex(data).decode("unicode_escape"))

        except:
            try: self.s.close()
            except: pass
            #self.output.append("CHIUSURAWBSOCKETUDP")


    def send_messagge(self, messagge):
        with lock_invo_messaggio_udp[self.id_cella]:
            if self.econnesso:
                for carattere in messagge:
                    with lock_recv_udp[self.id_cella]:
                        
                        self.s.setblocking(1)
                        self.s.settimeout(MAX_SECONDI_RISPOSTA_UDP)

                        msg = ""
                        while True:
                            try:
                                self.s.sendto(prepara_messaggio_invio(carattere, CARATTERI_PROTOCOLLO_INVIO_INIZIO_UDP, 250), (self.indirizzo_ip,self.porta))
                                stringa_byte, addr = self.s.recvfrom(4096)
                                msg = prepara_messaggio_ricezione_udp(stringa_byte)
                                break
                            except sck.error: 
                                pass
                            except: break


                        self.output.append(msg)

                        self.s.settimeout(None)
                        self.s.setblocking(0)

                self.s.sendto(prepara_messaggio_invio("\r", CARATTERI_PROTOCOLLO_INVIO_INIZIO_UDP, 250), (self.indirizzo_ip,self.porta))
                
            

class WSTerminaleUDP(threading.Thread):
    def __init__(self, address, port, id_cella):
        super().__init__()
        self.port = port
        self.address = address
        self.id_cella = id_cella
        self.running = True
        self.loop = None
    def run(self):
        #print(f"°°°°°°°WEB SOCKET PARTITO°°°°°°°°")
        self.loop = asyncio.new_event_loop()
        ws_server = websockets.serve(self.invia_dati_aggiornamento, self.address, self.port,
                                     ping_timeout=None, ping_interval=None, loop=self.loop)
        self.loop.run_until_complete(ws_server)
        self.loop.run_forever()

    async def invia_dati_aggiornamento(self, websocket, path):
        blocco_recv = True
        
        while self.running:
            if blocco_recv:
                data = await websocket.recv()
                blocco_recv = False
                #if "PRONTOARICEVERE" in data:
            try:
                if not lista_celle[self.id_cella]["connessione_cella_udp"].econnesso:
                    await websocket.send("Errore nella connessione UDP. Verifica che il robot sia acceso.\n") 
                    blocco_recv = True
                    sleep(3)
                else:
                    if len(lista_celle[self.id_cella]["connessione_cella_udp"].output) > 0:
                        valore = lista_celle[self.id_cella]["connessione_cella_udp"].output.pop(0)
                        if valore == "CHIUSURAWBSOCKETUDP":
                            await websocket.send("CHIUSURAWBSOCKETUDP")
                            blocco_recv = True
                            break   
                        else:
                            await websocket.send(valore) 
                            blocco_recv = True  
            except:
                await websocket.send("Errore nella connessione UDP. Verifica che il robot sia acceso.\n") 
                blocco_recv = True
                sleep(3)




class WSTerminale(threading.Thread):
    def __init__(self, address, port, id_cella):
        super().__init__()
        self.port = port
        self.address = address
        self.id_cella = id_cella
        self.output = [[],[],[],[]]
        self.running = True
        self.loop = None
        self.elimina_array = [True, True, True, True]

    def run(self):
        #print(f"°°°°°°°WEB SOCKET PARTITO°°°°°°°°")
        self.loop = asyncio.new_event_loop()
        ws_server = websockets.serve(self.invia_dati_aggiornamento, self.address, self.port,
                                     ping_timeout=None, ping_interval=None, loop=self.loop)
        self.loop.run_until_complete(ws_server)
        self.loop.run_forever()

    async def invia_dati_aggiornamento(self, websocket, path):
        blocco_recv = True

        while self.running:
            if blocco_recv:
                data = await websocket.recv()
                #print(data)
                #if "PRONTOARICEVERE" in data:
                blocco_recv = False

            try:
                if len(lista_celle[self.id_cella]["connessione_cella"].output) > 0:
                    valore = lista_celle[self.id_cella]["connessione_cella"].output.pop(0)

                    for arr in self.output:
                        arr.append(valore)

                    await websocket.send(valore)
                    blocco_recv = True

                    n_schede = (''.join(self.output[1][-len(FINE_SCHEDA):])).count(FINE_SCHEDA)-(''.join(self.output[1][-len(FINE_SCHEDA):-1])).count(FINE_SCHEDA)

                    if self.id_cella not in n_schede_fatte: n_schede_fatte[self.id_cella] = 0
                    n_schede_fatte[self.id_cella] += n_schede




                for i in range(len(self.output)):
                    if (self.elimina_array[i] and len(self.output[i]) > 100) : # inizio a svuotare l'array
                        self.output[i].pop(0)
            except:
                print("Errore nella connessione TCP. Nuovo tentativo...")
                await websocket.send("Errore nella connessione TCP. Nuovo tentativo...\n") 
                blocco_recv = True
                sleep(3)


class WSInfo(threading.Thread):
    def __init__(self, address, port, id_cella, address_robot):
        super().__init__()
        self.port = port
        self.address = address
        self.id_cella = id_cella
        self.running = True
        self.loop = None
        self.s = None
        self.address_robot = address_robot

    def run(self):
        #print(f"°°°°°°°WEB SOCKET PARTITO°°°°°°°°")
        self.loop = asyncio.new_event_loop()
        ws_server = websockets.serve(self.invia_dati_aggiornamento, self.address, self.port,
                                     ping_timeout=None, ping_interval=None, loop=self.loop)
        self.loop.run_until_complete(ws_server)
        self.loop.run_forever()
    
    def creare_connessione(self):
        self.s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.s.connect((self.address_robot, PORTA_CONNESSIONE_INFO)) # tupla --> indirizzo ip, porta
        self.s.settimeout(3)

    async def invia_dati_aggiornamento(self, websocket, path):
        blocco_recv = True

        lista_celle[self.id_cella]["connessione_cella"].send_messagge("abort 6")
        lista_celle[self.id_cella]["connessione_cella"].send_messagge("kill 6")
        lista_celle[self.id_cella]["connessione_cella"].send_messagge("delete info.v2")
        lista_celle[self.id_cella]["connessione_cella"].send_messagge("y")
        lista_celle[self.id_cella]["connessione_cella"].send_messagge("load D:\\info.v2")
        lista_celle[self.id_cella]["connessione_cella"].send_messagge("execute 6 info.v2")

        sleep(1)

        self.creare_connessione()
        self.s.sendall("INVIA".encode())

        dati = ""

        while self.running:
            if blocco_recv:
                data = await websocket.recv()
                #print(data)
                #if "PRONTOARICEVERE" in data:
                blocco_recv = False
            
            try:
                var = self.s.recv(4096).decode()
                dati += var
                
            except:
                #print("Errore v2 1")
                await websocket.send("@ERRORE@Web socket dello stato degli input non più disponibile. Riavvialo.")
                blocco_recv = True
                self.running = False
            if self.running:
                try:
                    if "}" in dati:
                        #print(dati[:dati.find("}")])
                        await websocket.send(dati[:dati.find("}")+1])
                        blocco_recv = True
                        dati = dati[dati.find("}")+1:]
                        self.s.sendall("INVIA".encode())
                except:
                    #print("Errore v2 2")
                    await websocket.send("@ERRORE@Web socket dello stato degli input non più disponibile. Riavvialo.")
                    blocco_recv = True
                    self.running = False
    
        
            sleep(0.2)


def main():
    global indirizzo_ip, indirizzo_ip_ethernet, nome_python

    con = sqlite3.connect(f"{dir_path}{separatore}calibrazione.db")
    cur = con.cursor()
    cur.execute('SELECT * FROM celle')
    output = cur.fetchall()
    con.close()

    for riga in output:
        if riga[5] == "ON":
            celle_disponibili[riga[0]] = [riga[4]]
            lista_celle[riga[0]] = copy.deepcopy(prototipo_cella)

            lock_cella[riga[0]] = Lock()
            lock_invio_messaggio_tcp[riga[0]] = Lock()
            lock_invo_messaggio_udp[riga[0]] = Lock()
            lock_recv_tcp[riga[0]] = Lock()
            lock_recv_udp[riga[0]] = Lock()
            lock_upload[riga[0]] = Lock()
            lock_upload_programma[riga[0]] = Lock()
            lock_calibrazione[riga[0]] = Lock()
            lock_connetti[riga[0]] = Lock()
            lock_cambia_ip[riga[0]] = Lock()

    while True:
        indirizzo_ip = input("Indirizzo ip del web server (default 0.0.0.0): ").replace(" ", "")
        if isIp(indirizzo_ip): break
        elif indirizzo_ip == '':
            indirizzo_ip = "0.0.0.0"
            break
        else: print("Errore: indirizzo ip non valido")
    
    while True:
        indirizzo_ip_ethernet = input("Indirizzo ip della scheda ethernet (default 172.16.110.1): ").replace(" ", "")
        if isIp(indirizzo_ip_ethernet): break
        elif indirizzo_ip_ethernet == '':
            indirizzo_ip_ethernet = "172.16.110.1"
            break
        else: print("Errore: indirizzo ip non valido")


    controllo_utenti_collegati = ControlloUtentiCollegati()
    controllo_utenti_collegati.start()

    web_server = WebServer()
    web_server.start()

    sleep(1)

    _webbrowser.open('http://'+indirizzo_ip+':{}'.format(PORTA_WEB_SERVER))  # or webbrowser.open_new_tab()"""

    try: version_python = subprocess.run(["python3", "--version"], capture_output=True).stdout.decode()
    except: version_python = "Errore"

    if "Python 3." not in version_python:
        try: version_python = subprocess.run(["python", "--version"], capture_output=True).stdout.decode()
        except: version_python = "Errore"
        if "Python 3." not in version_python:
            prRed("Per eseguire questo programma è necessario Python 3.")
            exit()
        else: nome_python = "python"
    else: nome_python = "python3"

    tftp_server = TFTPServer()
    tftp_server.start()



    
if __name__ == "__main__":
    main()

