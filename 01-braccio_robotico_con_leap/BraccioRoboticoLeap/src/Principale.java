public class Principale extends PrincipaleProcessing{
    public static final float INCREMENTO_MOTORI = 0.25F;
    public static final int R_SFUMATURA = 255;
    public static final int G_SFUMATURA = 215;
    public static final int B_SFUMATURA = 153;
    public static final int PROFONDITA_JOYSTICK = -60;
    public static final int AMPIEZZA_SFUMATURA = 50;
    public static final int[] COLORE_SCRITTA_TABELLA = new int[]{255,215,153};
    private int raggio_circonferenza = 50;
    private Arduino arduino;
    private float[] motori_precedenti = new float[]{0,0,0,0,58};
    private Tabella tbl = new Tabella(this, 300, 400, 6, 2,
            20, 18);
    private boolean eInizializzata = false;
    private int e20 = 0;

    public static void main(String[] args){
        Principale pc = new Principale();

        LeapProcessing lp = new LeapProcessing("Principale");

    }

    @Override
    public void addPAappletComponents() {
        if(!eInizializzata){
            this.inizializzaArduino();
            eInizializzata = true;
        }

        //getHands()[0] is the right hand, getHands()[1] is the left hand.
        //text(super.getHands()[0].getDataHand().getCoordPalmoProcessing()[0]+"", 200, 200);
        fill(R_SFUMATURA, G_SFUMATURA, B_SFUMATURA);
        this.disegnaJoyStick( (float)(width-300)/4, 300, true, 1);
        fill(125,242,139);
        this.disegnaJoyStick( (float)(width-300)*3/4, 300, false, 0);
        lights();
        this.tbl.drawTabella();
        this.completaTabella();
        if(e20 != 20){
            e20++;
        }
        else {
            e20 = 0;
            this.inviaDatiArduino();
        }

    }

    public void disegnaJoyStick(float centro_x, float width_tabella, boolean isJoyStickSinistra, int index_mano){
        noStroke();
        pushMatrix();
        //float centro_x = (width-width_tabella)/4;
        pointLight(R_SFUMATURA,G_SFUMATURA,B_SFUMATURA, getHands()[index_mano].getDataHand().getCoordPalmProcessing()[0],
                getHands()[index_mano].getDataHand().getCoordPalmProcessing()[1], AMPIEZZA_SFUMATURA);
        translate(centro_x, (float) ((height*3/5)),PROFONDITA_JOYSTICK);
        box((width-width_tabella)/4, 100, PROFONDITA_JOYSTICK-2);
        if(isJoyStickSinistra){
            box(100, (float)(height/4), PROFONDITA_JOYSTICK-2);
        }
        popMatrix();

        pushMatrix();
        translate(centro_x, (float) (height*3/5),PROFONDITA_JOYSTICK*4/5);
        sphere(this.raggio_circonferenza);
        popMatrix();
    }


    public void completaTabella(){
        this.tbl.pushTestoInTabella("Motore", 0, 0, COLORE_SCRITTA_TABELLA);
        this.tbl.pushTestoInTabella("Valore\nin gradi", 1, 0, COLORE_SCRITTA_TABELLA);

        this.tbl.pushTestoInTabella("distanza indice\npollice", 0, 1, COLORE_SCRITTA_TABELLA);
        this.tbl.pushTestoInTabella(String.valueOf(this.getHands()[0].thumbIndexDistance()),
                1, 1, COLORE_SCRITTA_TABELLA);

        if(isValoreValido(0)){
            this.motori_precedenti[4] = 108-this.getHands()[0].thumbIndexDistance()+58;
            if(this.motori_precedenti[4] < 58){
                this.motori_precedenti[4] = 58;
            }
            else if(motori_precedenti[4] > 108){
                this.motori_precedenti[4] = 108;
            }
        }

        for(int a = 0; a < 4; a++){
            //Mano destra: destra-sinistra muove il motore 3, distanza pollice e indice muove il motore 4
            //Mano sinistra: destra-sinistra muove il motore 0, avanti-indietro muove il motore 1-2
            this.tbl.pushTestoInTabella("direzione motore "+a+" :", 0, a+2, COLORE_SCRITTA_TABELLA);
            String testo = switch (a) {
                case 0 -> posizioneMano((float) (width - 300) / 4, (float) (height * 3 / 5),
                        this.getHands()[1].getDataHand().getCoordPalmProcessing()[0],
                        this.getHands()[1].getDataHand().getCoordPalmProcessing()[1], 0, 1);
                case 3 -> posizioneMano((float) (width - 300) * 3 / 4, (float) (height * 3 / 5),
                        this.getHands()[0].getDataHand().getCoordPalmProcessing()[0],
                        this.getHands()[0].getDataHand().getCoordPalmProcessing()[1], 3, 0);
                case 1, 2 -> this.invertiFrecce(posizioneMano((float) (height * 3 / 5), (float) (width - 300) / 4,
                        this.getHands()[1].getDataHand().getCoordPalmProcessing()[1],
                        this.getHands()[1].getDataHand().getCoordPalmProcessing()[0], a, 1), a);

                default -> "";
            };
            this.tbl.pushTestoInTabella(testo, 1, a+2, COLORE_SCRITTA_TABELLA);
        }
    }

    public String invertiFrecce(String testo, int n_motore){
        if(testo.equals("->")){
            testo = "<-";
            this.motori_precedenti[n_motore] = Math.max(this.motori_precedenti[n_motore]-INCREMENTO_MOTORI*2, 0);
        }
        else if(testo.equals("<-")){
            testo = "->";
            this.motori_precedenti[n_motore] = Math.min(this.motori_precedenti[n_motore]+INCREMENTO_MOTORI*2, 180);
        }
        return testo;
    }

    public String posizioneMano(float centro_x, float centro_y, float coord_x, float coord_y, int n_motore, int index_mano){
        String testo = "";
        if(isValoreValido(index_mano)){
            testo = "==";
            if(calcolaDistanzaPunti(new float[]{centro_x, centro_y}, new float[]{coord_x, coord_y}) <=
                    this.raggio_circonferenza){
                testo = "==";
            }
            else if(coord_x > (float)(centro_x+this.raggio_circonferenza) ||
                    coord_x < (float)(centro_x-this.raggio_circonferenza)){
                if(centro_x < coord_x){
                    testo="->";
                    this.motori_precedenti[n_motore] = Math.min(this.motori_precedenti[n_motore]+INCREMENTO_MOTORI, 180);
                }
                else{
                    testo = "<-";
                    this.motori_precedenti[n_motore] = Math.max(this.motori_precedenti[n_motore]-INCREMENTO_MOTORI, 0);
                }
            }
        }

        return  testo;
    }

    public float calcolaDistanzaPunti(float[] coord_nodo1, float[] coord_nodo2){

        float result_x = (float) Math.pow(coord_nodo1[0]-coord_nodo2[0],2);
        float result_y = (float) Math.pow(coord_nodo1[1]-coord_nodo2[1],2);
        float somma_coord = result_x + result_y;

        return (float) Math.sqrt(somma_coord);
    }

    public void inviaDatiArduino(){
        for(int a = 0; a < motori_precedenti.length; a++){
            System.out.println(a+":"+(int)this.motori_precedenti[a]+"#");
            arduino.serialWrite(a+":"+(int)this.motori_precedenti[a]+"#");
        }


    }
    public void inizializzaArduino(){
        String ArduinoPort = "/dev/ttyUSB0"; //TODO: Insert your port name here
        int BAUD_RATE = 115200;
        this.arduino = new Arduino(ArduinoPort, BAUD_RATE);
        this.arduino.openConnection();
        this.inviaDatiArduino();
    }

    public boolean isValoreValido(int index_mano){
               return this.getHands()[index_mano].getDataHand().getCoordPalmProcessing()[0] >= 0 &&
                this.getHands()[index_mano].getDataHand().getCoordPalmProcessing()[0] < displayWidth &&
                this.getHands()[index_mano].getDataHand().getCoordPalmProcessing()[1] > -1 &&
                this.getHands()[index_mano].getDataHand().getCoordPalmProcessing()[1] < displayHeight;
    }

}