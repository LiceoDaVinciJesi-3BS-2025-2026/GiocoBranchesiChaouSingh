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
ALTEZZA_SCHERMO = 700     # Altezza totale della finestra

# -------------------------
# GRIGLIA DI GIOCO
# -------------------------
# Il campo di gioco è diviso in una griglia di celle quadrate.
# Le torri vengono piazzate nelle celle, i nemici si muovono lungo le celle.
DIMENSIONE_CELLA = 50   # Ogni cella è 50x50 pixel
CELLE_LARGHE = 16       # 16 celle in orizzontale (16 * 50 = 800px)
CELLE_ALTE = 12         # 12 celle in verticale (12 * 50 = 600px)

# -------------------------
# COLORI
# -------------------------
# Tutti i colori sono definiti come tuple RGB (Red, Green, Blue)
# Ogni valore va da 0 a 255
# Esempio: (255, 0, 0) = rosso puro, (0, 255, 0) = verde puro
VERDE_ERBA = (34, 139, 34)          # Verde scuro per l'erba del campo
VERDE_SCURO = (0, 100, 0)           # Verde più scuro per le linee della griglia
MARRONE_SENTIERO = (139, 90, 43)    # Marrone per il sentiero dei nemici
GRIGIO = (128, 128, 128)            # Grigio per il pannello UI
NERO = (0, 0, 0)                    # Nero per bordi e testo
BIANCO = (255, 255, 255)            # Bianco per testo chiaro
BLU = (30, 144, 255)                # Blu per torre arciere e pulsante ondata
VIOLA = (147, 112, 219)             # Viola per torre cannone
ARANCIONE = (255, 140, 0)           # Arancione per torre magia
ROSSO = (220, 20, 60)               # Rosso per nemici orchi e testo vite
GIALLO = (255, 215, 0)              # Giallo per testo soldi e selezione
VERDE_CHIARO = (0, 255, 0)          # Verde chiaro per validazione positiva

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
    (3, 8), (4, 8), (5, 8), (6, 8), (7, 8),

    # Scende ancora
    (7, 9), (7, 10),

    # Va verso destra
    (8, 10), (9, 10), (10, 10), (11, 10),

    # Sale verso l’alto
    (11, 9), (11, 8), (11, 7), (11, 6), (11, 5), (11, 4),

    # Va verso destra
    (12, 4), (13, 4), (14, 4),

    # Scende
    (14, 5), (14, 6), (14, 7), (14, 8),

    # Uscita verso destra
    (15, 8), (16, 8)
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
}
FPS = 60  # Il gioco gira a 60 frame per secondo

def griglia_a_pixel(griglia_x, griglia_y):

    pixel_x = griglia_x * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2
    pixel_y = griglia_y * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2
    return (pixel_x, pixel_y)


def pixel_a_griglia(pixel_x, pixel_y):

    griglia_x = pixel_x // DIMENSIONE_CELLA
    griglia_y = pixel_y // DIMENSIONE_CELLA
    return (griglia_x, griglia_y)


def ottieni_percorso_pixel():

    return [griglia_a_pixel(x, y) for x, y in PERCORSO_GRIGLIA]


# =============================================================================
# SISTEMA DELLE ONDATE E LIVELLI
# =============================================================================
# Queste funzioni gestiscono la progressione della difficoltà nel gioco.
# Ogni ondata è più difficile della precedente.

def calcola_statistiche_nemici(ondata):
    
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

    return 5 + (ondata * 3)


# =============================================================================
# LOGICA DEI NEMICI
# =============================================================================

def crea_nemico(salute, velocita, ricompensa, tipo='goblin'):

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

def disegna_sfondo(schermo):
    """Disegna sfondo e griglia"""
    schermo.fill(VERDE_ERBA)
    
    for x in range(CELLE_LARGHE):
        for y in range(CELLE_ALTE):
            rettangolo = pygame.Rect(x * DIMENSIONE_CELLA, y * DIMENSIONE_CELLA,
                                    DIMENSIONE_CELLA, DIMENSIONE_CELLA)
            pygame.draw.rect(schermo, VERDE_SCURO, rettangolo, 1)


def disegna_percorso(schermo):
    """Disegna il sentiero"""
    for gx, gy in PERCORSO_GRIGLIA:
        rettangolo = pygame.Rect(gx * DIMENSIONE_CELLA, gy * DIMENSIONE_CELLA,
                                DIMENSIONE_CELLA, DIMENSIONE_CELLA)
        pygame.draw.rect(schermo, MARRONE_SENTIERO, rettangolo)


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
