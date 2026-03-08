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

# Carica l'immagine di sfondo
sfondo_img = pygame.image.load("sfondo.png").convert()
sfondo_img = pygame.transform.scale(sfondo_img, (LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))

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
        torre['cooldown'] -=