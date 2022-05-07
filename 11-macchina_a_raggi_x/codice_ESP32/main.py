import socket
from time import sleep, time
import _thread
import machine

rele_filamento = machine.Pin(26, machine.Pin.OUT)
rele_alta_tensione = machine.Pin(25, machine.Pin.OUT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(2)


pagina = 'HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n<html><body><form method="get" action="/"><table border=1><tr><td>Tempo durata macchina</td><td><input type="number" min=-1 value="-1" name="tempo"></td></tr><tr><td>Accendi macchina</td><td><input type="submit" name="on" value="ON"></td></tr><tr><td>Spegni macchina</td><td><input type="submit" name="off" value="OFF"></td></tr><tr><td>Risposta</td><td>RISPOSTA</td></tr></table></form></body></html>'

thread_attivo = _thread.allocate_lock()
thread_kill = _thread.allocate_lock()
thread_killato = _thread.allocate_lock()

def accensione(tempo):
    if tempo > 0:
        # accensione pin
        rele_filamento.value(1)
        sleep(3)
        rele_alta_tensione.value(1)
        
        tempo_iniziale = int(time())
        while int(time())-tempo_iniziale < tempo:
            #print(int(tempo_iniziale+tempo))
            
            if thread_kill.locked():
                break

            
        if thread_kill.locked():
            thread_killato.acquire()
 
        # spegnimento pin
        
        rele_filamento.value(0)
        rele_alta_tensione.value(0)

    thread_attivo.release()
    print("Fine thread")


running = True
while running:
  conn, addr = s.accept()
  #print('Got a connection from '+str(addr))
  request = conn.recv(1024).decode()
  #print('Content = '+request)
  
  # gestire il doppio invio
  
  # -- API -- #
  pos_tempo = request.find('/?tempo=')
  pos_on = request.find('&on=ON')
  pos_off = request.find('&off=OFF')
  
  response = "ERRORE"
  if pos_tempo != -1 and (pos_on != -1 or pos_off != -1):
      if pos_off != -1:
          # tasto off premuto, metto a off i pin e killo thread
          if thread_attivo.locked():
            thread_kill.acquire()
            
            while not thread_killato.locked(): pass
            
            thread_killato.release()
            thread_kill.release()

          response = "SPEGNIMENTO"


      elif pos_on != -1:
          if not thread_attivo.locked():
            # tasto on premuto, leggo il tempo e metto on i pin e creo thread
            tempo = float(request[pos_tempo+8:pos_on])
            print("Tempo ricevuto "+str(tempo))
            thr = _thread.start_new_thread(accensione, (tempo,))
            thread_attivo.acquire()
            response = "ACCENSIONE PER "+str(tempo)+" SECONDI"
          else: response = "THREAD GIÀ IN ESECUZIONE"


  conn.sendall(pagina.replace("RISPOSTA", response))
  conn.close()
    
  # -- FINE API -- #



