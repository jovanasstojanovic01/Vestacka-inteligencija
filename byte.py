#########################################################################################
#1. faza
import copy
import math
import time
import marshal
smerovi_kretanja=('GL','GD','DL','DD')
pomeraji={'GL':(-1,-1),'GD':(-1,1),'DL':(1,-1),'DD':(1,1)}

def UnesiParametreIgre():
    ispravanunos = False
    i = 0
    while not ispravanunos and i<3:
        n = input("Uneti dimenziju table N: (N moze biti 8, 10 ili 16):")
        if n=='8' or n=='10' or n=='16':
            n= int(n)
            ispravanunos=True
        else:
            print("Neispravan unos.")
        i+=1
    if i==3:
        n=8
        print("Dimenzija table je 8x8")
    return n


#Pravi pocetno stanje - postavlja tabelu
def startState(n):
    stanje={'tabela':dict(),'rowNames':list(),'stekovi':{'X':0,'O':0},'naPotezu':'X','covek':'X','n':n}
    stanje['rowNames']=initializeRowNames(n)
    tabela={}
    player={
        0:'X',
        1:'O'
    }
    
    for i in range(1,n+1):
        tabela[i]={}
        tmp=i%2
        for j in range(1 if tmp==1 else 2,n+1,2):
            tabela[i][j]=[]
            if i!=1 and i!=n:
                tabela[i][j].append(player[tmp])
    stanje['tabela']=tabela
    return stanje

#za vrste table - pravi hesh tablicu, slika redni broj u karakter
def initializeRowNames(n):
    asci=65
    rowNames={}
    for i in range(0,n):
        rowNames[i+1]=chr(asci+i)
    return rowNames

#Vraca znak kojim igra covek, default X
def koPrviIgra():       
    var = 'X'
    ispravanunos = False
    i = 0
    while not ispravanunos and i<3:
        value = input("Zelite da igrate kao prvi igrac(X) ili drugi igrac(O)? Uneti odgovarajuci karakter:")
        if value == 'x' or value =='X':
            ispravanunos=True
        else:
            if value == 'o' or value == 'O':
                var = 'O'
                ispravanunos=True
            else:
                print('Molimo unesite X ili O')
        i+=1
    if i==3:
        print("Igrate kao prvi igrac")
    
    return var

#stampa tablu
def showState(stanje):
    
    def polje_za_stampu(i,j,indeks):
        return ' ' if j not in stanje['tabela'][i] else '.' if len(stanje['tabela'][i][j])<indeks+1 else stanje['tabela'][i][j][indeks]
    def printText(txt):
        print(txt,end="")
    
    polje=" {prvo}{drugo}{trece}"
    
    for i in range(1,stanje['n']+1):
        if i >=10:
            printText("  {}".format(i))
        else:
            printText("   {}".format(i))
    print()
    
    for i in range(1,stanje['n']+1):
        for redStampe in range(0,3):
            if redStampe!=1:
                printText(" ")
            else:
                printText(stanje['rowNames'][i])
            for j in range(1,stanje['n']+1):
                printText(polje.format(prvo=polje_za_stampu(i,j,6-(3*redStampe)),drugo=polje_za_stampu(i,j,6-(3*redStampe)+1),trece=polje_za_stampu(i,j,6-(3*redStampe)+2)))
            print()
    print("X:{} O:{}".format(stanje['stekovi']['X'], stanje['stekovi']['O']))

#vraca potez u formatu lista koja sadrzi [string string int string] 
def UnesiPotez(stanje):               
    ispravno = False                  
    i = 1
    while not ispravno:
        red = input("{} na potezu! Unesi potez:".format(stanje['naPotezu']))  
        potez = red.split(' ')
        
        if(len(potez)==4 and len(potez[0])==1 and potez[2].isdigit() and potez[1].isdigit()):
            potez[2]=int(potez[2])
            potez[0] = ord(potez[0]) - ord('A') + 1
            potez[1] = int(potez[1])
            ispravno = ispravanPotez(potez[0],potez[1],potez[2], potez[3],stanje) and valjanostPoteza(potez[0],potez[1],potez[2], potez[3],stanje)
        
        if i%4==0:
            print("Uputstvo za unos poteza - bitno!!!")
            print("Molimo unesite svoje poteze u sledecem formatu: RED KOLONA POZICIJA_NA_STEKU GL/GD/DL/DD")
            print("GL - Gore Levo. GD - Gore Desno. DL - Dole Levo. DD - Dole Desno")
        i+=1
    return potez

#Vraca true ako je potez validan
def ispravanPotez(red,kolona,mesto_na_steku,smer_pomeranja,stanje):
    tabela=stanje['tabela']
    
    if(red in tabela 
    and kolona in tabela[red] 
    and mesto_na_steku>=0 
    and mesto_na_steku<len(tabela[red][kolona]) 
    and tabela[red][kolona][mesto_na_steku]==stanje['naPotezu']
    and smer_pomeranja in smerovi_kretanja
    ):
        return True
    return False

def KrajIgre(stanje):    
    velicinatable=stanje['n']
    stekovi=stanje['stekovi']
    tabla=stanje['tabela']
    kraj_igre=False
    granica = velicinatable*(velicinatable-2)//32

    if stekovi['X']>granica:
        kraj_igre=True
    else:
        if stekovi['O']>granica:
            kraj_igre=True
        else:
            if((stekovi['O']+stekovi['X'])==(velicinatable*(velicinatable-2)/16)):
                kraj_igre=True
    return kraj_igre
#########################################################################################
#2. faza
def okolinaPrazna(red, kolona,stanje):
    return len(list(filter(lambda p:len(stanje['tabela'][p[0]][p[1]])!=0,validniPomeraji(red,kolona,stanje['n']))))==0

def priblizavanjeNajblizemSteku(red,kolona,smer_pomeranja,stanje):
    najblizi=najbliziStekovi(red,kolona,stanje)
    pomeraj=pomeraji[smer_pomeranja]
    prvobitna_razdaljina=distance((red,kolona),najblizi[0])
    razdaljine=[distance((red+pomeraj[0],kolona+pomeraj[1]),polje) for polje in najblizi]
    return len(list(filter(lambda x:x<prvobitna_razdaljina,razdaljine)))!=0

def najbliziStekovi(red,kolona,stanje):
    tabela=stanje['tabela']
    n=stanje['n']
    najblizi=list()
    obidjeni=list()
    obidjeni.append((red,kolona,))
    neobidjeni=list(map(lambda x:(x[0],x[1]),validniPomeraji(red,kolona,n)))
    while(len(najblizi)==0 and len(neobidjeni)!=0):
        nove_destinacije=list()
        for polje in neobidjeni:
            obidjeni.append(polje)
            if len(tabela[polje[0]][polje[1]])!=0:
                najblizi.append(polje)
            destinacije=list(map(lambda x:(x[0],x[1]),validniPomeraji(polje[0],polje[1],n)))
            for dest in destinacije:
                if dest not in obidjeni and dest not in neobidjeni and dest not in nove_destinacije:
                    nove_destinacije.append(dest)
        neobidjeni=nove_destinacije
    return najblizi
    
def valjanostPoteza(red, kolona,mesto_na_steku,smer_pomeranja,stanje):
    novo_polje=(red+pomeraji[smer_pomeranja][0],kolona+pomeraji[smer_pomeranja][1],smer_pomeranja)
    if novo_polje not in validniPomeraji(red,kolona,stanje['n']):
        return False
    broj_figura_na_novom_polju=len(stanje['tabela'][novo_polje[0]][novo_polje[1]])
    if(broj_figura_na_novom_polju==0):
        if mesto_na_steku!=0:
            return False
        if not okolinaPrazna(red,kolona,stanje):
            return False
        return priblizavanjeNajblizemSteku(red,kolona,smer_pomeranja,stanje)
    
    if not (mesto_na_steku)<broj_figura_na_novom_polju:
        return False
    if not (broj_figura_na_novom_polju+len(stanje['tabela'][red][kolona])-mesto_na_steku)<=8:
        return False
    return True

def validniPomeraji(red,kolona,n):
    moguciPomeraji=[(red+pomeraji[smer][0],kolona+pomeraji[smer][1],smer) for smer in smerovi_kretanja]
    return list(filter(lambda p:p[0]>=1 and p[0]<=n and p[1]>=1 and p[1]<=n,moguciPomeraji))

def OdigrajPotez(potez,original):
    red = potez[0]
    vrsta = potez[1]
    novi_red = red + pomeraji[potez[3]][0]
    nova_vrsta = vrsta + pomeraji[potez[3]][1]
    mesto_u_steku = potez[2]
    stanje=marshal.loads(marshal.dumps(original))
    premesta_se = stanje["tabela"][red][vrsta][mesto_u_steku:]
    stanje["tabela"][red][vrsta] = stanje["tabela"][red][vrsta][:mesto_u_steku]
    stanje["tabela"][novi_red][nova_vrsta].extend(premesta_se)

    if len(stanje["tabela"][novi_red][nova_vrsta]) == 8:
        stanje["stekovi"][stanje["tabela"][novi_red][nova_vrsta][-1]] += 1
        stanje["tabela"][novi_red][nova_vrsta].clear()
    
    return stanje

def OdigravanjePartije():
    stanje=startState(UnesiParametreIgre())
    stanje['covek']=koPrviIgra()
    showState(stanje)
    print("Uputstvo za unos poteza - bitno!!!")
    print("Molimo unesite svoje poteze u sledecem formatu: RED KOLONA POZICIJA_NA_STEKU GL/GD/DL/DD")
    print("GL - Gore Levo. GD - Gore Desno. DL - Dole Levo. DD - Dole Desno")
    while not KrajIgre(stanje):
        potez = UnesiPotez(stanje)
        stanje= OdigrajPotez(potez,stanje)
        if stanje['naPotezu']=='X':
            moguci=moguciPotezi(stanje,'O')
            prvi=next(moguci,None)
            if prvi is not None:
                stanje['naPotezu']='O'
        else:
            moguci=moguciPotezi(stanje,'X')
            prvi=next(moguci,None)
            if prvi is not None:
                stanje['naPotezu']='X'
        showState(stanje)
    saigrac=''
    if stanje['covek']=='X':
        saigrac='O'
    else:
        saigrac='X'

    if stanje['stekovi'][stanje['covek']] > stanje['stekovi'][saigrac]:
        print("Pobedili ste!")
    else:
        if stanje['stekovi'][stanje['covek']] == stanje['stekovi'][saigrac]:
            print("Nereseno!")
        else:
            print("Izgubili ste!")
    print("Krajnji rezultat je:")
    print("X:{} O:{}".format(stanje['stekovi']['X'], stanje['stekovi']['O']))

def moguciPotezi(stanje,igrac):
    polja=[(red,kolona,p) for red,v in stanje['tabela'].items() for kolona,p in v.items()]
    poljaSaFiguramaIgraca =list(filter(lambda x:igrac in x[2],polja))
    figure=[(red,kolona,[m  for m in range(0,len(l)) if l[m]==igrac]) for red,kolona,l in poljaSaFiguramaIgraca]
    figureNeprazna=filter(lambda x:not okolinaPrazna(x[0],x[1],stanje),figure)
    for red,kolona,l in figureNeprazna:
        for pomeraj in validniPomeraji(red,kolona,stanje['n']):
            polje=(pomeraj[0],pomeraj[1])
            
            brojFiguraNoviStek=len(stanje['tabela'][polje[0]][polje[1]])
            dozvoljenoNaStek=8-brojFiguraNoviStek
            najniziDozvoljen=len(stanje['tabela'][red][kolona])-dozvoljenoNaStek
            
            good=list(filter(lambda x:x>=najniziDozvoljen and x<brojFiguraNoviStek,l))
            for m in good:
                yield (red,kolona,m,pomeraj[2])
    figurePraznaOkolina=filter(lambda x:okolinaPrazna(x[0],x[1],stanje),figure)
    for red,kolona,l in figurePraznaOkolina:
        if 0 in l:
            najblizi=najbliziStekovi(red,kolona,stanje)
            if(len(najblizi)>0):
                prvobitna_razdaljina=distance((red,kolona),najblizi[0])
                for pomeraj in validniPomeraji(red,kolona,stanje['n']):
                    razdaljine=[distance((pomeraj[0],pomeraj[1]),polje) for polje in najblizi]
                    if len(list(filter(lambda x:x<prvobitna_razdaljina,razdaljine)))!=0:
                        yield (red,kolona,0,pomeraj[2])

def mogucaStanja(stanje,igrac):
    for potez in moguciPotezi(stanje,igrac):
        yield (OdigrajPotez(potez,stanje),potez)


def distance(polje1,polje2):
    return max(abs(polje1[0]-polje2[0]),abs(polje1[1]-polje2[1]))
#########################################################################################
#3. faza

def OdigravanjePartijeSaRacunarom():
    stanje=startState(UnesiParametreIgre())
    stanje['covek']=koPrviIgra()
    
    showState(stanje)
    print("Uputstvo za unos poteza - bitno!!!")
    print("Molimo unesite svoje poteze u sledecem formatu: RED KOLONA POZICIJA_NA_STEKU GL/GD/DL/DD")
    print("GL - Gore Levo. GD - Gore Desno. DL - Dole Levo. DD - Dole Desno")
    brPoteza=0
    
    maxDubina=2
    while not KrajIgre(stanje):
        
        
        if stanje['naPotezu']==stanje['covek']:        
            potez = UnesiPotez(stanje)
            stanje= OdigrajPotez(potez,stanje)   
        else:
            print("AI na potezu...")
            
            potezRacunara = iterative_deepening(stanje,maxDubina,True)

            potez=potezRacunara[0]
            maxDubina=potezRacunara[1]
            stanje=OdigrajPotez(potez,stanje)
            brPoteza+=1
            print("{0} {1} {2} {3}".format(stanje['rowNames'][potez[0]],potez[1],potez[2], potez[3])) 
             
        if stanje['naPotezu']=='X':
            moguci=moguciPotezi(stanje,'O')
            prvi=next(moguci,None)
            if prvi is not None:
                stanje['naPotezu']='O'
        else:
            moguci=moguciPotezi(stanje,'X')
            prvi=next(moguci,None)
            if prvi is not None:
                stanje['naPotezu']='X'
        showState(stanje)
    saigrac=''
    if stanje['covek']=='X':
        saigrac='O'
    else:
        saigrac='X'

    if stanje['stekovi'][stanje['covek']] > stanje['stekovi'][saigrac]:
        print("Pobedili ste!")
    else:
        if stanje['stekovi'][stanje['covek']] == stanje['stekovi'][saigrac]:
            print("Nereseno!")
        else:
            print("Izgubili ste!")
    print("Krajnji rezultat je:")
    print("X:{} O:{}".format(stanje['stekovi']['X'], stanje['stekovi']['O']))
def iterative_deepening(stanje,start_depth,igraRacunar):
    start_time=time.time()
    allowed_time=5
    def max_value(prvi,stanje, dubina, alpha, beta, potez=None):
        if not prvi and time.time()-start_time>allowed_time:
            return None
        mogucaStanjaGen = mogucaStanja(stanje,'X' if stanje['covek']=='O' else 'O')
        moguceStanje=next(mogucaStanjaGen,None)
        if dubina == 0 or KrajIgre(stanje):
            return (potez, proceni_stanje(stanje,'X' if stanje['covek']=='O' else 'O'),)
        if moguceStanje is None:
            return min_value(prvi,stanje,dubina-1,alpha,beta,potez)
        else:
            while moguceStanje is not None:
                m=min_value(prvi,moguceStanje[0], dubina - 1,alpha, beta,  moguceStanje[1] if potez is None else potez)
                if m is None:
                    return None
                alpha = max(alpha, m, key=lambda x: x[1])
                if alpha[1] >= beta[1]:
                    return beta
                moguceStanje=next(mogucaStanjaGen,None)
        return alpha
    def min_value(prvi,stanje, dubina, alpha, beta, potez=None):
        if not prvi and time.time()-start_time>allowed_time:
            return None
        mogucaStanjaGen = mogucaStanja(stanje,stanje['covek'])
        moguceStanje=next(mogucaStanjaGen,None)
        if dubina == 0 or KrajIgre(stanje):
            return (potez, proceni_stanje(stanje,'X' if stanje['covek']=='O' else 'O'),)
        if moguceStanje is None:
            return max_value(prvi,stanje,dubina-1,alpha,beta,potez)
        else:
            while moguceStanje is not None:
                m=max_value(prvi,moguceStanje[0], dubina - 1,alpha, beta, moguceStanje[1] if potez is None else potez)
                if m is None:
                    return None
                beta = min(beta, m, key=lambda x: x[1])
                if beta[1] <= alpha[1]:
                    return alpha
                moguceStanje=next(mogucaStanjaGen,None)
                
        return beta

    def minimax_alfa_beta(prvi,stanje,dubina,igraRacunar,alpha=(None,-math.inf),beta=(None,math.inf)):
        if igraRacunar:
            return max_value(prvi,stanje,dubina,alpha,beta)
        else:
            return min_value(prvi,stanje,dubina,alpha,beta)
    depth=start_depth
    potez=minimax_alfa_beta(True,stanje,depth,igraRacunar)
    depth+=1
    while time.time()-start_time<=allowed_time and depth<30:
        novi_potez=minimax_alfa_beta(False,stanje,depth,igraRacunar)
        if novi_potez:
            potez=novi_potez
            depth+=1
    return (potez[0],depth-1)
    


def proceni_stanje(stanje, racunar):
    if KrajIgre(stanje):
        if stanje['stekovi'][racunar]>stanje['stekovi'][stanje['covek']]:
            return 100000000
        else:
            if stanje['stekovi'][racunar]<stanje['stekovi'][stanje['covek']]:
                return -100000000
            else:
                return 0
    
    praznaokolina={'X':0,'O':0}
    samojedan={'X':0,'O':0}
    vise={'X':0,'O':0}
    vrhovi={'X':0,'O':0}
    for i in stanje['tabela']:
        for j in stanje['tabela'][i]:
            if len(stanje['tabela'][i][j])>0:
                vrhovi[stanje['tabela'][i][j][-1]]+=1
                pomeraji=validniPomeraji(i,j,stanje['n'])
                zauzeta=0
                for pom in pomeraji:
                    if len(stanje['tabela'][pom[0]][pom[1]])>0:
                        zauzeta+=1
                if(zauzeta==0):
                    
                    praznaokolina[stanje['tabela'][i][j][0]]+=1
                else:
                    if zauzeta==1:
                        samojedan[stanje['tabela'][i][j][0]]+=1
                    else:
                        vise[stanje['tabela'][i][j][0]]+=1
    
    tezinaPoen=14
    tezinaPrazno=15
    tezinaJedan=5
    tezinaVise=3
    tezinaVrhovi=1
    ocenaRacunar=stanje['stekovi'][racunar]*tezinaPoen+praznaokolina[racunar]*tezinaPrazno+samojedan[racunar]*tezinaJedan+vise[racunar]*tezinaVise+vrhovi[racunar]*tezinaVrhovi
    
    ocenaCovek=stanje['stekovi'][stanje['covek']]*tezinaPoen+praznaokolina[stanje['covek']]*tezinaPrazno+samojedan[stanje['covek']]*tezinaJedan+vise[stanje['covek']]*tezinaVise+vrhovi[stanje['covek']]*tezinaVrhovi
    ocena = ocenaRacunar-ocenaCovek
    return ocena


OdigravanjePartijeSaRacunarom()

