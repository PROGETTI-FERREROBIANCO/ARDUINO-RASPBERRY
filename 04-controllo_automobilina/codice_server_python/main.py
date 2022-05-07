import os
import serial
from pyngrok import ngrok
from flask import Flask, request
from signalwire.messaging_response import MessagingResponse
from signalwire.rest import Client as signalwire_client
import socket as sck

HOST = '127.0.0.1'   # indirizzo del server
N_PORTA = 3000      # porta del server

s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)


app = Flask(__name__)

@app.route('/', methods = ['POST'])
def ricevi_dati():
    dati_ricevuti = eval(str(request.form).replace("ImmutableMultiDict", ""))[0][1]
    print(dati_ricevuti)

    s.sendto(dati_ricevuti.encode(), (HOST, N_PORTA))

    return "ok"


def start_ngrok():
    # Set up a tunnel on port 5000 for our Flask object to interact locally
    url = ngrok.connect(5000).public_url
    print(' * Tunnel URL:', url)


# In the previous step, we declared where the tunnel will be opened, however we must start ngrok before a tunnel will be available to open
# This checks your os to see if ngrok is already running and if it is not, ngrok will start
if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        start_ngrok()
    app.run(debug=True)
