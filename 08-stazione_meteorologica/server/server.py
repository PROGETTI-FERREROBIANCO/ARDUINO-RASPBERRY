"""



   _____ _            _                    __  __      _                       _             _              _____ ______ _______      ________ _____  
  / ____| |          (_)                  |  \/  |    | |                     | |           (_)            / ____|  ____|  __ \ \    / /  ____|  __ \ 
 | (___ | |_ __ _ _____  ___  _ __   ___  | \  / | ___| |_ ___  ___  _ __ ___ | | ___   __ _ _  ___ __ _  | (___ | |__  | |__) \ \  / /| |__  | |__) |
  \___ \| __/ _` |_  / |/ _ \| '_ \ / _ \ | |\/| |/ _ \ __/ _ \/ _ \| '__/ _ \| |/ _ \ / _` | |/ __/ _` |  \___ \|  __| |  _  / \ \/ / |  __| |  _  / 
  ____) | || (_| |/ /| | (_) | | | |  __/ | |  | |  __/ ||  __/ (_) | | | (_) | | (_) | (_| | | (_| (_| |  ____) | |____| | \ \  \  /  | |____| | \ \ 
 |_____/ \__\__,_/___|_|\___/|_| |_|\___| |_|  |_|\___|\__\___|\___/|_|  \___/|_|\___/ \__, |_|\___\__,_| |_____/|______|_|  \_\  \/   |______|_|  \_\
                                                                                        __/ |                                                         
                                                                                       |___/                                                          



"""

""" _______________________INCLUSIONE LIBRERIE________________________"""

from logging import NOTSET
from flask import Flask, render_template, jsonify, send_file
import threading
from pathlib import Path
import logzero
import requests
import sqlite3
import time
from mega import Mega
import datetime
import os
import subprocess
import pandas as pd
import urllib3

""" //////////////////////////////////////////////////////////////// """


""" ______________________DEFINIZIONE VARIABILI_____________________ """

#           DELAY          #
SECONDI_TRA_AGGIORNAMENTO_DATI = 60*1
# ------------------------ #

#          THREAD          #
blocco_thread = threading.Lock()
convertitore_db_a_csv = threading.Thread()
ottenimento_dati = threading.Thread()
raggruppamento_dati = threading.Thread()
eliminazione_dati_vecchi = threading.Thread()
gestione_comandi = threading.Thread()
# ------------------------ #

#   ACCESSO ACCOUNT MEGA   #
email = "..."
password = "..."
# ------------------------ #

#          SOCKET          #
SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 4000
TIPO_SITO = "http"
# ------------------------ #

#    PERCORSO CARTELLA     #
dir_path = str(Path(__file__).parent.resolve())
print(dir_path)
# ------------------------ #

#      FILE PER ERRORI     #
file_info_error= logzero.setup_logger(name='file_info_error', logfile=f"{dir_path}/log/file_info_error.csv") 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ------------------------ #

#      DATI STAZIONI       #
stazioni_elenco_ID = []
stazioni_sensori = {}
stazioni_address = {}
stazioni_lock_csv = {}
# ------------------------ #

#     OPZIONI POSSIBILI    #
altre_opzioni = ["dati_attuali", "dati_giornalieri", "dati_mensili", "dati_annuali"]
# ------------------------ #

#            DATI          #
dati_raggruppati_giornalieri = {}
dati_raggruppati_mensili = {}
dati_raggruppati_annuali = {}
dati_raggruppati_attuali = {}
# ------------------------ #
""" //////////////////////////////////////////////////////////////// """



""" ____________________DEFINIZIONI ROUTE FLASK_____________________ """

app = Flask(__name__)

@app.route("/stazione-meteorologica/<numero_stazione>/html/<pagina_richiesta>")
def inviaPagina(numero_stazione, pagina_richiesta):
    try:
        numero_stazione = int(numero_stazione)
        if numero_stazione in stazioni_elenco_ID and pagina_richiesta in stazioni_sensori[numero_stazione]: 
            elenco_sens = ""
            for el in stazioni_sensori[numero_stazione]:
                elenco_sens += f"{el},"
            return render_template(f'{pagina_richiesta}.html', dati_della_stazione_meteorologica=[f"{TIPO_SITO}{SERVER_ADDRESS}:{SERVER_PORT}",numero_stazione, elenco_sens[:-1]])
        elif numero_stazione in stazioni_elenco_ID and pagina_richiesta == "index": 
            elenco_sens = ""
            for el in stazioni_sensori[numero_stazione]:
                elenco_sens += f"{el},"
            return render_template("index.html", dati_della_stazione_meteorologica=[f"{TIPO_SITO}://{SERVER_ADDRESS}:{SERVER_PORT}",numero_stazione, elenco_sens[:-1]])
        else: return render_template("pagina_non_trovata.html")
    except:
        file_info_error.error("error web page")
        return render_template("pagina_di_errore.html")


@app.route("/stazione-meteorologica/<numero_stazione>/dato/<tipo>/<dato_richiesto>")
def inviaDato(numero_stazione, tipo, dato_richiesto):
    try:
        numero_stazione = int(numero_stazione)
        if numero_stazione in stazioni_elenco_ID and (dato_richiesto in stazioni_sensori[numero_stazione] or dato_richiesto == "tutti")and tipo in altre_opzioni:
            if tipo == altre_opzioni[0]:
                if dato_richiesto == "tutti":
                    return jsonify(dati_raggruppati_attuali[numero_stazione])
                else:
                    return jsonify({"data_ora":dati_raggruppati_attuali[numero_stazione]["data_ora_stazione"], "dato_richiesto": dati_raggruppati_attuali[numero_stazione][dato_richiesto]})
            elif tipo == altre_opzioni[1]:
                if dato_richiesto == "tutti":
                    return jsonify(dati_raggruppati_giornalieri[numero_stazione])
                else:
                    return jsonify({"data_ora":dati_raggruppati_giornalieri[numero_stazione]["data_ora_stazione"],"dato_richiesto":dati_raggruppati_giornalieri[numero_stazione][dato_richiesto]})
            elif tipo == altre_opzioni[2]:
                if dato_richiesto == "tutti":
                    return jsonify(dati_raggruppati_mensili[numero_stazione])
                else:
                    return jsonify({"data_ora":dati_raggruppati_mensili[numero_stazione]["data_giorno"],"dato_richiesto":dati_raggruppati_mensili[numero_stazione][dato_richiesto]})
            elif tipo == altre_opzioni[3]:
                if dato_richiesto == "tutti":
                    return jsonify(dati_raggruppati_annuali[numero_stazione])
                else:
                    return jsonify({"data_ora":dati_raggruppati_annuali[numero_stazione]["data_mese"],"dato_richiesto":dati_raggruppati_annuali[numero_stazione][dato_richiesto]})
        else:
            return render_template("dato_non_trovato.html")
    except:
        file_info_error.error("data request error")
        return render_template("pagina_di_errore.html")

@app.route("/stazione-meteorologica/download/<numero_stazione>/<tipo_tabella>")
def download(numero_stazione, tipo_tabella):
    try:
        numero_stazione = int(numero_stazione)
        if numero_stazione in stazioni_elenco_ID and tipo_tabella in altre_opzioni[1:]:
            while stazioni_lock_csv[numero_stazione].locked():
                pass

            if tipo_tabella == altre_opzioni[1]:
                return send_file(f"{dir_path}/csv/dati_sensori_giornalieri_{numero_stazione}.csv", as_attachment=True)
            elif tipo_tabella == altre_opzioni[2]:
                return send_file(f"{dir_path}/csv/dati_sensori_mensili_{numero_stazione}.csv", as_attachment=True)
            elif tipo_tabella == altre_opzioni[3]:
                return send_file(f"{dir_path}/csv/dati_sensori_annuali_{numero_stazione}.csv", as_attachment=True)
    except:
        file_info_error.error("error download csv")
        return render_template("pagina_di_errore.html")
    

""" //////////////////////////////////////////////////////////////// """

""" _________________SPECIALIZZAZIONI CLASSI THREAD_________________ """

class ConvertitoreDBaCSV(threading.Thread):
    """
    Questo thread permette di convertire tabelle di un database in formato csv
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running:

            with blocco_thread:

                try:

                    conn = sqlite3.connect(f"{dir_path}/database/dati_sensori_stazioni.db", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)

                    try:
                        for n in stazioni_elenco_ID:
                            with stazioni_lock_csv[n]:
                                db_df = pd.read_sql_query(f"SELECT * FROM dati_stazione_{n}", conn)
                                db_df.to_csv(f"{dir_path}/csv/dati_sensori_giornalieri_{n}.csv", index=False)
                                db_df = pd.read_sql_query(f"SELECT * FROM media_giorni_dati_stazione_{n}", conn)
                                db_df.to_csv(f"{dir_path}/csv/dati_sensori_mensili_{n}.csv", index=False)
                                db_df = pd.read_sql_query(f"SELECT * FROM media_mesi_dati_stazione_{n}", conn)
                                db_df.to_csv(f"{dir_path}/csv/dati_sensori_annuali_{n}.csv", index=False)
                    except:
                        file_info_error.error("error in the conversion from database to CSV")

                    conn.close()

                except:
                    file_info_error.error("error database thread ConvertitoreDBaCSV")


            time.sleep(SECONDI_TRA_AGGIORNAMENTO_DATI)



class OttenimentoDati(threading.Thread):
    """
    Questo thread permette di acquisire i dati dalle varie stazioni
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        global dati_raggruppati_attuali

        while self.running:

            with blocco_thread:

                try:

                    conn = sqlite3.connect(f"{dir_path}/database/dati_sensori_stazioni.db", timeout=20) # connessione al database
                    cur = conn.cursor()

                    try:

                        for n in stazioni_elenco_ID:  

                            continuare = True 

                            try:
                                dict_ricevuto = eval(requests.get(f"{stazioni_address[n]}/stazione-meteorologica/dato/sensori-attuali", verify=False, timeout=20).text) # richiesta di invio dati
                                # anche se ci sono degli / di troppo tra stazioni_address[n] e link della risorsa non importa
                            except:
                                file_info_error.error(f"station number {n} data reception error")
                                continuare = False


                            if continuare:
                                print(f"salvataggio dati_stazione_{n} su database")

                                data_ora_server = str(datetime.datetime.utcnow())
                                data_ora_stazione = dict_ricevuto["data_ora_stazione"]

                                dati_raggruppati_attuali[n] = dict_ricevuto.copy()

                                del dict_ricevuto["data_ora_stazione"]

                                # CARICAMENTO DATI SU DATABASE
                                nomi_colonne = "data_ora_server,data_ora_stazione,"
                                for nome_sensore in stazioni_sensori[n]:
                                    nomi_colonne += f"\"{nome_sensore}\","


                                sql = f"INSERT INTO dati_stazione_{n} ({nomi_colonne[:-1]}) VALUES (\"{data_ora_server}\",\"{data_ora_stazione}\","

                                for nome_sensore in stazioni_sensori[n]:
                                    dato = 9999.9
                                    try:
                                        dato = dict_ricevuto[nome_sensore]
                                    except:
                                        print("aggiungere sensore nel file di configurazione del raspberry")

                                    sql += f"{dato},"

                                sql = sql[:-1]
                                sql += ")"

                                cur.execute(sql)
                                
                                conn.commit()

                    except:
                        file_info_error.error("error in saving data on database")
                    
                    conn.close()

                except:
                    file_info_error.error("error database thread OttenimentoDati")

            time.sleep(SECONDI_TRA_AGGIORNAMENTO_DATI)



class RaggruppamentoDati(threading.Thread):
    """
    Questo thread raggruppa per tipo tutti i dati fino ad ora caricati sul database
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        global dati_raggruppati_giornalieri
        global dati_raggruppati_mensili
        global dati_raggruppati_annuali

        data = str(datetime.datetime.utcnow())
        giorno_att = data.split(" ")[0].split("-")[2]
        mese_att = data.split(" ")[0].split("-")[1]
        anno_att = data.split(" ")[0].split("-")[0]
        giorno_prec = giorno_att
        mese_prec = mese_att


        while self.running:

            with blocco_thread:

                try:

                    conn = sqlite3.connect(f"{dir_path}/database/dati_sensori_stazioni.db", timeout=20) # connessione al database
                    cur = conn.cursor()

                    try:                    
                        data = str(datetime.datetime.utcnow())
                        giorno_att = data.split(" ")[0].split("-")[2]
                        mese_att = data.split(" ")[0].split("-")[1]
                        anno_att = data.split(" ")[0].split("-")[0]

                        for n in stazioni_elenco_ID:   

                            # estrazione dati da tabella totale

                            dict_dati_giornalieri = {}

                            dict_dati_giornalieri["data_ora_stazione"] = []

                            for tipo_sensore in stazioni_sensori[n]:
                                dict_dati_giornalieri[tipo_sensore] = []


                            for row in cur.execute(f"SELECT * FROM dati_stazione_{n} WHERE dati_stazione_{n}.data_ora_stazione LIKE \"{anno_att}-{mese_att}-{giorno_att} %:%:%.%\""): # acquisisco i dati solo del giorno
                                dict_dati_giornalieri["data_ora_stazione"].append(row[2])
                                for numero_sensore, tipo_sensore in enumerate(stazioni_sensori[n]):
                                    if row[numero_sensore+3] == None:
                                        dict_dati_giornalieri[tipo_sensore].append(9999.9)
                                    else:
                                        dict_dati_giornalieri[tipo_sensore].append(row[numero_sensore+3])  # +3 perché salto l'id + le due date

                            dati_raggruppati_giornalieri[n] = dict_dati_giornalieri.copy()

                            # estrazione dati da tabella giorni

                            dict_dati_mensili = {}

                            dict_dati_mensili["data_giorno"] = []

                            for tipo_sensore in stazioni_sensori[n]:
                                dict_dati_mensili[tipo_sensore] = []

                            for row in cur.execute(f"SELECT * FROM media_giorni_dati_stazione_{n} WHERE media_giorni_dati_stazione_{n}.data_giorno LIKE \"{anno_att}-{mese_att}-%\""): # acquisisco i dati solo del giorno
                                dict_dati_mensili["data_giorno"].append(row[1])
                                for numero_sensore, tipo_sensore in enumerate(stazioni_sensori[n]):
                                    if row[numero_sensore+2] == None:
                                        dict_dati_mensili[tipo_sensore].append(9999.9)
                                    else:
                                        dict_dati_mensili[tipo_sensore].append(row[numero_sensore+2])

                            dati_raggruppati_mensili[n] = dict_dati_mensili.copy()

                            # estrazione dati da tabella mese

                            dict_dati_annuali = {}

                            dict_dati_annuali["data_mese"] = []

                            for tipo_sensore in stazioni_sensori[n]:
                                dict_dati_annuali[tipo_sensore] = []

                            for row in cur.execute(f"SELECT * FROM media_mesi_dati_stazione_{n}"):
                                dict_dati_annuali["data_mese"].append(row[1])
                                for numero_sensore, tipo_sensore in enumerate(stazioni_sensori[n]):
                                    if row[numero_sensore+2] == None:
                                        dict_dati_annuali[tipo_sensore].append(9999.9)
                                    else:
                                        dict_dati_annuali[tipo_sensore].append(row[numero_sensore+2])

                            dati_raggruppati_annuali[n] = dict_dati_annuali.copy()




                            # --------------------------------------------------------------- #
                            # --------------------------------------------------------------- #
                            
                            if giorno_att != giorno_prec:
                                sql = ""
                                if mese_att != mese_prec:
                                    # devo estrarre i dati dalla tabella di media mesi e fare la media
                                    dict_media_dati_annuali = {}

                                    dict_media_dati_annuali["data_mese"] = f"{anno_att}-{mese_prec}"

                                    for tipo_sensore in stazioni_sensori[n]:
                                        for row in cur.execute(f"SELECT avg(media_giorni_dati_stazione_{n}.{tipo_sensore}) FROM media_giorni_dati_stazione_{n} WHERE media_giorni_dati_stazione_{n}.data_giorno LIKE \"{anno_att}-{mese_prec}-%\" and media_giorni_dati_stazione_{n}.{tipo_sensore} != 9999.9 and media_giorni_dati_stazione_{n}.{tipo_sensore} != 8888.8 and media_giorni_dati_stazione_{n}.{tipo_sensore} NOT NULL"):
                                            if row[0] == None: dict_media_dati_annuali[tipo_sensore] = 9999.9
                                            else: dict_media_dati_annuali[tipo_sensore] = row[0]

                                    # inserire i dati nel database

                                    nomi_colonne = "data_mese,"
                                    for nome_sensore in stazioni_sensori[n]:
                                        nomi_colonne += f"\"{nome_sensore}\","

                                    sql = f"INSERT INTO media_mesi_dati_stazione_{n} ({nomi_colonne[:-1]}) VALUES (\"{dict_media_dati_annuali['data_mese']}\","
                                    
                                    for nome_sensore in stazioni_sensori[n]:
                                        sql += f"{dict_media_dati_annuali[nome_sensore]},"

                                    sql = sql[:-1]
                                    sql += ")"

                                else: # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                                    
                                    dict_media_dati_mensili = {}

                                    dict_media_dati_mensili["data_giorno"] = f"{anno_att}-{mese_att}-{giorno_prec}"

                                    for tipo_sensore in stazioni_sensori[n]:
                                        for row in cur.execute(f"SELECT avg(dati_stazione_{n}.{tipo_sensore}) FROM dati_stazione_{n} WHERE dati_stazione_{n}.data_ora_stazione LIKE \"{anno_att}-{mese_att}-{giorno_prec} %:%:%.%\" and dati_stazione_{n}.{tipo_sensore} != 9999.9 and dati_stazione_{n}.{tipo_sensore} != 8888.8 and dati_stazione_{n}.{tipo_sensore} NOT NULL"):
                                            if row[0] == None: dict_media_dati_mensili[tipo_sensore] = 9999.9
                                            else: dict_media_dati_mensili[tipo_sensore] = row[0]

                                    
                                    # inserire i dati nel database

                                    nomi_colonne = "data_giorno,"
                                    for nome_sensore in stazioni_sensori[n]:
                                        nomi_colonne += f"\"{nome_sensore}\","

                                    sql = f"INSERT INTO media_giorni_dati_stazione_{n} ({nomi_colonne[:-1]}) VALUES (\"{dict_media_dati_mensili['data_giorno']}\","
                                    
                                    for nome_sensore in stazioni_sensori[n]:
                                        sql += f"{dict_media_dati_mensili[nome_sensore]},"

                                    sql = sql[:-1]
                                    sql += ")"
                                    
                                cur.execute(sql)
                                conn.commit()
                            
                            giorno_prec = giorno_att
                            mese_prec = mese_att

                    except:
                        file_info_error.error("error in extract data from database")

                    conn.close()   

                except:
                    file_info_error.error("error database thread OttenimentoDati")             
            
            time.sleep(SECONDI_TRA_AGGIORNAMENTO_DATI)



class EliminazioneDatiVecchi(threading.Thread):
    """
    Questo thread permette di caricare su cloud, eliminare e ricreare il databse 
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
    
    def run(self):
        parametro_backup = datetime.datetime.utcnow().year
        parametro_backup_precedente = datetime.datetime.utcnow().year

        while self.running:

            data_ora_corrente = datetime.datetime.utcnow()
            parametro_backup = data_ora_corrente.year
            

            if parametro_backup != parametro_backup_precedente:
                with blocco_thread:

                    try: 
                        errore = False

                        data_ora_corrente = str(data_ora_corrente).replace(":", "-")    
                        
                        # rinominazione database
                        subprocess.run(["mv", f"{dir_path}/database/dati_sensori_stazioni.db", f"{dir_path}/database/{data_ora_corrente}.db"])

                        try:
                            mega = Mega()
                            m = mega.login(email, password)
                            
                            # SALVATAGGIO DATABASE SU CLOUD
                            print("salvataggio dati su cloud")

                            folder = m.find('StazioneMeteorologica/database', exclude_deleted=True)
                            m.upload(f"{dir_path}/database/{data_ora_corrente}.db", folder[0])
                        except:
                            file_info_error.error("error upload mega")
                            errore = True

                        if errore == False:
                            # se è successo un errore non elimino il database
                            print("eliminazione dati")
                            subprocess.run(["rm", f"{dir_path}/database/{data_ora_corrente}.db"])

                    except:
                        file_info_error.error("error in the EliminazioneDatiVecchi thread")

                    try:
                        # ricreo il database
                        inizializzazioneStazioniMeteorologiche()
                    except:
                        file_info_error.error("database creation error")
                    
            parametro_backup_precedente = parametro_backup
            time.sleep(60)  



class GestioneComandi(threading.Thread):
    """
    Questo thread permette di gestire il programma del server con alcuni comandi
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
    
    def run(self):
        while self.running:
        
            comando = input("")

            if comando == "refresh":
                with blocco_thread:
                    inizializzazioneStazioniMeteorologiche()
                print("\nREFRESH EFFETTUATO\n")
            elif "delete:" in comando:
                stz_id = int(comando.split(":")[1])
                if stazioni_elenco_ID.count(stz_id) == 0:
                    print(f"\nID: {stz_id}, NON PRESENTE NELLA LISTA DI ID_STAZIONI\n")
                else:
                    i = stazioni_elenco_ID.index(stz_id)
                    with blocco_thread:
                        stazioni_elenco_ID.pop(i)
                    print(f"\nID: {stz_id}, ELIMINATO DALLA LISTA DI ID_STAZIONI\n")
            elif comando == "list":
                print(stazioni_elenco_ID)
                print("\n")
            elif comando == "data":
                print("\n")
                for n in stazioni_elenco_ID:
                    print("|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|")
                    print(f"ID: {n}")
                    print(f"Elenco sensori: {stazioni_sensori[n]}")
                    print(f"Address: {stazioni_address[n]}")
                    print("|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|")
                print("\n")
            elif comando == "stop":
                print("\nATTENDERE...")
                with blocco_thread:
                    print("\n--> Digitare Ctrl+c fino a quando il programma termina (uscita dall'opzione tra 10 secondi) <--\n")
                    time.sleep(10)
                    print("Tempo scaduto\n")
            elif comando == "help":
                print("\nCOMANDI:\n")
                print("- refresh --> serve per aggiornare il server quando si aggiungono nuove stazioni meteorologiche o si modificano i dati\n")
                print("- delete:ID --> serve per eliminare dal server una stazione con l'ID specificato\n")
                print("- list --> serve per mostrare la lista degli id delle stazioni meteorologiche attive \n")
                print("- data --> serve per mostrare i dati che il server sa sulle stazioni meteorologiche\n")
                print("- stop --> serve per poter terminare il programma in modo sicuro\n")
                print("- help --> serve per mostrare i comandi possibili con le loro spiegazioni\n")
                print("\n")
            else: print("\nCOMANDO NON RICONOSCIUTO\n")



            
        
""" //////////////////////////////////////////////////////////////// """

def inizializzazioneStazioniMeteorologiche():
    """
    Questa funzione legge il contenuto dei file presenti nella cartella dati_stazioni, ne estrapola il contenuto
    e va ad aggiornale le strutture dati presenti nel programma
    """

    global stazioni_elenco_ID
    global stazioni_sensori
    global stazioni_address
    global stazioni_lock_csv

    stazioni_elenco_ID = []
    stazioni_sensori = {}
    stazioni_address = {}
    stazioni_lock_csv = {}
    
    id = -1

    for _, _, files in os.walk(f"{dir_path}/dati_stazioni"):

        con = sqlite3.connect(f"{dir_path}/database/dati_sensori_stazioni.db", timeout=20)
        cur = con.cursor()
        
        for file in files:

            try:
                with open(f"{dir_path}/dati_stazioni/{file}") as config_file_stazione:
                    righe = config_file_stazione.readlines()
                    
                    # estrazione ID
                    id = int(righe[1].replace("\n",""))
                    stazioni_elenco_ID.append(id)

                    # estrazione elenco_sensori e tipi_sensori
                    stazioni_sensori[id] = righe[0].replace("\n","").split(",")   # aggiungo ["data_ora_server"] per poi potere memoriazzare l'ora di salvataggio dei dati
                    
                    # estrazione address_stazione
                    stazioni_address[id] = righe[2].replace("\n","")

                    stazioni_lock_csv[id] = threading.Lock()

                    # creazione tabella contenente dati sensori -------------------------------------------------------------
                    stringa_creazione_tabella = f"CREATE TABLE if not exists \"dati_stazione_{id}\" (\"ID_misurazioni\" INTEGER NOT NULL, \"data_ora_server\" TEXT, \"data_ora_stazione\" TEXT, "
                    

                    for sensore in stazioni_sensori[id]:
                        stringa_creazione_tabella += f"\"{sensore}\" REAL, "

                    stringa_creazione_tabella += "PRIMARY KEY(\"ID_misurazioni\" AUTOINCREMENT))"
                    cur.execute(stringa_creazione_tabella)
                    
                    con.commit()

                    # verifica aggiunta di nuovi sensori

                    cursor = con.execute(f'select * from dati_stazione_{id}')
                    names = [description[0] for description in cursor.description]

                    diff = list(set(stazioni_sensori[id]) - set(names))

                    for ns in diff:
                        cur.execute(f"ALTER TABLE dati_stazione_{id} ADD COLUMN {ns} REAL")

                    con.commit()

                    # creazione tabella contenente media giorni sensori ---------------------------------------------------
                    stringa_creazione_tabella = f"CREATE TABLE if not exists \"media_giorni_dati_stazione_{id}\" (\"ID_media_giorno\" INTEGER NOT NULL, \"data_giorno\" TEXT, "
                    

                    for sensore in stazioni_sensori[id]:
                        stringa_creazione_tabella += f"\"{sensore}\" REAL, "

                    stringa_creazione_tabella += "PRIMARY KEY(\"ID_media_giorno\" AUTOINCREMENT))"
                    cur.execute(stringa_creazione_tabella)

                    con.commit()

                    # verifica aggiunta di nuovi sensori

                    cursor = con.execute(f'select * from media_giorni_dati_stazione_{id}')
                    names = [description[0] for description in cursor.description]

                    diff = list(set(stazioni_sensori[id]) - set(names))

                    for ns in diff:
                        cur.execute(f"ALTER TABLE media_giorni_dati_stazione_{id} ADD COLUMN {ns} REAL")

                    con.commit()

                    # creazione tabella contenente media mese sensori -------------------------------------------------------
                    stringa_creazione_tabella = f"CREATE TABLE if not exists \"media_mesi_dati_stazione_{id}\" (\"ID_media_mese\" INTEGER NOT NULL, \"data_mese\" TEXT, "
                    

                    for sensore in stazioni_sensori[id]:
                        stringa_creazione_tabella += f"\"{sensore}\" REAL, "

                    stringa_creazione_tabella += "PRIMARY KEY(\"ID_media_mese\" AUTOINCREMENT))"
                    cur.execute(stringa_creazione_tabella)

                    con.commit()

                    # verifica aggiunta di nuovi sensori

                    cursor = con.execute(f'select * from media_mesi_dati_stazione_{id}')
                    names = [description[0] for description in cursor.description]

                    diff = list(set(stazioni_sensori[id]) - set(names))

                    for ns in diff:
                        cur.execute(f"ALTER TABLE media_mesi_dati_stazione_{id} ADD COLUMN {ns} REAL")

                    con.commit()

            
            except:
                file_info_error.error(f"error in creating the weather station")

        
        con.close()



""" ------------------MAIN------------------ """

def main():

    inizializzazioneStazioniMeteorologiche()

    global convertitore_db_a_csv
    convertitore_db_a_csv = ConvertitoreDBaCSV()
    convertitore_db_a_csv.start()

    global ottenimento_dati
    ottenimento_dati = OttenimentoDati()
    ottenimento_dati.start()

    global raggruppamento_dati
    raggruppamento_dati = RaggruppamentoDati()
    raggruppamento_dati.start()

    global eliminazione_dati_vecchi
    eliminazione_dati_vecchi = EliminazioneDatiVecchi()
    eliminazione_dati_vecchi.start()

    global gestione_comandi
    gestione_comandi = GestioneComandi()
    gestione_comandi.start()

    app.run(host=SERVER_ADDRESS, port=SERVER_PORT)

""" --------------------------------------- """

if __name__ == "__main__":
    main()
