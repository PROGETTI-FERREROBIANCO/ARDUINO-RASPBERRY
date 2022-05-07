import processing.core.PApplet;

class Tabella{

    private PApplet pApplet;
    private float larghezza_tabella;
    private float altezza_tabella;
    private float num_righe;
    private float num_colonne;
    private float shift_text_down;
    private int font_size;

    private int[] colore_tabella;

    Tabella(PApplet pApplet, float larghezza_tabella, float altezza_tabella, float num_righe, float num_colonne, float shift_text_down, int font_size){

        this.pApplet = pApplet;
        this.larghezza_tabella = larghezza_tabella;
        this.altezza_tabella = altezza_tabella;
        this.num_righe = num_righe;
        this.num_colonne = num_colonne;
        this.shift_text_down = shift_text_down;
        this.font_size = font_size;

        // colore tabella
        colore_tabella = new int[3];
        colore_tabella[0] = 0;
        colore_tabella[1] = 0;
        colore_tabella[2] = 0;


    }

    public void drawTabella(){
        this.pApplet.strokeWeight(1);
        this.pApplet.stroke(255,215,153);
        this.pApplet.fill(colore_tabella[0], colore_tabella[1], colore_tabella[2]);
        this.pApplet.rect(this.pApplet.width-this.larghezza_tabella, 0, this.larghezza_tabella, this.altezza_tabella);

        this.pApplet.strokeWeight(3);
        //this.pApplet.stroke(255);
        // DISEGNO RIGHE
        for(int i=0; i<=this.num_righe; i++) this.pApplet.line(this.pApplet.width-this.larghezza_tabella,i*(this.altezza_tabella/this.num_righe),0,this.pApplet.width,i*(this.altezza_tabella/this.num_righe),0);
        // DISEGNO COLONNE
        for(int i=0; i<=this.num_colonne; i++) this.pApplet.line((this.pApplet.width-this.larghezza_tabella)+i*(this.larghezza_tabella/this.num_colonne),0,0,(this.pApplet.width-this.larghezza_tabella)+i*(this.larghezza_tabella/this.num_colonne),this.altezza_tabella,0);
    }

    public void pushTestoInTabella(String testo, int num_colonna, int num_riga, int[] rgb){
        //println("LARGHEZZA TESTO: "+textWidth(testo));
        float x = ((this.larghezza_tabella/this.num_colonne - this.pApplet.textWidth(testo))/2) +
                (num_colonna*(this.larghezza_tabella/this.num_colonne)) + (this.pApplet.width - this.larghezza_tabella);
        float y = ((this.altezza_tabella/this.num_righe)*num_riga) + this.shift_text_down;
        this.pApplet.fill(rgb[0], rgb[1], rgb[2]);
        this.pApplet.textSize(this.font_size);
        this.pApplet.text(testo, x, y);
    }
}