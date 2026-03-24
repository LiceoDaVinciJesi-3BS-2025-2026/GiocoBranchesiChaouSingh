"""
=============================================================================
TOWER DEFENSE - GIOCO COMPLETO
=============================================================================

Tutto in un unico file - meccanica di gioco e sistema dei livelli.
"""

import pygame
import math
import os

# =============================================================================
# CONFIGURAZIONE GENERALE
# =============================================================================

LARGHEZZA_SCHERMO = 1220
ALTEZZA_SCHERMO = 700

DIMENSIONE_CELLA = 42
CELLE_LARGHE = 26
CELLE_ALTE = 16

GRIGIO = (128, 128, 128)
NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
BLU = (30, 144, 255)
VIOLA = (147, 112, 219)
ARANCIONE = (255, 140, 0)
ROSSO = (220, 20, 60)
GIALLO = (255, 215, 0)
VERDE_CHIARO = (0, 255, 0)

pygame.init()
schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

global sfondo_img
sfondo_img = pygame.image.load("srondo.png").convert()
sfondo_img = pygame.transform.scale(sfondo_img, (1000, ALTEZZA_SCHERMO))

PERCORSO_GRIGLIA = [
    (0, 3), (1, 3), (2, 3),
    (2, 4), (2, 5), (2, 6), (2, 7),
    (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
    (8, 8), (8, 9), (8, 10), (8, 11), (8, 12),
    (9, 12), (10, 12), (11, 12), (12, 12), (13, 12), (14, 12),
    (14, 11), (14, 10), (14, 9), (14, 8), (14, 7),
    (13, 7), (12, 7),
    (12, 6), (12, 5), (12, 4), (12, 3), (12, 2),
    (13, 2), (14, 2), (15, 2), (16, 2), (17, 2), (18, 2),
    (18, 3), (18, 4), (18, 5), (18, 6), (18, 7),
    (19, 7), (20, 7), (21, 7), (22, 7), (23, 7),
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
# CARICAMENTO IMMAGINI SPRITE (da codiceconimmagini)
# =============================================================================

def carica_immagini():
    """
    Carica tutti gli sprite dalla cartella del gioco.
    Se un file non esiste, restituisce None e il codice userà
    il disegno geometrico originale come fallback.
    """
    cartella = os.path.dirname(os.path.abspath(__file__))

    DIM_NEMICO     = (60, 60)
    DIM_TORRE      = (68, 68)
    DIM_PROIETTILE = (22, 22)
    DIM_MONETA     = (24, 24)

    def carica(nome_file, dimensione):
        percorso = os.path.join(cartella, nome_file)
        try:
            img = pygame.image.load(percorso).convert_alpha()
            return pygame.transform.scale(img, dimensione)
        except Exception:
            return None  # fallback geometrico

    immagini = {}

    # Nemici per direzione
    for tipo in ('goblin', 'orco', 'demone'):
        immagini[f'{tipo}_destra'] = carica(f'{tipo}_versodestra.png', DIM_NEMICO)
        immagini[f'{tipo}_alto']   = carica(f'{tipo}_versoalto.png',   DIM_NEMICO)
        src_alto   = immagini[f'{tipo}_alto']
        src_destra = immagini[f'{tipo}_destra']
        immagini[f'{tipo}_basso']    = (pygame.transform.flip(src_alto,   False, True)
                                         if src_alto   else None)
        immagini[f'{tipo}_sinistra'] = (pygame.transform.flip(src_destra, True,  False)
                                         if src_destra else None)

    # Torri
    for tipo in ('arciere', 'cannone', 'magia'):
        immagini[f'torre_{tipo}'] = carica(f'torre_{tipo}.png', DIM_TORRE)

    # Proiettili
    for tipo in ('arciere', 'cannone', 'magia'):
        immagini[f'colpo_{tipo}'] = carica(f'colpo_{tipo}.png', DIM_PROIETTILE)

    # Moneta (animazione)
    immagini['moneta'] = carica('moneta.png', DIM_MONETA)

    return immagini


def ottieni_immagine_nemico(immagini, tipo, dx, dy):
    """Restituisce lo sprite giusto in base alla direzione di movimento."""
    if abs(dx) >= abs(dy):
        direzione = 'destra' if dx > 0 else 'sinistra'
    else:
        direzione = 'basso' if dy > 0 else 'alto'
    return immagini.get(f'{tipo}_{direzione}')


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
        salute_base = 50
        incremento_salute = 20
        velocita_base = 1.0
        ricompensa_base = 20
    elif ondata <= 7:
        tipo = 'orco'
        salute_base = 80
        incremento_salute = 25
        velocita_base = 1.2
        ricompensa_base = 30
    else:
        tipo = 'demone'
        salute_base = 120
        incremento_salute = 30
        velocita_base = 1.4
        ricompensa_base = 40

    salute = salute_base + (ondata * incremento_salute)
    velocita = velocita_base + (ondata * 0.1)
    velocita = min(velocita, 3.0)
    ricompensa = ricompensa_base + (ondata * 5)

    return (tipo, salute, velocita, ricompensa)


def calcola_numero_nemici(ondata):
    return 5 + (ondata * 3)


# =============================================================================
# LOGICA DEI NEMICI
# =============================================================================

def crea_nemico(salute, velocita, ricompensa, tipo='goblin'):
    return {
        'salute_max': salute,
        'salute': salute,
        'velocita': velocita,
        'ricompensa': ricompensa,
        'indice_percorso': 0,
        'x': 0,
        'y': 0,
        'tipo': tipo,
        'dx': 1,   # direzione corrente per lo sprite
        'dy': 0,
    }


def muovi_nemico(nemico, percorso_pixel):
    if nemico['indice_percorso'] < len(percorso_pixel) - 1:
        target_x, target_y = percorso_pixel[nemico['indice_percorso'] + 1]
        dx = target_x - nemico['x']
        dy = target_y - nemico['y']
        distanza = math.sqrt(dx**2 + dy**2)

        nemico['dx'] = dx
        nemico['dy'] = dy

        if distanza < nemico['velocita']:
            nemico['indice_percorso'] += 1
            if nemico['indice_percorso'] < len(percorso_pixel):
                nemico['x'], nemico['y'] = percorso_pixel[nemico['indice_percorso']]
        else:
            direzione_x = dx / distanza
            direzione_y = dy / distanza
            nemico['x'] += direzione_x * nemico['velocita']
            nemico['y'] += direzione_y * nemico['velocita']

    return nemico['indice_percorso'] >= len(percorso_pixel) - 1


def danneggia_nemico(nemico, danno):
    nemico['salute'] -= danno
    return nemico['salute'] <= 0


def disegna_nemico(schermo, nemico, immagini):
    """Sprite se disponibile, altrimenti cerchio colorato originale."""
    x = int(nemico['x'])
    y = int(nemico['y'])

    img = ottieni_immagine_nemico(immagini, nemico['tipo'], nemico['dx'], nemico['dy'])

    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w // 2, y - h // 2))
        raggio = h // 2
    else:
        # Fallback grafico originale
        if nemico['tipo'] == 'goblin':
            colore = (0, 200, 0)
            raggio = 16
        elif nemico['tipo'] == 'orco':
            colore = (200, 50, 50)
            raggio = 19
        else:
            colore = (150, 0, 200)
            raggio = 22
        pygame.draw.circle(schermo, colore, (x, y), raggio)
        pygame.draw.circle(schermo, NERO, (x, y), raggio, 2)

    # Barra vita originale
    larghezza_barra = 44
    altezza_barra = 6
    x_barra = x - larghezza_barra // 2
    y_barra = y - raggio - 10
    percentuale = nemico['salute'] / nemico['salute_max']

    pygame.draw.rect(schermo, GRIGIO, (x_barra, y_barra, larghezza_barra, altezza_barra))
    pygame.draw.rect(schermo, VERDE_CHIARO,
                     (x_barra, y_barra, larghezza_barra * percentuale, altezza_barra))


# =============================================================================
# ANIMAZIONI MONETE (da codiceconimmagini)
# =============================================================================

def crea_animazione_moneta(x, y, valore):
    return {'x': x, 'y': y, 'valore': valore, 'durata': 60, 'timer': 0}


def aggiorna_animazioni(animazioni):
    for anim in animazioni[:]:
        anim['timer'] += 1
        anim['y'] -= 1
        if anim['timer'] >= anim['durata']:
            animazioni.remove(anim)


def disegna_animazioni(schermo, animazioni, immagini, font):
    for anim in animazioni:
        alpha = max(0, 255 - int(255 * anim['timer'] / anim['durata']))
        surf = pygame.Surface((60, 24), pygame.SRCALPHA)
        img_moneta = immagini.get('moneta')
        if img_moneta:
            im = img_moneta.copy()
            im.set_alpha(alpha)
            surf.blit(im, (0, 2))
        testo = font.render(f"+${anim['valore']}", True, GIALLO)
        testo.set_alpha(alpha)
        surf.blit(testo, (24, 0))
        schermo.blit(surf, (int(anim['x']) - 10, int(anim['y'])))


# =============================================================================
# LOGICA DELLE TORRI
# =============================================================================

def crea_torre(griglia_x, griglia_y, tipo_torre):
    pixel_x, pixel_y = griglia_a_pixel(griglia_x, griglia_y)

    if tipo_torre == 'arciere':
        raggio = 120
        danno = 15
        velocita_sparo = 60
        colore = BLU
        tipo_proiettile = 'arciere'
    elif tipo_torre == 'cannone':
        raggio = 200
        danno = 40
        velocita_sparo = 120
        colore = VIOLA
        tipo_proiettile = 'cannone'
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
    torre['bersaglio'] = None
    for nemico in lista_nemici:
        dx = nemico['x'] - torre['x']
        dy = nemico['y'] - torre['y']
        distanza = math.sqrt(dx**2 + dy**2)
        if distanza <= torre['raggio']:
            torre['bersaglio'] = nemico
            break


def aggiorna_torre(torre):
    if torre['cooldown'] > 0:
        torre['cooldown'] -= 1


def puo_sparare_torre(torre):
    bersaglio = torre['bersaglio']
    if bersaglio and bersaglio['salute'] > 0 and torre['cooldown'] == 0:
        dx = bersaglio['x'] - torre['x']
        dy = bersaglio['y'] - torre['y']
        distanza = math.sqrt(dx**2 + dy**2)
        return distanza <= torre['raggio']
    return False


def spara_torre(torre):
    torre['cooldown'] = torre['velocita_sparo']
    return crea_proiettile(torre['x'], torre['y'], torre['bersaglio'],
                           torre['danno'], torre['tipo_proiettile'])


def disegna_torre(schermo, torre, immagini, mostra_raggio=False):
    """Sprite se disponibile, altrimenti quadrato colorato originale."""
    x = int(torre['x'])
    y = int(torre['y'])

    if mostra_raggio:
        pygame.draw.circle(schermo, (*torre['colore'], 50), (x, y), torre['raggio'], 1)

    img = immagini.get(f"torre_{torre['tipo']}")
    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w // 2, y - h // 2))
    else:
        # Fallback originale
        dimensione = 32
        rettangolo = pygame.Rect(x - dimensione // 2, y - dimensione // 2,
                                 dimensione, dimensione)
        pygame.draw.rect(schermo, torre['colore'], rettangolo)
        pygame.draw.rect(schermo, NERO, rettangolo, 2)


# =============================================================================
# LOGICA DEI PROIETTILI
# =============================================================================

def crea_proiettile(x, y, bersaglio, danno, tipo='arciere'):
    return {
        'x': x,
        'y': y,
        'bersaglio': bersaglio,
        'danno': danno,
        'velocita': 8,
        'tipo': tipo,
        'angolo': 0,
    }


def muovi_proiettile(proiettile):
    bersaglio = proiettile['bersaglio']
    if bersaglio and bersaglio['salute'] > 0:
        dx = bersaglio['x'] - proiettile['x']
        dy = bersaglio['y'] - proiettile['y']
        distanza = math.sqrt(dx**2 + dy**2)
        if distanza < proiettile['velocita']:
            return True
        proiettile['angolo'] = -math.degrees(math.atan2(dy, dx))
        proiettile['x'] += (dx / distanza) * proiettile['velocita']
        proiettile['y'] += (dy / distanza) * proiettile['velocita']
        return False
    return True


def disegna_proiettile(schermo, proiettile, immagini):
    """Sprite ruotato se disponibile, altrimenti cerchio colorato originale."""
    x = int(proiettile['x'])
    y = int(proiettile['y'])

    img = immagini.get(f"colpo_{proiettile['tipo']}")
    if img:
        img_ruotata = pygame.transform.rotate(img, proiettile['angolo'])
        w, h = img_ruotata.get_size()
        schermo.blit(img_ruotata, (x - w // 2, y - h // 2))
    else:
        # Fallback originale
        if proiettile['tipo'] == 'arciere':
            colore = (139, 90, 43)
        elif proiettile['tipo'] == 'cannone':
            colore = (80, 80, 80)
        else:
            colore = (255, 0, 255)
        pygame.draw.circle(schermo, colore, (x, y), 4)


# =============================================================================
# MECCANICA DI GIOCO
# =============================================================================

def inizializza_gioco():
    return {
        'soldi': SOLDI_INIZIALI,
        'vite': VITE_INIZIALI,
        'ondata': 0,
        'ondata_in_corso': False,
        'nemici_da_spawnare': 0,
        'timer_spawn': 0,
        'nemici': [],
        'torri': [],
        'proiettili': [],
        'animazioni': [],
        'torre_selezionata': None,
        'game_over': False,
        'vittoria': False
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


def puo_piazzare_torre(stato, griglia_x, griglia_y):
    if (griglia_x, griglia_y) in PERCORSO_GRIGLIA:
        return False
    for torre in stato['torri']:
        if torre['griglia_x'] == griglia_x and torre['griglia_y'] == griglia_y:
            return False
    return True


def piazza_torre(stato, griglia_x, griglia_y):
    if not stato['torre_selezionata']:
        return False
    if not puo_piazzare_torre(stato, griglia_x, griglia_y):
        return False
    tipo_torre = stato['torre_selezionata']
    costo = COSTI_TORRI[tipo_torre]
    if stato['soldi'] < costo:
        return False
    torre = crea_torre(griglia_x, griglia_y, tipo_torre)
    stato['torri'].append(torre)
    stato['soldi'] -= costo
    return True


def aggiorna_gioco(stato):
    if stato['game_over']:
        return

    # Spawn nemici
    if stato['ondata_in_corso'] and stato['nemici_da_spawnare'] > 0:
        stato['timer_spawn'] += 1
        if stato['timer_spawn'] >= FRAME_TRA_SPAWN:
            spawna_nemico(stato)
            stato['nemici_da_spawnare'] -= 1
            stato['timer_spawn'] = 0

    # Nemici
    percorso = ottieni_percorso_pixel()
    for nemico in stato['nemici'][:]:
        ha_raggiunto_fine = muovi_nemico(nemico, percorso)
        if ha_raggiunto_fine:
            stato['vite'] -= 1
            stato['nemici'].remove(nemico)
            if stato['vite'] <= 0:
                stato['game_over'] = True
                stato['vittoria'] = False

    # Torri
    for torre in stato['torri']:
        aggiorna_torre(torre)
        trova_bersaglio_torre(torre, stato['nemici'])
        if puo_sparare_torre(torre):
            proiettile = spara_torre(torre)
            stato['proiettili'].append(proiettile)

    # Proiettili
    for proiettile in stato['proiettili'][:]:
        ha_colpito = muovi_proiettile(proiettile)
        if ha_colpito:
            bersaglio = proiettile['bersaglio']
            if bersaglio and bersaglio['salute'] > 0:
                e_morto = danneggia_nemico(bersaglio, proiettile['danno'])
                if e_morto:
                    stato['soldi'] += bersaglio['ricompensa']
                    stato['animazioni'].append(
                        crea_animazione_moneta(bersaglio['x'], bersaglio['y'],
                                               bersaglio['ricompensa'])
                    )
                    if bersaglio in stato['nemici']:
                        stato['nemici'].remove(bersaglio)
            stato['proiettili'].remove(proiettile)

    # Animazioni
    aggiorna_animazioni(stato['animazioni'])

    # Fine ondata
    if (stato['nemici_da_spawnare'] == 0 and
            len(stato['nemici']) == 0 and
            stato['ondata_in_corso']):
        stato['ondata_in_corso'] = False
        stato['soldi'] += BONUS_FINE_ONDATA

    # Vittoria
    if (stato['ondata'] >= ONDATE_TOTALI and
            not stato['ondata_in_corso'] and
            len(stato['nemici']) == 0):
        stato['game_over'] = True
        stato['vittoria'] = True


# =============================================================================
# RENDERING – grafica originale di __init__.py
# =============================================================================

def disegna_sfondo(schermo):
    schermo.blit(sfondo_img, (0, 0))
    for x in range(CELLE_LARGHE):
        for y in range(CELLE_ALTE):
            rettangolo = pygame.Rect(x * DIMENSIONE_CELLA, y * DIMENSIONE_CELLA,
                                     DIMENSIONE_CELLA, DIMENSIONE_CELLA)


def disegna_percorso(schermo):
    for gx, gy in PERCORSO_GRIGLIA:
        rettangolo = pygame.Rect(gx * DIMENSIONE_CELLA, gy * DIMENSIONE_CELLA,
                                 DIMENSIONE_CELLA, DIMENSIONE_CELLA)


def disegna_preview_torre(schermo, griglia_x, griglia_y, valida):
    colore = VERDE_CHIARO if valida else ROSSO
    superficie = pygame.Surface((DIMENSIONE_CELLA, DIMENSIONE_CELLA))
    superficie.set_alpha(100)
    superficie.fill(colore)
    schermo.blit(superficie, (griglia_x * DIMENSIONE_CELLA, griglia_y * DIMENSIONE_CELLA))


def disegna_pannello_ui(schermo, soldi, vite, ondata):
    pygame.draw.rect(schermo, GRIGIO, (1000, 0, 220, ALTEZZA_SCHERMO))
    font_grande = pygame.font.Font(None, 36)
    testo_soldi  = font_grande.render(f"Soldi: ${soldi}", True, GIALLO)
    testo_vite   = font_grande.render(f"Vite: {vite}",    True, ROSSO)
    testo_ondata = font_grande.render(f"Ondata: {ondata}/10", True, BIANCO)
    schermo.blit(testo_soldi,  (1010, 10))
    schermo.blit(testo_vite,   (1010, 50))
    schermo.blit(testo_ondata, (1010, 90))


def disegna_pulsante_torre(schermo, tipo_torre, costo, pos_y, soldi, selezionato):
    if selezionato:
        colore = GIALLO
    elif soldi >= costo:
        colore = VERDE_CHIARO
    else:
        colore = GRIGIO

    rettangolo = pygame.Rect(1010, pos_y, 190, 70)
    pygame.draw.rect(schermo, colore, rettangolo)
    pygame.draw.rect(schermo, NERO, rettangolo, 2)

    font = pygame.font.Font(None, 30)
    testo_nome  = font.render(tipo_torre.capitalize(), True, NERO)
    testo_costo = font.render(f"${costo}", True, NERO)
    schermo.blit(testo_nome,  (rettangolo.x + 12, rettangolo.y + 12))
    schermo.blit(testo_costo, (rettangolo.x + 12, rettangolo.y + 42))

    return rettangolo


def disegna_pulsante_ondata(schermo, ondata_in_corso):
    if ondata_in_corso:
        return None

    rettangolo = pygame.Rect(1010, 460, 190, 70)
    pygame.draw.rect(schermo, BLU, rettangolo)
    pygame.draw.rect(schermo, NERO, rettangolo, 2)

    font = pygame.font.Font(None, 30)
    testo = font.render("Avvia Ondata", True, BIANCO)
    schermo.blit(testo, (rettangolo.x + 18, rettangolo.y + 24))

    return rettangolo


def disegna_game_over(schermo, vittoria):
    overlay = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
    overlay.set_alpha(128)
    overlay.fill(NERO)
    schermo.blit(overlay, (0, 0))

    font_grande  = pygame.font.Font(None, 80)
    font_piccolo = pygame.font.Font(None, 40)

    if vittoria:
        testo_principale = font_grande.render("VITTORIA!", True, GIALLO)
    else:
        testo_principale = font_grande.render("GAME OVER", True, ROSSO)

    testo_riavvio = font_piccolo.render("Premi R per ricominciare", True, BIANCO)

    schermo.blit(testo_principale,
                 (LARGHEZZA_SCHERMO // 2 - testo_principale.get_width() // 2,
                  ALTEZZA_SCHERMO // 2 - 60))
    schermo.blit(testo_riavvio,
                 (LARGHEZZA_SCHERMO // 2 - testo_riavvio.get_width() // 2,
                  ALTEZZA_SCHERMO // 2 + 30))


def disegna_tutto(schermo, stato, pulsanti_torri, immagini, font_piccolo):
    disegna_sfondo(schermo)
    disegna_percorso(schermo)

    mostra_raggio = stato['torre_selezionata'] is not None
    for torre in stato['torri']:
        disegna_torre(schermo, torre, immagini, mostra_raggio)

    for nemico in stato['nemici']:
        disegna_nemico(schermo, nemico, immagini)

    for proiettile in stato['proiettili']:
        disegna_proiettile(schermo, proiettile, immagini)

    disegna_animazioni(schermo, stato['animazioni'], immagini, font_piccolo)

    disegna_pannello_ui(schermo, stato['soldi'], stato['vite'], stato['ondata'])

    if stato['torre_selezionata']:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x < 1000:
            griglia_x, griglia_y = pixel_a_griglia(mouse_x, mouse_y)
            valida = puo_piazzare_torre(stato, griglia_x, griglia_y)
            disegna_preview_torre(schermo, griglia_x, griglia_y, valida)

    if stato['game_over']:
        disegna_game_over(schermo, stato['vittoria'])


# =============================================================================
# GESTIONE INPUT
# =============================================================================

def gestisci_click(stato, mouse_x, mouse_y, pulsanti_torri, pulsante_ondata):
    if stato['game_over']:
        return

    for tipo_torre, rettangolo in pulsanti_torri.items():
        if rettangolo.collidepoint(mouse_x, mouse_y):
            if stato['soldi'] >= COSTI_TORRI[tipo_torre]:
                if stato['torre_selezionata'] == tipo_torre:
                    stato['torre_selezionata'] = None
                else:
                    stato['torre_selezionata'] = tipo_torre
            return

    if pulsante_ondata and pulsante_ondata.collidepoint(mouse_x, mouse_y):
        avvia_ondata(stato)
        return

    if mouse_x < 1000 and stato['torre_selezionata']:
        griglia_x, griglia_y = pixel_a_griglia(mouse_x, mouse_y)
        if piazza_torre(stato, griglia_x, griglia_y):
            stato['torre_selezionata'] = None


# =============================================================================
# LOOP PRINCIPALE
# =============================================================================

def main():
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
    pygame.display.set_caption("Tower Defense")
    clock = pygame.time.Clock()

    font_piccolo = pygame.font.Font(None, 20)

    immagini = carica_immagini()

    stato = inizializza_gioco()
    pulsanti_torri = {}
    pulsante_ondata = None

    in_esecuzione = True
    while in_esecuzione:

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = evento.pos
                gestisci_click(stato, mouse_x, mouse_y, pulsanti_torri, pulsante_ondata)

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and stato['game_over']:
                    stato = inizializza_gioco()
                if evento.key == pygame.K_ESCAPE:
                    stato['torre_selezionata'] = None

        aggiorna_gioco(stato)

        disegna_tutto(schermo, stato, pulsanti_torri, immagini, font_piccolo)

        pulsanti_torri['arciere'] = disegna_pulsante_torre(
            schermo, 'arciere', 100, 140, stato['soldi'],
            stato['torre_selezionata'] == 'arciere')
        pulsanti_torri['magia'] = disegna_pulsante_torre(
            schermo, 'magia', 150, 230, stato['soldi'],
            stato['torre_selezionata'] == 'magia')
        pulsanti_torri['cannone'] = disegna_pulsante_torre(
            schermo, 'cannone', 200, 320, stato['soldi'],
            stato['torre_selezionata'] == 'cannone')

        pulsante_ondata = disegna_pulsante_ondata(schermo, stato['ondata_in_corso'])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
