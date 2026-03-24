# TOWER DEFENSE

import pygame
import math
import os

def main():
    # Inizializza pygame e crea la finestra
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()

    # Creo i font una sola volta (crearli ogni frame è lento)
    font_grande  = pygame.font.Font(None, 48)
    font_medio   = pygame.font.Font(None, 32)
    font_piccolo = pygame.font.Font(None, 22)

    # Carico tutte le immagini del gioco
    immagini = carica_immagini()

    # La classifica sopravvive tra una partita e l'altra
    classifica = []

    
    # LOOP ESTERNO: gira finché il giocatore non esce
    # Ad ogni giro mostra il menu e aspetta una scelta
    
    while True:

        scelta = mostra_menu(schermo, immagini, clock)

        if scelta == "esci":
            break  # esce dal loop esterno → pygame.quit() sotto

        if scelta == "istruzioni":
            # Mostra le istruzioni e poi torna al menu
            if not mostra_istruzioni(schermo, immagini, font_grande, font_medio, font_piccolo, clock):
                break  # se chiude la finestra dalle istruzioni, esci
            continue  # altrimenti ricomincia il loop esterno (torna al menu)

        if scelta == "gioca":
            # Crea uno stato di gioco fresco per una nuova partita
            stato = crea_stato()

            # pulsanti e p_ondata vengono aggiornati ogni frame da disegna_schermo()
            # Li inizializzo vuoti perché al primo frame non esistono ancora
            pulsanti = {}
            p_ondata = None

            # LOOP INTERNO: gira ogni frame durante la partita
        
            in_gioco = True
            while in_gioco:

                # --- Gestione eventi (tastiera e mouse) ---
                for evento in pygame.event.get():

                    # L'utente ha chiuso la finestra con la X
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        return  # esco completamente dal programma

                    # Click del mouse
                    if evento.type == pygame.MOUSEBUTTONDOWN:
                        gestisci_click(stato, evento.pos[0], evento.pos[1], pulsanti, p_ondata)

                    # Tasti premuti
                    if evento.type == pygame.KEYDOWN:

                        # R = riavvia la partita (solo se è game over)
                        if evento.key == pygame.K_r and stato["game_over"]:
                            # Salvo il punteggio nella classifica prima di ricominciare
                            if stato["punteggio"] > 0:
                                classifica.append(stato["punteggio"])
                                classifica.sort(reverse=True)
                                classifica = classifica[:5]  # tengo solo i top 5
                            # Azzero tutto per la nuova partita
                            stato    = crea_stato()
                            pulsanti = {}
                            p_ondata = None

                        # ESC = comportamento diverso a seconda del contesto
                        elif evento.key == pygame.K_ESCAPE:
                            if stato["game_over"]:
                                in_gioco = False  # torna al menu principale
                            else:
                                stato["torre_scelta"] = None  # deseleziona la torre

                # --- Aggiornamento e disegno (solo se la partita è ancora attiva) ---
                if in_gioco:
                    aggiorna_gioco(stato)
                    pulsanti, p_ondata = disegna_schermo(
                        schermo, stato, immagini, classifica,
                        font_grande, font_medio, font_piccolo
                    )
                    pygame.display.flip()   # mostra il frame disegnato
                    clock.tick(FPS)         # limita a 60 frame al secondo

    pygame.quit()

# COSTANTI

# Dimensioni della finestra
LARGHEZZA_SCHERMO  = 1350
ALTEZZA_SCHERMO    = 694
LARGHEZZA_GIOCO    = 1130  # zona sinistra dove si gioca
LARGHEZZA_PANNELLO = 220   # pannello laterale destro

# Griglia di gioco: il campo è diviso in celle quadrate
DIM_CELLA = 30  # ogni cella è 30x30 pixel
CELLE_X   = 38  # numero di celle in orizzontale
CELLE_Y   = 23  # numero di celle in verticale

# Colori (formato RGB)
NERO         = (0,   0,   0)
BIANCO       = (255, 255, 255)
GRIGIO       = (128, 128, 128)
GRIGIO_SCURO = (40,  40,  50)
GRIGIO_MED   = (65,  65,  80)
BLU          = (30,  144, 255)
VIOLA        = (147, 112, 219)
ARANCIONE    = (255, 140,  0)
ROSSO        = (220,  20, 60)
GIALLO       = (255, 215,  0)
VERDE        = (0,   200,  0)
VERDE_ERBA   = (34,  139, 34)
VERDE_SCURO  = (0,   100,  0)
MARRONE      = (139,  90, 43)

# Percorso che i nemici seguono, scritto come lista di celle (colonna, riga).
# BUG ORIGINALE CORRETTO: mancava una virgola dopo (3,14) → errore di sintassi.
PERCORSO = [
    (0,19),(1,19),(2,19),(3,19),                                                            # entra da sinistra
    (3,18),(3,17),(3,16),(3,15),(3,14),                                                     # sale verso l'alto
    (4,14),(5,14),(6,14),                                                                   # curva a destra
    (6,13),(6,12),(6,11),(6,10),(6,9),(6,8),(6,7),(6,6),(6,5),                              # lunga salita
    (7,5),(8,5),(9,5),(10,5),(11,5),(12,5),                                                 # tratto in cima
    (12,6),(12,7),(12,8),                                                                   # scende un po'
    (13,8),(14,8),(15,8),(16,8),(17,8),(18,8),(19,8),(20,8),                                # tratto orizzontale
    (20,9),(20,10),(20,11),(20,12),(20,13),(20,14),(20,15),(20,16),(20,17),                 # lunga discesa
    (21,17),(22,17),(23,17),(24,17),(25,17),(26,17),(27,17),(28,17),(29,17),(30,17),(31,17),# tratto in basso
    (31,16),(31,15),(31,14),(31,13),(31,12),(31,11),                                        # risale
    (32,11),(33,11),(34,11),(35,11),(36,11),(37,11),                                        # esce a destra
]

# Parametri generali della partita
SOLDI_INIZIO  = 300   # soldi con cui si inizia
VITE_INIZIO   = 15    # vite con cui si inizia
ONDATE_TOTALI = 10    # numero di ondate da superare per vincere
BONUS_ONDATA  = 50    # soldi extra dati al giocatore dopo ogni ondata
FRAME_SPAWN   = 60    # quanti frame aspettare tra un nemico e il successivo
FPS           = 60    # frame al secondo

# Costo in soldi per comprare ogni tipo di torre
COSTO_TORRE = {
    "arciere": 100,
    "magia":   150,
    "cannone": 200,
}

# Statistiche delle torri: (raggio di attacco, danno, frame tra spari, colore)
STATS_TORRE = {
    "arciere": (120, 15,  60, BLU),
    "cannone": (200, 40, 120, VIOLA),
    "magia":   (100,  8,  20, ARANCIONE),
}


# ============================================================
# IMMAGINI
# ============================================================

def carica_immagini():
    # Cerco i file nella stessa cartella dello script
    cartella = os.path.dirname(os.path.abspath(__file__))
    im = {}

    # Sfondo del campo di gioco e immagine del menu principale
    im["sfondo"] = carica_singola(cartella, "sfondo.png",             (LARGHEZZA_GIOCO, ALTEZZA_SCHERMO), alpha=False)
    im["menu"]   = carica_singola(cartella, "schermata_iniziale.png", (LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), alpha=False)
    im["moneta"] = carica_singola(cartella, "moneta.png", (24, 24))

    # Per ogni tipo di nemico carico 2 immagini base e ne ricavo 4 direzioni
    for tipo in ("goblin", "orco", "demone"):
        verso_destra = carica_singola(cartella, f"{tipo}_versodestra.png", (60, 60))
        verso_alto   = carica_singola(cartella, f"{tipo}_versoalto.png",   (60, 60))

        im[f"{tipo}_destra"]   = verso_destra
        im[f"{tipo}_sinistra"] = pygame.transform.flip(verso_destra, True, False)  if verso_destra else None
        im[f"{tipo}_alto"]     = verso_alto
        im[f"{tipo}_basso"]    = pygame.transform.flip(verso_alto,   False, True)  if verso_alto   else None

    # Sprite delle torri e dei proiettili
    for tipo in ("arciere", "cannone", "magia"):
        im[f"torre_{tipo}"] = carica_singola(cartella, f"torre_{tipo}.png", (68, 68))
        im[f"colpo_{tipo}"] = carica_singola(cartella, f"colpo_{tipo}.png", (22, 22))

    return im

def carica_singola(cartella, nome_file, dimensione, alpha=True):
    # Provo a caricare il file; se non esiste restituisco None
    # (le funzioni di disegno useranno forme geometriche come alternativa)
    try:
        percorso = os.path.join(cartella, nome_file)
        if alpha:
            img = pygame.image.load(percorso).convert_alpha()
        else:
            img = pygame.image.load(percorso).convert()
        return pygame.transform.scale(img, dimensione)
    except Exception:
        return None

# MENU PRINCIPALE

def mostra_menu(schermo, immagini, clock):
    # Mostra il menu e aspetta che l'utente clicchi o prema un tasto
    # Ritorna: "gioca", "istruzioni" oppure "esci"

    while True:
        # Disegno lo sfondo del menu (ridisegno ogni frame così
        # lo schermo non rimane bloccato sull'ultimo frame di gioco)
        sfondo = immagini.get("menu")
        if sfondo:
            schermo.blit(sfondo, (0, 0))
        else:
            schermo.fill((20, 20, 40))  # colore di riserva se manca l'immagine

        pygame.display.flip()
        clock.tick(FPS)

        # Rettangoli invisibili sovrapposti ai pulsanti dell'immagine
        # (le posizioni dipendono da dove sono disegnati i pulsanti nell'immagine)
        cx = LARGHEZZA_SCHERMO // 2
        area_gioca     = pygame.Rect(cx - 110, 546, 220, 58)
        area_istruzioni= pygame.Rect(cx - 90,  612, 180, 34)
        area_esci      = pygame.Rect(cx - 60,  650, 120, 34)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "esci"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "gioca"
                if evento.key == pygame.K_ESCAPE:
                    return "esci"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                x, y = evento.pos
                if area_gioca.collidepoint(x, y):
                    return "gioca"
                if area_istruzioni.collidepoint(x, y):
                    return "istruzioni"
                if area_esci.collidepoint(x, y):
                    return "esci"

# SCHERMATA ISTRUZIONI

def mostra_istruzioni(schermo, immagini, font_grande, font_medio, font_piccolo, clock):
    # Mostra una schermata con le istruzioni di gioco
    # Ritorna True se si vuole tornare al menu, False se si chiude il gioco

    # Lista di righe da mostrare: (titolo, descrizione)
    # Se descrizione è "" la riga è un'intestazione di sezione
    righe = [
        ("TORRI", ""),
        ("Arciere  $100", "Raggio 120 | Danno 15 | Cadenza media"),
        ("Magia    $150", "Raggio 100 | Danno 8  | Cadenza alta"),
        ("Cannone  $200", "Raggio 200 | Danno 40 | Cadenza bassa"),
        ("", ""),
        ("CONTROLLI", ""),
        ("Clic su un pulsante", "Seleziona il tipo di torre"),
        ("Clic sul campo",      "Piazza la torre (non sul sentiero)"),
        ("Avvia Ondata",        "Fa apparire i nemici"),
        ("ESC",                 "Deseleziona la torre corrente"),
        ("R",                   "Riavvia dopo il Game Over"),
        ("", ""),
        ("PUNTEGGIO", ""),
        ("Nemico ucciso",       "× 100 punti"),
        ("Ondata completata",   "× 500 punti"),
        ("Vita rimasta",        "× 200 punti"),
        ("Vittoria",            "+ 2000 bonus"),
    ]

    while True:
        # Sfondo
        sfondo = immagini.get("menu")
        if sfondo:
            schermo.blit(sfondo, (0, 0))
        else:
            schermo.fill((20, 20, 40))

        # Rettangolo scuro semitrasparente sopra lo sfondo
        velo = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), pygame.SRCALPHA)
        velo.fill((0, 0, 0, 180))
        schermo.blit(velo, (0, 0))

        # Box centrale con le istruzioni
        box = pygame.Rect(150, 40, 700, 590)
        pygame.draw.rect(schermo, (30, 30, 45), box, border_radius=16)
        pygame.draw.rect(schermo, GIALLO, box, 3, border_radius=16)

        # Titolo
        t = font_grande.render("ISTRUZIONI", True, GIALLO)
        schermo.blit(t, (LARGHEZZA_SCHERMO // 2 - t.get_width() // 2, 58))
        pygame.draw.line(schermo, GIALLO, (200, 108), (800, 108), 1)

        # Righe di testo
        y = 122
        for titolo_riga, descrizione in righe:
            if titolo_riga == "":
                y += 8  # riga vuota = spazio extra
                continue
            if descrizione == "":
                # È un'intestazione di sezione: scritta in giallo
                schermo.blit(font_medio.render(titolo_riga, True, GIALLO), (220, y))
            else:
                # È una voce normale: titolo bianco + descrizione grigia
                schermo.blit(font_medio.render(titolo_riga,  True, BIANCO),         (220, y))
                schermo.blit(font_piccolo.render(descrizione, True, (180, 180, 180)), (430, y + 4))
            y += 28

        # Pulsante Indietro
        btn = pygame.Rect(400, 570, 200, 44)
        pygame.draw.rect(schermo, (60, 20, 20), btn, border_radius=10)
        pygame.draw.rect(schermo, ROSSO, btn, 2, border_radius=10)
        lbl = font_medio.render("← INDIETRO", True, BIANCO)
        schermo.blit(lbl, (btn.x + (200 - lbl.get_width()) // 2,
                           btn.y + (44  - lbl.get_height()) // 2))

        pygame.display.flip()
        clock.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return True
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(evento.pos):
                    return True

# STATO DI GIOCO
def crea_stato():
    # Restituisce un dizionario con tutti i dati di una partita nuova.
    # È il "cervello" del gioco: tutto passa da qui.
    return {
        "soldi":        SOLDI_INIZIO,
        "vite":         VITE_INIZIO,
        "ondata":       0,           # ondata attuale (0 = nessuna ancora iniziata)
        "in_corso":     False,       # True mentre i nemici stanno arrivando
        "da_spawnare":  0,           # nemici che devono ancora apparire in questa ondata
        "timer_spawn":  0,           # conta i frame tra uno spawn e il successivo
        "nemici":       [],          # lista dei nemici presenti in campo
        "torri":        [],          # lista delle torri piazzate
        "proiettili":   [],          # lista dei proiettili in volo
        "monete_anim":  [],          # animazioni "+$X" quando un nemico muore
        "torre_scelta": None,        # tipo di torre selezionata per il piazzamento
        "game_over":    False,
        "vittoria":     False,
        "punti":        0,           # punti accumulati (100 per ogni nemico ucciso)
        "punteggio":    0,           # punteggio finale, calcolato a fine partita
    }

# PUNTEGGIO

def calcola_punteggio(stato):
    # Formula: nemici uccisi × 100 + ondate × 500 + vite rimaste × 200 + 2000 se vinto
    return (
        stato["punti"] +
        stato["ondata"] * 500 +
        stato["vite"]   * 200 +
        (2000 if stato["vittoria"] else 0)
    )

# AGGIORNAMENTO GIOCO (chiamato ogni frame)

def aggiorna_gioco(stato):
    # Se la partita è finita non faccio nulla
    if stato["game_over"]:
        return

    # Converto il percorso in pixel (lo uso più volte in questa funzione)
    percorso = percorso_in_pixel()

    # --- Fase 1: faccio apparire i nemici uno alla volta ---
    if stato["in_corso"] and stato["da_spawnare"] > 0:
        stato["timer_spawn"] += 1
        if stato["timer_spawn"] >= FRAME_SPAWN:
            # È arrivato il momento di far apparire un nuovo nemico
            nemico = crea_nemico(stato["ondata"])
            nemico["x"], nemico["y"] = percorso[0]  # parte dall'inizio del percorso
            stato["nemici"].append(nemico)
            stato["da_spawnare"] -= 1
            stato["timer_spawn"]  = 0

    # --- Fase 2: muovo ogni nemico lungo il percorso ---
    for nemico in stato["nemici"][:]:  # uso una copia perché potrei rimuovere elementi
        arrivato = muovi_nemico(nemico, percorso)
        if arrivato:
            # Il nemico ha raggiunto la fine: il giocatore perde una vita
            stato["vite"]  -= 1
            stato["nemici"].remove(nemico)
            if stato["vite"] <= 0:
                # Vite esaurite: game over
                stato["game_over"] = True
                stato["vittoria"]  = False
                stato["punteggio"] = calcola_punteggio(stato)

    # --- Fase 3: ogni torre cerca un bersaglio e spara ---
    for torre in stato["torri"]:
        aggiorna_torre(torre, stato["nemici"])
        proiettile = spara(torre)
        if proiettile:
            stato["proiettili"].append(proiettile)

    # --- Fase 4: muovo i proiettili e applico i danni ---
    for proiettile in stato["proiettili"][:]:
        colpito = muovi_proiettile(proiettile)
        if colpito:
            bersaglio = proiettile["bersaglio"]
            if bersaglio and bersaglio["salute"] > 0:
                # Applico il danno
                bersaglio["salute"] -= proiettile["danno"]
                if bersaglio["salute"] <= 0:
                    # Nemico ucciso: guadagno soldi e mostro l'animazione moneta
                    stato["soldi"] += bersaglio["ricompensa"]
                    stato["punti"] += 100
                    animazione = crea_animazione_moneta(bersaglio["x"], bersaglio["y"], bersaglio["ricompensa"])
                    stato["monete_anim"].append(animazione)
                    if bersaglio in stato["nemici"]:
                        stato["nemici"].remove(bersaglio)
            stato["proiettili"].remove(proiettile)

    # --- Fase 5: aggiorno le animazioni delle monete ---
    aggiorna_animazioni_monete(stato["monete_anim"])

    # --- Fase 6: controllo se l'ondata è finita ---
    if stato["in_corso"] and stato["da_spawnare"] == 0 and len(stato["nemici"]) == 0:
        stato["in_corso"] = False
        stato["soldi"]   += BONUS_ONDATA  # bonus a fine ondata

    # --- Fase 7: controllo se il giocatore ha vinto ---
    if stato["ondata"] >= ONDATE_TOTALI and not stato["in_corso"] and len(stato["nemici"]) == 0:
        stato["game_over"] = True
        stato["vittoria"]  = True
        stato["punteggio"] = calcola_punteggio(stato)

# GESTIONE CLICK DEL MOUSE
def gestisci_click(stato, x, y, pulsanti, pulsante_ondata):
    # Ignoro i click se la partita è finita
    if stato["game_over"]:
        return

    # Click su un pulsante torre nel pannello?
    for tipo, area in pulsanti.items():
        if area.collidepoint(x, y):
            if stato["soldi"] >= COSTO_TORRE[tipo]:
                # Toggle: se clicco la stessa torre già selezionata, la deseleziono
                if stato["torre_scelta"] == tipo:
                    stato["torre_scelta"] = None
                else:
                    stato["torre_scelta"] = tipo
            return  # il click è stato gestito

    # Click sul pulsante "Avvia Ondata"?
    if pulsante_ondata and pulsante_ondata.collidepoint(x, y):
        stato["ondata"]      += 1
        stato["da_spawnare"]  = 5 + stato["ondata"] * 3  # più nemici alle ondate alte
        stato["in_corso"]     = True
        stato["timer_spawn"]  = 0
        return

    # Click nell'area di gioco mentre ho una torre selezionata?
    if x < LARGHEZZA_GIOCO and stato["torre_scelta"]:
        cella_x, cella_y = x // DIM_CELLA, y // DIM_CELLA

        # Controllo che la cella sia libera
        sul_percorso   = (cella_x, cella_y) in PERCORSO
        gia_occupata   = any(t["cx"] == cella_x and t["cy"] == cella_y for t in stato["torri"])
        ho_abbastanza  = stato["soldi"] >= COSTO_TORRE[stato["torre_scelta"]]

        if not sul_percorso and not gia_occupata and ho_abbastanza:
            # Piazzo la torre e addebito il costo
            stato["torri"].append(crea_torre(cella_x, cella_y, stato["torre_scelta"]))
            stato["soldi"]       -= COSTO_TORRE[stato["torre_scelta"]]
            stato["torre_scelta"] = None  # deseleziono dopo il piazzamento

# COORDINATE: conversione cella ↔ pixel
def cella_a_pixel(cx, cy):
    # Restituisce il centro in pixel della cella (cx, cy)
    px = cx * DIM_CELLA + DIM_CELLA // 2
    py = cy * DIM_CELLA + DIM_CELLA // 2
    return px, py

def percorso_in_pixel():
    # Converte tutte le celle del PERCORSO in coordinate pixel
    return [cella_a_pixel(cx, cy) for cx, cy in PERCORSO]

# NEMICI
def crea_nemico(ondata):
    # Le statistiche del nemico crescono con il numero di ondata
    if ondata <= 3:
        tipo, salute_base, incremento, velocita_base, ricompensa_base = "goblin", 50, 20, 1.0, 20
    elif ondata <= 7:
        tipo, salute_base, incremento, velocita_base, ricompensa_base = "orco",   80, 25, 1.2, 30
    else:
        tipo, salute_base, incremento, velocita_base, ricompensa_base = "demone", 120, 30, 1.4, 40

    salute     = salute_base + ondata * incremento
    velocita   = min(velocita_base + ondata * 0.1, 3.0)  # max 3.0 per non saltare le waypoint
    ricompensa = ricompensa_base + ondata * 5

    return {
        "tipo":       tipo,
        "salute":     salute,
        "salute_max": salute,
        "velocita":   velocita,
        "ricompensa": ricompensa,
        "waypoint":   0,      # indice della prossima tappa nel percorso pixel
        "x":          0.0,
        "y":          0.0,
        "dir_x":      1,      # direzione orizzontale (usata per scegliere lo sprite)
        "dir_y":      0,      # direzione verticale
    }

def muovi_nemico(nemico, percorso):
    # Sposta il nemico di un passo verso la prossima waypoint.
    # Restituisce True se ha raggiunto la fine del percorso.

    if nemico["waypoint"] >= len(percorso) - 1:
        return True  # è già alla fine

    # Calcolo la direzione verso la prossima tappa
    prossima_x, prossima_y = percorso[nemico["waypoint"] + 1]
    dx = prossima_x - nemico["x"]
    dy = prossima_y - nemico["y"]
    distanza = math.sqrt(dx * dx + dy * dy)

    # Salvo la direzione per usarla nello sprite
    nemico["dir_x"] = dx
    nemico["dir_y"] = dy

    if distanza < nemico["velocita"]:
        # Sono abbastanza vicino: salto direttamente alla waypoint
        nemico["waypoint"] += 1
        nemico["x"], nemico["y"] = percorso[nemico["waypoint"]]
    else:
        # Avanzo nella direzione normalizzata
        nemico["x"] += (dx / distanza) * nemico["velocita"]
        nemico["y"] += (dy / distanza) * nemico["velocita"]

    return nemico["waypoint"] >= len(percorso) - 1

def disegna_nemico(schermo, nemico, immagini):
    x = int(nemico["x"])
    y = int(nemico["y"])

    # Scelgo lo sprite in base alla direzione di movimento prevalente
    if abs(nemico["dir_x"]) >= abs(nemico["dir_y"]):
        direzione = "destra" if nemico["dir_x"] > 0 else "sinistra"
    else:
        direzione = "basso" if nemico["dir_y"] > 0 else "alto"

    img = immagini.get(f"{nemico['tipo']}_{direzione}")

    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w // 2, y - h // 2))
        raggio = h // 2
    else:
        # Fallback: cerchio colorato se manca lo sprite
        colori = {"goblin": (0, 200, 0), "orco": (200, 50, 50), "demone": (150, 0, 200)}
        raggi  = {"goblin": 16, "orco": 19, "demone": 22}
        raggio = raggi[nemico["tipo"]]
        pygame.draw.circle(schermo, colori[nemico["tipo"]], (x, y), raggio)
        pygame.draw.circle(schermo, NERO, (x, y), raggio, 2)

    # Disegno la barra della salute sopra il nemico
    percentuale = nemico["salute"] / nemico["salute_max"]
    if percentuale > 0.5:
        colore_barra = VERDE
    elif percentuale > 0.25:
        colore_barra = GIALLO
    else:
        colore_barra = ROSSO

    barra_x = x - 22
    barra_y = y - raggio - 10
    pygame.draw.rect(schermo, (180, 0, 0),   (barra_x, barra_y, 44, 6))                     # sfondo rosso
    pygame.draw.rect(schermo, colore_barra,  (barra_x, barra_y, int(44 * percentuale), 6))  # vita rimasta

# TORRI

def crea_torre(cx, cy, tipo):
    # Crea una torre nella cella (cx, cy) del tipo scelto
    px, py = cella_a_pixel(cx, cy)
    raggio, danno, cooldown, colore = STATS_TORRE[tipo]
    return {
        "tipo":      tipo,
        "cx":        cx,       # posizione nella griglia
        "cy":        cy,
        "x":         px,       # posizione in pixel (centro)
        "y":         py,
        "raggio":    raggio,   # distanza massima di attacco
        "danno":     danno,
        "cd_max":    cooldown, # frame di attesa tra uno sparo e il successivo
        "cd":        0,        # cooldown attuale (conta da 0 a cd_max)
        "colore":    colore,
        "bersaglio": None,     # nemico preso di mira
    }

def aggiorna_torre(torre, nemici):
    # Decremento il cooldown
    if torre["cd"] > 0:
        torre["cd"] -= 1

    # Cerco il bersaglio migliore nel raggio della torre.
    torre["bersaglio"] = None
    for nemico in nemici:
        dx = nemico["x"] - torre["x"]
        dy = nemico["y"] - torre["y"]
        distanza = math.sqrt(dx * dx + dy * dy)

        if distanza <= torre["raggio"]:
            if torre["bersaglio"] is None:
                torre["bersaglio"] = nemico
            elif nemico["waypoint"] > torre["bersaglio"]["waypoint"]:
                torre["bersaglio"] = nemico  # più avanzato nel percorso
            elif nemico["waypoint"] == torre["bersaglio"]["waypoint"] and nemico["salute"] < torre["bersaglio"]["salute"]:
                torre["bersaglio"] = nemico  # stesso avanzamento ma più debole

def spara(torre):
    # Restituisce un proiettile se la torre può sparare, altrimenti None
    bersaglio = torre["bersaglio"]

    # Condizioni per sparare: c'è un bersaglio vivo e il cooldown è finito
    if bersaglio is None or bersaglio["salute"] <= 0 or torre["cd"] > 0:
        return None

    # Verifico che il bersaglio sia ancora nel raggio (potrebbe essersi mosso)
    dx = bersaglio["x"] - torre["x"]
    dy = bersaglio["y"] - torre["y"]
    if math.sqrt(dx * dx + dy * dy) > torre["raggio"]:
        return None

    # Sparo: reimposto il cooldown e creo il proiettile
    torre["cd"] = torre["cd_max"]
    return {
        "x":         float(torre["x"]),
        "y":         float(torre["y"]),
        "bersaglio": bersaglio,
        "danno":     torre["danno"],
        "tipo":      torre["tipo"],
        "angolo":    0,    # aggiornato ogni frame per ruotare lo sprite
        "velocita":  8,    # pixel per frame
    }

def disegna_torre(schermo, torre, immagini, mostra_raggio=False):
    x = int(torre["x"])
    y = int(torre["y"])

    # Se sto piazzando una torre, mostro il cerchio del raggio di attacco
    if mostra_raggio:
        r = torre["raggio"]
        superficie = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(superficie, (*torre["colore"], 40),  (r, r), r)      # area piena semitrasparente
        pygame.draw.circle(superficie, (*torre["colore"], 120), (r, r), r, 2)   # bordo
        schermo.blit(superficie, (x - r, y - r))

    img = immagini.get(f"torre_{torre['tipo']}")
    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w // 2, y - h // 2))
    else:
        # Fallback: quadrato colorato
        rettangolo = pygame.Rect(x - 16, y - 16, 32, 32)
        pygame.draw.rect(schermo, torre["colore"], rettangolo)
        pygame.draw.rect(schermo, NERO, rettangolo, 2)

# PROIETTILI
def muovi_proiettile(proiettile):
    # Muove il proiettile verso il bersaglio (inseguimento diretto).
    # Restituisce True se ha colpito oppure se il bersaglio è già morto.

    bersaglio = proiettile["bersaglio"]

    # Se il bersaglio è già morto, elimino il proiettile
    if bersaglio is None or bersaglio["salute"] <= 0:
        return True

    dx = bersaglio["x"] - proiettile["x"]
    dy = bersaglio["y"] - proiettile["y"]
    distanza = math.sqrt(dx * dx + dy * dy)

    # Se sono abbastanza vicino, considero il colpo andato a segno
    if distanza < proiettile["velocita"]:
        return True

    # Aggiorno l'angolo per ruotare lo sprite nella direzione giusta
    proiettile["angolo"] = -math.degrees(math.atan2(dy, dx))

    # Avanzo verso il bersaglio
    proiettile["x"] += (dx / distanza) * proiettile["velocita"]
    proiettile["y"] += (dy / distanza) * proiettile["velocita"]

    return False  # proiettile ancora in volo

def disegna_proiettile(schermo, proiettile, immagini):
    x = int(proiettile["x"])
    y = int(proiettile["y"])

    img = immagini.get(f"colpo_{proiettile['tipo']}")
    if img:
        # Ruoto lo sprite nella direzione di movimento
        img_ruotata = pygame.transform.rotate(img, proiettile["angolo"])
        w, h = img_ruotata.get_size()
        schermo.blit(img_ruotata, (x - w // 2, y - h // 2))
    else:
        # Fallback: cerchio colorato
        colori = {"arciere": (139, 90, 43), "cannone": (80, 80, 80), "magia": (255, 0, 255)}
        pygame.draw.circle(schermo, colori.get(proiettile["tipo"], BIANCO), (x, y), 4)


# ANIMAZIONI MONETE (+$X quando un nemico muore)
def crea_animazione_moneta(x, y, valore):
    # Crea un'animazione che sale verso l'alto e svanisce in 60 frame
    return {"x": float(x), "y": float(y), "valore": valore, "timer": 0, "durata": 60}

def aggiorna_animazioni_monete(animazioni):
    # Ogni frame: faccio salire l'icona di 1 pixel e rimuovo quelle scadute
    for anim in animazioni[:]:
        anim["timer"] += 1
        anim["y"]     -= 1
        if anim["timer"] >= anim["durata"]:
            animazioni.remove(anim)

def disegna_animazioni_monete(schermo, animazioni, immagini, font):
    for anim in animazioni:
        # L'opacità diminuisce con il passare del tempo
        alpha = max(0, 255 - int(255 * anim["timer"] / anim["durata"]))

        # Creo una piccola superficie trasparente dove disegno icona + testo
        superficie = pygame.Surface((60, 24), pygame.SRCALPHA)

        icona = immagini.get("moneta")
        if icona:
            icona_copia = icona.copy()
            icona_copia.set_alpha(alpha)
            superficie.blit(icona_copia, (0, 2))

        testo = font.render(f"+${anim['valore']}", True, GIALLO)
        testo.set_alpha(alpha)
        superficie.blit(testo, (24, 0))

        schermo.blit(superficie, (int(anim["x"]) - 10, int(anim["y"])))


# DISEGNO SCHERMO (chiamato ogni frame)

def disegna_schermo(schermo, stato, immagini, classifica, font_grande, font_medio, font_piccolo):
    # Disegna tutto sullo schermo, nell'ordine corretto (dal basso verso l'alto):
    # 1. Mappa (prato + griglia + sentiero)
    # 2. Torri
    # 3. Nemici
    # 4. Proiettili
    # 5. Animazioni monete
    # 6. Anteprima cella (se sto piazzando una torre)
    # 7. Pannello laterale
    # 8. Schermata di game over (se applicabile)
    # Restituisce (pulsanti, pulsante_ondata) per gestire i click del frame successivo

    disegna_mappa(schermo)

    # Mostro il raggio di tutte le torri mentre ne sto piazzando una nuova
    mostra_raggio = stato["torre_scelta"] is not None
    for torre in stato["torri"]:
        disegna_torre(schermo, torre, immagini, mostra_raggio)

    for nemico in stato["nemici"]:
        disegna_nemico(schermo, nemico, immagini)

    for proiettile in stato["proiettili"]:
        disegna_proiettile(schermo, proiettile, immagini)

    disegna_animazioni_monete(schermo, stato["monete_anim"], immagini, font_piccolo)

    # Anteprima verde/rossa sulla cella sotto il cursore
    if stato["torre_scelta"]:
        mx, my = pygame.mouse.get_pos()
        if mx < LARGHEZZA_GIOCO:
            cx, cy = mx // DIM_CELLA, my // DIM_CELLA
            disegna_anteprima_cella(schermo, stato, cx, cy)

    pulsanti, pulsante_ondata = disegna_pannello(schermo, stato, immagini, font_grande, font_medio, font_piccolo)

    if stato["game_over"]:
        disegna_game_over(schermo, stato, classifica, font_grande, font_medio, font_piccolo)

    return pulsanti, pulsante_ondata

def disegna_mappa(schermo):
    # Prato verde con griglia
    schermo.fill(VERDE_ERBA)
    for cx in range(CELLE_X):
        for cy in range(CELLE_Y):
            pygame.draw.rect(schermo, VERDE_SCURO,
                             (cx * DIM_CELLA, cy * DIM_CELLA, DIM_CELLA, DIM_CELLA), 1)
    # Sentiero marrone
    for cx, cy in PERCORSO:
        pygame.draw.rect(schermo, MARRONE, (cx * DIM_CELLA, cy * DIM_CELLA, DIM_CELLA, DIM_CELLA))

def disegna_anteprima_cella(schermo, stato, cx, cy):
    # Verde se posso piazzare la torre, rosso altrimenti
    sul_percorso  = (cx, cy) in PERCORSO
    gia_occupata  = any(t["cx"] == cx and t["cy"] == cy for t in stato["torri"])
    colore = VERDE if not sul_percorso and not gia_occupata else ROSSO

    superficie = pygame.Surface((DIM_CELLA, DIM_CELLA), pygame.SRCALPHA)
    superficie.fill((*colore, 100))  # semitrasparente
    schermo.blit(superficie, (cx * DIM_CELLA, cy * DIM_CELLA))

def disegna_pannello(schermo, stato, immagini, font_grande, font_medio, font_piccolo):
    X = LARGHEZZA_GIOCO  # coordinata x dove inizia il pannello

    # Sfondo del pannello
    pygame.draw.rect(schermo, GRIGIO_SCURO, (X, 0, LARGHEZZA_PANNELLO, ALTEZZA_SCHERMO))
    pygame.draw.rect(schermo, GRIGIO_MED,   (X + 2, 2, LARGHEZZA_PANNELLO - 4, ALTEZZA_SCHERMO - 4))
    pygame.draw.line(schermo, (100, 100, 120), (X, 0), (X, ALTEZZA_SCHERMO), 2)

    # Titolo del gioco
    titolo = font_grande.render("TOWER DEFENSE", True, GIALLO)
    schermo.blit(titolo, (X + (LARGHEZZA_PANNELLO - titolo.get_width()) // 2, 10))
    pygame.draw.line(schermo, GIALLO, (X + 10, 42), (X + LARGHEZZA_PANNELLO - 10, 42), 1)

    # Schede informative (soldi, vite, ondata, punteggio)
    # Ogni scheda ha: etichetta piccola in alto + valore grande in basso
    schede = [
        ("SOLDI",     f"$ {stato['soldi']}",        GIALLO,         52),
        ("VITE",      f"♥  {stato['vite']}",         ROSSO,         102),
        ("ONDATA",    f"{stato['ondata']} / 10",     BIANCO,        152),
        ("PUNTEGGIO", f"{calcola_punteggio(stato)}", (255, 165, 0), 202),
    ]
    for etichetta, valore, colore_valore, y in schede:
        rettangolo = pygame.Rect(X + 8, y, LARGHEZZA_PANNELLO - 16, 42)
        pygame.draw.rect(schermo, GRIGIO_SCURO, rettangolo, border_radius=6)
        pygame.draw.rect(schermo, (90, 90, 110),  rettangolo, 1, border_radius=6)
        schermo.blit(font_piccolo.render(etichetta, True, (160, 160, 180)), (X + 14, y + 4))
        schermo.blit(font_medio.render(valore,      True, colore_valore),   (X + 14, y + 20))

    # Separatore e pulsanti torre
    sep = font_piccolo.render("── TORRI ──", True, (180, 180, 200))
    schermo.blit(sep, (X + (LARGHEZZA_PANNELLO - sep.get_width()) // 2, 250))

    pulsanti = {}
    torri_da_mostrare = [
        ("arciere", "Arciere  $100", "Rng 120 | Dmg 15", 266),
        ("magia",   "Magia    $150", "Rng 100 | Dmg 8",  320),
        ("cannone", "Cannone  $200", "Rng 200 | Dmg 40", 374),
    ]
    for tipo, nome, dettaglio, y in torri_da_mostrare:
        # Colore del pulsante in base allo stato
        if stato["torre_scelta"] == tipo:
            colore_sfondo = (80, 70, 0)
            colore_bordo  = GIALLO   # selezionato
        elif stato["soldi"] >= COSTO_TORRE[tipo]:
            colore_sfondo = (0, 60, 0)
            colore_bordo  = VERDE    # acquistabile
        else:
            colore_sfondo = (50, 50, 60)
            colore_bordo  = GRIGIO   # non abbastanza soldi

        btn = pygame.Rect(X + 8, y, LARGHEZZA_PANNELLO - 16, 46)
        pygame.draw.rect(schermo, colore_sfondo, btn, border_radius=6)
        pygame.draw.rect(schermo, colore_bordo,  btn, 2, border_radius=6)
        schermo.blit(font_medio.render(nome,      True, BIANCO),          (X + 14, y + 4))
        schermo.blit(font_piccolo.render(dettaglio, True, (160, 160, 180)), (X + 14, y + 26))
        pulsanti[tipo] = btn

    # Pulsante "Avvia Ondata" (scompare mentre l'ondata è in corso)
    pulsante_ondata = None
    if not stato["in_corso"]:
        btn_on = pygame.Rect(X + 8, 432, LARGHEZZA_PANNELLO - 16, 48)
        pygame.draw.rect(schermo, (20, 60, 130), btn_on, border_radius=8)
        pygame.draw.rect(schermo, BLU,           btn_on, 2, border_radius=8)
        testo = font_medio.render("▶  Avvia Ondata", True, BIANCO)
        schermo.blit(testo, (
            btn_on.x + (btn_on.width  - testo.get_width())  // 2,
            btn_on.y + (btn_on.height - testo.get_height()) // 2
        ))
        pulsante_ondata = btn_on

    # Legenda tasti in fondo al pannello
    pygame.draw.line(schermo, (90, 90, 110),
                     (X + 10, ALTEZZA_SCHERMO - 60),
                     (X + LARGHEZZA_PANNELLO - 10, ALTEZZA_SCHERMO - 60), 1)
    schermo.blit(font_piccolo.render("ESC  deseleziona torre",  True, (140, 140, 160)), (X + 10, ALTEZZA_SCHERMO - 52))
    schermo.blit(font_piccolo.render("R    riavvia (game over)", True, (140, 140, 160)), (X + 10, ALTEZZA_SCHERMO - 34))

    return pulsanti, pulsante_ondata

def disegna_game_over(schermo, stato, classifica, font_grande, font_medio, font_piccolo):
    # Overlay scuro semitrasparente sopra il gioco
    velo = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), pygame.SRCALPHA)
    velo.fill((0, 0, 0, 160))
    schermo.blit(velo, (0, 0))

    cx = LARGHEZZA_SCHERMO // 2  # centro orizzontale dello schermo

    if stato["vittoria"]:
        titolo    = font_grande.render("VITTORIA!", True, GIALLO)
        colore_box = (40, 80, 0)
    else:
        titolo    = font_grande.render("GAME OVER", True, ROSSO)
        colore_box = (80, 0, 0)

    # Box centrale
    box = pygame.Rect(cx - 250, 60, 500, 560)
    pygame.draw.rect(schermo, colore_box, box, border_radius=14)
    pygame.draw.rect(schermo, BIANCO,     box, 3, border_radius=14)

    schermo.blit(titolo, (cx - titolo.get_width() // 2, 85))

    # Punteggio
    t_punteggio = font_medio.render(f"Punteggio: {stato['punteggio']}", True, (255, 165, 0))
    schermo.blit(t_punteggio, (cx - t_punteggio.get_width() // 2, 165))

    t_formula = font_piccolo.render("nemici×100 + ondate×500 + vite×200 + vittoria 2000", True, (180, 180, 180))
    schermo.blit(t_formula, (cx - t_formula.get_width() // 2, 205))

    # Classifica
    pygame.draw.line(schermo, GIALLO, (cx - 180, 245), (cx + 180, 245), 2)
    t_cls = font_medio.render("MIGLIORI PUNTEGGI", True, GIALLO)
    schermo.blit(t_cls, (cx - t_cls.get_width() // 2, 258))

    posti    = ["1.", "2.", "3.", "4.", "5."]
    colori_c = [GIALLO, (192, 192, 192), (205, 127, 50), BIANCO, BIANCO]
    for i, punteggio in enumerate(classifica[:5]):
        t = font_medio.render(f"{posti[i]}  {punteggio}", True, colori_c[i])
        schermo.blit(t, (cx - t.get_width() // 2, 295 + i * 36))

    # Istruzioni per continuare
    t_fine = font_piccolo.render("R = ricomincia   |   ESC = torna al menu", True, BIANCO)
    schermo.blit(t_fine, (cx - t_fine.get_width() // 2, 510))

# AVVIO DEL GIOCO

main()
