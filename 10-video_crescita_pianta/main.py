from datetime import *
import logging
import time
from subprocess import Popen, PIPE

i=0

while True:
    try:
        if(int(str(datetime.now()).split(" ")[1].split(":")[1]) % 15 is 0):
           Popen(["fswebcam", "-r", "1280x720", "--no-banner", "img_"+str(i)+".jpeg"], stdout=PIPE, stderr=PIPE)
           time.sleep(20)
           i+=1
    except Exception:
        logging.error("Errore nello scatto della foto")
