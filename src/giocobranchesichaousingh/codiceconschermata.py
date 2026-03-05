"""
=============================================================================
TOWER DEFENSE - GIOCO COMPLETO CON GRAFICA
=============================================================================
"""

import pygame
import math
import os

# =============================================================================
# CONFIGURAZIONE GENERALE
# =============================================================================

LARGHEZZA_SCHERMO = 1350
ALTEZZA_SCHERMO = 694

DIMENSIONE_CELLA = 30
CELLE_LARGHE = 45
CELLE_ALTE = 23

VERDE_ERBA = (34, 139, 34)
VERDE_SCURO = (0, 100, 0)
MARRONE_SENTIERO = (139, 90, 43)
GRIGIO = (128, 128, 128)
NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
BLU = (30, 144, 255)
VIOLA = (147, 112, 219)
ARANCIONE = (255, 140, 0)
ROSSO = (220, 20, 60)
GIALLO = (255, 215, 0)
VERDE_CHIARO = (0, 255, 0)

PERCORSO_GRIGLIA = [
    (0, 4), (1, 4), (2, 4),
    (2, 5), (2, 6), (2, 7), (2, 8),
    (3, 8), (4, 8), (5, 8), (6, 8), (7, 8),
    (7, 9), (7, 10),
    (8, 10), (9, 10), (10, 10), (11, 10),
    (11, 9), (11, 8), (11, 7), (11, 6), (11, 5), (11, 4),
    (12, 4), (13, 4), (14, 4),
    (14, 5), (14, 6), (14, 7), (14, 8),
    (15, 8), (16, 8)
]

SOLDI_INIZIALI = 300
VITE_INIZIALI = 20
ONDATE_TOTALI = 10
BONUS_FINE_ONDATA = 50
FRAME_TRA_SPAWN = 60

COSTI_TORRI = {
    'arciere': 100,
    'magia': 150,
    'cannone': 200
}

FPS = 60


# =============================================================================
# CARICAMENTO IMMAGINI
# =============================================================================

def carica_immagini():
    cartella = os.path.dirname(os.path.abspath(__file__))
    immagini = {}

    DIM_NEMICO     = (50, 50)
    DIM_TORRE      = (44, 44)
    DIM_PROIETTILE = (16, 16)
    DIM_MONETA     = (20, 20)

    def carica(nome_file, dimensione):
        percorso = os.path.join(cartella, nome_file)
        try:
            img = pygame.image.load(percorso).convert_alpha()
            return pygame.transform.scale(img, dimensione)
        except Exception:
            surf = pygame.Surface(dimensione, pygame.SRCALPHA)
            surf.fill((255, 0, 255, 180))
            return surf

    def carica_sfondo(nome_file):
        percorso = os.path.join(cartella, nome_file)
        try:
            img = pygame.image.load(percorso).convert()
            return pygame.transform.scale(img, (LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
        except Exception:
            return None

    # Schermata iniziale
    immagini['schermata_iniziale'] = carica_sfondo('schermata_iniziale.png')

    # Nemici
    immagini['goblin_destra']   = carica('goblin_versodestra.png', DIM_NEMICO)
    immagini['goblin_alto']     = carica('goblin_versoalto.png',   DIM_NEMICO)
    immagini['goblin_basso']    = pygame.transform.flip(carica('goblin_versoalto.png', DIM_NEMICO), False, True)
    immagini['goblin_sinistra'] = pygame.transform.flip(immagini['goblin_destra'], True, False)

    immagini['orco_destra']     = carica('orco_versodestra.png',   DIM_NEMICO)
    immagini['orco_alto']       = carica('orco_versoalto.png',     DIM_NEMICO)
    immagini['orco_basso']      = pygame.transform.flip(carica('orco_versoalto.png', DIM_NEMICO), False, True)
    immagini['orco_sinistra']   = pygame.transform.flip(immagini['orco_destra'], True, False)

    immagini['demone_destra']   = carica('demone_versodestra.png', DIM_NEMICO)
    immagini['demone_alto']     = carica('demone_versoalto.png',   DIM_NEMICO)
    immagini['demone_basso']    = pygame.transform.flip(carica('demone_versoalto.png', DIM_NEMICO), False, True)
    immagini['demone_sinistra'] = pygame.transform.flip(immagini['demone_destra'], True, False)

    # Torri
    immagini['torre_arciere'] = carica('torre_arciere.png', DIM_TORRE)
    immagini['torre_cannone'] = carica('torre_cannone.png', DIM_TORRE)
    immagini['torre_magia']   = carica('torre_magia.png',   DIM_TORRE)

    # Proiettili
    immagini['colpo_arciere'] = carica('colpo_arciere.png', DIM_PROIETTILE)
    immagini['colpo_cannone'] = carica('colpo_cannone.png', DIM_PROIETTILE)
    immagini['colpo_magia']   = carica('colpo_magia.png',   DIM_PROIETTILE)

    # Moneta
    immagini['moneta'] = carica('moneta.png', DIM_MONETA)

    return immagini


def ottieni_immagine_nemico(immagini, tipo, dx, dy):
    if abs(dx) >= abs(dy):
        direzione = 'destra' if dx > 0 else 'sinistra'
    else:
        direzione = 'basso' if dy > 0 else 'alto'
    chiave = f'{tipo}_{direzione}'
    return immagini.get(chiave, immagini.get(f'{tipo}_destra'))


# =============================================================================
# SCHERMATA INIZIALE
# =============================================================================

def disegna_schermata_iniziale(schermo, immagini, font_medio):
    """
    Mostra schermata_iniziale.png come sfondo a schermo intero.
    I 3 pulsanti (AVVIA, IMPOSTAZIONI, ESCI) sono sovrapposti
    nelle posizioni corrispondenti all'immagine originale.
    """

    # Sfondo: immagine a schermo intero
    sfondo = immagini.get('schermata_iniziale')
    if sfondo:
        schermo.blit(sfondo, (0, 0))
    else:
        # Fallback se l'immagine manca
        schermo.fill((20, 20, 40))
        font_tmp = pygame.font.Font(None, 48)
        t = font_tmp.render("schermata_iniziale.png non trovata", True, ROSSO)
        schermo.blit(t, (LARGHEZZA_SCHERMO // 2 - t.get_width() // 2, 300))

    # -------------------------------------------------------
    # Pulsanti sovrapposti — posizioni calibrate sull'immagine
    # L'immagine originale è 1228×921, scalata a 1000×700
    # scala_x = 1000/1228 ≈ 0.815   scala_y = 700/921 ≈ 0.760
    #
    # AVVIA:         centro ~(614, 748) orig → (500, 569) scaled  largh ~280
    # IMPOSTAZIONI:  centro ~(614, 830) orig → (500, 631) scaled  largh ~200
    # ESCI:          centro ~(614, 886) orig → (500, 674) scaled  largh ~140
    # -------------------------------------------------------

    # AVVIA
    w_avvia = 220
    h_avvia = 58
    r_avvia = pygame.Rect(0, 0, w_avvia, h_avvia)
    r_avvia.centerx = LARGHEZZA_SCHERMO // 2
    r_avvia.centery = 575
    # Overlay semi-trasparente per rendere cliccabile ma non coprire l'arte
    overlay_avvia = pygame.Surface((w_avvia, h_avvia), pygame.SRCALPHA)
    overlay_avvia.fill((0, 0, 0, 0))   # completamente trasparente: cliccabile ma invisibile
    schermo.blit(overlay_avvia, r_avvia.topleft)

    # IMPOSTAZIONI
    w_imp = 180
    h_imp = 34
    r_imp = pygame.Rect(0, 0, w_imp, h_imp)
    r_imp.centerx = LARGHEZZA_SCHERMO // 2
    r_imp.centery = 636
    overlay_imp = pygame.Surface((w_imp, h_imp), pygame.SRCALPHA)
    overlay_imp.fill((0, 0, 0, 0))
    schermo.blit(overlay_imp, r_imp.topleft)

    # ESCI
    w_esci = 120
    h_esci = 34
    r_esci = pygame.Rect(0, 0, w_esci, h_esci)
    r_esci.centerx = LARGHEZZA_SCHERMO // 2
    r_esci.centery = 674
    overlay_esci = pygame.Surface((w_esci, h_esci), pygame.SRCALPHA)
    overlay_esci.fill((0, 0, 0, 0))
    schermo.blit(overlay_esci, r_esci.topleft)

    return r_avvia, r_imp, r_esci


def schermata_iniziale_loop(schermo, immagini, font_medio, clock):
    """
    Loop della schermata iniziale.
    Ritorna: 'gioca', 'impostazioni', o False (esci)
    """
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return 'gioca'
                if evento.key == pygame.K_ESCAPE:
                    return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                r_avvia, r_imp, r_esci = disegna_schermata_iniziale(schermo, immagini, font_medio)
                if r_avvia.collidepoint(mx, my):
                    return 'gioca'
                if r_imp.collidepoint(mx, my):
                    return 'impostazioni'
                if r_esci.collidepoint(mx, my):
                    return False

        disegna_schermata_iniziale(schermo, immagini, font_medio)
        pygame.display.flip()
        clock.tick(FPS)


def schermata_impostazioni_loop(schermo, immagini, font_grande, font_medio, font_piccolo, clock):
    """
    Schermata impostazioni semplice con le istruzioni di gioco.
    Premi ESC o clicca INDIETRO per tornare al menu.
    """
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return True
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = evento.pos
                if r_indietro.collidepoint(mx, my):
                    return True

        # Sfondo
        sfondo = immagini.get('schermata_iniziale')
        if sfondo:
            schermo.blit(sfondo, (0, 0))
        else:
            schermo.fill((20, 20, 40))

        # Overlay scuro
        overlay = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        schermo.blit(overlay, (0, 0))

        # Box
        box = pygame.Rect(150, 60, 700, 560)
        pygame.draw.rect(schermo, (30, 30, 45), box, border_radius=16)
        pygame.draw.rect(schermo, GIALLO, box, 3, border_radius=16)

        t = font_grande.render("IMPOSTAZIONI", True, GIALLO)
        schermo.blit(t, (LARGHEZZA_SCHERMO // 2 - t.get_width() // 2, 80))
        pygame.draw.line(schermo, GIALLO, (200, 130), (800, 130), 1)

        istruzioni = [
            ("TORRI",           ""),
            ("Arciere  $100",   "Raggio 120 · Danno 15 · Velocità media"),
            ("Magia    $150",   "Raggio 100 · Danno 8  · Velocità alta"),
            ("Cannone  $200",   "Raggio 200 · Danno 40 · Velocità bassa"),
            ("",                ""),
            ("CONTROLLI",       ""),
            ("Clic su torre",   "Seleziona il tipo di torre"),
            ("Clic sul campo",  "Piazza la torre (non sul sentiero)"),
            ("Avvia Ondata",    "Fa partire i nemici"),
            ("ESC",             "Deseleziona la torre"),
            ("R",               "Riavvia dopo Game Over"),
            ("",                ""),
            ("OBIETTIVO",       ""),
            ("Sopravvivi",      "a tutte e 10 le ondate senza perdere le 20 vite"),
        ]

        y = 150
        for chiave, valore in istruzioni:
            if chiave == "" :
                y += 8
                continue
            if valore == "":
                t_k = font_medio.render(chiave, True, GIALLO)
                schermo.blit(t_k, (220, y))
            else:
                t_k = font_medio.render(chiave, True, BIANCO)
                t_v = font_piccolo.render(valore, True, (180, 180, 180))
                schermo.blit(t_k, (220, y))
                schermo.blit(t_v, (430, y + 4))
            y += 30

        # Pulsante INDIETRO
        r_indietro = pygame.Rect(400, 575, 200, 45)
        pygame.draw.rect(schermo, (60, 20, 20), r_indietro, border_radius=10)
        pygame.draw.rect(schermo, ROSSO, r_indietro, 2, border_radius=10)
        t_ind = font_medio.render("← INDIETRO", True, BIANCO)
        schermo.blit(t_ind, (r_indietro.x + (200 - t_ind.get_width()) // 2,
                               r_indietro.y + (45 - t_ind.get_height()) // 2))

        pygame.display.flip()
        clock.tick(FPS)


# =============================================================================
# FUNZIONI DI CONVERSIONE
# =============================================================================

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

def calcola_statistiche_nemici(ondata):
    if ondata <= 3:
        tipo = 'goblin'
        salute_base, incremento_salute, velocita_base, ricompensa_base = 50, 20, 1.0, 20
    elif ondata <= 7:
        tipo = 'orco'
        salute_base, incremento_salute, velocita_base, ricompensa_base = 80, 25, 1.2, 30
    else:
        tipo = 'demone'
        salute_base, incremento_salute, velocita_base, ricompensa_base = 120, 30, 1.4, 40

    salute   = salute_base + (ondata * incremento_salute)
    velocita = min(velocita_base + (ondata * 0.1), 3.0)
    ricompensa = ricompensa_base + (ondata * 5)
    return (tipo, salute, velocita, ricompensa)


def calcola_numero_nemici(ondata):
    return 5 + (ondata * 3)


# =============================================================================
# LOGICA DEI NEMICI
# =============================================================================

def crea_nemico(salute, velocita, ricompensa, tipo='goblin'):
    return {
        'salute_max': salute, 'salute': salute,
        'velocita': velocita, 'ricompensa': ricompensa,
        'indice_percorso': 0, 'x': 0, 'y': 0,
        'tipo': tipo, 'dx': 1, 'dy': 0
    }


def muovi_nemico(nemico, percorso_pixel):
    if nemico['indice_percorso'] < len(percorso_pixel) - 1:
        tx, ty = percorso_pixel[nemico['indice_percorso'] + 1]
        dx = tx - nemico['x']
        dy = ty - nemico['y']
        distanza = math.sqrt(dx**2 + dy**2)
        nemico['dx'] = dx
        nemico['dy'] = dy
        if distanza < nemico['velocita']:
            nemico['indice_percorso'] += 1
            if nemico['indice_percorso'] < len(percorso_pixel):
                nemico['x'], nemico['y'] = percorso_pixel[nemico['indice_percorso']]
        else:
            nemico['x'] += (dx / distanza) * nemico['velocita']
            nemico['y'] += (dy / distanza) * nemico['velocita']
    return nemico['indice_percorso'] >= len(percorso_pixel) - 1


def danneggia_nemico(nemico, danno):
    nemico['salute'] -= danno
    return nemico['salute'] <= 0


def disegna_nemico(schermo, nemico, immagini):
    x, y = int(nemico['x']), int(nemico['y'])
    img = ottieni_immagine_nemico(immagini, nemico['tipo'], nemico['dx'], nemico['dy'])
    w, h = img.get_size()
    schermo.blit(img, (x - w // 2, y - h // 2))

    lb, ab = 34, 5
    xb = x - lb // 2
    yb = y - h // 2 - 10
    pct = nemico['salute'] / nemico['salute_max']
    pygame.draw.rect(schermo, (180, 0, 0), (xb, yb, lb, ab))
    cb = VERDE_CHIARO if pct > 0.5 else (GIALLO if pct > 0.25 else ROSSO)
    pygame.draw.rect(schermo, cb, (xb, yb, int(lb * pct), ab))
    pygame.draw.rect(schermo, NERO, (xb, yb, lb, ab), 1)


# =============================================================================
# ANIMAZIONI MONETE
# =============================================================================

def crea_animazione_moneta(x, y, valore):
    return {'x': x, 'y': y, 'valore': valore, 'durata': 60, 'timer': 0}


def aggiorna_animazioni(animazioni):
    for a in animazioni[:]:
        a['timer'] += 1
        a['y'] -= 1
        if a['timer'] >= a['durata']:
            animazioni.remove(a)


def disegna_animazioni(schermo, animazioni, immagini, font):
    for a in animazioni:
        alpha = max(0, 255 - int(255 * a['timer'] / a['durata']))
        surf = pygame.Surface((60, 24), pygame.SRCALPHA)
        img_m = immagini['moneta'].copy()
        img_m.set_alpha(alpha)
        surf.blit(img_m, (0, 2))
        t = font.render(f"+${a['valore']}", True, GIALLO)
        t.set_alpha(alpha)
        surf.blit(t, (24, 0))
        schermo.blit(surf, (int(a['x']) - 10, int(a['y'])))


# =============================================================================
# LOGICA DELLE TORRI
# =============================================================================

def crea_torre(griglia_x, griglia_y, tipo_torre):
    px, py = griglia_a_pixel(griglia_x, griglia_y)
    cfg = {
        'arciere': (120, 15, 60,  BLU,    'arciere'),
        'cannone': (200, 40, 120, VIOLA,  'cannone'),
        'magia':   (100, 8,  20,  ARANCIONE, 'magia'),
    }
    raggio, danno, vel_sparo, colore, tipo_proj = cfg[tipo_torre]
    return {
        'griglia_x': griglia_x, 'griglia_y': griglia_y,
        'x': px, 'y': py, 'tipo': tipo_torre,
        'raggio': raggio, 'danno': danno,
        'velocita_sparo': vel_sparo, 'colore': colore,
        'tipo_proiettile': tipo_proj, 'cooldown': 0, 'bersaglio': None
    }


def trova_bersaglio_torre(torre, lista_nemici):
    torre['bersaglio'] = None
    for n in lista_nemici:
        dx = n['x'] - torre['x']
        dy = n['y'] - torre['y']
        if math.sqrt(dx**2 + dy**2) <= torre['raggio']:
            torre['bersaglio'] = n
            break


def aggiorna_torre(torre):
    if torre['cooldown'] > 0:
        torre['cooldown'] -= 1


def puo_sparare_torre(torre):
    b = torre['bersaglio']
    if b and b['salute'] > 0 and torre['cooldown'] == 0:
        dx = b['x'] - torre['x']
        dy = b['y'] - torre['y']
        return math.sqrt(dx**2 + dy**2) <= torre['raggio']
    return False


def spara_torre(torre):
    torre['cooldown'] = torre['velocita_sparo']
    return crea_proiettile(torre['x'], torre['y'], torre['bersaglio'],
                           torre['danno'], torre['tipo_proiettile'])


def disegna_torre(schermo, torre, immagini, mostra_raggio=False):
    x, y = int(torre['x']), int(torre['y'])
    if mostra_raggio:
        r = torre['raggio']
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*torre['colore'], 40), (r, r), r)
        pygame.draw.circle(s, (*torre['colore'], 120), (r, r), r, 2)
        schermo.blit(s, (x - r, y - r))
    img = immagini.get(f"torre_{torre['tipo']}")
    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w // 2, y - h // 2))
    else:
        d = 20
        rct = pygame.Rect(x - d // 2, y - d // 2, d, d)
        pygame.draw.rect(schermo, torre['colore'], rct)
        pygame.draw.rect(schermo, NERO, rct, 2)


# =============================================================================
# LOGICA DEI PROIETTILI
# =============================================================================

def crea_proiettile(x, y, bersaglio, danno, tipo='arciere'):
    return {'x': x, 'y': y, 'bersaglio': bersaglio, 'danno': danno,
            'velocita': 8, 'tipo': tipo, 'angolo': 0}


def muovi_proiettile(proiettile):
    b = proiettile['bersaglio']
    if b and b['salute'] > 0:
        dx = b['x'] - proiettile['x']
        dy = b['y'] - proiettile['y']
        dist = math.sqrt(dx**2 + dy**2)
        if dist < proiettile['velocita']:
            return True
        proiettile['angolo'] = -math.degrees(math.atan2(dy, dx))
        proiettile['x'] += (dx / dist) * proiettile['velocita']
        proiettile['y'] += (dy / dist) * proiettile['velocita']
        return False
    return True


def disegna_proiettile(schermo, proiettile, immagini):
    x, y = int(proiettile['x']), int(proiettile['y'])
    img = immagini.get(f"colpo_{proiettile['tipo']}")
    if img:
        ir = pygame.transform.rotate(img, proiettile['angolo'])
        w, h = ir.get_size()
        schermo.blit(ir, (x - w // 2, y - h // 2))
    else:
        colori = {'arciere': (139, 90, 43), 'cannone': (80, 80, 80), 'magia': (255, 0, 255)}
        pygame.draw.circle(schermo, colori.get(proiettile['tipo'], BIANCO), (x, y), 4)


# =============================================================================
# MECCANICA DI GIOCO
# =============================================================================

def inizializza_gioco():
    return {
        'soldi': SOLDI_INIZIALI, 'vite': VITE_INIZIALI,
        'ondata': 0, 'ondata_in_corso': False,
        'nemici_da_spawnare': 0, 'timer_spawn': 0,
        'nemici': [], 'torri': [], 'proiettili': [], 'animazioni': [],
        'torre_selezionata': None,
        'game_over': False, 'vittoria': False
    }


def avvia_ondata(stato):
    stato['ondata'] += 1
    stato['nemici_da_spawnare'] = calcola_numero_nemici(stato['ondata'])
    stato['ondata_in_corso'] = True
    stato['timer_spawn'] = 0


def spawna_nemico(stato):
    tipo, salute, velocita, ricompensa = calcola_statistiche_nemici(stato['ondata'])
    nemico = crea_nemico(salute, velocita, ricompensa, tipo)
    percorso = ottieni_percorso_pixel()
    nemico['x'], nemico['y'] = percorso[0]
    stato['nemici'].append(nemico)


def puo_piazzare_torre(stato, gx, gy):
    if (gx, gy) in PERCORSO_GRIGLIA:
        return False
    for t in stato['torri']:
        if t['griglia_x'] == gx and t['griglia_y'] == gy:
            return False
    return True


def piazza_torre(stato, gx, gy):
    if not stato['torre_selezionata']:
        return False
    if not puo_piazzare_torre(stato, gx, gy):
        return False
    tipo = stato['torre_selezionata']
    costo = COSTI_TORRI[tipo]
    if stato['soldi'] < costo:
        return False
    stato['torri'].append(crea_torre(gx, gy, tipo))
    stato['soldi'] -= costo
    return True


def aggiorna_gioco(stato):
    if stato['game_over']:
        return

    if stato['ondata_in_corso'] and stato['nemici_da_spawnare'] > 0:
        stato['timer_spawn'] += 1
        if stato['timer_spawn'] >= FRAME_TRA_SPAWN:
            spawna_nemico(stato)
            stato['nemici_da_spawnare'] -= 1
            stato['timer_spawn'] = 0

    percorso = ottieni_percorso_pixel()
    for n in stato['nemici'][:]:
        if muovi_nemico(n, percorso):
            stato['vite'] -= 1
            stato['nemici'].remove(n)
            if stato['vite'] <= 0:
                stato['game_over'] = True
                stato['vittoria'] = False

    for torre in stato['torri']:
        aggiorna_torre(torre)
        trova_bersaglio_torre(torre, stato['nemici'])
        if puo_sparare_torre(torre):
            stato['proiettili'].append(spara_torre(torre))

    for proj in stato['proiettili'][:]:
        if muovi_proiettile(proj):
            b = proj['bersaglio']
            if b and b['salute'] > 0:
                if danneggia_nemico(b, proj['danno']):
                    stato['soldi'] += b['ricompensa']
                    stato['animazioni'].append(
                        crea_animazione_moneta(b['x'], b['y'], b['ricompensa']))
                    if b in stato['nemici']:
                        stato['nemici'].remove(b)
            stato['proiettili'].remove(proj)

    aggiorna_animazioni(stato['animazioni'])

    if stato['nemici_da_spawnare'] == 0 and len(stato['nemici']) == 0 and stato['ondata_in_corso']:
        stato['ondata_in_corso'] = False
        stato['soldi'] += BONUS_FINE_ONDATA

    if stato['ondata'] >= ONDATE_TOTALI and not stato['ondata_in_corso'] and len(stato['nemici']) == 0:
        stato['game_over'] = True
        stato['vittoria'] = True


# =============================================================================
# RENDERING GIOCO
# =============================================================================

def disegna_sfondo(schermo):
    schermo.fill(VERDE_ERBA)
    for x in range(CELLE_LARGHE):
        for y in range(CELLE_ALTE):
            pygame.draw.rect(schermo, VERDE_SCURO,
                             pygame.Rect(x * DIMENSIONE_CELLA, y * DIMENSIONE_CELLA,
                                         DIMENSIONE_CELLA, DIMENSIONE_CELLA), 1)


def disegna_percorso(schermo):
    for gx, gy in PERCORSO_GRIGLIA:
        r = pygame.Rect(gx * DIMENSIONE_CELLA, gy * DIMENSIONE_CELLA,
                        DIMENSIONE_CELLA, DIMENSIONE_CELLA)
        pygame.draw.rect(schermo, MARRONE_SENTIERO, r)
        pygame.draw.rect(schermo, (100, 60, 20), r, 1)


def disegna_preview_torre(schermo, gx, gy, valida):
    colore = VERDE_CHIARO if valida else ROSSO
    s = pygame.Surface((DIMENSIONE_CELLA, DIMENSIONE_CELLA), pygame.SRCALPHA)
    s.fill((*colore, 100))
    schermo.blit(s, (gx * DIMENSIONE_CELLA, gy * DIMENSIONE_CELLA))


def disegna_pannello_ui(schermo, soldi, vite, ondata, immagini, font_grande, font_piccolo):
    pygame.draw.rect(schermo, (50, 50, 60),  (800, 0, 200, ALTEZZA_SCHERMO))
    pygame.draw.rect(schermo, (70, 70, 85),  (802, 2, 196, ALTEZZA_SCHERMO - 4))
    pygame.draw.line(schermo, (100, 100, 120), (800, 0), (800, ALTEZZA_SCHERMO), 2)

    t = font_grande.render("TOWER DEFENSE", True, GIALLO)
    schermo.blit(t, (800 + (200 - t.get_width()) // 2, 8))
    pygame.draw.line(schermo, GIALLO, (810, 36), (990, 36), 1)

    img_m = immagini.get('moneta')
    if img_m:
        schermo.blit(img_m, (810, 44))
    schermo.blit(font_grande.render(f"${soldi}", True, GIALLO), (835, 44))
    schermo.blit(font_grande.render(f"♥ {vite}", True, ROSSO), (810, 70))
    schermo.blit(font_grande.render(f"Ondata {ondata}/10", True, BIANCO), (810, 96))


def disegna_pulsante_torre(schermo, tipo_torre, costo, pos_y, soldi, selezionato, immagini, font):
    if selezionato:
        cs, cb = (200, 170, 0), GIALLO
    elif soldi >= costo:
        cs, cb = (40, 80, 40), VERDE_CHIARO
    else:
        cs, cb = (60, 60, 60), GRIGIO

    r = pygame.Rect(812, pos_y, 176, 58)
    pygame.draw.rect(schermo, cs, r, border_radius=6)
    pygame.draw.rect(schermo, cb, r, 2, border_radius=6)

    img = immagini.get(f"torre_{tipo_torre}")
    if img:
        schermo.blit(pygame.transform.scale(img, (36, 36)), (r.x + 6, r.y + 11))

    ct = BIANCO if soldi >= costo else (130, 130, 130)
    nomi = {'arciere': 'Arciere', 'magia': 'Magia', 'cannone': 'Cannone'}
    schermo.blit(font.render(nomi.get(tipo_torre, tipo_torre), True, ct), (r.x + 48, r.y + 10))
    schermo.blit(font.render(f"${costo}", True, GIALLO if soldi >= costo else (130, 130, 130)),
                 (r.x + 48, r.y + 34))
    return r


def disegna_pulsante_ondata(schermo, ondata_in_corso, font):
    if ondata_in_corso:
        return None
    r = pygame.Rect(812, 360, 176, 50)
    pygame.draw.rect(schermo, (20, 80, 160), r, border_radius=8)
    pygame.draw.rect(schermo, BLU, r, 2, border_radius=8)
    t = font.render("▶  Avvia Ondata", True, BIANCO)
    schermo.blit(t, (r.x + (176 - t.get_width()) // 2, r.y + (50 - t.get_height()) // 2))
    return r


def disegna_legenda(schermo, font_piccolo):
    y = 430
    pygame.draw.line(schermo, (100, 100, 120), (810, y), (990, y), 1)
    schermo.blit(font_piccolo.render("ESC = deseleziona torre", True, (160, 160, 160)), (810, y + 6))
    schermo.blit(font_piccolo.render("R = riavvia (game over)", True, (160, 160, 160)), (810, y + 22))


def disegna_game_over(schermo, vittoria, font_grande, font_piccolo):
    overlay = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    schermo.blit(overlay, (0, 0))

    if vittoria:
        t = font_grande.render("VITTORIA!", True, GIALLO)
        cb = (60, 100, 0)
    else:
        t = font_grande.render("GAME OVER", True, ROSSO)
        cb = (100, 0, 0)

    box = pygame.Rect(LARGHEZZA_SCHERMO // 2 - 200, ALTEZZA_SCHERMO // 2 - 70, 400, 140)
    pygame.draw.rect(schermo, cb, box, border_radius=12)
    pygame.draw.rect(schermo, BIANCO, box, 3, border_radius=12)
    schermo.blit(t, (LARGHEZZA_SCHERMO // 2 - t.get_width() // 2, ALTEZZA_SCHERMO // 2 - 50))
    r = font_piccolo.render("Premi  R  per ricominciare", True, BIANCO)
    schermo.blit(r, (LARGHEZZA_SCHERMO // 2 - r.get_width() // 2, ALTEZZA_SCHERMO // 2 + 20))


def disegna_tutto(schermo, stato, pulsanti_torri, immagini, font_grande, font_medio, font_piccolo):
    disegna_sfondo(schermo)
    disegna_percorso(schermo)

    mostra_raggio = stato['torre_selezionata'] is not None
    for torre in stato['torri']:
        disegna_torre(schermo, torre, immagini, mostra_raggio)
    for n in stato['nemici']:
        disegna_nemico(schermo, n, immagini)
    for p in stato['proiettili']:
        disegna_proiettile(schermo, p, immagini)

    disegna_animazioni(schermo, stato['animazioni'], immagini, font_piccolo)
    disegna_pannello_ui(schermo, stato['soldi'], stato['vite'], stato['ondata'],
                        immagini, font_medio, font_piccolo)

    if stato['torre_selezionata']:
        mx, my = pygame.mouse.get_pos()
        if mx < 800:
            gx, gy = pixel_a_griglia(mx, my)
            disegna_preview_torre(schermo, gx, gy, puo_piazzare_torre(stato, gx, gy))

    pulsanti_torri['arciere'] = disegna_pulsante_torre(
        schermo, 'arciere', 100, 130, stato['soldi'],
        stato['torre_selezionata'] == 'arciere', immagini, font_medio)
    pulsanti_torri['magia'] = disegna_pulsante_torre(
        schermo, 'magia', 150, 198, stato['soldi'],
        stato['torre_selezionata'] == 'magia', immagini, font_medio)
    pulsanti_torri['cannone'] = disegna_pulsante_torre(
        schermo, 'cannone', 200, 266, stato['soldi'],
        stato['torre_selezionata'] == 'cannone', immagini, font_medio)

    pulsante_ondata = disegna_pulsante_ondata(schermo, stato['ondata_in_corso'], font_medio)
    disegna_legenda(schermo, font_piccolo)

    if stato['game_over']:
        disegna_game_over(schermo, stato['vittoria'], font_grande, font_piccolo)

    return pulsante_ondata


# =============================================================================
# GESTIONE INPUT
# =============================================================================

def gestisci_click(stato, mx, my, pulsanti_torri, pulsante_ondata):
    if stato['game_over']:
        return
    for tipo_torre, r in pulsanti_torri.items():
        if r.collidepoint(mx, my):
            if stato['soldi'] >= COSTI_TORRI[tipo_torre]:
                stato['torre_selezionata'] = (
                    None if stato['torre_selezionata'] == tipo_torre else tipo_torre)
            return
    if pulsante_ondata and pulsante_ondata.collidepoint(mx, my):
        avvia_ondata(stato)
        return
    if mx < 800 and stato['torre_selezionata']:
        gx, gy = pixel_a_griglia(mx, my)
        if piazza_torre(stato, gx, gy):
            stato['torre_selezionata'] = None


# =============================================================================
# LOOP PRINCIPALE
# =============================================================================

def main():
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()

    font_grande  = pygame.font.Font(None, 48)
    font_medio   = pygame.font.Font(None, 28)
    font_piccolo = pygame.font.Font(None, 20)

    immagini = carica_immagini()

    # === LOOP MENU ===
    in_menu = True
    while in_menu:
        risultato = schermata_iniziale_loop(schermo, immagini, font_medio, clock)

        if risultato == False:
            pygame.quit()
            return
        elif risultato == 'impostazioni':
            continua = schermata_impostazioni_loop(
                schermo, immagini, font_grande, font_medio, font_piccolo, clock)
            if not continua:
                pygame.quit()
                return
            # Torna al menu
        elif risultato == 'gioca':
            in_menu = False

    # === LOOP GIOCO ===
    stato = inizializza_gioco()
    pulsanti_torri = {}
    pulsante_ondata = None

    in_esecuzione = True
    while in_esecuzione:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                gestisci_click(stato, *evento.pos, pulsanti_torri, pulsante_ondata)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and stato['game_over']:
                    stato = inizializza_gioco()
                if evento.key == pygame.K_ESCAPE:
                    stato['torre_selezionata'] = None

        aggiorna_gioco(stato)
        pulsante_ondata = disegna_tutto(schermo, stato, pulsanti_torri, immagini,
                                        font_grande, font_medio, font_piccolo)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
