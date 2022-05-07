var id_aggiornamento_dati;
var percorso = ""; //più il resto del percorso

/*creo un dizionario dati che contiene come chiave i nomi dei sensori e come valore gli 
ultimi dati richiesti al server*/
var dati = {
    "tutti": "",
    "temperatura": 0,
    "giroscopio": "0#0#0"
};

//Creo un dizionario per le unità di misura
var unita_di_misura = {
    "temperatura" : "°C",
    "temperatura_interna" : "°C",
    "pressione" : "hPa",
    "pioggia" : "%",
    "umidita": "%RH",
    "uv":"",
    "luce":"KLux",
    "aria":"-",
    "giroscopio": "°/s",
    "fulmini":"-",
    "magnetometro": "µT"
}

//creo un dizionario dati che contiene come chiave i nomi dei sensori e come valore i loro canvas
var canvas_sensori = {
    "temperatura": ""
}
/*----------------FUNZIONI PER AGGIORNARE I DATI DELLA TABELLA NELLA PAGINA PRINCIPALE---------------- */
function aggiornaDati() {
    $.ajax({
        url: percorso+"dato/dati_attuali/tutti",
        type: "GET",
        dataType: "json",
        success: function(dati_sensori) {
            dati["tutti"] = dati_sensori;
            aggiornaPagina(dati_sensori);
            
          }
      });
}

function aggiornaPaginaPrincipale(){
    aggiornaDati()
}

function inizializzazionePaginaPrincipale(id_della_stazione_meteorologica, stringa_lista_sensori){
    disegnaBarraOrizzontale(stringa_lista_sensori, id_della_stazione_meteorologica, true);
    calcolaPercorso(id_della_stazione_meteorologica)
    aggiornaPaginaPrincipale();
    id_aggiornamento_dati = setInterval(aggiornaPaginaPrincipale, 10000);
}

function inizializzazionePagineSensori(id_della_stazione_meteorologica, sensore, stringa_lista_sensori){
    disegnaBarraOrizzontale(stringa_lista_sensori, id_della_stazione_meteorologica, false);
    calcolaPercorso(id_della_stazione_meteorologica)
    onLoadSensore(sensore, unita_di_misura[sensore])
}

function aggiornaPagina(dati_sensori){
    paragrafo = document.getElementById("ora_dati");
    tblSensori = document.getElementById("tblSensori");
    tblSensori.innerHTML = "<tr><th class=\"thSensori\">Nome Sensore</th><th class=\"thSensori\">Valore</th></tr>";
    for(const [key, value] of Object.entries(dati_sensori)){
        if(key == "data_ora_stazione"){
            var data_paragrafo = value.split(":");
            if(data_paragrafo[1].length < 2){
                data_paragrafo[1] = "0" + data_paragrafo[1];
            }
            if(data_paragrafo[2].length < 2){
                data_paragrafo[2] = "0" + data_paragrafo[2];
            }
            paragrafo.innerHTML = "Dati aggiornati il "+data_paragrafo[0] + ":" + data_paragrafo[1] + ":" + data_paragrafo[2];
        }
        else{
            tblSensori.innerHTML += "<tr><td class=\"tdSensori\">"+key+"</td><td class=\"tdSensori\">"+value+"  "+unita_di_misura[key]+"</td></tr>";
        }
    }
    tblSensori.innerHTML += ""
}


/*------------------------------------------------------------------------------------------- */


/*---------------------FUNZIONE PER RICAVARE I DATI DI UN SENSORE-------------------------------- */
//Quando carico la pagina di uno dei sensori creo un primo canvas vuoto e chiedo i dati del sensore specifico
function onLoadSensore(sensore, unitaMisura){
    if(sensore != "giroscopio"){
         canvas_sensori[sensore] = new Chart(
    document.getElementById('grafico'),
    );
        ottieniDatoAttuale(sensore);
        opzioneSelezionata(sensore, unitaMisura);
    }
    else{
        ottieniDatiGiroscopio();
        setInterval(ottieniDatiGiroscopio, 10000);
    }
    
}

function ottieniDatiGiroscopio(){
    $.ajax({
        url: percorso+"dato/giroscopio",
        type: "GET",
        dataType: "json",
        success: function(dati_sensori){
            console.log("Aggiornamento in immagine effettuato")
            dati["giroscopio"] = dati_sensori["dato_richiesto"][dati_sensori["dato_richiesto"].length -1];
            document.getElementById("valoreAttualeX").innerHTML = "X: "+dati["giroscopio"].split("#")[0]+"°/s";
            document.getElementById("valoreAttualeY").innerHTML = "Y: "+dati["giroscopio"].split("#")[1]+"°/s";
            document.getElementById("valoreAttualeZ").innerHTML = "Z: "+dati["giroscopio"].split("#")[2]+"°/s";
        }
});
//aggiornaImmagine();
}

//Ottengo i dati del sensore richiesti dal serer e chiamo la funzione per visualizzarli


function ottieniDatiGiornalieri(sensore, unitaMisura){
    console.log(sensore)
    $.ajax({
        url: percorso+"dato/dati_giornalieri/"+sensore,
        type: "GET",
        dataType: "json",
        success: function(dati_sensori) {
            if(sensore != "giroscopio"){
                dati_sensori = eliminaDatiErrore(dati_sensori);
                dati_sensori["data_ora"] = dati_sensori["data_ora"].map(valore => valore.split(" ")[1].split(":")[0]+":"+valore.split(" ")[1].split(":")[1])
                visualizzaDati(sensore, 'Valori '+sensore + "("+unitaMisura+")", unitaMisura, dati_sensori);
            }
          
          }
      });
}

function ottieniDatiMensili(sensore, unitaMisura){
    $.ajax({
        url: percorso+"dato/dati_mensili/"+sensore,
        type: "GET",
        dataType: "json",
        success: function(dati_sensori) {
            if(sensore != "giroscopio"){
                dati_sensori = eliminaDatiErrore(dati_sensori);
                dati_sensori["data_ora"] = dati_sensori["data_ora"].map(valore => valore.split("-")[2]);
                visualizzaDati(sensore, 'Valori '+sensore + "("+unitaMisura+")", unitaMisura, dati_sensori);
                
            }
          
          }
      });
}

function ottieniDatiAnnuali(sensore, unitaMisura){
    $.ajax({
        url: percorso+"dato/dati_annuali/"+sensore,
        type: "GET",
        dataType: "json",
        success: function(dati_sensori) {
            if(sensore != "giroscopio"){
                dati_sensori = eliminaDatiErrore(dati_sensori);
                dati_sensori["data_ora"] = dati_sensori["data_ora"].map(valore => valore.split("-")[1]);
                visualizzaDati(sensore, 'Valori '+sensore + "("+unitaMisura+")", unitaMisura, dati_sensori);   
            }
          
          }
      });
}

function ottieniDatoAttuale(sensore) {
    $.ajax({
        url: percorso+"dato/dati_attuali/"+sensore,
        type: "GET",
        dataType: "json",
        success: function(dati_sensori) {
            dati[sensore] =  dati_sensori["dato_richiesto"];
          }
      });
}

function eliminaDatiErrore(dati_sensori){
    var dati_da_eliminare = [];
            
    for(let a = 0; a < dati_sensori["dato_richiesto"].length; a++){
        if(dati_sensori["dato_richiesto"][a]== 9999.9 || dati_sensori["dato_richiesto"][a]== 8888.8){
            dati_da_eliminare.push(a);
        }
    }

    for(let a = 0; a < dati_da_eliminare.length; a++){
        dati_sensori["dato_richiesto"].splice(dati_da_eliminare[a]-a, 1);
        dati_sensori["data_ora"].splice(dati_da_eliminare[a]-a, 1);
    }
    return dati_sensori;
}
/*------------------------------------------------------------------------------------------- */

/*----------------FUNZIONI CHE VENGONO CHIAMATE PER POTER REALIZZARE I GRAFICI---------------------- */

function visualizzaDati(sensore, etichetta, unitaMisura, dati_da_rappresentare){
    document.getElementById("valoreAttuale").innerHTML = (Math.round(dati[sensore]*10)/10) + unitaMisura;
    //formato = 2021/6/5 15.10.7
    //Questa funzione ritorna un array contenete i valori che devo rappresentare nel grafico

    const labels = dati_da_rappresentare;
    const data = {
        labels: dati_da_rappresentare["data_ora"],
        datasets: [{
          label: etichetta,
          backgroundColor: 'rgb(255,140,20)',
          
          data: dati_da_rappresentare["dato_richiesto"],
          borderColor: function(context) {
            const chart = context.chart;
            const {ctx, chartArea} = chart;
    
            if (!chartArea) {
              // This case happens on initial chart load
              return null;
            }
            return getGradient(ctx, chartArea);
          },
        }]
      };
      const config = {
        type: 'line',
        data,
        options: {}
      };
      
      //Distruggo il vecchio canvas e ne creo un altro
      canvas_sensori[sensore].destroy();
      canvas_sensori[sensore] = new Chart(
      document.getElementById('grafico'),
      config
      );

}

let width, height, gradient;
function getGradient(ctx, chartArea) {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;
  if (gradient === null || width !== chartWidth || height !== chartHeight) {
    // Create the gradient because this is either the first render
    // or the size of the chart has changed
    width = chartWidth;
    height = chartHeight;
    gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, '#FBEF59');
    gradient.addColorStop(0.5, '#FF8C14');
    gradient.addColorStop(1, '#FF390D');
  }

  return gradient;
}

//Controllo quale delle seguenti opzioni e selezionati e ritorno l'array contentente di dati che mi interessano
function opzioneSelezionata(sensore, unitaMisura){
    var opzione = document.getElementById("arco_temporale").value;
    var c;
    if(opzione == "optgiorno"){
       ottieniDatiGiornalieri(sensore, unitaMisura);
    }
    else if(opzione == "optmese"){
        ottieniDatiMensili(sensore, unitaMisura);
        }
    else {
        ottieniDatiAnnuali(sensore, unitaMisura);
    }
}

/*------------------------------------------------------------------------------------------ */

/*------------------FUNZIONI CHE COLORANO E DECOLORANO LE ICONE------------------------------*/
function coloraIcona(nome){
    var img = document.getElementById("img_"+nome).src = "/static/img/"+nome+"_arancione.png";
}

function decoloraIcona(nome){
    var img = document.getElementById("img_"+nome).src = "/static/img/"+nome+".png";
}
/*------------------------------------------------------------------------------------------ */

/*------------------FUNZIONI CHE SI OCCUPANO DEL GIROSCOPIO------------------------------*/
function salvaNuoveCoordinateGiroscopio(){
    console.log(dati["giroscopio"])
    return dati["giroscopio"].split("#");
}

function cambiaModelloImmagineGiroscopio(id_mostra, id_nascosto){
    document.getElementById(id_mostra).style.display = "block";
    document.getElementById(id_nascosto).style.display = "none";
}

/*------------------------------------------------------------------------------------------ */

function calcolaPercorso(numero_stazione){
    percorso = "/stazione-meteorologica/"+numero_stazione+"/"
    console.log(numero_stazione);
}


function disegnaBarraOrizzontale(stringaListaSensori, id_della_stazione_meteorologica, eIndex){
    //I sensori sono separati dalla ,
    lista_sensori = stringaListaSensori.split(",");

    testo_html = "<nav class=\"menu-visibility\"><ul>"+
    "<li><a class=\"submenu\" href=\"/stazione-meteorologica/"+id_della_stazione_meteorologica+"/html/index\""+
    "onmousemove=\"coloraIcona('home')\" onmouseleave=\"decoloraIcona('home')\">"+
        "<img id=img_home src=\"/static/img/home.png\" class = \"icon_sensori\"></a>";
    
    if(eIndex){
        testo_html += " <ul><li><a href=\"#chi\">Chi siamo</a></li><li><a href=\"#dati\">Dati in tempo reale</a></li><li><a href=\"#scarica_dati\">Scarica i dati</a></li>"+		
                    "<li><a href=\"#dove\">Dove si trova</a></li><li><a href=\"#contatti\">Contatti utili</a></li></ul>";
    }

    testo_html += "</li>";

    for (let a = 0; a < lista_sensori.length; a++){
        testo_html +=  "<li ><a href="+lista_sensori[a]+" onmousemove=\"coloraIcona('"+lista_sensori[a]+"')\" onmouseleave=\"decoloraIcona('"+lista_sensori[a]+"')\">"+
        "<img id=\"img_"+lista_sensori[a]+"\" src=\"/static/img/"+lista_sensori[a]+".png\" class = \"icon_sensori\"></a></li>";
    }

    testo_html += "</ul></nav>"
    document.getElementById("divSensori").innerHTML = testo_html;
}


/*------------------FUNZIONI CHE COLORANO E DECOLORANO I PULSANTI PER SCARICARE IL CODICE------------------------------*/
function coloraButton(id){
    document.getElementById(id).style.fontWeight = "bold";
    document.getElementById(id).style.backgroundColor = "#FF9115";
}
function decoloraButton(id){
    document.getElementById(id).style.fontWeight = "normal";
    document.getElementById(id).style.backgroundColor = "#FFD666";
}
/*------------------------------------------------------------------------------------------------------------------ */