var comandi = [];
var dizionario_comandi_validi = {};
var max_parametri = 0;
var termina = false;
var x_prec = 0;
var y_prec = 0;
var istruzione_iniziale = 0;

function Comando(tipo, etichetta_parametri, id, parametri_default) {
    this.tipo = tipo;
    this.id = id;
    this.etichetta_parametri = [...etichetta_parametri];
    this.parametri = parametri_default;
    if (parametri_default.length == 0){
        for(let a=0; a < this.etichetta_parametri.length; a++){
            this.parametri[a] = "";
        }
    }
    this.lunghezza_vecchio_parametro = this.parametri.length;
    this.getTipo = function() {
        return this.tipo;
    }
    this.setParametri = function() {
        // id del parametro: parametro_idoggetto_idparametro
        for (let a = 0; a < this.lunghezza_vecchio_parametro && a < this.parametri.length; a++){
            this.parametri[a] = parseInt(document.getElementById("parametro_"+this.id+"_"+a).value);
            document.getElementById("parametro_"+this.id+"_"+a).value = this.parametri[a]+"";
        }
        this.lunghezza_vecchio_parametro = this.parametri.length;
        
    }
    this.getParametri = function() {
        return this.parametri;
    }
    this.getId = function(){
        return this.id;
    }
    this.setId = function(id){
        this.id = id;
    }
    this.setTipo = function(){
        tp = document.getElementById("comando_"+this.id).value;

        if(tp in dizionario_comandi_validi){
            this.tipo = tp;
            let l = [];
            for (let a = 0; a < dizionario_comandi_validi[this.tipo].length; a++){
                l.push("");
            }
            this.cambiaNParametri(l, dizionario_comandi_validi[this.tipo]);
        }else{
            this.tipo = "NaN"
        }
    }
    this.cambiaNParametri = function(lista_parametri, ep){
        this.parametri = lista_parametri;
        this.etichetta_parametri = ep;
    }
    this.toString = function(){
        //codifica tipo(parametro1, parametro2, parametro3)\n
        var stringa_ritorno = this.getTipo()+"(";
        for(let a = 0; a < this.parametri.length; a++){
            stringa_ritorno += this.parametri[a]+",";
        }
        return stringa_ritorno.slice(0, -1)+")\n";
    }

    this.disegnaComando = function(){
        var nuovo_elemento = 
            '<tr class="tr_comando" id="tr_'+this.id+'"> <td id="stato_'+this.id+'" class="td_stato">'+this.id+'</td>'+
            '<td><input type="text" id="comando_'+this.id+'" value="'+this.tipo+'" class="td_comando td_'+this.id+'" size="'+this.tipo.length+'";></td>'+
            '<td>(</td>';
        for (let a = 0; a < this.parametri.length; a++){
            nuovo_elemento += '<td><input class="td_parametro td_'+this.id+'" type="text" id="parametro_'+this.id+'_'+a+'" value="'+this.parametri[a]+'" placeholder = "'+this.etichetta_parametri[a]+'" size="'+(this.etichetta_parametri[a]+"").length+'">, ';
        }
        nuovo_elemento = nuovo_elemento.slice(0,-2);
        nuovo_elemento += '</td><td colspan="'+(max_parametri-this.parametri.length)+'"></td>';
        nuovo_elemento += '<td>)</td>'+
        '<td><input class="td_pulsante" type="button" value="X" onclick="eliminaComando('+this.id+')"></td>'+
        '<td><input class="td_pulsante" type="button" value="↑" onclick="spostaSu('+this.id+')"></td>'+
        '<td><input class="td_pulsante" type="button" value="↓" onclick="spostaGiu('+this.id+')"></td>'+
        '<td><input class="td_pulsante" type="button" value="✔" onclick="eseguiComandi('+this.id+')"></td></tr>';

        document.getElementById("elenco_istruzioni").innerHTML += nuovo_elemento;
    }
    
}

document.addEventListener("DOMContentLoaded", function () {
    const handleUpload = (event) => {
      const files = event.target.files;
      const formData = new FormData();
      formData.append("file_to_upload", files[0]);
  
      fetch("/comandi/upload", {
      method: "POST",
      body: formData,
    })
    .then((response) => response.json())
      .then((data) => {
        console.log("File uploaded successfully");
        console.log(data);
        comandi = [];
        comandi_caricati = data["response"].split("\n");
        for(let a=0; a<comandi_caricati.length; a++){
            tipo = comandi_caricati[a].split("(")[0]
            parametri = comandi_caricati[a].split("(")[1].replace(")", "")
            comandi.push(new Comando(tipo, dizionario_comandi_validi[tipo], comandi.length, parametri.split(",")));
        }
        aggiornaDisegno();
      })
      .catch((error) => {
        console.error(error);
      });
  };
  
    document.querySelector("#file_picker").addEventListener("change", (event) => {
        if(confirm('Verranno perse tutte istruzioni finora caricate!')){
            console.log("Uploading file");
            handleUpload(event);
        }
    });
  });


let scaricaComandi = () => {
    	
    confermaTuttiComandi(0);
    var stringa_da_inviare = "";
    for(let a = 0; a < comandi.length; a++){
        stringa_da_inviare += comandi[a].toString();
    }
    if(stringa_da_inviare.slice(0, -1).includes("NaN")){ alert("Errore nel codice!")}
    else{
    
        // Convert the text to BLOB.
        const textToBLOB = new Blob([stringa_da_inviare.slice(0, -1)], { type: 'text/plain' });
        const sFileName = 'codice.txt';	   // The file to save the data.

        let newLink = document.createElement("a");
        newLink.download = sFileName;

        if (window.webkitURL != null) {
            newLink.href = window.webkitURL.createObjectURL(textToBLOB);
        }
        else {
            newLink.href = window.URL.createObjectURL(textToBLOB);
            newLink.style.display = "none";
            document.body.appendChild(newLink);
        }

        newLink.click(); 
    }
}



function aggiornaParametro(id_comando, id_parametro){
    comandi[id_comando].setParametro(id_parametro);
    confermaTuttiComandi(0);
}

function aggiornaTipo(id_comando){
    comandi[id_comando].setTipo();
    confermaTuttiComandi(0);
}

function aggiornaDisegno(){
    document.getElementById("elenco_istruzioni").innerHTML = "";
    for (let a = 0; a < comandi.length; a++){
        comandi[a].disegnaComando();
    }

}

function aggiungiComando(tipo, parametri){
    confermaTuttiComandi(0);
    var par = []
    comandi.push(new Comando(tipo, parametri.split(","), comandi.length, par));
    aggiornaDisegno();
}

function eliminaComando(indice){
    confermaTuttiComandi(0);
    comandi.splice(indice,1);
    for (let a = indice; a < comandi.length; a++){
        comandi[a].setId(a);
    }
    aggiornaDisegno();
    
}

function spostaSu(indice){
    confermaTuttiComandi(0);
    if(indice > 0){
        let c = comandi[indice];
        comandi[indice] = comandi[indice-1];
        comandi[indice-1] = c;
        comandi[indice].setId(indice)
        comandi[indice-1].setId(indice-1)
    }
    aggiornaDisegno();
}

function spostaGiu(indice){
    confermaTuttiComandi(0);
    if(indice < comandi.length-1){
        let c = comandi[indice];
        comandi[indice] = comandi[indice+1];
        comandi[indice+1] = c;
        comandi[indice].setId(indice)
        comandi[indice+1].setId(indice+1)
    }
    aggiornaDisegno();
}

function coloraRiga(indice){
    for (let a = istruzione_iniziale; a < comandi.length; a++){
        if (a == indice){
            if(termina){
                document.getElementById("stato_"+a).style.backgroundColor = "#FF8585";
                document.getElementById("stato_"+a).style.borderRightColor = "#FF2E2E";
            }
            else{
                document.getElementById("stato_"+a).style.backgroundColor = "#FFC285";
                document.getElementById("stato_"+a).style.borderRightColor = "#FF9830";
            }
            
        }
        else{
            if(!termina){
                if(a < indice ){
                    document.getElementById("stato_"+a).style.backgroundColor = "#E7FFCF";
                    document.getElementById("stato_"+a).style.borderRightColor = "#5EBD00";
                }
                else{
                    document.getElementById("stato_"+a).style.backgroundColor ="#808080";
                    document.getElementById("stato_"+a).style.borderRightColor = "#505050";
                }
            }
        }
            
    }
}

function confermaTuttiComandi(indice){
    for(let a = indice; a < comandi.length; a++){
        comandi[a].setTipo();
        comandi[a].setParametri();
    }
    aggiornaDisegno();
}


function eseguiComandi(indice){
    confermaTuttiComandi(indice);
    var stringa_da_inviare = "";
    for(let a = indice; a < comandi.length; a++){
        stringa_da_inviare += comandi[a].toString();
    }
    if(stringa_da_inviare.slice(0, -1).includes("NaN")){ alert("Errore nel codice!")}
    else{
        istruzione_iniziale = indice;
        document.getElementById("btn_esegui").disabled = true;
        document.getElementById("btn_pausa").disabled = false;
        document.getElementById("btn_termina").disabled = false;
        document.getElementById("btn_riprendi").disabled = true;
        document.getElementById("btn_elimina").disabled = true;
        post("/comandi/esegui", stringa_da_inviare.slice(0, -1));
    }
}


function get(indirizzo) {
    var dati;
    $.ajax({
        url: indirizzo,
        type: 'get',
        dataType: 'json',
        success: function(dato){
            dati = dato;
        }
    });
    return dati;
}

function post(indirizzo, dato_da_inviare) {
    var dati;
    $.ajax({
        url: indirizzo,
        type: 'post',
        data: dato_da_inviare,
        success: function(dato){
            dati = dato;
        }
    });
    return dati;
}

function riprendiCodice(){
    document.getElementById("btn_pausa").disabled = false;
    document.getElementById("btn_termina").disabled = false;
    document.getElementById("btn_riprendi").disabled = true;
   
    get("/comandi/riprendi");

}

function eliminaTuttiComandi(){
    comandi = [];
    aggiornaDisegno();
}

function pausaCodice(){
    document.getElementById("btn_pausa").disabled = true;
    document.getElementById("btn_termina").disabled = false;
    document.getElementById("btn_riprendi").disabled = false;
    get("/comandi/pausa");
    
}

function setZero(){
    get("/comandi/set-zero");
}

function terminaCodice(){
    termina = true;
    get("/comandi/termina");

    document.getElementById("btn_esegui").disabled = false;
    document.getElementById("btn_pausa").disabled = true;
    document.getElementById("btn_termina").disabled = true;
    document.getElementById("btn_riprendi").disabled = true;
    document.getElementById("btn_elimina").disabled = false;
}

function main(dict_comandi){ 
    dizionario_comandi_validi = dict_comandi;
    disegnaCardComandi();
    dimensioniCanvas();
    document.getElementById("btn_esegui").disabled = false;
    document.getElementById("btn_pausa").disabled = true;
    document.getElementById("btn_termina").disabled = true;
    document.getElementById("btn_riprendi").disabled = true;
    document.getElementById("btn_elimina").disabled = false;
}

function disegnaCardComandi(){

    var stringa_card_comandi = "<tr>";
    var n_elementi = 0;
    for (var key in dizionario_comandi_validi) {
        // check if the property/key is defined in the object itself, not in parent
        
        if (dizionario_comandi_validi.hasOwnProperty(key)) {           
            if(n_elementi%3==0){
                stringa_card_comandi += "</tr><tr>";
            }
            stringa_card_comandi += '<th><div class="card"><div class="card-body">'+
                    '<input type="button" class="btn btn-dark" value="'+key+'" onclick="aggiungiComando(\''+key+'\', \''+dizionario_comandi_validi[key]+'\');"></div></div></th>';
        }
        n_elementi++;
        if(dizionario_comandi_validi[key].length > max_parametri){
            max_parametri = dizionario_comandi_validi[key].length;
        }
    }
    max_parametri ++;
    stringa_card_comandi += "</tr>";

    document.getElementById("tipi_comando").innerHTML = stringa_card_comandi;
}

function aggiornaCoordinate(coord){
    document.getElementById("tr_posizione").innerHTML ='<tr>'+
    '<th colspan="2">X: '+coord.split("%")[0]+'</th>'+
    '<th colspan="2">Y: '+coord.split("%")[1]+'</th>'+
    '<th colspan="2">Z: '+coord.split("%")[2]+'</th>';
    aggiornaTurtle(coord.split("%")[0], coord.split("%")[1], coord.split("%")[2]);
}

function aggiornaFinecorsa(dati_finecorsa){
    var html_dati = "";
    
    html_dati+= scegliColore(dati_finecorsa.split("%")[0])+'FC X 1</th>';
    html_dati+= scegliColore(dati_finecorsa.split("%")[1])+'FC X 2</th>';
    html_dati+= scegliColore(dati_finecorsa.split("%")[2])+'FC Y 1</th>';
    html_dati+= scegliColore(dati_finecorsa.split("%")[3])+'FC Y 2</th>';
    html_dati+= scegliColore(dati_finecorsa.split("%")[4])+'FC Z 1</th>';
    html_dati+= scegliColore(dati_finecorsa.split("%")[5])+'FC Z 2</th>';
    html_dati+= '<th><button  style="margin-left: 5%;" title="pulisci canvas" onclick="pulireCanvas()" class="btn_tabella btn-secondary">pulisci</button></th>';

    document.getElementById("tr_finecorsa").innerHTML = html_dati;
          
}


function scegliColore(valore){
    if (valore == "True"){
        return '<th style="background-color: rgb(255, 124, 124);">';
    }
    return '<th style="background-color: rgb(124, 255, 174);">';
}

function spostaPunta(){
    document.getElementById("btn_pausa").disabled = true;
    document.getElementById("btn_termina").disabled = false;
    document.getElementById("btn_riprendi").disabled = false;
    

    coordx = parseInt(document.getElementById("coordx").value)+"";
    coordy = parseInt(document.getElementById("coordy").value)+"";
    coordz = parseInt(document.getElementById("coordz").value)+"";
    document.getElementById("coordx").value = coordx;
    document.getElementById("coordy").value = coordy;
    document.getElementById("coordz").value = coordz;

    if(coordx!= 'NaN' && coordy!= 'NaN' && coordz != 'NaN'){
        post("/comandi/esegui-punta", "vai_incrementale("+coordx+","+coordy+","+coordz+")")
    }
    else{
        alert("Valori non validi!")
    }
}

function aggiornaTurtle(x, y, z){
    x = parseFloat(x)/20;
    y = parseFloat(y)/20;
    z = parseFloat(z);

    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");

    ctx.beginPath();
    ctx.lineWidth = 1;

    if(z==0){
        ctx.strokeStyle = '#ff0000';
    }else if(z > 0){
        ctx.strokeStyle = '#00ff00';
    }else if(z < 0){
        ctx.strokeStyle = '#0000ff';
    }


    ctx.moveTo(x_prec, y_prec);
    ctx.lineTo(x, y);
    ctx.stroke();

    x_prec = x;
    y_prec = y;
}

function pulireCanvas(){
    var c = document.getElementById('myCanvas');
    var ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
}

function dimensioniCanvas(){
    var c = document.getElementById('myCanvas');
    c.width = document.getElementById('div_dx').clientWidth;
    c.height = document.documentElement.clientHeight - (document.getElementById('div_dx').clientHeight - 300);
}
