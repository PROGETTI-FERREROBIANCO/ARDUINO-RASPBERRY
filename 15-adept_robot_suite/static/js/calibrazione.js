const MIN_X = -1000
const MAX_X = 1000
const MIN_Y = -1000
const MAX_Y = 1000
const MIN_Z = -1000
const MAX_Z = 1000
const MIN_YAW = -1000
const MAX_YAW = 1000
const MIN_PITCH = -1000
const MAX_PITCH = 1000
const MIN_ROLL = -1000
const MAX_ROLL = 1000
var dati_input = {}

$( function () {
    var dialog_alim, dialog_pinza, form,
      allFields = $( [] ),
      tips = $( ".validateTips" );
 
    function updateTips( t ) {
      tips
        .text( t )
        .addClass( "ui-state-highlight" );
      setTimeout(function() {
        tips.removeClass( "ui-state-highlight", 1500 );
      }, 500 );
    }
 
    function checkLength( n, min, max ) {
      var o = $( "#"+n )
      if ( o.val().length > max || o.val().length < min ) {
        o.addClass( "ui-state-error" );
        updateTips( "Length of " + n + " must be between " +
          min + " and " + max + "." );
        return false;
      } else {
        return true;
      }
    }

    function isnotEmptyControl(o){
      var stringa = o.val()
      if(stringa == "") {
        o.addClass( "ui-state-error" );
        return false
      }
      return true
    }
 
    function checkRegexp( o, regexp, n ) {
      if ( !( regexp.test( o.val() ) ) ) {
        o.addClass( "ui-state-error" );
        updateTips( n );
        return false;
      } else {
        return true;
      }
    }

    function checkNumber(n, min, max){
      var o = $( "#"+n )
      if(o.val() == "") {
        o.addClass( "ui-state-error" );
        return false
      }
      if((o.val() <= max) && (o.val() >= min)) return true;
      o.addClass( "ui-state-error" );
      return false
    }
 
    function modificaInformazioniPinza() {
      var valid = true;

      allFields = $( [] ).add( "#funzione_pinza" ).add( "#tipo_pinza" ).add( "#coord_x_pinza" ).add( "#coord_y_pinza" ).add( "#coord_z_pinza" ).add( "#coord_yaw_pinza" ).add( "#coord_pitch_pinza" ).add( "#coord_roll_pinza" ).add( "#altezza_alim" ).add( "#altezza_ins_comp" )
      allFields.removeClass( "ui-state-error" );
      
      valid = valid &&  isnotEmptyControl($( "#funzione_pinza"))
      valid = valid && checkNumber("coord_x_pinza", MIN_X, MAX_X); 
      valid = valid && checkNumber("coord_y_pinza", MIN_Y, MAX_Y); 
      valid = valid && checkNumber("coord_z_pinza", MIN_Z, MAX_Z); 
      valid = valid && checkNumber("coord_yaw_pinza", MIN_YAW, MAX_YAW); 
      valid = valid && checkNumber("coord_pitch_pinza", MIN_PITCH, MAX_PITCH); 
      valid = valid && checkNumber("coord_roll_pinza", MIN_ROLL, MAX_ROLL); 
      valid = valid && checkNumber("altezza_alim", MIN_Z, MAX_Z); 
      valid = valid && checkNumber("altezza_ins_comp", MIN_Z, MAX_Z);
      
      
      if ( valid ) {
        var num_pinza = ($('#dialog-pinza').dialog('option', 'title')).split(" ")[2];

        dati_input["pinze"][num_pinza][1] = document.getElementById("tipo_pinza").value
        dati_input["pinze"][num_pinza][2] = document.getElementById("funzione_pinza").value;
        dati_input["pinze"][num_pinza][3] = document.getElementById("altezza_alim").value;
        dati_input["pinze"][num_pinza][4] = document.getElementById("altezza_ins_comp").value;
        var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]
        for (let a = 0; a<nomi_coord.length; a++){
          dati_input["pinze"][num_pinza][a+8] = document.getElementById("coord_"+nomi_coord[a]+"_pinza").value;
        }

        if(document.getElementById("ckb_pinza").checked) dati_input["pinze"][num_pinza][14] = "ON"
        else dati_input["pinze"][num_pinza][14] = "OFF"
      }
      
      if (valid) dialog_pinza.dialog( "close" );
      verificaAttivo(dati_input["pinze"], "pinza")
      return valid;
    }
 
    dialog_pinza = $( "#dialog-pinza" ).dialog({
      autoOpen: false,
      height: 400,
      width: 500,
      modal: true,
      buttons: {
        "Salva": modificaInformazioniPinza,
        Annulla: function() {
          dialog_pinza.dialog( "close" );
        }
      },
      close: function() {
        //form[ 0 ].reset();
        allFields.removeClass( "ui-state-error" );
        document.getElementById("funzione_pinza").value = "";
        document.getElementById("altezza_alim").value = "";
        document.getElementById("altezza_ins_comp").value = "";
        var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]
        for (let a = 0; a<nomi_coord.length; a++){
          document.getElementById("coord_"+nomi_coord[a]+"_pinza").value = "";
        }
      },
      open: function(){
        console.log("ciao")
      }
    });

    function modificaInformazioniAlim() {
        var valid = true;

        allFields = $( [] ).add( "#funzione_alim" ).add( "#tipo_alim" ).add( "#coord_x_alim" ).add( "#coord_y_alim" ).add( "#coord_z_alim" ).add( "#coord_yaw_alim" ).add( "#coord_pitch_alim" ).add( "#coord_roll_alim" )
        allFields.removeClass( "ui-state-error" );
        
        valid = valid &&  isnotEmptyControl($( "#funzione_alim"))
        valid = valid && checkNumber("coord_x_alim", MIN_X, MAX_X); 
        valid = valid && checkNumber("coord_y_alim", MIN_Y, MAX_Y); 
        valid = valid && checkNumber("coord_z_alim", MIN_Z, MAX_Z); 
        valid = valid && checkNumber("coord_yaw_alim", MIN_YAW, MAX_YAW); 
        valid = valid && checkNumber("coord_pitch_alim", MIN_PITCH, MAX_PITCH); 
        valid = valid && checkNumber("coord_roll_alim", MIN_ROLL, MAX_ROLL);
        
        if ( valid ) {
          var num_alim = ($('#dialog-alim').dialog('option', 'title')).split(" ")[2];
          dati_input["alimentatori"][num_alim][1] = document.getElementById("tipo_alim").value
          dati_input["alimentatori"][num_alim][2] = document.getElementById("funzione_alim").value

          var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]
          for (let a = 0; a<nomi_coord.length; a++){
            dati_input["alimentatori"][num_alim][a+6] = document.getElementById("coord_"+nomi_coord[a]+"_alim").value
          }
          if(document.getElementById("ckb_alim").checked) dati_input["alimentatori"][num_alim][12] = "ON"
          else dati_input["alimentatori"][num_alim][12] = "OFF"
        }
        
        console.log(dati_input["alimentatori"][num_alim])
        if (valid) dialog_alim.dialog( "close" );
        verificaAttivo(dati_input["alimentatori"], "alim")
        return valid;
      }

    dialog_alim = $( "#dialog-alim" ).dialog({
      autoOpen: false,
      height: 400,
      width: 500,
      modal: true,
      buttons: {
        "Salva": modificaInformazioniAlim,
        Annulla: function() {
          dialog_alim.dialog( "close" );
        }
      },
      close: function() {
        //form[ 0 ].reset();
        allFields.removeClass( "ui-state-error" );
        document.getElementById("tipo_alim").value = ""
        document.getElementById("funzione_alim").value = ""

        var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]
        for (let a = 0; a<nomi_coord.length; a++){
          document.getElementById("coord_"+nomi_coord[a]+"_alim").value = ""
        }
      }
    });


    function modificaInformazioniZero() {
        var valid = true;
        allFields = $( [] ).add( "#desc_zero").add( "#coord_x_zero" ).add( "#coord_y_zero" ).add( "#coord_z_zero" ).add( "#coord_yaw_zero" ).add( "#coord_pitch_zero" ).add( "#coord_roll_zero" )
        allFields.removeClass( "ui-state-error" );

        valid = valid &&  isnotEmptyControl($( "#desc_zero"))
        valid = valid && checkNumber("coord_x_zero", MIN_X, MAX_X); 
        valid = valid && checkNumber("coord_y_zero", MIN_Y, MAX_Y); 
        valid = valid && checkNumber("coord_z_zero", MIN_Z, MAX_Z); 
        valid = valid && checkNumber("coord_yaw_zero", MIN_YAW, MAX_YAW); 
        valid = valid && checkNumber("coord_pitch_zero", MIN_PITCH, MAX_PITCH); 
        valid = valid && checkNumber("coord_roll_zero", MIN_ROLL, MAX_ROLL);
        
        if ( valid ) {
          let id_zero = ottieni_nome_zero($('#dialog-zero').dialog('option', 'title'))
          dati_input["punti_specifici"][id_zero][2] = document.getElementById("desc_zero").value
          for (let a = 1; a<allFields.length; a++){
              dati_input["punti_specifici"][id_zero][a+5] = parseFloat(allFields[a].value)
          }
          console.log(dati_input)
          iconaZero(dati_input["punti_specifici"])
          dialog_zero.dialog( "close" );
        }
        return valid;
      }

      dialog_zero = $( "#dialog-zero" ).dialog({
      autoOpen: false,
      height: 400,
      width: 500,
      modal: true,
      buttons: {
        "Salva": modificaInformazioniZero,
        Annulla: function() {
            dialog_zero.dialog( "close" );
        }
      },
      close: function() {
        //form[ 0 ].reset();
        allFields.removeClass( "ui-state-error" );
      }
    });
 
 
    $( "#create-pinza-1, #create-pinza-2, #create-pinza-3, #create-pinza-4, "+
        "#create-pinza-5, #create-pinza-6, #create-pinza-7, #create-pinza-8,  #create-pinza-9, #create-pinza-10,"+ 
        "#create-alim-1, #create-alim-2, #create-alim-3, #create-alim-4, "+
        "#create-alim-5, #create-alim-6, #create-alim-7, #create-alim-8, "+
        "#create-alim-9, #create-alim-10, #create-zero, #create-mg-dx, #create-mg-sx" ).button().on( "click", function(){
      var numero = document.getElementById(this.id).value;
      var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]

      if (numero.includes("PINZA")){
        $('#dialog-pinza').dialog('option', 'title', 'POSIZIONE '+numero.replace("_", " "));

        document.getElementById("ckb_pinza").checked = false;
        var info_pinza = dati_input["pinze"][numero.split("_")[1]]
        if(!(info_pinza.length === 0)){
          document.getElementById("tipo_pinza").value = info_pinza[1];
          document.getElementById("funzione_pinza").value = info_pinza[2];
          document.getElementById("altezza_alim").value = info_pinza[3];
          document.getElementById("altezza_ins_comp").value = info_pinza[4];

          for (let a = 0; a<nomi_coord.length; a++){
            document.getElementById("coord_"+nomi_coord[a]+"_pinza").value = info_pinza[a+8];
          }

          if(info_pinza[14] == "ON") document.getElementById("ckb_pinza").checked = true;
          else document.getElementById("ckb_pinza").checked = false;
        }
        dis_abFinestre('pinza')
        verificaSelectCalibrazione()
        dialog_pinza.dialog( "open" );
      }
      else if(numero.includes("ALIMENTATORE")){
        $('#dialog-alim').dialog('option', 'title', 'POSIZIONE '+numero.replace("_", " "));

        document.getElementById("ckb_alim").checked = false;
        var info_alim = dati_input["alimentatori"][numero.split("_")[1]]
        if(!(info_alim.length === 0)){
          document.getElementById("ckb_alim").checked = true;
          document.getElementById("tipo_alim").value = info_alim[1];
          document.getElementById("funzione_alim").value = info_alim[2];
          for (let a = 0; a<nomi_coord.length; a++){
            document.getElementById("coord_"+nomi_coord[a]+"_alim").value = info_alim[a+6];
          }

          if(info_alim[12] == "ON") document.getElementById("ckb_alim").checked = true;
          else document.getElementById("ckb_alim").checked = false;

        }
        dis_abFinestre('alim')
        dialog_alim.dialog( "open" );
      }
      else{
        let stringa_nome = "zero della scheda"
        if(numero.includes("MAGAZZINO_SX")){
          stringa_nome = " magazzino sinistro della cella"
        }else if(numero.includes("MAGAZZINO_DX")){
          stringa_nome = " magazzino destro della cella"
        }
        $('#dialog-zero').dialog('option', 'title', 'Impostazione  '+stringa_nome);
        let id_zero = ottieni_nome_zero($('#dialog-zero').dialog('option', 'title'))
        console.log("id zero: "+id_zero)
        if(((dati_input["punti_specifici"][id_zero]).length > 2)){
          document.getElementById("desc_zero").value = dati_input["punti_specifici"][id_zero][2];
          for (let a = 0; a<nomi_coord.length; a++){
            document.getElementById("coord_"+nomi_coord[a]+"_zero").value = dati_input["punti_specifici"][id_zero][a+6];
          }
        }else{
          document.getElementById("desc_zero").value = "";
          for (let a = 0; a<nomi_coord.length; a++){
          document.getElementById("coord_"+nomi_coord[a]+"_zero").value = "";
          }
        }
        dialog_zero.dialog( "open" );
      }
    });
  } );


function ottieni_nome_zero(stringa_titolo){
  var stringa = "set_zero"
  if(stringa_titolo.includes(" magazzino sinistro")) stringa = "mg_sx"
  else if (stringa_titolo.includes(" magazzino destro")) stringa = "mg_dx"
  for (const [key, value] of Object.entries(dati_input["punti_specifici"])) {
    if(value[1] == stringa) return key
  }
  return -1
}

function dis_abFinestre(tipo_f){
  var disabilitato = !(document.getElementById("ckb_"+tipo_f).checked)
  if(disabilitato) document.getElementById("dialog-"+tipo_f).style.opacity = "0.5"
  else document.getElementById("dialog-"+tipo_f).style.opacity = "1"
  var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]
  for (let a = 0; a<nomi_coord.length; a++){
    document.getElementById("coord_"+nomi_coord[a]+"_"+tipo_f).disabled = disabilitato;
  }
  document.getElementById("salva_coord_"+tipo_f).disabled = disabilitato

  document.getElementById("tipo_"+tipo_f).disabled = disabilitato
  document.getElementById("funzione_"+tipo_f).disabled = disabilitato
  if(tipo_f == "pinza"){
    document.getElementById("altezza_alim").disabled = disabilitato
    document.getElementById("altezza_ins_comp").disabled = disabilitato
  }
}

function richiediDati(id_cella){
  $.ajax({
    type: "GET",
    url: '/calibrazione?id_cella='+id_cella+"&comando=download",
    async: false,
    success: function(datas) {// success callback
      dati_input = datas
      console.log(dati_input)
    }
  });

  completaSelect(dati_input["tipi_componenti"], "tipo_alim")
  completaSelect(dati_input["tipi_componenti"], "tipo_pinza")
  verificaAttivo(dati_input["pinze"], "pinza")
  verificaAttivo(dati_input["alimentatori"], "alim")
  dati_input["punti_specifici"] = verificaZeroAttivo(dati_input["punti_specifici"])
  iconaZero(dati_input["punti_specifici"])
}

function completaSelect(dizionario_lista, id_select){
  var option_alim = "";
  for (let a = 0; a < dizionario_lista.length; a++){
    option_alim += "<option value="+dizionario_lista[a][0]+">"+dizionario_lista[a][1]+"</option>"
  }
  document.getElementById(id_select).innerHTML = option_alim;
}


function verificaAttivo(dizionario_lista, id_select){
  for (const [key, value] of Object.entries(dizionario_lista)) {
    if (value.length === 0 || (id_select=="pinza" && value[14] == "OFF") || (id_select=="alim" && value[12] == "OFF")) {
      document.getElementById("create-"+id_select+"-"+key).style.opacity = "0.7";
    }
    else document.getElementById("create-"+id_select+"-"+key).style.opacity = "1";
  }
}

function verificaZeroAttivo(p_s){
  let lista_nomi = ["mg_sx", "mg_dx", "set_zero"]
  let lista_indici_vuoti = []
  for (const [key, value] of Object.entries(p_s)) {
    if ((value.length != 0) && lista_nomi.includes(value[1])){
      lista_nomi.splice(lista_nomi.indexOf(value[1]), 1)
    }else{
      lista_indici_vuoti.push(key)
    }
  }
  console.log(lista_indici_vuoti)
  for(let a = 0; a<lista_indici_vuoti.length; a++){
    p_s[lista_indici_vuoti[a]][1] = lista_nomi[a]
  }

  return p_s
}

function iconaZero(p_s){
  for (const [key, value] of Object.entries(p_s)) {
    let idz = "create-"+value[1].replace("set_", "").replace("_", "-")
    console.log(idz)
    if (value.length > 3) document.getElementById(idz).style.opacity = '1'
    else document.getElementById(idz).style.opacity = '0.7'
  }
}

function getKeyByValue(object, valore) {
  for (const [key, value] of Object.entries(object)) {
    if(value[1] === valore) return value[0]
  }
  return -1
}

function verificaSelectCalibrazione(){
  var valore = getKeyByValue(dati_input["tipi_componenti"], "calibrazione")
  console.log(valore)
  if(valore != -1){
    if(document.getElementById("tipo_pinza").value == valore) 
    {
      document.getElementById("altezza_alim").value = 0;
      document.getElementById("altezza_alim").disabled = true;
      document.getElementById("altezza_ins_comp").value = 0;
      document.getElementById("altezza_ins_comp").disabled = true;
    }else{
      document.getElementById("altezza_alim").disabled = false;
      document.getElementById("altezza_ins_comp").disabled = false;
    }
  }
}

function salvaCoord(el){
  var coord = []
  $.ajax({
    type: "GET",
    url: '/calibrazione?id_cella='+id_cella+"&comando=pos",
    async: false,
    success: function(datas) {// success callback
      coord = datas
    }
  });
  console.log(coord)
  console.log(el.value)
  for (const [key, value] of Object.entries(coord)) {
    document.getElementById("coord_"+key+"_"+el.value).value = parseFloat(value);
  }
  console.log("ciao")
  
}

function vaiQui(el){
  var id_e = el.value
  $.ajax({
    type: "POST",
    url: '/calibrazione?id_cella='+id_cella+"&comando=esegui_movimento",
    data: {"x":document.getElementById("coord_x_"+id_e).value, "y":document.getElementById("coord_y_"+id_e).value,
           "z":document.getElementById("coord_z_"+id_e).value, "ya":document.getElementById("coord_yaw_"+id_e).value, 
           "p":document.getElementById("coord_pitch_"+id_e).value, "r":document.getElementById("coord_roll_"+id_e).value},
    async: false,
    success: function(datas) {// success callbac
    }
  });  
}

function prendi_pinza_cal(id_cella){
  $.ajax({
    type: "GET",
    url: '/calibrazione?id_cella='+id_cella+"&comando=prendi_pinza_cal",
    async: false,
    success: function(msg) {// success callback
      if(msg.includes("Errore")){
        document.getElementById("div_alert_cal").innerHTML = msg
        document.getElementById("div_alert_cal").classList.replace("alert-success", "alert-danger");
        document.getElementById("div_alert_cal").style.display = "block";
        do_sleep()
      }
    }
  });  
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function posa_pinza_cal(id_cella){
  $.ajax({
    type: "GET",
    url: '/calibrazione?id_cella='+id_cella+"&comando=posa_pinza_cal",
    async: false,
    success: function(msg) {// success callback
      if(msg.includes("Errore")){
        document.getElementById("div_alert_cal").innerHTML = msg
        document.getElementById("div_alert_cal").classList.replace("alert-success", "alert-danger");
        document.getElementById("div_alert_cal").style.display = "block";

        do_sleep()
      }
    }
  });  
}

const do_sleep = async() => {
  await sleep(5000);
  document.getElementById("div_alert_cal").style.display = "none";
}

function inviaDatiModificati(id_cella){
  var nomi_coord = ["x", "y", "z", "yaw", "pitch", "roll"]
  console.log(dati_input)
  for (const [key, value] of Object.entries(dati_input["punti_specifici"])) {
    if(value.length < 3){
      document.getElementById("div_alert_cal").innerHTML = "Impossibile salvare questa calibrazione! Set zero e/o i due magazzini non sono definiti!";
      document.getElementById("div_alert_cal").classList.replace("alert-success", "alert-danger");
      document.getElementById("div_alert_cal").style.display = "block";

      do_sleep()
  
      return;
    }
  }

  var dati_nuovi = {};
  for (const [key, value] of Object.entries(dati_input["pinze"])) {
    let chiave = "pinza_"+key;
    dati_nuovi[chiave] = {};
    if (value.length == 0){
      dati_nuovi[chiave] = {'id_cella':id_cella,'stato':'OFF', 'num_pos_in_cella':key}
    }else{
      dati_nuovi[chiave]['stato'] = value[14]
      dati_nuovi[chiave]['id_cella'] = id_cella;
      dati_nuovi[chiave]['id_tipo_pinza'] = value[1]
      dati_nuovi[chiave]['num_pos_in_cella'] = key
      dati_nuovi[chiave]['funzione'] = value[2]
      dati_nuovi[chiave]['h_alim'] = value[3]
      dati_nuovi[chiave]['h_ins_comp'] = value[4]
      for (let a = 0; a<nomi_coord.length; a++){
        dati_nuovi[chiave][nomi_coord[a]] = value[a+8]
      }
    }
  }

  for (const [key, value] of Object.entries(dati_input["alimentatori"])) {
    let chiave = "alimentatore_"+key;
    dati_nuovi[chiave] = {};
    if (value.length == 0){
      dati_nuovi[chiave] = {'id_cella':id_cella,'stato':'OFF', 'num_pos_in_cella':key}
    }else{
      dati_nuovi[chiave]['stato'] = value[12]
      dati_nuovi[chiave]['id_cella'] = id_cella;
      dati_nuovi[chiave]['id_tipo_alimentatore'] = value[1]
      dati_nuovi[chiave]['num_pos_in_cella'] = key
      dati_nuovi[chiave]['funzione'] = value[2]
      for (let a = 0; a<nomi_coord.length; a++){
        dati_nuovi[chiave][nomi_coord[a]] = value[a+6]
      }
    }
  }

  for (const [key, value] of Object.entries(dati_input["punti_specifici"])) {
    let chiave = "punto_specifico_"+key;
    dati_nuovi[chiave] = {};
    dati_nuovi[chiave]['id_cella'] = id_cella;
    dati_nuovi[chiave]['nome'] = value[1]
    dati_nuovi[chiave]['descrizione'] = value[2]
    for (let a = 0; a<nomi_coord.length; a++){
      dati_nuovi[chiave][nomi_coord[a]] = value[a+6]
    }
    }
    console.log(dati_nuovi)

    $.ajax({
      type: "POST",
      url: '/calibrazione?id_cella='+id_cella+"&comando=save",
      data: {"json":JSON.stringify(dati_nuovi)},
      async: false,
      success: function(msg_ritorno) {// success callback
        if (msg_ritorno == "OK"){
          document.getElementById("div_alert_cal").innerHTML = "Salvataggio completato";
          document.getElementById("div_alert_cal").classList.replace("alert-danger", "alert-success");
          richiediDati(id_cella)
        }else{
          document.getElementById("div_alert_cal").innerHTML = "La modifica non è andata a buon fine! "+msg_ritorno;
          document.getElementById("div_alert_cal").classList.replace("alert-success", "alert-danger");
        }
        document.getElementById("div_alert_cal").style.display = "block";
        do_sleep()
      }
    });
}