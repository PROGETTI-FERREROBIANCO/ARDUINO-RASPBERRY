from flask import Flask, render_template, redirect, request, session, jsonify
from flask_session import Session
import pymysql
from pathlib import Path
import datetime
import numpy as np
import re
from time import sleep
import threading as thr
import requests
import serial
import websockets
import asyncio
import socket
import pandas as pd

"""
pip install Flask-Session
pip install telebot
pip install telethon
pip install flask
pip install websockets
pip install PyMySQL
pip install numpy
pip install pyserial
pip install pandas
"""

dir_path = str(Path(__file__).parent.resolve())

opzioni_icone_stanze = ["ion-android-globe", "ion-android-happy", "ion-android-home", "ion-android-boat"]
opzioni_colore_stanze = ["bg-info", "bg-warning"]
html_stanze = """
<div class="col-lg-3 col-6">
            <!-- small box -->
            <div class="small-box COLORE_STANZA">
              <div class="inner">
                <h4>NOME_PROPRIETARIO</h4>

                <p>DESCRIZIONE</p>
              </div>
              <div class="icon">
                <i class="ion ICONA_SCELTA"></i>
              </div>
              <a href="/stanza?id_stanza=ID_STANZA" class="small-box-footer">Controlla <i class="fas fa-arrow-circle-right"></i></a>
            </div>
          </div>
"""

html_dispositivi = """
<div class="col-lg-3 col-6">
            <!-- small box -->
            <div class="small-box COLORE_DISPOSITIVO">
              <div class="inner">
                <h4>NOME_DISPOSITIVO</h4>

                <p>DESCRIZIONE</p>
              </div>
              <div class="icon">
                <i class="ion ICONA_SCELTA"></i>
              </div>
              <a href="/dispositivo?id_dispositivo=ID_DISPOSITIVO" class="small-box-footer">Controlla <i class="fas fa-arrow-circle-right"></i></a>
            </div>
          </div>
"""


html_opzione_admin = """
<a href="/admin" class="dropdown-item">
  <i class="fa fa-database mr-2"></i>Gestione DB
</a>
"""


html_pulsante_download = """
<button type="button" onclick='/download?id_stanza=ID_STANZA&id_dipositivo=ID_DISPOSITIVO' class="btn btn-success btn-block">Download dati<i class="fa fa-chart-line"></i></button>

"""

NUM_MAX_TENATIVI_FALLITI_PASSWORD = 3
TIMER_TENTATIVI_FALLITI = 10

MIN_LUNGHEZZA_PASSWORD = 8
MAX_LUNGHEZZA_PASSWORD = 16

MIN_LUNGHEZZA_USERNAME = 8
MAX_LUNGHEZZA_USERNAME = 16

N_TENTATIVI_MESSAGGIO = 10
TEMPO_LETTURA_CONSUMI = 60
MIN_PORT = 40000
MAX_PORT = 40100


hostname = 'localhost'
dbusername = '...'
dbpassword = '...'
dbname = 'casa'


arduino = serial.Serial('/dev/ttyACM0',9600)
sleep(5)
lock_arduino = thr.Lock()

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
  # check if the users exist or not
    if not session.get("user_id"):
        # if not there in the session then redirect to the login page
        return redirect("/login")
    
    codice_stanze, errore1 = get_html_lista_stanze()
    utente, errore2 = get_nome_utente_da_id(session["user_id"])

    if errore1 == "OK":
      if errore2 == "OK":
        return render_template('index.html', codice_stanze=codice_stanze, utente=utente, opzione_admin=session["opzione_admin"])
      else: return render_template("server_error.html", errore=errore2)

    else: return render_template("server_error.html", errore=errore1)
  
@app.route("/login", methods=["POST", "GET"])
def login():
    error = None
    timer = None

    if session.get("user_id"):
      session.pop('user_id')
  
    if request.method == "POST":

        #sleep(1) # per protezione da attacchi brute force

        username = request.form['username'].replace(" ", "")
        password = request.form['password'].replace(" ", "")

        if not session.get("blocco_password"):
              session["blocco_password"] = False
        
        if session['blocco_password'] == False:
          completion, errore_db, grado_amministrazione = validate(username, password, request.remote_addr)
          
          if errore_db == "OK":
            if completion == None:
                verifica_brute_force(username, request.remote_addr)

                if not session.get("brute_force_count"):
                  session["brute_force_count"] = 1
                  error = f'Credenziali sbagliate. Provare di nuovo. Tentativi rimanenti: {NUM_MAX_TENATIVI_FALLITI_PASSWORD-session["brute_force_count"]}'
                  timer = None
                else:

                  session["brute_force_count"] += 1

                  if session["brute_force_count"] == NUM_MAX_TENATIVI_FALLITI_PASSWORD:
                    session["blocco_password"] = True

                    if not session.get("brute_force_tempo_blocco"):
                      session["brute_force_tempo_blocco"] = TIMER_TENTATIVI_FALLITI
                    else:
                      session["brute_force_tempo_blocco"] += TIMER_TENTATIVI_FALLITI

                    session["brute_force_data_blocco"] = datetime.datetime.now()

                    error = "Troppi tentativi sbagliati"
                    timer = int(abs((datetime.datetime.now() - (session["brute_force_data_blocco"] + datetime.timedelta(seconds=session["brute_force_tempo_blocco"]))).total_seconds()))
                    
                  else:
                    error = f'Credenziali sbagliate. Provare di nuovo. Tentativi rimanenti: {NUM_MAX_TENATIVI_FALLITI_PASSWORD-session["brute_force_count"]}'
                    timer = None
                
            else:
                # password inserita correttamente
                if session.get("brute_force_count"): session.pop('brute_force_count')
                if session.get("brute_force_data_blocco"): session.pop('brute_force_data_blocco')
                if session.get("brute_force_tempo_blocco"): session.pop('brute_force_tempo_blocco')

                session["user_id"] = completion
                session['grado_amministrazione'] = grado_amministrazione

                if session['grado_amministrazione'] == "amministratore":
                  session["opzione_admin"] = html_opzione_admin
                else: 
                  session["opzione_admin"] = None

                session["output_last_query"] = ""
                
                return redirect("/")
          else: return render_template("server_error.html", errore=errore_db)
        
        

    if session.get('brute_force_data_blocco'):
      if (datetime.datetime.now() - (session["brute_force_data_blocco"] + datetime.timedelta(seconds=session["brute_force_tempo_blocco"]))).total_seconds() >= 0:
        # tempo punizione terminato
        session["brute_force_count"] = 1
        session["blocco_password"] = False
        session.pop('brute_force_data_blocco')

        error = f'Hai solo {NUM_MAX_TENATIVI_FALLITI_PASSWORD-session["brute_force_count"]} tentativi prima di essere di nuovo bloccato'
        timer = None
      else:
        error = 'Sei stato bloccato!'
        timer = int(abs((datetime.datetime.now() - (session["brute_force_data_blocco"] + datetime.timedelta(seconds=session["brute_force_tempo_blocco"]))).total_seconds()))


    return render_template("login.html", error=error, timer=timer)


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")

@app.route("/stanza", methods=['GET'])
def stanza():
    if not session.get("user_id"):
        return redirect("/login")
    
    if "id_stanza" in request.args:
        id_stanza = request.args["id_stanza"]
        codice_dis, nome_stanza, errore1 = get_html_lista_dispositivi(id_stanza)
        if errore1 != 'OK': return render_template("stanza.html", error=errore1)
        
        if codice_dis == "":
            codice_dis = """<div class="col-md-3">
            <div class="card card-danger">
              <div class="card-header">
                <h3 class="card-title">Nessun dispositivo trovato per questa stanza!</h3>
              </div>
              <div class="card-body">
                <a href="/" class="small-box-footer">Vedi tutte le stanze</a>
              </div>
              <!-- /.card-body -->
            </div>
            <!-- /.card -->
            </div>"""
        
        utente, errore2 =get_nome_utente_da_id(session["user_id"])

        if errore2 == "OK":
          return render_template("stanza.html", utente=utente, codice_dispositivi=codice_dis, id_stanza=id_stanza, opzione_admin=session["opzione_admin"], nome_stanza=nome_stanza)
        else: return render_template("server_error.html", errore_2=errore2)
    return redirect("/")

@app.route("/dispositivo", methods=['GET', 'POST'])
def dispositivo():
    if not session.get("user_id"):
        return redirect("/login")
    
    
    if "id_dispositivo" in request.args:
      errore1 = None
      if "tipo_post" in request.form: # in caso ci fossero più richieste post
        if request.form["tipo_post"] == "cambia_stato":
          if 'stato_attuale' in request.form:
            errore1, errore_1_db = cambia_stato(request.form["stato_attuale"], request.args["id_dispositivo"], session["user_id"])

            if errore_1_db != "OK": return render_template("server_error.html", errore=errore_1_db) 

            return "cambio stato avvenuto"
        
      _ , id_stanza, nome, errore2, errore_2_db, _ = get_informazioni_dispositivo(request.args["id_dispositivo"])
      if errore_2_db != "OK": return render_template("server_error.html", errore=errore_2_db) 
      if errore2 == "OK":
        utente, errore3 =get_nome_utente_da_id(session["user_id"])
        if errore3 == 'OK':
          if request.args["id_dispositivo"].isnumeric():
            porta = next_free_port()
            thread_websocket= MyWsServerDispositivo('0.0.0.0', porta, int(request.args["id_dispositivo"]))
            thread_websocket.start()
            return render_template("dispositivo.html", utente=utente, nome_dispositivo=nome, ip=extract_ip(), opzione_admin=session["opzione_admin"], porta=porta, id_dispositivo=request.args["id_dispositivo"], id_stanza=id_stanza)
          else: return render_template("server_error.html", errore="id dispositivo non valido!")
        else:
          # mettere il render template con l'errore
          return render_template("server_error.html", errore=errore3)
      else:
        html_errore = f"""<div class="col-md-3">
          <div class="card card-danger">
            <div class="card-header">
              <h3 class="card-title">{errore2}</h3>
            </div>    
          """
        if errore1 != "OK" and errore1 != None:
          html_errore += f"""
          <div class="card-header">
              <h3 class="card-title">{errore1}</h3>
            </div>
          """


        html_errore += """
        <div class="card-body">
              <a href="/" class="small-box-footer">Vedi tutte le stanze</a>
            </div>
            <!-- /.card-body -->
          </div>
          <!-- /.card -->
          </div> 
        """

        utente, errore4 = get_nome_utente_da_id(session["user_id"])
        if errore4 == 'OK':
          return render_template("dispositivo.html", utente=utente, errore_2=html_errore, opzione_admin=session["opzione_admin"])
        else:
          # mettere il render template con l'errore
          return render_template("server_error.html", errore=errore4) 

    return redirect("/")





@app.route("/cambia_password", methods=['GET', 'POST'])
def cambia_password():
    if not session.get("user_id"):
        return redirect("/login")

      
    errore = None

    if request.method == "POST":
      stato_operazione = valuta_sicurezza_password(request.form['password'], request.form['conferma_password'])
      if stato_operazione == 'OK':
        stato_operazione = cambia_password_utente(session["user_id"], request.form['password'])
      else: errore = stato_operazione

      if stato_operazione == "OK":
        session.pop("user_id")
        return redirect("/")
      else: errore = stato_operazione 

    return render_template("cambia_password.html", error=errore)

@app.route("/cambia_nome", methods=['GET', 'POST'])
def cambia_nome():
    if not session.get("user_id"):
        return redirect("/login")

      
    errore = None

    if request.method == "POST":
      stato_operazione = valuta_correttezza_nome(request.form['nome'], request.form['conferma_nome'])
      if stato_operazione == 'OK':
        stato_operazione = cambia_nome_utente(session["user_id"], request.form['nome'])
      else: errore = stato_operazione

      if stato_operazione == "OK":
        session.pop("user_id")
        return redirect("/")
      else: errore = stato_operazione 

    return render_template("cambia_nome.html", error=errore)


@app.route("/analizza_consumi", methods=["GET", "POST"])
def analizza_consumi():

  if not session.get("user_id"):
        return redirect("/login")

  if "id_stanza" in request.args:
    id_stanza = request.args["id_stanza"]

    utente, errore1 =get_nome_utente_da_id(session["user_id"])
    if errore1 != "OK": return render_template("server_error.html", errore=errore1) 

    porta = next_free_port()

    if id_stanza == "all":
      # tutta casa
      nome = "Casa"
      id_dispositivi = get_informazioni_casa()
    else:
      # stanza specifica
      id_stanza = int(id_stanza)
      nome, descrizione, id_dispositivi, errore2, errore_db_1 = get_informazioni_stanza(id_stanza)
      if errore_db_1 != "OK": return render_template("server_error.html", errore=errore_db_1) 
      if errore2 != "OK":
        html_errore = f"""<div class="col-md-3">
            <div class="card card-danger">
              <div class="card-header">
                <h3 class="card-title">{errore2}</h3>
              </div>
              <div class="card-body">
                <a href="/" class="small-box-footer">Vedi tutte le stanze</a>
              </div>
              <!-- /.card-body -->
            </div>
            <!-- /.card -->
            </div>"""

        return render_template("analizza_consumi.html", utente=utente, errore_2=html_errore, opzione_admin=session["opzione_admin"])
      


    # spegnimento a blocchi
    if "tipo_post" in request.form:
      if request.form["tipo_post"] == "spegni_tutto":
        for id_dis in id_dispositivi:
          consumo, _, _, errore3, errore_db_2, zero_dispositivo = get_informazioni_dispositivo(id_dis)
          if errore3 == "OK" and errore_db_2 == "OK" and consumo != 9999.9:
            if consumo-zero_dispositivo > 0:
              cambia_stato("1", id_dis, session["user_id"])
        return "spegnimento avvenuto con successo"


    thread_websocket= MyWsServerAnalizzaConsumi('0.0.0.0', porta, id_dispositivi)
    thread_websocket.start()

    return render_template("analizza_consumi.html", utente=utente, nome=nome, ip=extract_ip(), opzione_admin=session["opzione_admin"], porta=porta, id_stanza=id_stanza)

  return redirect("/") 



@app.route("/download", methods=["GET"])
def download():
  if not session.get("user_id"):
    return redirect("/login")

  try:
    if "id_stanza" in request.args:
      id_stanza = request.args["id_stanza"]

      if "da" in request.args and "a" in request.args:
        da = request.args["da"].replace("-", "/")
        al = request.args["a"].replace("-", "/")

        #print(da)
        #print(al)

        if len(da.split(" ")) > 1 and da.split(" ")[1] != "":
          da = str(datetime.datetime.strptime(da, '%Y/%m/%d %H:%M:%S'))
        else:
          da = str(datetime.datetime.strptime(da, '%Y/%m/%d'))

        if len(al.split(" ")) > 1 and al.split(" ")[1] != "":
          al = str(datetime.datetime.strptime(al, '%Y/%m/%d %H:%M:%S'))
        else:
          al = str(datetime.datetime.strptime(al, '%Y/%m/%d'))

        
        da = da.replace("/", "-")
        al = al.replace("/", "-")


        dati = []

        if id_stanza == "all":
          dati=[da, al]
          query = "SELECT consumi.id, consumi.id_dispositivo, consumi.data_ora, consumi.consumo, stanze.id, stanze.nome, dispositivi.nome FROM consumi,stanze,dispositivi WHERE consumi.data_ora >= %s AND consumi.data_ora <= %s AND consumi.id_dispositivo = dispositivi.id AND dispositivi.id_stanza = stanze.id AND consumi.consumo != 9999.9"
          
        else:
          if "id_dispositivo" in request.args:
            dati=[da, al]
            id_dispositivo = request.args["id_dispositivo"]

            if id_dispositivo == "all":
              query = "SELECT consumi.id, consumi.id_dispositivo, consumi.data_ora, consumi.consumo, stanze.id, stanze.nome, dispositivi.nome FROM consumi,stanze,dispositivi WHERE consumi.data_ora >= %s AND consumi.data_ora <= %s AND consumi.id_dispositivo = dispositivi.id AND dispositivi.id_stanza = stanze.id AND stanze.id = %s AND consumi.consumo != 9999.9"
              dati.append(int(id_stanza))
            else:
              query = "SELECT consumi.id, consumi.id_dispositivo, consumi.data_ora, consumi.consumo, stanze.id, stanze.nome, dispositivi.nome FROM consumi, stanze, dispositivi WHERE consumi.data_ora >= %s AND consumi.data_ora <= %s AND consumi.id_dispositivo = %s AND consumi.id_dispositivo = dispositivi.id AND dispositivi.id_stanza = stanze.id  AND stanze.id = %s AND consumi.consumo != 9999.9"
              dati.append(int(id_dispositivo))
              dati.append(int(id_stanza))
      else:

        if id_stanza == "all":
            query = "SELECT consumi.id, consumi.id_dispositivo, consumi.data_ora, consumi.consumo, stanze.id, stanze.nome, dispositivi.nome FROM consumi,stanze,dispositivi WHERE consumi.id_dispositivo = dispositivi.id AND dispositivi.id_stanza = stanze.id AND consumi.consumo != 9999.9"
            dati = None
            
        else:
          if "id_dispositivo" in request.args:
            id_dispositivo = request.args["id_dispositivo"]

            if id_dispositivo == "all":
              query = "SELECT consumi.id, consumi.id_dispositivo, consumi.data_ora, consumi.consumo, stanze.id, stanze.nome, dispositivi.nome FROM consumi,stanze,dispositivi WHERE consumi.id_dispositivo = dispositivi.id AND dispositivi.id_stanza = stanze.id AND stanze.id = %s AND consumi.consumo != 9999.9"
              dati = [int(id_stanza)]
            else:
              query = "SELECT consumi.id, consumi.id_dispositivo, consumi.data_ora, consumi.consumo, stanze.id, stanze.nome, dispositivi.nome FROM consumi,stanze,dispositivi WHERE consumi.id_dispositivo = %s AND consumi.id_dispositivo = dispositivi.id AND dispositivi.id_stanza = stanze.id AND stanze.id = %s AND consumi.consumo != 9999.9"
              dati = [int(id_dispositivo), int(id_stanza)]

      #print(query)

      con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
      cur = con.cursor()
      cur.execute(query, dati)
      output = cur.fetchall()
      con.close()

      if len(output) == 0:
        output = {}

      #print(output)

      return jsonify(pd.DataFrame(output).to_dict())

  except:
    try: con.close()
    except: pass

  return render_template("server_error.html", errore="Errore nel download") 


@app.route("/admin", methods=["GET", "POST"])
def admin():
  risultato = None
  query = ""

  if not session.get("user_id"):
    return redirect("/login")

  try:
    if session['grado_amministrazione'] == "amministratore":
      if request.method == "POST":
        if "CONFERMA" in request.form:
          query = request.form["query"]
          con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
          cur = con.cursor()
          cur.execute(query)
          output = cur.fetchall()
          con.commit()
          con.close()

          session["output_last_query"] = pd.DataFrame(output).to_dict()

          risultato = ""

          if len(output) > 0:
            for row in output:
              risultato += "<tr>"
              for col in row:
                risultato += f"<td>{col}</td>"
              risultato += "</tr>"
          else:
            risultato = "<tr><td>Nessun output</td></tr>"

        else:
          return jsonify(session["output_last_query"])

    else:
      return render_template("server_error.html", errore="Utente non registrato come ADMIN") 


  except pymysql.Error as err:
    try: con.close()
    except: pass
    risultato = f"<tr><td class='text-danger'>{err}</td></tr>"
    
  
  return render_template("admin.html", risultato=risultato, query=query, utente="admin")

"""*******************FUNZIONI****************************"""
  
def validate(username, password, indirizzo_ip):

    errore = "OK"
    completion = None
    grado_amministrazione = None
    esito = "NEGATIVO"
    data_ora = str(datetime.datetime.now()).split('.')[0]
  
    try:
      con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
      cur = con.cursor()
      cur.execute("SELECT * FROM utenti")
      rows = cur.fetchall()
      for row in rows:
          dbUser = row[1]
          dbPass = row[2]
          if dbUser == username:
              if dbPass == password:
                  esito = "POSITIVO"
                  completion = int(row[0])
                  grado_amministrazione = row[3]
                  
                  cur.execute("INSERT INTO log_accessi (username, data_ora_accesso, esito, id_utente, indirizzo_ip) VALUES (%s, %s, %s, %s, %s)", [username, data_ora, esito, completion, indirizzo_ip])
                
      if esito == "NEGATIVO": 
        cur.execute("INSERT INTO log_accessi (username, data_ora_accesso, esito, indirizzo_ip) VALUES (%s, %s, %s, %s)", [username, data_ora, esito, indirizzo_ip])


      con.commit()
      con.close()
    except:
      try: con.close()
      except: pass
      errore = "Errore database"
  
    return completion, errore, grado_amministrazione


def get_html_lista_stanze():

  errore = "OK"
  codice_html = ""
  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM stanze")
    stanze = cur.fetchall()
    con.close()

    for id_stanza, stanza in enumerate(stanze):
        codice_html += html_stanze.replace("ID_STANZA", str(stanza[0])).replace("NOME_PROPRIETARIO", stanza[1]).replace("DESCRIZIONE", stanza[2]).replace("ICONA_SCELTA", np.random.choice(opzioni_icone_stanze)).replace("COLORE_STANZA", opzioni_colore_stanze[id_stanza%2])

    
  except:
    try: con.close()
    except: pass
    errore = "Errore database"

  return codice_html, errore

def get_nome_utente_da_id(id_utente):
  errore = "OK"
  utente = None
  try:
    
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM utenti WHERE id = %s", [id_utente])
    utente = cur.fetchall()[0][1]
    con.close()

  except:
    try: con.close()
    except: pass
    errore = "Errore database"
  
  return utente, errore

def get_html_lista_dispositivi(id_stanza):
  errore = "OK"
  codice_html = ""
  nome_stanza = ""
  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT nome FROM stanze WHERE id = %s", [id_stanza])
    output_nome = cur.fetchall()
    if len(output_nome)>0:
      nome_stanza = output_nome[0][0]

    cur.execute("SELECT * FROM dispositivi WHERE id_stanza = %s", [id_stanza])
    dispositivi = cur.fetchall()
    for id_dis, dispositivo in enumerate(dispositivi):
      codice_html += html_dispositivi.replace("ID_DISPOSITIVO", str(dispositivo[0])).replace("DESCRIZIONE", dispositivo[3]).replace("ICONA_SCELTA", np.random.choice(opzioni_icone_stanze)).replace("COLORE_DISPOSITIVO", opzioni_colore_stanze[id_dis%2]).replace("NOME_DISPOSITIVO", dispositivo[2])
    
    con.close()

  except: 
      try: con.close()
      except: pass
      errore = "Errore database"
  
  return codice_html, nome_stanza, errore


def get_informazioni_casa():
  errore = "OK"
  id_dispositivi = []

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT id FROM stanze")
    info_stanze = cur.fetchall()
    
    if len(info_stanze) > 0:
      for id_stanza in info_stanze:
        _, _, id_dis, errore, errore_db = get_informazioni_stanza(id_stanza[0])
        if errore == "OK" and errore_db == "OK":
          id_dispositivi += id_dis
    else:
      errore = "Errore database"

    con.close()
       
  except:
    try: con.close()
    except: pass
    errore = "Errore database"

  return id_dispositivi



def get_informazioni_stanza(id_stanza):
  descrizione = None
  nome = None
  id_dispositivi = []
  errore_db = "OK"
  errore = "OK"

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM stanze WHERE id = %s", [id_stanza])
    info_stanza = cur.fetchall()
    
    if len(info_stanza) > 0:
      info_stanza = info_stanza[0]
      nome = info_stanza[1]
      descrizione = info_stanza[2]


      cur.execute("SELECT dispositivi.id FROM stanze,dispositivi WHERE dispositivi.id_stanza = stanze.id AND stanze.id = %s", [id_stanza])
      elenco_dispositivi = cur.fetchall()
      
      if len(elenco_dispositivi) > 0:
        for id_dis in elenco_dispositivi:
          id_dispositivi.append(id_dis[0])

    else:
      errore = "Stanza non presente sul database"

    con.close()
        
  except:
    try: con.close()
    except: pass
    errore_db = "Errore database"

  return nome, descrizione, id_dispositivi, errore, errore_db



def get_informazioni_dispositivo(id_dispositivo):

  descrizione = None
  consumo = None
  errore_db = "OK"
  errore = "OK"
  zero_dispositivo = 0
  id_stanza = 0

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM dispositivi WHERE id = %s", [id_dispositivo])
    info_dispositivo = cur.fetchall()
    con.close()
    if len(info_dispositivo) > 0:
      info_dispositivo = info_dispositivo[0]
      id_stanza = info_dispositivo[1]
      tecnologia_lettura_dati = info_dispositivo[5]
      valore_tecn_utilizzata = info_dispositivo[6]
      zero_dispositivo = info_dispositivo[7]
      try:
        consumo = sendMessage("INPUT", tecnologia_lettura_dati, valore_tecn_utilizzata)
        descrizione = info_dispositivo[3]

      except:
        errore_db = "Errore lettura"

    else:
      errore = "Dispositivo non presente sul database"
       
  except:
    try: con.close()
    except: pass
    errore_db = "Errore database"

  return consumo, id_stanza, descrizione, errore, errore_db, zero_dispositivo

def cambia_stato(stato_attuale, id_dispositivo, id_utente):
  errore_db = "OK"
  errore = "OK"

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM dispositivi WHERE id = %s", [id_dispositivo])
    info_dispositivo = cur.fetchall()
    con.close()
    
    if len(info_dispositivo) > 0:
      info_dispositivo = info_dispositivo[0]
      pinout = info_dispositivo[4]
      try:
        if stato_attuale == "1": sendMessage("OUTPUT", pinout, "0")
        else: sendMessage("OUTPUT", pinout, "1")

        salva_log_comandi(id_utente, f'accensione/spegnimento dispositivo n. {id_dispositivo}')

      except: errore = "Problema con il cambiamento dello stato!"
    
    else:
      errore = "Dispositivo non presente sul database"
      

  except: 
    errore_db = "Errore database"
    try: con.close()
    except: pass
  return errore, errore_db



def salva_log_comandi(id_utente, messaggio):
  try:
    data_ora = str(datetime.datetime.now()).split('.')[0]

    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("INSERT INTO log_comandi (id_utente, data_ora_comando, descrizione) VALUES (%s, %s, %s)", [id_utente, data_ora, messaggio])
    con.commit()
    con.close()
  except:
    try: con.close()
    except:pass


def cambia_nome_utente(id_utente, nuovo_nome_utente):
  errore = "OK"

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("UPDATE utenti SET username = %s WHERE id = %s", [nuovo_nome_utente, id_utente])
    con.commit()
    con.close()

    salva_log_comandi(id_utente, f'cambio il nome utente n. {id_utente}')
     

  except: 
    try: con.close()
    except: pass
    errore = "Errore database"
  return errore

def cambia_password_utente(id_utente, nuova_password_utente):
  errore = "OK"
  nuova_password_utente = nuova_password_utente.replace(' ', '')

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("UPDATE utenti SET password = %s WHERE id = %s", [nuova_password_utente, id_utente])
    con.commit()
    con.close()

    salva_log_comandi(id_utente, f'cambio la password utente n. {id_utente}')    

  except: 
    try: con.close()
    except: pass
    errore = "Errore database"
  return errore


def valuta_sicurezza_password(password, conferma_password):
  password = password.replace(' ', '')
  if password == '':
      return 'Inserire una password'
  elif len(password) < MIN_LUNGHEZZA_PASSWORD:
      return f"La tua password è troppo corta (min lunghezza = {MIN_LUNGHEZZA_PASSWORD})"
  elif len(password) > MAX_LUNGHEZZA_PASSWORD:
    return f"La tua password è troppo lunga (max lunghezza = {MAX_LUNGHEZZA_PASSWORD})"
  elif re.search('[0-9]',password) is None:
      return 'La tua password non contiene numeri'
  elif re.search('[A-Z]',password) is None: 
      return "La tua password non contiene lettere maiuscole"
  elif re.search('[a-z]', password) is None:
      return 'La tua password non contiene lettere minuscole'
  elif password != conferma_password:
      return 'Le password non corrispondono'
  else:
      return 'OK'


def valuta_correttezza_nome(nome, conferma_nome):
  nome = nome.replace(' ', '')
  if nome == '':
    return 'Inserire un nome'
  elif len(nome) < MIN_LUNGHEZZA_USERNAME:
    return f"Il tuo username è troppo corto (min lunghezza = {MIN_LUNGHEZZA_USERNAME})"
  elif len(nome) > MAX_LUNGHEZZA_USERNAME:
    return f"Il tuo username è troppo lungo (max lunghezza = {MAX_LUNGHEZZA_PASSWORD})"
  elif nome != conferma_nome:
    return 'I nomi non coincidono'
  else:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM utenti WHERE username = %s", [nome])
    n_username = len(cur.fetchall())
    con.close()
    if n_username == 0:
      return 'OK'
    return 'Nome utente non disponibile'
  
def verifica_brute_force(username, indirizzo_ip):
  errore = "OK"
  data_ora = str(datetime.datetime.now()).split(":")[0]+":00:00"

  #print(data_ora)

  try:
    con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
    cur = con.cursor()
    cur.execute("SELECT * FROM log_accessi WHERE log_accessi.data_ora_accesso > %s AND log_accessi.esito = 'NEGATIVO' AND indirizzo_ip = %s", [data_ora, indirizzo_ip])
    n_errori = cur.fetchall()
    print(n_errori)
    n_errori = len(n_errori)
    con.close()
    if  n_errori >= N_TENTATIVI_MESSAGGIO:
      telegram_bot_sendtext(f"ATTENZIONE!\nQualcuno nell'ultima ora ha provato ad accedere più di {N_TENTATIVI_MESSAGGIO} volte.\nDi seguito maggiori informazioni:\nUtente: {username} \nIndirizzo IP: {indirizzo_ip}")
      #print("**********MESSAGGI INVIATO**********")

  except:
    try: con.close()
    except: pass
    salvataggio_errore("Errore database")
  
  return errore

def telegram_bot_sendtext(bot_message):
  try:
    bot_token = '...'
    bot_chatID = '...'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)
  except:
    salvataggio_errore("Errore di rete! Impossibile inviare il messaggio su telegram")


def salvataggio_errore(errore):
  with open(f"{dir_path}/log.txt", "a") as f:
      f.write(f"{datetime.datetime.now()}: {errore}\n")


def next_free_port(port=MIN_PORT, max_port=MAX_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port <= max_port:
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError('no free ports')

class LettoreConsumi(thr.Thread):
    def _init_(self):
        thr.Thread._init_(self)
        
    def run(self):
        while True:
          try:
            con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
            cur = con.cursor()
            cur.execute("SELECT id FROM dispositivi")
            lista_dispositivi = cur.fetchall()
            con.close()
            data_ora = str(datetime.datetime.now()).split('.')[0]
            for dispositivo in lista_dispositivi:
              dispositivo = dispositivo[0]
              consumo, _, _, errore, errore_db, _ = get_informazioni_dispositivo(dispositivo)
              if errore == "OK" and errore_db == "OK":
                con = pymysql.connect(host=hostname,user=dbusername,db=dbname,password=dbpassword)
                cur = con.cursor()
                cur.execute("INSERT INTO consumi (id_dispositivo, data_ora, consumo) VALUES (%s, %s, %s)", [dispositivo, data_ora, consumo])
                con.commit()
                con.close()
          except:
            try: con.close()
            except: pass
            salvataggio_errore("Errore nel salvataggio dei consumi sul database")

        
          sleep(TEMPO_LETTURA_CONSUMI)


def sendMessage(IO, dato1, dato2):
  global arduino
  with lock_arduino:
    try:
      arduino.write(f"{IO}#{dato1}#{dato2}!".encode())

      stringa = ""
      last_char = ""
      while last_char != "-":
        last_char = arduino.read().decode()
        if last_char != "-": 
          if last_char != "\n" and last_char != "\r": stringa += last_char
      

      if IO == "INPUT":
        return float(stringa)
      else:
        return None
    except:
      try: arduino.close()
      except: pass
      try:
        arduino = serial.Serial('/dev/ttyACM0',9600)
        sleep(5)
      except: pass

      telegram_bot_sendtext("Errore arduino")
      
      if IO == "INPUT":
        return 9999.9
      else:
        return None


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP




# CREAZIONE WEBSOCKET #
class MyWsServerDispositivo(thr.Thread):
    def __init__(self, address, port, id_dispositivo):
        super().__init__()
        self.port = port
        self.address = address
        self.id_dispositivo = id_dispositivo

    def run(self):
        #print(f"°°°°°°°WEB SOCKET PARTITO°°°°°°°°")
        loop = asyncio.new_event_loop()
        ws_server = websockets.serve(self.invia_dati_aggiornamento, self.address, self.port,
                                     ping_timeout=None, ping_interval=None, loop=loop)
        loop.run_until_complete(ws_server)
        loop.run_forever()

    async def invia_dati_aggiornamento(self, websocket, path):
        while True:
          #è stato inserito un try except perché nel momento in cui si aggiorna la pagina
          #e l'invio dei dati non è più richiesto su questa porta, genera un'eccezione
          #che viene gestita usendo dal while true
          try:
            consumo, _, _, errore, errore_db, zero_dispositivo = get_informazioni_dispositivo(self.id_dispositivo)
            if errore == "OK" and errore_db == "OK" and consumo != 9999.9:
              if consumo-zero_dispositivo > 0:
                await websocket.send(f"stato#ON#consumo#{consumo}")
              else: await websocket.send(f"stato#OFF#consumo#{consumo}")
          except:
            break

          sleep(1)


class MyWsServerAnalizzaConsumi(thr.Thread):
    def __init__(self, address, port, lista_dispositivi):
        super().__init__()
        self.port = port
        self.address = address
        self.lista_dispositivi = lista_dispositivi

    def run(self):
        #print(f"°°°°°°°WEB SOCKET PARTITO°°°°°°°°")
        loop = asyncio.new_event_loop()
        ws_server = websockets.serve(self.invia_dati_aggiornamento, self.address, self.port,
                                     ping_timeout=None, ping_interval=None, loop=loop)
        loop.run_until_complete(ws_server)
        loop.run_forever()

    async def invia_dati_aggiornamento(self, websocket, path):
        while True:
          #è stato inserito un try except perché nel momento in cui si aggiorna la pagina
          #e l'invio dei dati non è più richiesto su questa porta, genera un'eccezione
          #che viene gestita usendo dal while true
          try:
            consumi =[]
            for id_dispositivo in self.lista_dispositivi:
              consumo, _, _, errore, errore_db, _ = get_informazioni_dispositivo(id_dispositivo)
              if errore == "OK" and errore_db == "OK" and consumo != 9999.9:
                consumi.append(consumo)

            await websocket.send(f"consumi#{consumi}")
              
          except:
            break

          sleep(1)

if __name__ == "__main__":
    lettore_consumi = LettoreConsumi()
    lettore_consumi.start()

    app.run(port=80, host="127.0.0.1")
