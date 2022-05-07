#------------------------------------------------------------

# ORs <-    orizzontale verso sinistra          --> ridefinito 'a'
# ORd ->    orizzontale verso destra            --> ridefinito 'b'

#    ^
# Va |      verticale verso alto                --> ridefinito 'c'

# Vb |      verticale verso basso               --> ridefinito 'd'  
#    v

# OBas  \   obliquo alto a sinistra             --> ridefinito 'e'

# OBbs  /   obliquo basso a sinistra            --> ridefinito 'f'

# OBad  /   obliquo alto a destra               --> ridefinito 'g'

# OBbd  \   obliquo basso a destra              --> ridefinito 'h'

#------------------------------------------------------------

# SORs <-    spazio orizzontale verso sinistra  --> ridefinito 'i'
# SORd ->    spazio orizzontale verso destra    --> ridefinito 'j'

#     ^
# SVa |      spazio verticale verso alto        --> ridefinito 'k'

# SVb |      spazio verticale verso basso       --> ridefinito 'l'
#     v

# SOBas  \   spazio obliquo alto a sinistra     --> ridefinito 'm'

# SOBbs  /   spazio obliquo basso a sinistra    --> ridefinito 'n'

# SOBad  /   spazio obliquo alto a destra       --> ridefinito 'o'

# SOBbd  \   spazio obliquo basso a destra      --> ridefinito 'p'

#------------------------------------------------------------

class codificaLettere:
    numero_spostamenti = 0
    presenza_di_lettere_che_si_sviluppano_verso_il_basso = False
    def getCodifica(self, carattere):
        distanza_tra_righe = 3
        spazio_tra_lettere_di_una_stessa_parola = ['j']
        conversione_carattere = []
        if(carattere=='a'):
            conversione_carattere = ['l','l','b','b','b','d','d','d','d','a','a','a','c','c','b','b','c','a','a','c','l','l','l','j','b','j','k','k','k','k','k']
        elif(carattere=='b'):
            conversione_carattere = ['b','d','d','d','b','b','d','d','d','a','a','a','c','c','c','c','c','c','l','l','l','l','l','j','b','c','a','d','j','j','k','k','k','k','k']
        elif(carattere == 'c'):
            conversione_carattere = ['l','l','b','b','b','d','a','a','d','d','b','b','d','a','a','a','c','c','c','c','k','k','j','j','j']
        elif(carattere=='d'):
            conversione_carattere = ['j','j','b','d','d','d','d','d','d','a','a','a','c','c','c','b','b','c','c','c','l','l','l','l','a','d','b','c','j','k','k','k','k']
        elif(carattere == 'e'):
            conversione_carattere = ['l','l','b','b','b','d','d','a','a','d','b','b','d','a','a','a','c','c','c','c','l','j','b','j','k','k','k']
        elif(carattere=='f'):
            conversione_carattere = ['j','b','b','d','a','a','d','b','d','a','d','d','d','a','c','c','c','c','c','g','j','j']
        elif(carattere == 'g'):
            conversione_carattere = ['l','l','l','b','b','b','d','d','d','d','d','d','a','a','a','c','b','b','c','c','a','a','c','c','c','p','d','b','c','a','k','j','j']
        elif(carattere=='h'):
            conversione_carattere = ['b','d','d','d','b','h','d','d','a','c','c','a','d','d','a','c','c','c','c','c','c','j','j','j']
        elif(carattere == 'i'):
            conversione_carattere = ['b','d','a','c','l','l','b','d','d','d','d','a','c','c','c','c','j','k','k']
        elif(carattere=='j'):
            conversione_carattere = ['l','l','l','j','j','b','d','a','c','l','l','b','d','d','d','f','a','a','c','b','b','c','c','c','j','k','k','k','k','k']
        elif(carattere == 'k'):
            conversione_carattere = ['j','d','d','g','g','d','f','f','h','h','d','e','e','d','d','a','c','c','c','c','c','g','j','j']
        elif(carattere=='l'):
            conversione_carattere = ['b','d','d','d','d','d','b','d','a','a','c','c','c','c','c','c','j','j']
        elif(carattere == 'm'):
            conversione_carattere = ['l','l','j','d','b','b','b','h','d','d','a','c','c','a','d','d','a','c','c','a','d','d','a','c','c','c','g','j','j','j','j','k','k']
        elif(carattere=='n'):
            conversione_carattere = ['l','l','j','d','b','h','d','d','a','c','c','a','d','d','a','c','c','c','g','j','j','k','k']
        elif(carattere == 'o'):
            conversione_carattere = ['l','l','b','b','b','d','d','d','d','a','a','a','c','c','c','c','p','b','d','d','a','c','c','j','j','k','k','k']
        elif(carattere=='p'):
            conversione_carattere = ['l','l','l','b','b','b','d','d','d','a','a','d','d','d','a','c','c','c','c','c','c','p','b','d','a','c','j','j','k','k','k','k']
        elif(carattere == 'q'):
            conversione_carattere = ['l','l','l','b','b','b','d','d','d','d','d','d','a','c','c','c','a','a','c','c','c','p','b','d','a','c','j','j','k','k','k','k']
        elif(carattere=='r'):
            conversione_carattere = ['l','l','j','b','b','d','a','f','d','d','a','c','c','c','g','j','j','k','k']
        elif(carattere == 's'):
            conversione_carattere = ['l','l','b','b','b','d','a','a','d','b','b','d','d','a','a','a','c','b','b','c','i','a','c','c','j','j','j','k','k']
        elif(carattere=='t'):
            conversione_carattere = ['j','j','d','b','d','a','d','d','d','b','d','a','a','c','c','c','c','a','c','b','g','j']
        elif(carattere == 'u'):
            conversione_carattere = ['l','l','b','d','d','d','b','c','c','c','b','d','d','d','d','a','a','a','c','c','c','c','j','j','j','k','k']
        elif(carattere=='v'):
            conversione_carattere = ['l','l','b','d','d','h','g','c','c','b','d','d','f','f','e','e','c','c','j','j','j','j','k','k']
        elif(carattere == 'w'):
            conversione_carattere = ['l','l','b','d','d','d','g','c','b','d','h','c','c','c','b','d','d','d','f','e','a','f','e','c','c','c','j','j','j','j','j','k','k']
        elif(carattere=='x'):
            conversione_carattere = ['l','l','j','h','g','h','f','h','f','e','f','e','g','e','g','j','j','j','k','k']
        elif(carattere == 'y'):
            conversione_carattere = ['l','l','l','b','d','d','b','c','c','b','d','d','d','d','d','d','a','a','a','c','b','b','c','c','a','a','c','c','c','j','j','j','k','k','k']
        elif(carattere=='z'):
            conversione_carattere = ['l','l','b','b','b','d','f','f','b','b','d','a','a','a','c','g','g','a','a','c','j','j','j','k','k']
        elif(carattere == 'A'):
            conversione_carattere = ['b','b','b','b','d','d','d','d','d','d','a','c','c','a','a','d','d','a','c','c','c','c','c','c','p','b','b','d','a','a','c','j','j','j','k']
        elif(carattere=='B'):
            conversione_carattere = ['b','b','h','d','f','b','h','d','f','a','a','a','c','c','c','c','c','c','p','b','d','a','c','l','l','l','b','b','d','a','a','c','j','j','j','k','k','k','k']
        elif(carattere == 'C'):
            conversione_carattere = ['b','b','b','b','d','a','a','a','d','d','d','d','b','b','b','d','a','a','a','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere=='D'):
            conversione_carattere = ['b','b','b','h','d','d','d','d','f','a','a','a','c','c','c','c','c','c','p','b','h','d','d','f','a','c','c','c','c','j','j','j','k']
        elif(carattere == 'E'):
            conversione_carattere = ['b','b','b','b','d','a','a','a','d','b','b','d','a','a','d','d','b','b','b','d','a','a','a','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere=='F'):
            conversione_carattere = ['b','b','b','b','d','a','a','a','d','b','b','d','a','a','d','d','d','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere == 'G'):
            conversione_carattere = ['b','b','b','b','d','a','a','a','d','d','d','d','b','b','c','a','c','b','b','d','d','d','a','a','a','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere=='H'):
            conversione_carattere = ['b','d','d','b','b','c','c','b','d','d','d','d','d','d','a','c','c','c','a','a','d','d','d','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere == 'I'):
            conversione_carattere = ['b','b','b','d','a','d','d','d','d','b','d','a','a','a','c','b','c','c','c','c','a','c','j','j','j']
        elif(carattere=='J'):
            conversione_carattere = ['b','b','b','b','d','a','d','d','d','d','d','a','a','a','c','c','b','d','b','c','c','c','c','a','a','c','j','j','j','j']
        elif(carattere == 'K'):
            conversione_carattere = ['b','d','d','g','g','b','f','f','f','h','h','h','a','e','e','d','d','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere=='L'):
            conversione_carattere = ['b','d','d','d','d','d','b','b','b','d','b','b','b','b','c','c','c','c','c','c','j','j','j','j']
        elif(carattere == 'M'):
            conversione_carattere = ['b','h','g','b','d','d','d','d','d','d','a','c','c','c','c','c','f','e','d','d','d','d','d','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere=='N'):
            conversione_carattere = ['b','h','h','c','c','b','d','d','d','d','d','d','a','c','c','c','e','e','d','d','d','d','d','a','c','c','c','c','c','c','j','j','j','j']
        elif(carattere == 'O'):
            conversione_carattere = ['b','b','b','b','d','d','d','d','d','d','a','a','a','a','c','c','c','c','c','c','p','b','b','d','d','d','d','a','a','c','c','c','c','j','j','j','k']
        elif(carattere=='P'):
            conversione_carattere = ['b','b','b','b','d','d','d','a','a','a','d','d','d','a','c','c','c','c','c','c','p','b','b','d','a','a','c','j','j','j','k']
        elif(carattere == 'Q'):
            conversione_carattere = ['b','b','b','b','d','d','d','d','d','b','d','a','a','a','a','a','c','c','c','c','c','c','p','b','b','d','d','d','d','a','a','c','c','c','c','j','j','j','j','k']
        elif(carattere=='R'):
            conversione_carattere = ['b','b','b','b','d','d','d','a','a','h','h','d','e','e','e','d','d','d','a','c','c','c','c','c','c','p','b','b','d','a','a','c','j','j','j','k']
        elif(carattere == 'S'):
            conversione_carattere = ['j','b','b','b','d','a','a','a','d','b','b','h','d','d','f','a','a','a','c','b','b','b','c','c','a','a','e','c','g','j','j','j']
        elif(carattere=='T'):
            conversione_carattere = ['b','b','b','d','a','d','d','d','d','d','a','c','c','c','c','c','a','c','j','j','j']
        elif(carattere == 'U'):
            conversione_carattere = ['b','d','d','d','d','d','b','b','c','c','c','c','c','b','d','d','d','d','d','f','a','a','e','c','c','c','c','c','j','j','j','j']
        elif(carattere=='V'):
            conversione_carattere = ['b','d','d','d','d','h','g','c','c','c','c','b','d','d','d','d','f','f','e','e','c','c','c','c','j','j','j','j']
        elif(carattere == 'W'):
            conversione_carattere = ['b','d','d','d','d','h','g','c','c','b','d','d','h','g','c','c','c','c','b','d','d','d','d','f','f','e','a','f','e','e','c','c','c','c','j','j','j','j','j','j','j']
        elif(carattere=='X'):
            conversione_carattere = ['j','h','h','g','g','h','f','f','h','h','f','e','e','f','f','e','g','g','e','e','g','j','j','j','j','j']
        elif(carattere == 'Y'):
            conversione_carattere = ['b','h','b','g','b','f','f','d','d','d','d','a','c','c','c','c','e','e','j','j','j','j','j']
        elif(carattere=='Z'):
            conversione_carattere = ['b','b','b','b','d','f','f','f','d','b','b','b','d','a','a','a','a','c','c','g','g','g','a','a','a','c','j','j','j','j']
        elif(carattere == '0'):
            conversione_carattere = ['l','l','j','b','h','d','d','f','a','e','c','c','g','l','b','d','d','a','c','c','j','j','k','k','k']
        elif(carattere=='1'):
            conversione_carattere = ['l','l','j','b','d','d','d','d','a','c','c','c','f','c','g','j','k','k']
        elif(carattere == '2'):
            conversione_carattere = ['l','l','b','b','b','d','d','a','a','a','d','d','b','b','b','c','a','a','c','j','c','a','a','c','j','j','j','k','k']
        elif(carattere=='3'):
            conversione_carattere = ['l','l','j','b','b','d','d','d','d','a','a','e','b','b','e','g','a','a','g','j','j','k','k']
        elif(carattere == '4'):
            conversione_carattere = ['l','l','j','j','j','d','d','d','d','a','c','a','a','g','g','g','k','k']
        elif(carattere=='5'):
            conversione_carattere = ['l','l','b','b','h','a','a','d','b','b','d','f','a','a','c','b','b','c','i','a','c','c','j','j','j','k','k']
        elif(carattere == '6'):
            conversione_carattere = ['l','l','b','b','b','d','a','a','d','b','b','d','d','a','a','a','c','c','c','c','l','l','l','j','b','j','j','j','k','k']
        elif(carattere=='7'):
            conversione_carattere = ['l','l','b','b','d','d','b','d','a','d','a','c','a','c','b','c','a','c','j','j','j','k','k']
        elif(carattere == '8'):
            conversione_carattere = ['l','l','j','b','h','d','d','f','a','e','c','c','g','l','b','d','d','a','c','c','l','b','j','k','k','k','k']
        elif(carattere=='9'):
            conversione_carattere = ['l','l','b','b','b','d','d','d','d','a','a','a','c','b','b','c','a','a','c','c','p','b','j','j','j','k','k']
        elif(carattere==' '):
            conversione_carattere = ['j','j']
        elif(carattere=='\n'):

            #ritorna ad inizio riga
            cont=0
            while(cont<self.numero_spostamenti):
                conversione_carattere.append('i')
                cont+=1
            
            #vado a capo
            cont=0
            spazi_verticali=0
            if(self.presenza_di_lettere_che_si_sviluppano_verso_il_basso==True):
                spazi_verticali=9+distanza_tra_righe
            else:
                spazi_verticali=6+distanza_tra_righe
            while(cont<spazi_verticali):
                conversione_carattere.append('l')
                cont+=1

            #resetto le variabili
            self.numero_spostamenti=0
            self.presenza_di_lettere_che_si_sviluppano_verso_il_basso=False

        print(conversione_carattere)

        # gestisco le casistiche in cui carattere sia uguale a "\n" oppure a " "
        if(carattere!='\n'):
            self.numero_spostamenti+=codificaLettere.getLarghezza(self, carattere)
            if(carattere!=' '):
                self.numero_spostamenti+=len(spazio_tra_lettere_di_una_stessa_parola)
                conversione_carattere.append('j')
            if(codificaLettere.getAltezza(self, carattere)==9):
                self.presenza_di_lettere_che_si_sviluppano_verso_il_basso=True
        
        return conversione_carattere
    
    #metodo che restituisice l'altezza
    def getLarghezza(self, carattere):
        larghezza = 0
        if((carattere >='a' and carattere <= 'z') or (carattere >='0' and carattere<='9')):
            if(carattere == 'm' or carattere == 'w'):
                larghezza = 5
            elif(carattere == 'i'):
                larghezza = 1
            elif(carattere == 'l' or carattere == '1'):
                larghezza = 2
            elif(carattere == 'x' or carattere == 'v'):
                larghezza = 4
            else:
                larghezza = 3
        elif(carattere >= 'A' and carattere <= 'Z'):
            if(carattere == 'Q' or carattere == 'Y'):
                larghezza = 5
            elif(carattere == 'I' or carattere == 'T'):
                larghezza = 3
            elif(carattere == 'X'):
                larghezza = 6
            elif(carattere == 'W'):
                larghezza = 7
            else:
                larghezza = 4
        elif(carattere==' '):
            larghezza=2
        else:
            print("Il carattere non è stato codificato!")
            larghezza=0
        return larghezza

    def getAltezza(self, carattere):
        altezza = 0
        if(carattere >= 'A' and carattere <= 'Z'):
            altezza = 6
        elif((carattere >='a' and carattere <= 'z') or (carattere >='0' and carattere<='9') ):
            if(carattere == 'b' or carattere == 'd' or carattere == 'f' or carattere == 'h' or carattere == 'i' or carattere == 'k' or carattere == 't' or carattere == 'l'):
                altezza = 6
            elif(carattere == 'g' or carattere == 'j' or carattere == 'q' or carattere == 'p' or carattere == 'y' ):
                altezza = 9
            else:
                altezza = 4
        else:
            print("Il carattere non è stato codificato!")
            altezza=0
        return altezza






