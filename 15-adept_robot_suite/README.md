
# Documentazione e consigli di utilizzo del software

Il software da noi realizzato è stato pensato per poter essere utilizzato da qualunque tipo di utente. Non è richiesta alcuna conoscenza del linguaggio utilizzato dal robot (V+), fatta eccezione per casi di errore o problematiche illustrate seguentemente.

## Procedura di installazione
Di seguito sono illustrate le procedure di installazione del web server e della configurazione di una nuova cella.


### *Configurazione nuova cella*
Per configurare una nuova cella in modo che si possa utilizzare in maniera completa questo software è necessario effettuare la seguente procedura:

 1. Connettersi alla macchina (*nel caso in cui non si conosca l'indirizzo IP, oppure quello riportato nella pagina di connessione non fosse corretto, utilizzare prima la procedura **cambio IP*** ).
 2. Utilizzando il pulsante *upload* caricare i file *main.v2, get_pos.v2, mv_rob.v2* e *info.v2* che si possono trovare all'interno del web server nella cartella *programs*.
 3.  In seguito è possibile utilizzare il software, tenendo presente che fino a quando non sarà effettuata una calibrazione, le funzioni che comportano un movimento del robot saranno limitate.
 

### *Installazione Web Server*
**Prerequisiti:**

 - Versione di python >= 3.8
 -  PIP
 **Librerie da installare**
 Di seguito sono riportate le librerie da installare:
	 >  pandas: `pip install pandas`
	 >  Flask: `pip install flask`
	 >  websockets: `pip install websockets`
	 >  requests: `pip install requests`
	 
**Esecuzione del python**
Per avviare il web server è necessario posizionarsi nella cartella del programma e digitare il seguente comando:
>Windows: **`python main.py`**

>Linux/Mac OS: **`sudo python main.py`**

## Procedure aggiuntive implementate
Di seguito sono riportate alcune procedure particolari implementate in questo software.

### *Avvio di una cella senza l'autoboot*
È possibile che, attraverso il relativo pin all'interno della cella, sia stato disabilitato l'autoboot. Di conseguenza al momento della connessione comparirà una *shell* di colore nero che permetterà di scegliere alcune configurazioni.
Nel caso si decida di caricare il sistema operativo dal server TFTP la cartella in cui si trova è la seguente:
>Windows: `\operating_system\cella{n_cella}\sistema_operativo\`

>Linux/Mac OS: `/operating_system/cella{n_cella}/sistema_operativo/`

---

### *Implementazione dell'applicativo Adept Network Controller*
Al momento della connessione ad una cella è presente un'altra opzione che prende il nome di *cambio ip*. Questa impostazione permette di modificare i seguenti parametri della cella:

- indirizzo IP
- subnet mask (*default 255.255.0.0*)
- AdeptWindows PC as default interface
- Enable autostart Auto.v2
- This PC is default NFS server
- Re-start adept controller
---

## Pagine presenti
Le pagine che sono presenti all'interno di questo software sono le seguenti.

### *Home page*
La *home page* del robot presenta la seguente interfaccia.

Nella parte destra dello schermo sono presenti due pulsanti che permettono di avviare e fermare la produzione di tutte le celle simultaneamente. Inoltre è presente anche il pulsante di caricamento dei file csv. Quest’ultima funzione viene utilizzata nel caso si volesse caricare il documento contenente tutte le coordinate in cui posizionare i componenti sulla scheda.

Il file csv può avere qualunque nome, ma all’interno devono essere presenti le seguenti colonne:
| Nome | Descrizione | 
|--|--|
| `N-cella` | È la cella che dovrà poi inserire il componente |
| `N-pinza` | È la posizione in cui si trova la pinza desiderata nella cella *(1-10)*|
| `N-alimentatore` |È la posizione in cui si trova l’alimentatore desiderato nella cella *(1-10)*|
| `Center-X(mm)` |È la coordinata X in millimetri della posizione desiderata a partire dal punto zero della scheda.|
| `Center-Y(mm)` |È la coordinata Y in millimetri della posizione desiderata a partire dal punto zero della scheda.|
| `Rotation` |È la rotazione (da -180° a 180°) desiderata a partire dal punto zero della scheda.|
*L’ordine dei campi non è rilevante.*

Si vuole precisare che non è possibile premere il pulsante *esegui* senza prima aver caricato un file e che all’interno di ogni documento caricato possono essere presenti solo le celle attive al momento dell’upload.

Lo stato delle celle ed eventualmente lo stato della produzione è possibile visionarlo nella tabella presente al centro dello schermo, mentre il tempo di esecuzione di una produzione è presente in alto a sinistra.

In caso di errore di una qualunque procedura, comparirà un alert nella pagina che spiegherà cosa è andato storto e il comportamento che l’utente dovrebbe adottare.

---
### *Pagina di connessione*
La pagina di connessione del robot presenta la seguente interfaccia.

All’interno di questa pagina si possono effettuare solamente due azioni: la connessione al robot oppure il cambio di indirizzo IP.

Nel primo caso il software tenterà di connettersi ad un robot utilizzando l’indirizzo IP e la porta sopra riportati (ad esempio il *172.16.110.124* e la porta *1999*).  
Nel secondo caso invece (seguendo la procedura) sarà possibile cambiare alcune opzioni di configurazioni del robot (Per maggiori informazioni visualizzare *Implementazione dell'applicativo Adept Network Controller* nella sezione **Procedure aggiuntive implementate**).

---

### *Pagina di controllo del robot*

La pagina di controllo del robot presenta la seguente interfaccia e può essere divisa in alcune sezioni:

1.  **Terminale e input per esso**
Nella parte sinistra dello schermo è presente il terminale del robot, sul quale si possono visualizzare gli output che restituisce. Se si volesse scrivere un qualunque comando utilizzando la shell V+, è possibile utilizzando la barra dei comandi sottostante.
Ci sono alcune combinazioni di tasti che non sono supportate, mentre altre, come il CTRL C e l’ESC, è possibile utilizzarle premendo i relativi pulsanti presenti a fianco della barra dei comandi.
È inoltre possibile “ripulire” la shell con l’apposito pulsante, CLEAR.

2.  **Pulsanti generali**
Nella parte superiore destra dello schermo sono presenti il pulsante di DISCONNESSIONE e il pulsante di CALIBRAZIONE.

3.  **Gestione del programma**
    Nella parte destra dello schermo sono presenti i pulsanti per poter caricare e scaricare un file. Il protocollo utilizzato è il TFTP.

4.  **Gestione della produzione**
    Nella parte destra dello schermo sono presenti due pulsanti che permettono di avviare e fermare la produzione.
Inoltre è presente anche il pulsante di caricamento dei file csv. Quest’ultima funzione viene utilizzata nel caso si volesse caricare il documento contenente tutte le coordinate in cui posizionare i componenti sulla scheda.
Il file csv può avere qualunque nome, ma all’interno devono essere presenti le seguenti colonne:

| Nome | Descrizione | 
|--|--|
| `N-pinza` | È la posizione in cui si trova la pinza desiderata nella cella *(1-10)*|
| `N-alimentatore` |È la posizione in cui si trova l’alimentatore desiderato nella cella *(1-10)*|
| `Center-X(mm)` |È la coordinata X in millimetri della posizione desiderata a partire dal punto zero della scheda.|
| `Center-Y(mm)` |È la coordinata Y in millimetri della posizione desiderata a partire dal punto zero della scheda.|
| `Rotation` |È la rotazione (da -180° a 180°) desiderata a partire dal punto zero della scheda.|
*L’ordine dei campi non è rilevante.*

5.  **Gestione delle informazioni**
    Nella parte destra dello schermo sono presenti due pulsanti che permettono di avviare e fermare un programma che fornisce delle informazioni sul robot. Questa parte si occupa di evidenziare in una tabella quali siano i pin di input del robot al momento attivi e di disegnare in appositi canvas, presenti nella parte inferiore sinistra dello schermo, la posizione attuale degli assi del robot.
Inoltre è presente un ulteriore sezione che permette di attivare e disattivare alcuni pin di output.

In caso di errore di una qualunque procedura, comparirà un *alert* nella pagina che spiegherà cosa è andato storto e il comportamento che l’utente dovrebbe adottare.

---

### *Pagina di calibrazione*

  **Descrizione**
All’interno di questa pagina è presente una tabella che è una rappresentazione della cella, con tutte le postazioni disponibili. Nel momento in cui si effettua una calibrazione è possibile attivare o disattivare un alimentatore, una pinza e cambiare qualunque parametro precedentemente impostato. Per effettuare queste procedure bisognerà premere il pulsante corretto, effettuare le modifiche e salvare.
    
Inoltre, per facilitare l’utente, nel caso sia necessario ottenere delle misure di una determinata postazione o di verificare che queste siano corrette, sono stati implementati due pulsanti: il vai qui che muove il robot nella posizione indicata e il memorizza che riporta all’interno dei campi le coordinate attuali del robot.

Nella zona in alto a destra sono presenti i pulsanti *PRENDI CAL* e *POSA CAL* che permettono rispettivamente di prendere e posare la punta di calibrazione (ovviamente se quest’ultima è stata correttamente memorizzata all’interno di una della postazioni).

In caso di errore di una qualunque procedura, comparirà un *alert* nella pagina che spiegherà cosa è andato storto e il comportamento che l’utente dovrebbe adottare.

**Informazioni richieste**

Le informazioni che sono richieste all’interno di questa pagina sono:

> **Posizioni del magazzino e lo zero della scheda**
> *All’interno della calibrazione sono presenti il magazzino di destra, il magazzino di sinistra e la posizione zero della scheda.*

| Campo | Descrizione |
|--|--|
| `Descrizione` | Permette di capire all’utente la posizione di cui si sta parlando. |
|`Coordinata X`|La coordinata x del robot quando si trova in quella posizione.|
|`Coordinata Y`|La coordinata y del robot quando si trova in quella posizione.|
|`Coordinata Z`|La coordinata z del robot quando si trova in quella posizione.|
|`Yaw`|La yaw del robot quando si trova in quella posizione *(solitamente corrisponde a 0)*.|
|`Pitch`|La pitch del robot quando si trova in quella posizione *(solitamente corrisponde a 180)*.|
|`Roll`|La roll del robot quando si trova in quella posizione *(è un valore compreso tra -180° e 180°)*.|

---
> **Per ogni alimentatore**

| Campo | Descrizione |
|--|--|
| `Descrizione` | Permette di capire all’utente l’alimentatore di cui si sta parlando e quali componenti possono essere montati. |
|`Tipo alimentatore`|Può essere assiale o radiale.|
|`Coordinata X`|La coordinata x del robot per prendere un componente da quel determinato alimentatore.|
|`Coordinata Y`|La coordinata y del robot per prendere un componente da quel determinato alimentatore.|
|`Coordinata Z`|La coordinata z del robot per prendere un componente da quel determinato alimentatore.|
|`Yaw`|La yaw del robot per prendere un componente da quel determinato alimentatore *(solitamente corrisponde a 0)*.|
|`Pitch`|La pitch del robot per prendere un componente da quel determinato alimentatore *(solitamente corrisponde a 180)*.|
|`Roll`|La roll del robot per prendere un componente da quel determinato alimentatore *(è un valore compreso tra -180° e 180°)*.|

---
> **Per ogni pinza**

| Campo | Descrizione |
|--|--|
| `Descrizione` | Permette di capire all’utente la pinza di cui si sta parlando. |
|`Tipo alimentatore`|Può essere assiale, radiale o di calibrazione.|
|`Coordinata X`|La coordinata x del robot per prendere quella pinza in quella determinata postazione.|
|`Coordinata Y`|La coordinata y del robot per prendere quella pinza in quella determinata postazione.|
|`Coordinata Z`|La coordinata z del robot per prendere quella pinza in quella determinata postazione.|
|`Yaw`|La yaw del robot per prendere quella pinza in quella determinata postazione *(solitamente corrisponde a 0)*.|
|`Pitch`|La pitch del robot per prendere quella pinza in quella determinata postazione *(solitamente corrisponde a 180)*.|
|`Roll`|La roll del robot per prendere quella pinza in quella determinata postazione *(è un valore compreso tra -180° e 180°)*.|
|`Altezza alimentatore`|L’offset sull’asse z presente tra la pinza di calibrazione (con la quale è stata effettuata la misurazione dell’alimentatore) e la pinza con cui effettivamente si prenderà il componente dall’alimentatore.|
|`Altezza inserimento componente`|L’offset presente tra la pinza di calibrazione (con la quale è stata effettuata la misura set zero) e la pinza con cui effettivamente si poserà il componente sulla scheda.|

---

## Consigli utili

Di seguito sono riportati alcuni consigli per un buon utilizzo del *software*:

- Dopo aver acceso una cella, aperto una porta o premuto un pulsante, per poter muovere il robot è necessario dare il comando `ENABLE POWER` sulla *shell*.
- Dopo la disconnessione da una cella attendere circa 10 secondi prima di provare a ricollegarsi
- 
