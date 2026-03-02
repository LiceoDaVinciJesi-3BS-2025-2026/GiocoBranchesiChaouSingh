"""
=============================================================================
TOWER DEFENSE - GIOCO COMPLETO
=============================================================================

Tutto in un unico file - meccanica di gioco e sistema dei livelli.
NESSUN import esterno (tranne pygame e math).

Struttura:
1. Configurazione
2. Sistema delle ondate e livelli
3. Logica dei nemici
4. Logica delle torri
5. Logica dei proiettili
6. Piazzamento e combattimento
7. Loop principale
"""

import pygame
import math

# =============================================================================
# CONFIGURAZIONE GENERALE
# =============================================================================

# -------------------------
# DIMENSIONI SCHERMO
# -------------------------
# Lo schermo del gioco è diviso in due parti:
# - Parte sinistra (800px): campo di gioco con la griglia
# - Parte destra (200px): pannello UI con informazioni e pulsanti
LARGHEZZA_SCHERMO = 1000  # Larghezza totale della finestra
ALTEZZA_SCHERMO = 490     # Altezza totale della finestra

# -------------------------
# GRIGLIA DI GIOCO
# -------------------------
# Il campo di gioco è diviso in una griglia di celle quadrate.
# Le torri vengono piazzate nelle celle, i nemici si muovono lungo le celle.
DIMENSIONE_CELLA = 29   # Ogni cella è 50x50 pixel
CELLE_LARGHE = 27       # 16 celle in orizzontale (16 * 50 = 800px)
CELLE_ALTE = 17         # 12 celle in verticale (12 * 50 = 600px)

# -------------------------
# COLORI
# -------------------------
# Tutti i colori sono definiti come tuple RGB (Red, Green, Blue)
# Ogni valore va da 0 a 255
# Esempio: (255, 0, 0) = rosso puro, (0, 255, 0) = verde puro
GRIGIO = (128, 128, 128)            # Grigio per il pannello UI
NERO = (0, 0, 0)                    # Nero per bordi e testo
BIANCO = (255, 255, 255)            # Bianco per testo chiaro
BLU = (30, 144, 255)                # Blu per torre arciere e pulsante ondata
VIOLA = (147, 112, 219)             # Viola per torre cannone
ARANCIONE = (255, 140, 0)           # Arancione per torre magia
ROSSO = (220, 20, 60)               # Rosso per nemici orchi e testo vite
GIALLO = (255, 215, 0)              # Giallo per testo soldi e selezione
VERDE_CHIARO = (0, 255, 0)          # Verde chiaro per validazione positiva

pygame.init()
schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()


global sfondo_img
sfondo_img = pygame.image.load("srondo.png").convert()
sfondo_img = pygame.transform.scale(sfondo_img, (800, ALTEZZA_SCHERMO))

# -------------------------
# PERCORSO DEI NEMICI
# -------------------------
# Questo è il sentiero che i nemici seguono dall'inizio alla fine.
# È una lista di coordinate (x, y) nella GRIGLIA (non in pixel).
# 
# Come leggere: (0, 5) significa "colonna 0, riga 5"
# - La colonna 0 è il lato sinistro dello schermo
# - La riga 5 è circa a metà dello schermo verticalmente
#
# Il percorso disegna una forma a "S":
# 1. Parte da sinistra (colonna 0)
# 2. Va verso destra fino alla colonna 6
# 3. Sale verso l'alto fino alla riga 1
# 4. Va ancora più a destra fino alla colonna 10
# 5. Scende verso il basso fino alla riga 7
# 6. Va a destra fino a uscire dallo schermo (colonna 16)
#
# Se un nemico raggiunge la fine del percorso, il giocatore perde una vita.
PERCORSO_GRIGLIA = [
    # Inizio da sinistra (parte alta)
    (0, 4), (1, 4), (2, 4),

    # Scende verso il basso
    (2, 5), (2, 6), (2, 7), (2, 8),

    # Va verso destra
    (3, 8), (4, 8), (5, 8), (6, 8), (7, 8),(8, 8),

    # Scende ancora
    (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14),

    # Va verso destra
    (9, 14), (10, 14), (11, 14), (12, 14), (13, 14), (14, 14), (15, 14),

    # Sale verso l’alto
    (15, 13), (15, 12), (15, 11), (15, 10), (15, 9), (15, 8),

    # Va verso destra
    (14, 8), (13, 8),
    
    
    (13, 7), (13, 6), (13, 5), (13, 4), (13, 3), (13, 2),
    
    (14, 2), (15, 2), (16, 2), (17, 2),(18, 2), (19, 2),
    
    (19, 3), (19, 4), (19, 5), (19, 6), (19, 7), (19, 8),
    
    (20, 8), (21, 8), (22, 8), (23, 8), (24, 8)


]

# -------------------------
# CONFIGURAZIONE DEL GIOCO
# -------------------------
# Questi valori determinano quanto è difficile il gioco e come funziona l'economia.

# RISORSE INIZIALI
SOLDI_INIZIALI = 300    # Il giocatore inizia con $300
                        # Abbastanza per comprare 3 torri arciere ($100 ciascuna)
                        # oppure 1 torre cannone ($200) + 1 arciere ($100)

VITE_INIZIALI = 20      # Il giocatore inizia con 20 vite
                        # Ogni volta che un nemico raggiunge la fine, perde 1 vita
                        # Quando le vite arrivano a 0, il gioco finisce (sconfitta)

# PROGRESSIONE
ONDATE_TOTALI = 10      # Il gioco ha 10 ondate in totale
                        # Se il giocatore completa tutte e 10, vince
                        # Le ondate diventano progressivamente più difficili

# ECONOMIA
BONUS_FINE_ONDATA = 50  # Alla fine di ogni ondata, il giocatore riceve $50 bonus
                        # Questo aiuta a comprare nuove torri tra un'ondata e l'altra
                        # Esempio: dopo ondata 3, avrai guadagnato 3 × $50 = $150 di bonus

FRAME_TRA_SPAWN = 60    # Quanti frame aspettare tra uno spawn e l'altro
                        # A 60 FPS, 60 frame = 1 secondo
                        # Quindi i nemici spawnano uno al secondo
                        # Riduci questo numero per spawn più veloci (più difficile)
                        # Aumentalo per spawn più lenti (più facile)

# -------------------------
# COSTI DELLE TORRI
# -------------------------
# Ogni tipo di torre ha un prezzo diverso, bilanciato in base alle sue capacità.
# Il giocatore deve scegliere strategicamente quali torri comprare.
COSTI_TORRI = {
    'arciere': 100,   # Torre economica
                      # - Buon raggio (120 pixel)
                      # - Danno medio (15 HP)
                      # - Velocità media (spara ogni 60 frame = 1 secondo)
                      # Ideale per: inizio gioco, riempire spazi vuoti
    
    'magia': 150,     # Torre di velocità
                      # - Raggio corto (100 pixel)
                      # - Danno basso (8 HP)
                      # - Velocità altissima (spara ogni 20 frame = 0.33 secondi)
                      # Ideale per: ondate massive con tanti nemici deboli
    
    'cannone': 200    # Torre potente
                      # - Raggio lungo (200 pixel)
                      # - Danno alto (40 HP)
                      # - Velocità lenta (spara ogni 120 frame = 2 secondi)
                      # Ideale per: nemici forti nelle ondate avanzate
}

# -------------------------
# FRAME PER SECONDO
# -------------------------
FPS = 60  # Il gioco gira a 60 frame per secondo
          # Questo significa che tutte le funzioni di aggiornamento
          # (movimento nemici, cooldown torri, spawn, ecc.) vengono
          # chiamate 60 volte al secondo.
          # È lo standard per giochi fluidi.


# =============================================================================
# FUNZIONI DI CONVERSIONE
# =============================================================================
# Queste funzioni convertono tra due sistemi di coordinate:
# - GRIGLIA: coordinate intere (0-15 per x, 0-11 per y)
# - PIXEL: coordinate precise in pixel sullo schermo

def griglia_a_pixel(griglia_x, griglia_y):
    """
    Converte coordinate GRIGLIA in coordinate PIXEL (centro della cella).
    
    Perché serve?
    - La griglia usa numeri interi semplici come (5, 3)
    - Ma per disegnare sullo schermo servono coordinate pixel precise
    - Questa funzione fa la conversione
    
    Come funziona?
    - Moltiplica per DIMENSIONE_CELLA (50) per trovare l'angolo della cella
    - Aggiunge metà dimensione (25) per centrare nel mezzo della cella
    
    Esempio:
        griglia (5, 3) diventa:
        x = 5 * 50 + 25 = 275 pixel
        y = 3 * 50 + 25 = 175 pixel
    
    Parametri:
        griglia_x: coordinata x nella griglia (0-15)
        griglia_y: coordinata y nella griglia (0-11)
    
    Ritorna:
        tupla (pixel_x, pixel_y) con le coordinate in pixel
    """
    pixel_x = griglia_x * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2
    pixel_y = griglia_y * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2
    return (pixel_x, pixel_y)


def pixel_a_griglia(pixel_x, pixel_y):
    """
    Converte coordinate PIXEL in coordinate GRIGLIA.
    
    Perché serve?
    - Quando il giocatore clicca col mouse, otteniamo coordinate pixel
    - Ma dobbiamo sapere in quale cella della griglia ha cliccato
    - Questa funzione fa la conversione inversa
    
    Come funziona?
    - Divide per DIMENSIONE_CELLA (50)
    - L'operatore // fa una divisione intera (scarta la parte decimale)
    
    Esempio:
        pixel (275, 175) diventa:
        x = 275 // 50 = 5
        y = 175 // 50 = 3
        
    Nota: Anche se clicchi a (276, 178) o (249, 151), 
          finirai sempre nella stessa cella!
    
    Parametri:
        pixel_x: coordinata x in pixel
        pixel_y: coordinata y in pixel
    
    Ritorna:
        tupla (griglia_x, griglia_y) con le coordinate nella griglia
    """
    griglia_x = pixel_x // DIMENSIONE_CELLA
    griglia_y = pixel_y // DIMENSIONE_CELLA
    return (griglia_x, griglia_y)


def ottieni_percorso_pixel():
    """
    Converte tutto il percorso da coordinate griglia a coordinate pixel.
    
    Perché serve?
    - Il percorso è definito in coordinate griglia (più facile da editare)
    - Ma i nemici si muovono in pixel (movimento fluido)
    - Questa funzione converte tutto il percorso una volta sola
    
    Come funziona?
    - Prende ogni punto del PERCORSO_GRIGLIA
    - Lo converte in pixel usando griglia_a_pixel()
    - Crea una nuova lista con tutti i punti convertiti
    
    Esempio:
        PERCORSO_GRIGLIA = [(0, 5), (1, 5), (2, 5), ...]
        diventa
        [(25, 275), (75, 275), (125, 275), ...]
    
    Ritorna:
        lista di tuple (x, y) in coordinate pixel
    """
    return [griglia_a_pixel(x, y) for x, y in PERCORSO_GRIGLIA]


# =============================================================================
# SISTEMA DELLE ONDATE E LIVELLI
# =============================================================================
# Queste funzioni gestiscono la progressione della difficoltà nel gioco.
# Ogni ondata è più difficile della precedente.

def calcola_statistiche_nemici(ondata):
    """
    Calcola le statistiche dei nemici in base al numero dell'ondata.
    
    IL GIOCO HA 3 FASI DI DIFFICOLTÀ:
    
    ┌─────────────────────────────────────────────────────────────┐
    │ FASE 1 - TUTORIAL (Ondate 1-3)                            │
    │ Nemici: GOBLIN                                              │
    │ - Vita base: 50 HP                                          │
    │ - Incremento: +20 HP per ondata                             │
    │ - Velocità: lenta (1.0 pixel/frame base)                    │
    │ - Ricompensa: $20 base                                      │
    │ Risultato: Ondata 1 = 70 HP, Ondata 3 = 110 HP             │
    └─────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────┐
    │ FASE 2 - DIFFICOLTÀ MEDIA (Ondate 4-7)                    │
    │ Nemici: ORCHI                                               │
    │ - Vita base: 80 HP                                          │
    │ - Incremento: +25 HP per ondata                             │
    │ - Velocità: media (1.2 pixel/frame base)                    │
    │ - Ricompensa: $30 base                                      │
    │ Risultato: Ondata 4 = 180 HP, Ondata 7 = 255 HP            │
    └─────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────┐
    │ FASE 3 - DIFFICOLTÀ ALTA (Ondate 8-10)                    │
    │ Nemici: DEMONI                                              │
    │ - Vita base: 120 HP                                         │
    │ - Incremento: +30 HP per ondata                             │
    │ - Velocità: veloce (1.4 pixel/frame base)                   │
    │ - Ricompensa: $40 base                                      │
    │ Risultato: Ondata 8 = 360 HP, Ondata 10 = 420 HP           │
    └─────────────────────────────────────────────────────────────┘
    
    NOTA SULLA VELOCITÀ:
    - Ogni ondata aumenta la velocità di +0.1 pixel/frame
    - Ma c'è un limite massimo di 3.0 pixel/frame
    - Altrimenti i nemici diventerebbero impossibili da colpire!
    
    NOTA SULLA RICOMPENSA:
    - Ogni ondata aumenta la ricompensa di +$5
    - Questo permette al giocatore di comprare torri migliori
    - È un sistema di progressione bilanciato
    
    Parametri:
        ondata: numero dell'ondata corrente (1-10)
    
    Ritorna:
        tupla con (tipo, salute, velocità, ricompensa)
        Esempio: ('goblin', 70, 1.1, 25)
    """
    # FASE 1: Goblin (ondate 1-3)
    if ondata <= 3:
        tipo = 'goblin'
        salute_base = 50
        incremento_salute = 20
        velocita_base = 1.0
        ricompensa_base = 20
    
    # FASE 2: Orchi (ondate 4-7)
    elif ondata <= 7:
        tipo = 'orco'
        salute_base = 80
        incremento_salute = 25
        velocita_base = 1.2
        ricompensa_base = 30
    
    # FASE 3: Demoni (ondate 8-10)
    else:
        tipo = 'demone'
        salute_base = 120
        incremento_salute = 30
        velocita_base = 1.4
        ricompensa_base = 40
    
    # Calcola le statistiche finali
    salute = salute_base + (ondata * incremento_salute)
    velocita = velocita_base + (ondata * 0.1)
    velocita = min(velocita, 3.0)  # Limita a massimo 3.0 pixel/frame
    ricompensa = ricompensa_base + (ondata * 5)
    
    return (tipo, salute, velocita, ricompensa)


def calcola_numero_nemici(ondata):
    """
    Calcola quanti nemici spawnare in questa ondata.
    
    FORMULA: 5 nemici base + (3 nemici × numero ondata)
    
    Tabella completa:
    ┌─────────┬──────────────┬────────────┐
    │ Ondata  │ Formula      │ Totale     │
    ├─────────┼──────────────┼────────────┤
    │ 1       │ 5 + (1 × 3)  │  8 nemici  │
    │ 2       │ 5 + (2 × 3)  │ 11 nemici  │
    │ 3       │ 5 + (3 × 3)  │ 14 nemici  │
    │ 4       │ 5 + (4 × 3)  │ 17 nemici  │
    │ 5       │ 5 + (5 × 3)  │ 20 nemici  │
    │ 6       │ 5 + (6 × 3)  │ 23 nemici  │
    │ 7       │ 5 + (7 × 3)  │ 26 nemici  │
    │ 8       │ 5 + (8 × 3)  │ 29 nemici  │
    │ 9       │ 5 + (9 × 3)  │ 32 nemici  │
    │ 10      │ 5 + (10 × 3) │ 35 nemici  │
    └─────────┴──────────────┴────────────┘
    
    Perché questa formula?
    - All'inizio (ondata 1) ci sono pochi nemici per insegnare al giocatore
    - Cresce gradualmente ma non esponenzialmente
    - Ondata 10 ha abbastanza nemici da essere sfidante ma non impossibile
    
    Come modificare la difficoltà:
    - Più facile: cambia 5 + (ondata × 2)  [meno nemici]
    - Più difficile: cambia 8 + (ondata × 4)  [più nemici]
    
    Parametri:
        ondata: numero dell'ondata (1-10)
    
    Ritorna:
        numero intero di nemici da spawnare
    """
    return 5 + (ondata * 3)


# =============================================================================
# LOGICA DEI NEMICI
# =============================================================================

def crea_nemico(salute, velocita, ricompensa, tipo='goblin'):
    """
    Crea un nuovo nemico come dizionario con tutte le sue proprietà.
    
    COS'È UN NEMICO?
    Un nemico è un dizionario (come una scheda con informazioni) che contiene:
    - Quanta vita ha
    - Quanto veloce si muove
    - Quanti soldi dà quando viene ucciso
    - Dove si trova nel percorso
    - La sua posizione precisa sullo schermo
    - Che tipo di nemico è (goblin/orco/demone)
    
    CICLO DI VITA DI UN NEMICO:
    1. Viene creato con questa funzione
    2. Viene posizionato all'inizio del percorso da spawna_nemico()
    3. Si muove lungo il percorso ogni frame con muovi_nemico()
    4. Le torri gli sparano con danneggia_nemico()
    5. Quando la salute arriva a 0, viene rimosso e dà soldi al giocatore
    6. OPPURE raggiunge la fine e il giocatore perde una vita
    
    Parametri:
        salute: punti vita totali del nemico
                Esempio: un goblin dell'ondata 1 ha 70 HP
        velocita: quanti pixel si muove per frame
                  A 60 FPS, 1.5 pixel/frame = 90 pixel/secondo
        ricompensa: quanti soldi dà quando viene ucciso
                    Esempio: $25 per un goblin
        tipo: stringa che identifica il tipo ('goblin', 'orco', 'demone')
              Usato per sapere che colore disegnarlo
    
    Ritorna:
        dizionario con tutte le proprietà del nemico
        
    Esempio di nemico creato:
        {
            'salute_max': 70,      # Salute massima (per barra vita)
            'salute': 70,          # Salute attuale (diminuisce quando colpito)
            'velocita': 1.1,       # Pixel per frame
            'ricompensa': 25,      # Soldi che dà
            'indice_percorso': 0,  # A che punto del percorso si trova (0 = inizio)
            'x': 0,                # Posizione X in pixel (impostata dopo)
            'y': 0,                # Posizione Y in pixel (impostata dopo)
            'tipo': 'goblin'       # Tipo di nemico
        }
    """
    return {
        'salute_max': salute,      # Salute massima - serve per disegnare la barra vita
        'salute': salute,          # Salute attuale - diminuisce quando viene colpito
        'velocita': velocita,      # Quanto veloce si muove (pixel per frame)
        'ricompensa': ricompensa,  # Quanti soldi dà quando viene ucciso
        'indice_percorso': 0,      # Indice nel percorso (0 = inizio, len-1 = fine)
        'x': 0,                    # Posizione X in pixel (verrà impostata dopo)
        'y': 0,                    # Posizione Y in pixel (verrà impostata dopo)
        'tipo': tipo               # 'goblin', 'orco', o 'demone'
    }


def muovi_nemico(nemico, percorso_pixel):
    """
    Muove un nemico lungo il percorso in modo fluido.
    
    COME FUNZIONA IL MOVIMENTO:
    Il nemico non "salta" da un punto all'altro del percorso.
    Si muove gradualmente pixel per pixel verso il punto successivo.
    
    PROCESSO PASSO-PASSO:
    1. Controlla se c'è ancora un punto successivo nel percorso
    2. Calcola la direzione verso quel punto (dx, dy)
    3. Calcola la distanza dal punto successivo
    4. Se è abbastanza vicino (< velocità):
       - Passa al punto successivo nel percorso
       - Incrementa indice_percorso
    5. Altrimenti:
       - Si muove di "velocità" pixel verso quel punto
       - Usa la direzione normalizzata per movimento fluido
    
    ESEMPIO NUMERICO:
    Nemico in (25, 275), punto successivo in (75, 275), velocità = 1.5
    
    Frame 1: dx = 50, dy = 0, distanza = 50
             muove a (26.5, 275)  [+1.5 pixel in X]
    Frame 2: muove a (28, 275)
    Frame 3: muove a (29.5, 275)
    ...
    Frame 34: distanza < 1.5, passa al punto successivo!
    
    DIREZIONE NORMALIZZATA:
    Per muoversi sempre alla stessa velocità in tutte le direzioni:
    - Calcola dx/distanza e dy/distanza (vettore direzione)
    - Moltiplica per velocità
    - Risultato: movimento costante diagonale, orizzontale o verticale
    
    Parametri:
        nemico: dizionario del nemico da muovere
        percorso_pixel: lista completa del percorso in coordinate pixel
                       Esempio: [(25, 275), (75, 275), (125, 275), ...]
    
    Ritorna:
        True se il nemico ha raggiunto la FINE del percorso (perde vita)
        False se il nemico è ancora sul percorso
    """
    # Controlla se c'è ancora un punto successivo
    if nemico['indice_percorso'] < len(percorso_pixel) - 1:
        
        # Ottieni le coordinate del punto successivo
        target_x, target_y = percorso_pixel[nemico['indice_percorso'] + 1]
        
        # Calcola la direzione (differenza X e Y)
        dx = target_x - nemico['x']  # Quanto lontano in orizzontale
        dy = target_y - nemico['y']  # Quanto lontano in verticale
        
        # Calcola la distanza totale usando il teorema di Pitagora
        # distanza = √(dx² + dy²)
        distanza = math.sqrt(dx**2 + dy**2)
        
        # Se è vicino al punto successivo (distanza minore della velocità)
        if distanza < nemico['velocita']:
            # Passa al punto successivo
            nemico['indice_percorso'] += 1
            
            # Posizionalo esattamente sul punto
            if nemico['indice_percorso'] < len(percorso_pixel):
                nemico['x'], nemico['y'] = percorso_pixel[nemico['indice_percorso']]
        
        else:
            # Altrimenti continua a muoversi verso il punto successivo
            
            # Normalizza la direzione (dx/distanza, dy/distanza)
            # Questo crea un vettore di lunghezza 1 nella direzione giusta
            direzione_x = dx / distanza
            direzione_y = dy / distanza
            
            # Muovi il nemico di "velocità" pixel in quella direzione
            nemico['x'] += direzione_x * nemico['velocita']
            nemico['y'] += direzione_y * nemico['velocita']
    
    # Ritorna True se ha raggiunto l'ultimo punto (fine del percorso)
    return nemico['indice_percorso'] >= len(percorso_pixel) - 1


def danneggia_nemico(nemico, danno):
    """
    Infligge danno a un nemico.
    Ritorna True se è morto.
    """
    nemico['salute'] -= danno
    return nemico['salute'] <= 0


def disegna_nemico(schermo, nemico):
    """Disegna un nemico con la barra vita"""
    x = int(nemico['x'])
    y = int(nemico['y'])
    
    # Colore e dimensione in base al tipo
    if nemico['tipo'] == 'goblin':
        colore = (0, 200, 0)  # Verde
        raggio = 10
    elif nemico['tipo'] == 'orco':
        colore = (200, 50, 50)  # Rosso
        raggio = 12
    else:  # demone
        colore = (150, 0, 200)  # Viola
        raggio = 14
    
    # Disegna corpo
    pygame.draw.circle(schermo, colore, (x, y), raggio)
    pygame.draw.circle(schermo, NERO, (x, y), raggio, 2)
    
    # Barra vita
    larghezza_barra = 30
    altezza_barra = 4
    x_barra = x - larghezza_barra // 2
    y_barra = y - raggio - 10
    percentuale = nemico['salute'] / nemico['salute_max']
    
    pygame.draw.rect(schermo, GRIGIO, (x_barra, y_barra, larghezza_barra, altezza_barra))
    pygame.draw.rect(schermo, VERDE_CHIARO, (x_barra, y_barra, larghezza_barra * percentuale, altezza_barra))


# =============================================================================
# LOGICA DELLE TORRI
# =============================================================================

def crea_torre(griglia_x, griglia_y, tipo_torre):
    """Crea una nuova torre"""
    pixel_x, pixel_y = griglia_a_pixel(griglia_x, griglia_y)
    
    # Statistiche per tipo
    if tipo_torre == 'arciere':
        raggio = 120
        danno = 15
        velocita_sparo = 60
        colore = BLU
        tipo_proiettile = 'freccia'
    elif tipo_torre == 'cannone':
        raggio = 200
        danno = 40
        velocita_sparo = 120
        colore = VIOLA
        tipo_proiettile = 'palla'
    else:  # magia
        raggio = 100
        danno = 8
        velocita_sparo = 20
        colore = ARANCIONE
        tipo_proiettile = 'magia'
    
    return {
        'griglia_x': griglia_x,
        'griglia_y': griglia_y,
        'x': pixel_x,
        'y': pixel_y,
        'tipo': tipo_torre,
        'raggio': raggio,
        'danno': danno,
        'velocita_sparo': velocita_sparo,
        'colore': colore,
        'tipo_proiettile': tipo_proiettile,
        'cooldown': 0,
        'bersaglio': None
    }


def trova_bersaglio_torre(torre, lista_nemici):
    """Trova il nemico più vicino nel raggio"""
    torre['bersaglio'] = None
    
    for nemico in lista_nemici:
        dx = nemico['x'] - torre['x']
        dy = nemico['y'] - torre['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        if distanza <= torre['raggio']:
            torre['bersaglio'] = nemico
            break


def aggiorna_torre(torre):
    """Aggiorna il cooldown"""
    if torre['cooldown'] > 0:
        torre['cooldown'] -= 1


def puo_sparare_torre(torre):
    """Controlla se la torre può sparare"""
    bersaglio = torre['bersaglio']
    
    if bersaglio and bersaglio['salute'] > 0 and torre['cooldown'] == 0:
        dx = bersaglio['x'] - torre['x']
        dy = bersaglio['y'] - torre['y']
        distanza = math.sqrt(dx**2 + dy**2)
        return distanza <= torre['raggio']
    
    return False


def spara_torre(torre):
    """Fa sparare la torre e ritorna il proiettile"""
    torre['cooldown'] = torre['velocita_sparo']
    return crea_proiettile(torre['x'], torre['y'], torre['bersaglio'], 
                          torre['danno'], torre['tipo_proiettile'])


def disegna_torre(schermo, torre, mostra_raggio=False):
    """Disegna una torre"""
    x = int(torre['x'])
    y = int(torre['y'])
    
    # Raggio opzionale
    if mostra_raggio:
        pygame.draw.circle(schermo, (*torre['colore'], 50), (x, y), torre['raggio'], 1)
    
    # Torre come quadrato
    dimensione = 20
    rettangolo = pygame.Rect(x - dimensione//2, y - dimensione//2, dimensione, dimensione)
    pygame.draw.rect(schermo, torre['colore'], rettangolo)
    pygame.draw.rect(schermo, NERO, rettangolo, 2)


# =============================================================================
# LOGICA DEI PROIETTILI
# =============================================================================

def crea_proiettile(x, y, bersaglio, danno, tipo='freccia'):
    """Crea un nuovo proiettile"""
    return {
        'x': x,
        'y': y,
        'bersaglio': bersaglio,
        'danno': danno,
        'velocita': 8,
        'tipo': tipo
    }


def muovi_proiettile(proiettile):
    """
    Muove il proiettile verso il bersaglio.
    Ritorna True se ha colpito o il bersaglio è morto.
    """
    bersaglio = proiettile['bersaglio']
    
    if bersaglio and bersaglio['salute'] > 0:
        dx = bersaglio['x'] - proiettile['x']
        dy = bersaglio['y'] - proiettile['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        if distanza < proiettile['velocita']:
            return True  # Colpito
        
        proiettile['x'] += (dx / distanza) * proiettile['velocita']
        proiettile['y'] += (dy / distanza) * proiettile['velocita']
        return False
    
    return True  # Bersaglio morto


def disegna_proiettile(schermo, proiettile):
    """Disegna un proiettile"""
    x = int(proiettile['x'])
    y = int(proiettile['y'])
    
    # Colore per tipo
    if proiettile['tipo'] == 'freccia':
        colore = (139, 90, 43)  # Marrone
    elif proiettile['tipo'] == 'palla':
        colore = (80, 80, 80)  # Grigio
    else:  # magia
        colore = (255, 0, 255)  # Magenta
    
    pygame.draw.circle(schermo, colore, (x, y), 4)


# =============================================================================
# MECCANICA DI GIOCO
# =============================================================================

def inizializza_gioco():
    """Crea lo stato iniziale del gioco"""
    return {
        # Risorse
        'soldi': SOLDI_INIZIALI,
        'vite': VITE_INIZIALI,
        
        # Progressione
        'ondata': 0,
        'ondata_in_corso': False,
        'nemici_da_spawnare': 0,
        'timer_spawn': 0,
        
        # Entità
        'nemici': [],
        'torri': [],
        'proiettili': [],
        
        # UI
        'torre_selezionata': None,
        
        # Stato
        'game_over': False,
        'vittoria': False
    }


def avvia_ondata(stato):
    """Avvia una nuova ondata"""
    stato['ondata'] += 1
    stato['nemici_da_spawnare'] = calcola_numero_nemici(stato['ondata'])
    stato['ondata_in_corso'] = True
    stato['timer_spawn'] = 0


def spawna_nemico(stato):
    """Crea un nemico e lo aggiunge al gioco"""
    tipo, salute, velocita, ricompensa = calcola_statistiche_nemici(stato['ondata'])
    
    nemico = crea_nemico(salute, velocita, ricompensa, tipo)
    
    percorso = ottieni_percorso_pixel()
    nemico['x'], nemico['y'] = percorso[0]
    
    stato['nemici'].append(nemico)


def puo_piazzare_torre(stato, griglia_x, griglia_y):
    """Controlla se una torre può essere piazzata"""
    # Non sul percorso
    if (griglia_x, griglia_y) in PERCORSO_GRIGLIA:
        return False
    
    # Non dove c'è già una torre
    for torre in stato['torri']:
        if torre['griglia_x'] == griglia_x and torre['griglia_y'] == griglia_y:
            return False
    
    return True


def piazza_torre(stato, griglia_x, griglia_y):
    """
    Prova a piazzare una torre.
    Ritorna True se riesce.
    """
    if not stato['torre_selezionata']:
        return False
    
    if not puo_piazzare_torre(stato, griglia_x, griglia_y):
        return False
    
    tipo_torre = stato['torre_selezionata']
    costo = COSTI_TORRI[tipo_torre]
    
    if stato['soldi'] < costo:
        return False
    
    # Piazza la torre
    torre = crea_torre(griglia_x, griglia_y, tipo_torre)
    stato['torri'].append(torre)
    stato['soldi'] -= costo
    
    return True


def aggiorna_gioco(stato):
    """
    FUNZIONE PRINCIPALE - Aggiorna tutta la logica del gioco.
    Chiamata 60 volte al secondo.
    """
    if stato['game_over']:
        return
    
    # === SPAWN NEMICI ===
    if stato['ondata_in_corso'] and stato['nemici_da_spawnare'] > 0:
        stato['timer_spawn'] += 1
        if stato['timer_spawn'] >= FRAME_TRA_SPAWN:
            spawna_nemico(stato)
            stato['nemici_da_spawnare'] -= 1
            stato['timer_spawn'] = 0
    
    # === NEMICI ===
    percorso = ottieni_percorso_pixel()
    for nemico in stato['nemici'][:]:
        ha_raggiunto_fine = muovi_nemico(nemico, percorso)
        
        if ha_raggiunto_fine:
            stato['vite'] -= 1
            stato['nemici'].remove(nemico)
            
            if stato['vite'] <= 0:
                stato['game_over'] = True
                stato['vittoria'] = False
    
    # === TORRI ===
    for torre in stato['torri']:
        aggiorna_torre(torre)
        trova_bersaglio_torre(torre, stato['nemici'])
        
        if puo_sparare_torre(torre):
            proiettile = spara_torre(torre)
            stato['proiettili'].append(proiettile)
    
    # === PROIETTILI ===
    for proiettile in stato['proiettili'][:]:
        ha_colpito = muovi_proiettile(proiettile)
        
        if ha_colpito:
            bersaglio = proiettile['bersaglio']
            
            if bersaglio and bersaglio['salute'] > 0:
                e_morto = danneggia_nemico(bersaglio, proiettile['danno'])
                
                if e_morto:
                    stato['soldi'] += bersaglio['ricompensa']
                    if bersaglio in stato['nemici']:
                        stato['nemici'].remove(bersaglio)
            
            stato['proiettili'].remove(proiettile)
    
    # === FINE ONDATA ===
    if (stato['nemici_da_spawnare'] == 0 and 
        len(stato['nemici']) == 0 and 
        stato['ondata_in_corso']):
        stato['ondata_in_corso'] = False
        stato['soldi'] += BONUS_FINE_ONDATA
    
    # === VITTORIA ===
    if (stato['ondata'] >= ONDATE_TOTALI and 
        not stato['ondata_in_corso'] and 
        len(stato['nemici']) == 0):
        stato['game_over'] = True
        stato['vittoria'] = True


# =============================================================================
# RENDERING
# =============================================================================
# ASMAA --------------------------------------------------
def disegna_sfondo(schermo):
    """Disegna sfondo e griglia"""
    schermo.blit(sfondo_img, (0, 0))
    
    for x in range(CELLE_LARGHE):
        for y in range(CELLE_ALTE):
            rettangolo = pygame.Rect(x * DIMENSIONE_CELLA, y * DIMENSIONE_CELLA,
                                    DIMENSIONE_CELLA, DIMENSIONE_CELLA)


def disegna_percorso(schermo):
    """Disegna il sentiero"""
    for gx, gy in PERCORSO_GRIGLIA:
        rettangolo = pygame.Rect(gx * DIMENSIONE_CELLA, gy * DIMENSIONE_CELLA,
                                DIMENSIONE_CELLA, DIMENSIONE_CELLA)

#--------------------------------------------------------------------------

def disegna_preview_torre(schermo, griglia_x, griglia_y, valida):
    """Disegna preview semi-trasparente della torre"""
    colore = VERDE_CHIARO if valida else ROSSO
    
    superficie = pygame.Surface((DIMENSIONE_CELLA, DIMENSIONE_CELLA))
    superficie.set_alpha(100)
    superficie.fill(colore)
    
    schermo.blit(superficie, (griglia_x * DIMENSIONE_CELLA, griglia_y * DIMENSIONE_CELLA))


def disegna_pannello_ui(schermo, soldi, vite, ondata):
    """Disegna il pannello laterale"""
    pygame.draw.rect(schermo, GRIGIO, (800, 0, 200, ALTEZZA_SCHERMO))
    
    font_grande = pygame.font.Font(None, 32)
    
    testo_soldi = font_grande.render(f"Soldi: ${soldi}", True, GIALLO)
    testo_vite = font_grande.render(f"Vite: {vite}", True, ROSSO)
    testo_ondata = font_grande.render(f"Ondata: {ondata}/10", True, BIANCO)
    
    schermo.blit(testo_soldi, (810, 10))
    schermo.blit(testo_vite, (810, 40))
    schermo.blit(testo_ondata, (810, 70))


def disegna_pulsante_torre(schermo, tipo_torre, costo, pos_y, soldi, selezionato):
    """Disegna pulsante per comprare torre"""
    if selezionato:
        colore = GIALLO
    elif soldi >= costo:
        colore = VERDE_CHIARO
    else:
        colore = GRIGIO
    
    rettangolo = pygame.Rect(820, pos_y, 150, 60)
    pygame.draw.rect(schermo, colore, rettangolo)
    pygame.draw.rect(schermo, NERO, rettangolo, 2)
    
    font = pygame.font.Font(None, 24)
    nome = tipo_torre.capitalize()
    testo_nome = font.render(nome, True, NERO)
    testo_costo = font.render(f"${costo}", True, NERO)
    
    schermo.blit(testo_nome, (rettangolo.x + 10, rettangolo.y + 10))
    schermo.blit(testo_costo, (rettangolo.x + 10, rettangolo.y + 35))
    
    return rettangolo


def disegna_pulsante_ondata(schermo, ondata_in_corso):
    """Disegna pulsante per avviare ondata"""
    if ondata_in_corso:
        return None
    
    rettangolo = pygame.Rect(820, 350, 150, 60)
    pygame.draw.rect(schermo, BLU, rettangolo)
    pygame.draw.rect(schermo, NERO, rettangolo, 2)
    
    font = pygame.font.Font(None, 24)
    testo = font.render("Avvia Ondata", True, BIANCO)
    schermo.blit(testo, (rettangolo.x + 15, rettangolo.y + 20))
    
    return rettangolo


def disegna_game_over(schermo, vittoria):
    """Disegna schermata game over"""
    overlay = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
    overlay.set_alpha(128)
    overlay.fill(NERO)
    schermo.blit(overlay, (0, 0))
    
    font_grande = pygame.font.Font(None, 64)
    font_piccolo = pygame.font.Font(None, 32)
    
    if vittoria:
        testo_principale = font_grande.render("VITTORIA!", True, GIALLO)
    else:
        testo_principale = font_grande.render("GAME OVER", True, ROSSO)
    
    testo_riavvio = font_piccolo.render("Premi R per ricominciare", True, BIANCO)
    
    schermo.blit(testo_principale, 
                (LARGHEZZA_SCHERMO // 2 - testo_principale.get_width() // 2, 
                 ALTEZZA_SCHERMO // 2 - 50))
    schermo.blit(testo_riavvio, 
                (LARGHEZZA_SCHERMO // 2 - testo_riavvio.get_width() // 2, 
                 ALTEZZA_SCHERMO // 2 + 20))


def disegna_tutto(schermo, stato, pulsanti_torri, pulsante_ondata):
    """Disegna tutto sullo schermo"""
    # Sfondo
    disegna_sfondo(schermo)
    disegna_percorso(schermo)
    
    # Torri
    mostra_raggio = stato['torre_selezionata'] is not None
    for torre in stato['torri']:
        disegna_torre(schermo, torre, mostra_raggio)
    
    # Nemici
    for nemico in stato['nemici']:
        disegna_nemico(schermo, nemico)
    
    # Proiettili
    for proiettile in stato['proiettili']:
        disegna_proiettile(schermo, proiettile)
    
    # UI
    disegna_pannello_ui(schermo, stato['soldi'], stato['vite'], stato['ondata'])
    
    # Preview torre
    if stato['torre_selezionata']:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x < 800:
            griglia_x, griglia_y = pixel_a_griglia(mouse_x, mouse_y)
            valida = puo_piazzare_torre(stato, griglia_x, griglia_y)
            disegna_preview_torre(schermo, griglia_x, griglia_y, valida)
    
    # Game over
    if stato['game_over']:
        disegna_game_over(schermo, stato['vittoria'])


# =============================================================================
# GESTIONE INPUT
# =============================================================================

def gestisci_click(stato, mouse_x, mouse_y, pulsanti_torri, pulsante_ondata):
    """Gestisce i click del mouse"""
    if stato['game_over']:
        return
    
    # Click sui pulsanti torri
    for tipo_torre, rettangolo in pulsanti_torri.items():
        if rettangolo.collidepoint(mouse_x, mouse_y):
            if stato['soldi'] >= COSTI_TORRI[tipo_torre]:
                if stato['torre_selezionata'] == tipo_torre:
                    stato['torre_selezionata'] = None
                else:
                    stato['torre_selezionata'] = tipo_torre
            return
    
    # Click sul pulsante ondata
    if pulsante_ondata and pulsante_ondata.collidepoint(mouse_x, mouse_y):
        avvia_ondata(stato)
        return
    
    # Click sul campo di gioco
    if mouse_x < 800 and stato['torre_selezionata']:
        griglia_x, griglia_y = pixel_a_griglia(mouse_x, mouse_y)
        if piazza_torre(stato, griglia_x, griglia_y):
            stato['torre_selezionata'] = None


# =============================================================================
# LOOP PRINCIPALE
# =============================================================================

def main():
    """Funzione principale - loop del gioco"""
    # Inizializza Pygame
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()
    
    # Inizializza gioco
    stato = inizializza_gioco()
    pulsanti_torri = {}
    
    # Loop principale
    in_esecuzione = True
    while in_esecuzione:
        
        # === EVENTI ===
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = evento.pos
                pulsante_ondata = disegna_pulsante_ondata(schermo, stato['ondata_in_corso'])
                gestisci_click(stato, mouse_x, mouse_y, pulsanti_torri, pulsante_ondata)
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and stato['game_over']:
                    stato = inizializza_gioco()
                if evento.key == pygame.K_ESCAPE:
                    stato['torre_selezionata'] = None
        
        # === AGGIORNA LOGICA ===
        aggiorna_gioco(stato)
        
        # === DISEGNA ===
        disegna_tutto(schermo, stato, pulsanti_torri, None)
        
        # Disegna pulsanti e salva rettangoli
        pulsanti_torri['arciere'] = disegna_pulsante_torre(
            schermo, 'arciere', 100, 100, stato['soldi'],
            stato['torre_selezionata'] == 'arciere')
        
        pulsanti_torri['magia'] = disegna_pulsante_torre(
            schermo, 'magia', 150, 170, stato['soldi'],
            stato['torre_selezionata'] == 'magia')
        
        pulsanti_torri['cannone'] = disegna_pulsante_torre(
            schermo, 'cannone', 200, 240, stato['soldi'],
            stato['torre_selezionata'] == 'cannone')
        
        pulsante_ondata = disegna_pulsante_ondata(schermo, stato['ondata_in_corso'])
        
        # Aggiorna schermo
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()



