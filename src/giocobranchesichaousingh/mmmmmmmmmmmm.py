"""
=============================================================================
TOWER DEFENSE - GIOCO COMPLETO
=============================================================================
"""

import pygame
import math
import os

# =============================================================================
# CONFIGURAZIONE
# =============================================================================

LARGHEZZA_SCHERMO  = 1350
ALTEZZA_SCHERMO    = 694
LARGHEZZA_GIOCO    = 1130
LARGHEZZA_PANNELLO = 220

DIMENSIONE_CELLA = 30
CELLE_LARGHE = 38
CELLE_ALTE   = 23

GRIGIO       = (128, 128, 128)
NERO         = (0, 0, 0)
BIANCO       = (255, 255, 255)
BLU          = (30, 144, 255)
VIOLA        = (147, 112, 219)
ARANCIONE    = (255, 140, 0)
ROSSO        = (220, 20, 60)
GIALLO       = (255, 215, 0)
VERDE_CHIARO = (0, 255, 0)
VERDE_ERBA   = (34, 139, 34)
VERDE_SCURO  = (0, 100, 0)
MARRONE_SENTIERO = (139, 90, 43)  # Aggiunto per il percorso


PERCORSO_GRIGLIA = [
    (0, 4), (1, 4), (2, 4),
    (2, 5), (2, 6), (2, 7), (2, 8),
    (3, 8), (4, 8), (5, 8), (6, 8),
    (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14),
    (7, 14), (8, 14), (9, 14), (10, 14), (11, 14), (12, 14),
    (12, 13), (12, 12), (12, 11), (12, 10), (12, 9), (12, 8),
    (11, 8), (10, 8),
    (10, 7), (10, 6), (10, 5), (10, 4), (10, 3), (10, 2),
    (11, 2), (12, 2), (13, 2), (14, 2), (15, 2),
    (15, 3), (15, 4), (15, 5), (15, 6), (15, 7), (15, 8),
    (16, 8), (17, 8), (18, 8), (19, 8),
]


SOLDI_INIZIALI    = 300
VITE_INIZIALI     = 15
ONDATE_TOTALI     = 10
BONUS_FINE_ONDATA = 50
FRAME_TRA_SPAWN   = 60
FPS               = 60

COSTI_TORRI = {'arciere': 100, 'magia': 150, 'cannone': 200}


# =============================================================================
# CARICAMENTO IMMAGINI
# =============================================================================

def carica_immagini():
    cartella = os.path.dirname(os.path.abspath(__file__))

    def carica(nome, dim):
        try:
            img = pygame.image.load(os.path.join(cartella, nome)).convert_alpha()
            return pygame.transform.scale(img, dim)
        except Exception:
            return None

    def carica_sfondo(nome, dim):
        try:
            img = pygame.image.load(os.path.join(cartella, nome)).convert()
            return pygame.transform.scale(img, dim)
        except Exception:
            return None

    immagini = {}
    immagini['sfondo_gioco']       = carica_sfondo('sfondo.png', (LARGHEZZA_GIOCO, ALTEZZA_SCHERMO))
    immagini['schermata_iniziale'] = carica_sfondo('schermata_iniziale.png', (LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))

    for tipo in ('goblin', 'orco', 'demone'):
        dx = carica(f'{tipo}_versodestra.png', (60, 60))
        su = carica(f'{tipo}_versoalto.png',   (60, 60))
        immagini[f'{tipo}_destra']   = dx
        immagini[f'{tipo}_alto']     = su
        immagini[f'{tipo}_basso']    = pygame.transform.flip(su, False, True) if su else None
        immagini[f'{tipo}_sinistra'] = pygame.transform.flip(dx, True, False) if dx else None

    for tipo in ('arciere', 'cannone', 'magia'):
        immagini[f'torre_{tipo}'] = carica(f'torre_{tipo}.png',  (68, 68))
        immagini[f'colpo_{tipo}'] = carica(f'colpo_{tipo}.png',  (22, 22))
    immagini['moneta'] = carica('moneta.png', (24, 24))

    return immagini


def sprite_nemico(immagini, tipo, dx, dy):
    if abs(dx) >= abs(dy):
        dir = 'destra' if dx > 0 else 'sinistra'
    else:
        dir = 'basso' if dy > 0 else 'alto'
    return immagini.get(f'{tipo}_{dir}')


# =============================================================================
# COORDINATE
# =============================================================================

def griglia_a_pixel(gx, gy):
    return (gx * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2,
            gy * DIMENSIONE_CELLA + DIMENSIONE_CELLA // 2)

def pixel_a_griglia(px, py):
    return (px // DIMENSIONE_CELLA, py // DIMENSIONE_CELLA)

def percorso_in_pixel():
    return [griglia_a_pixel(x, y) for x, y in PERCORSO_GRIGLIA]


# =============================================================================
# NEMICI
# =============================================================================

def statistiche_nemico(ondata):
    if ondata <= 3:
        tipo, s, inc, v, r = 'goblin', 50, 20, 1.0, 20
    elif ondata <= 7:
        tipo, s, inc, v, r = 'orco',   80, 25, 1.2, 30
    else:
        tipo, s, inc, v, r = 'demone', 120, 30, 1.4, 40
    return tipo, s + ondata * inc, min(v + ondata * 0.1, 3.0), r + ondata * 5

def nemici_per_ondata(ondata):
    return 5 + ondata * 3

def crea_nemico(salute, velocita, ricompensa, tipo):
    return {'salute_max': salute, 'salute': salute, 'velocita': velocita,
            'ricompensa': ricompensa, 'indice_percorso': 0,
            'x': 0, 'y': 0, 'tipo': tipo, 'dx': 1, 'dy': 0}

def muovi_nemico(nemico, percorso):
    if nemico['indice_percorso'] < len(percorso) - 1:
        tx, ty = percorso[nemico['indice_percorso'] + 1]
        dx, dy = tx - nemico['x'], ty - nemico['y']
        dist = math.sqrt(dx**2 + dy**2)
        nemico['dx'], nemico['dy'] = dx, dy
        if dist < nemico['velocita']:
            nemico['indice_percorso'] += 1
            if nemico['indice_percorso'] < len(percorso):
                nemico['x'], nemico['y'] = percorso[nemico['indice_percorso']]
        else:
            nemico['x'] += (dx / dist) * nemico['velocita']
            nemico['y'] += (dy / dist) * nemico['velocita']
    return nemico['indice_percorso'] >= len(percorso) - 1

def danneggia_nemico(nemico, danno):
    nemico['salute'] -= danno
    return nemico['salute'] <= 0

def disegna_nemico(schermo, nemico, immagini):
    x, y = int(nemico['x']), int(nemico['y'])
    img = sprite_nemico(immagini, nemico['tipo'], nemico['dx'], nemico['dy'])
    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w//2, y - h//2))
        raggio = h // 2
    else:
        colori = {'goblin': (0,200,0), 'orco': (200,50,50), 'demone': (150,0,200)}
        raggi  = {'goblin': 16, 'orco': 19, 'demone': 22}
        raggio = raggi[nemico['tipo']]
        pygame.draw.circle(schermo, colori[nemico['tipo']], (x, y), raggio)
        pygame.draw.circle(schermo, NERO, (x, y), raggio, 2)
    lb, ab = 44, 6
    xb, yb = x - lb//2, y - raggio - 10
    pct = nemico['salute'] / nemico['salute_max']
    colore_vita = VERDE_CHIARO if pct > 0.5 else (GIALLO if pct > 0.25 else ROSSO)
    pygame.draw.rect(schermo, (180,0,0), (xb, yb, lb, ab))
    pygame.draw.rect(schermo, colore_vita, (xb, yb, int(lb*pct), ab))


# =============================================================================
# TORRI
# =============================================================================

CONFIG_TORRI = {
    'arciere': (120, 15, 60,  BLU,      'arciere'),
    'cannone': (200, 40, 120, VIOLA,    'cannone'),
    'magia':   (100, 8,  20,  ARANCIONE,'magia'),
}

def crea_torre(gx, gy, tipo):
    px, py = griglia_a_pixel(gx, gy)
    raggio, danno, vel, colore, tipo_proj = CONFIG_TORRI[tipo]
    return {'griglia_x': gx, 'griglia_y': gy, 'x': px, 'y': py,
            'tipo': tipo, 'raggio': raggio, 'danno': danno,
            'velocita_sparo': vel, 'colore': colore,
            'tipo_proiettile': tipo_proj, 'cooldown': 0, 'bersaglio': None}

def aggiorna_torre(torre):
    if torre['cooldown'] > 0:
        torre['cooldown'] -= 1

def trova_bersaglio(torre, nemici):
    torre['bersaglio'] = None
    for n in nemici:
        dx, dy = n['x'] - torre['x'], n['y'] - torre['y']
        if math.sqrt(dx**2 + dy**2) <= torre['raggio']:
            torre['bersaglio'] = n
            break

def puo_sparare(torre):
    b = torre['bersaglio']
    if b and b['salute'] > 0 and torre['cooldown'] == 0:
        dx, dy = b['x'] - torre['x'], b['y'] - torre['y']
        return math.sqrt(dx**2 + dy**2) <= torre['raggio']
    return False

def spara(torre):
    torre['cooldown'] = torre['velocita_sparo']
    return crea_proiettile(torre['x'], torre['y'], torre['bersaglio'],
                           torre['danno'], torre['tipo_proiettile'])

def disegna_torre(schermo, torre, immagini, mostra_raggio=False):
    x, y = int(torre['x']), int(torre['y'])
    if mostra_raggio:
        r = torre['raggio']
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*torre['colore'], 40), (r, r), r)
        pygame.draw.circle(s, (*torre['colore'], 120), (r, r), r, 2)
        schermo.blit(s, (x-r, y-r))
    img = immagini.get(f"torre_{torre['tipo']}")
    if img:
        w, h = img.get_size()
        schermo.blit(img, (x - w//2, y - h//2))
    else:
        d = 32
        r = pygame.Rect(x-d//2, y-d//2, d, d)
        pygame.draw.rect(schermo, torre['colore'], r)
        pygame.draw.rect(schermo, NERO, r, 2)


# =============================================================================
# PROIETTILI
# =============================================================================

def crea_proiettile(x, y, bersaglio, danno, tipo):
    return {'x': x, 'y': y, 'bersaglio': bersaglio, 'danno': danno,
            'velocita': 8, 'tipo': tipo, 'angolo': 0}

def muovi_proiettile(proj):
    b = proj['bersaglio']
    if b and b['salute'] > 0:
        dx, dy = b['x'] - proj['x'], b['y'] - proj['y']
        dist = math.sqrt(dx**2 + dy**2)
        if dist < proj['velocita']:
            return True
        proj['angolo'] = -math.degrees(math.atan2(dy, dx))
        proj['x'] += (dx / dist) * proj['velocita']
        proj['y'] += (dy / dist) * proj['velocita']
        return False
    return True

def disegna_proiettile(schermo, proj, immagini):
    x, y = int(proj['x']), int(proj['y'])
    img = immagini.get(f"colpo_{proj['tipo']}")
    if img:
        ir = pygame.transform.rotate(img, proj['angolo'])
        w, h = ir.get_size()
        schermo.blit(ir, (x - w//2, y - h//2))
    else:
        colori = {'arciere': (139,90,43), 'cannone': (80,80,80), 'magia': (255,0,255)}
        pygame.draw.circle(schermo, colori.get(proj['tipo'], BIANCO), (x, y), 4)


# =============================================================================
# ANIMAZIONI MONETE
# =============================================================================

def crea_moneta_anim(x, y, valore):
    return {'x': x, 'y': y, 'valore': valore, 'durata': 60, 'timer': 0}

def aggiorna_monete(animazioni):
    for a in animazioni[:]:
        a['timer'] += 1
        a['y'] -= 1
        if a['timer'] >= a['durata']:
            animazioni.remove(a)

def disegna_monete(schermo, animazioni, immagini, font):
    for a in animazioni:
        alpha = max(0, 255 - int(255 * a['timer'] / a['durata']))
        surf = pygame.Surface((60, 24), pygame.SRCALPHA)
        img_m = immagini.get('moneta')
        if img_m:
            im = img_m.copy(); im.set_alpha(alpha); surf.blit(im, (0, 2))
        t = font.render(f"+${a['valore']}", True, GIALLO)
        t.set_alpha(alpha); surf.blit(t, (24, 0))
        schermo.blit(surf, (int(a['x'])-10, int(a['y'])))


# =============================================================================
# PUNTEGGIO
# =============================================================================

def calcola_punteggio(stato):
    return (stato['punti']
            + stato['ondata'] * 500
            + stato['vite'] * 200
            + (2000 if stato['vittoria'] else 0))


# =============================================================================
# STATO DEL GIOCO
# =============================================================================

def inizializza_gioco():
    return {
        'soldi': SOLDI_INIZIALI, 'vite': VITE_INIZIALI,
        'ondata': 0, 'ondata_in_corso': False,
        'nemici_da_spawnare': 0, 'timer_spawn': 0,
        'nemici': [], 'torri': [], 'proiettili': [], 'monete_anim': [],
        'torre_selezionata': None,
        'game_over': False, 'vittoria': False,
        'punti': 0, 'punteggio_finale': 0,
    }

def avvia_ondata(stato):
    stato['ondata'] += 1
    stato['nemici_da_spawnare'] = nemici_per_ondata(stato['ondata'])
    stato['ondata_in_corso'] = True
    stato['timer_spawn'] = 0

def spawna_nemico(stato):
    tipo, salute, vel, ricomp = statistiche_nemico(stato['ondata'])
    n = crea_nemico(salute, vel, ricomp, tipo)
    percorso = percorso_in_pixel()
    n['x'], n['y'] = percorso[0]
    stato['nemici'].append(n)

def cella_libera(stato, gx, gy):
    if (gx, gy) in PERCORSO_GRIGLIA:
        return False
    return not any(t['griglia_x'] == gx and t['griglia_y'] == gy for t in stato['torri'])

def piazza_torre(stato, gx, gy):
    tipo = stato['torre_selezionata']
    if not tipo or not cella_libera(stato, gx, gy):
        return False
    if stato['soldi'] < COSTI_TORRI[tipo]:
        return False
    stato['torri'].append(crea_torre(gx, gy, tipo))
    stato['soldi'] -= COSTI_TORRI[tipo]
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

    percorso = percorso_in_pixel()
    for n in stato['nemici'][:]:
        if muovi_nemico(n, percorso):
            stato['vite'] -= 1
            stato['nemici'].remove(n)
            if stato['vite'] <= 0:
                stato['game_over'] = True
                stato['vittoria'] = False
                stato['punteggio_finale'] = calcola_punteggio(stato)

    for t in stato['torri']:
        aggiorna_torre(t)
        trova_bersaglio(t, stato['nemici'])
        if puo_sparare(t):
            stato['proiettili'].append(spara(t))

    for p in stato['proiettili'][:]:
        if muovi_proiettile(p):
            b = p['bersaglio']
            if b and b['salute'] > 0:
                if danneggia_nemico(b, p['danno']):
                    stato['soldi'] += b['ricompensa']
                    stato['punti'] += 100
                    stato['monete_anim'].append(crea_moneta_anim(b['x'], b['y'], b['ricompensa']))
                    if b in stato['nemici']:
                        stato['nemici'].remove(b)
            stato['proiettili'].remove(p)

    aggiorna_monete(stato['monete_anim'])

    if stato['ondata_in_corso'] and stato['nemici_da_spawnare'] == 0 and not stato['nemici']:
        stato['ondata_in_corso'] = False
        stato['soldi'] += BONUS_FINE_ONDATA

    if stato['ondata'] >= ONDATE_TOTALI and not stato['ondata_in_corso'] and not stato['nemici']:
        stato['game_over'] = True
        stato['vittoria'] = True
        stato['punteggio_finale'] = calcola_punteggio(stato)


# =============================================================================
# RENDERING GIOCO - FUNZIONI MODIFICATE DAL SECONDO CODICE
# =============================================================================

def disegna_sfondo(schermo):
    """Disegna sfondo e griglia DAL SECONDO CODICE"""
    schermo.fill(VERDE_ERBA)
    
    for x in range(CELLE_LARGHE):
        for y in range(CELLE_ALTE):
            rettangolo = pygame.Rect(x * DIMENSIONE_CELLA, y * DIMENSIONE_CELLA,
                                    DIMENSIONE_CELLA, DIMENSIONE_CELLA)
            pygame.draw.rect(schermo, VERDE_SCURO, rettangolo, 1)

def disegna_percorso(schermo):
    """Disegna il sentiero DAL SECONDO CODICE"""
    for gx, gy in PERCORSO_GRIGLIA:
        rettangolo = pygame.Rect(gx * DIMENSIONE_CELLA, gy * DIMENSIONE_CELLA,
                                DIMENSIONE_CELLA, DIMENSIONE_CELLA)
        pygame.draw.rect(schermo, MARRONE_SENTIERO, rettangolo)

def disegna_pulsante_torre(schermo, tipo_torre, costo, pos_y, soldi, selezionato):
    """Disegna pulsante per comprare torre DAL SECONDO CODICE"""
    if selezionato:
        colore = GIALLO
    elif soldi >= costo:
        colore = VERDE_CHIARO
    else:
        colore = GRIGIO
    
    rettangolo = pygame.Rect(LARGHEZZA_GIOCO + 10, pos_y, 200, 64)
    pygame.draw.rect(schermo, colore, rettangolo)
    pygame.draw.rect(schermo, NERO, rettangolo, 2)
    
    font = pygame.font.Font(None, 24)
    nome = tipo_torre.capitalize()
    testo_nome = font.render(nome, True, NERO)
    testo_costo = font.render(f"${costo}", True, NERO)
    
    schermo.blit(testo_nome, (rettangolo.x + 10, rettangolo.y + 10))
    schermo.blit(testo_costo, (rettangolo.x + 10, rettangolo.y + 35))
    
    return rettangolo

def disegna_pannello(schermo, stato, immagini, font_grande, font_medio, font_piccolo):
    """Disegna il pannello laterale"""
    X = LARGHEZZA_GIOCO
    pygame.draw.rect(schermo, (50,50,60), (X, 0, LARGHEZZA_PANNELLO, ALTEZZA_SCHERMO))
    pygame.draw.rect(schermo, (70,70,85), (X+2, 2, LARGHEZZA_PANNELLO-4, ALTEZZA_SCHERMO-4))
    pygame.draw.line(schermo, (100,100,120), (X, 0), (X, ALTEZZA_SCHERMO), 2)

    t = font_grande.render("TOWER DEFENSE", True, GIALLO)
    schermo.blit(t, (X + (LARGHEZZA_PANNELLO - t.get_width())//2, 8))
    pygame.draw.line(schermo, GIALLO, (X+10, 36), (X+LARGHEZZA_PANNELLO-10, 36), 1)

    img_m = immagini.get('moneta')
    if img_m: schermo.blit(img_m, (X+10, 44))
    schermo.blit(font_grande.render(f"${stato['soldi']}", True, GIALLO),           (X+38, 44))
    schermo.blit(font_grande.render(f"♥ {stato['vite']}", True, ROSSO),            (X+10, 72))
    schermo.blit(font_grande.render(f"Ondata {stato['ondata']}/10", True, BIANCO), (X+10, 100))
    schermo.blit(font_grande.render(f"Punti: {calcola_punteggio(stato)}", True, (255,165,0)), (X+10, 128))
    schermo.blit(font_piccolo.render("nemici+ondate+vite", True, (160,160,160)),    (X+10, 158))

def disegna_pulsanti_torri(schermo, stato, immagini, font):
    """Disegna tutti i pulsanti delle torri usando la nuova funzione"""
    pulsanti = {}
    posizioni = [('arciere', 185), ('magia', 258), ('cannone', 331)]
    
    for tipo, pos_y in posizioni:
        costo = COSTI_TORRI[tipo]
        selezionato = stato['torre_selezionata'] == tipo
        pulsanti[tipo] = disegna_pulsante_torre(schermo, tipo, costo, pos_y, stato['soldi'], selezionato)
    
    return pulsanti

def disegna_pulsante_ondata(schermo, ondata_in_corso, font):
    """Disegna pulsante per avviare ondata"""
    if ondata_in_corso:
        return None
    
    X = LARGHEZZA_GIOCO
    r = pygame.Rect(X+10, 415, 200, 54)
    pygame.draw.rect(schermo, (20,80,160), r, border_radius=8)
    pygame.draw.rect(schermo, BLU, r, 2, border_radius=8)
    t = font.render("▶  Avvia Ondata", True, BIANCO)
    schermo.blit(t, (r.x + (r.width-t.get_width())//2, r.y + (r.height-t.get_height())//2))
    return r

def disegna_legenda(schermo, font):
    X = LARGHEZZA_GIOCO
    y = 490
    pygame.draw.line(schermo, (100,100,120), (X+10, y), (X+LARGHEZZA_PANNELLO-10, y), 1)
    schermo.blit(font.render("ESC = deseleziona torre", True, (160,160,160)), (X+10, y+8))
    schermo.blit(font.render("R = riavvia (game over)",  True, (160,160,160)), (X+10, y+24))

def disegna_preview(schermo, stato, gx, gy):
    colore = VERDE_CHIARO if cella_libera(stato, gx, gy) else ROSSO
    s = pygame.Surface((DIMENSIONE_CELLA, DIMENSIONE_CELLA), pygame.SRCALPHA)
    s.fill((*colore, 100))
    schermo.blit(s, (gx*DIMENSIONE_CELLA, gy*DIMENSIONE_CELLA))

def disegna_game_over(schermo, stato, classifica, font_grande, font_medio, font_piccolo):
    overlay = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    schermo.blit(overlay, (0, 0))

    cx = LARGHEZZA_SCHERMO // 2
    if stato['vittoria']:
        t_titolo = font_grande.render("VITTORIA!", True, GIALLO)
        colore_box = (60,100,0)
    else:
        t_titolo = font_grande.render("GAME OVER", True, ROSSO)
        colore_box = (100,0,0)

    box = pygame.Rect(cx-250, 60, 500, 560)
    pygame.draw.rect(schermo, colore_box, box, border_radius=14)
    pygame.draw.rect(schermo, BIANCO, box, 3, border_radius=14)

    schermo.blit(t_titolo, (cx - t_titolo.get_width()//2, 80))
    t_score = font_medio.render(f"Punteggio: {stato['punteggio_finale']}", True, (255,165,0))
    schermo.blit(t_score, (cx - t_score.get_width()//2, 160))
    t_det = font_piccolo.render("nemici x100 + ondate x500 + vite x200 + vittoria 2000", True, (180,180,180))
    schermo.blit(t_det, (cx - t_det.get_width()//2, 200))

    pygame.draw.line(schermo, GIALLO, (cx-180, 240), (cx+180, 240), 2)
    t_cls = font_medio.render("MIGLIORI PUNTEGGI", True, GIALLO)
    schermo.blit(t_cls, (cx - t_cls.get_width()//2, 252))

    medaglie  = ["1.", "2.", "3.", "4.", "5."]
    colori_c  = [GIALLO, (192,192,192), (205,127,50), BIANCO, BIANCO]
    for i, score in enumerate(classifica[:5]):
        t = font_medio.render(f"{medaglie[i]}  {score}", True, colori_c[i])
        schermo.blit(t, (cx - t.get_width()//2, 290 + i*36))

    pygame.draw.line(schermo, GRIGIO, (cx-180, 490), (cx+180, 490), 1)
    t_r = font_piccolo.render("Premi  R  per ricominciare", True, BIANCO)
    schermo.blit(t_r, (cx - t_r.get_width()//2, 502))

def disegna_gioco(schermo, stato, immagini, classifica, font_grande, font_medio, font_piccolo):
    """Disegna l'intera schermata di gioco. Ritorna (pulsanti_torri, pulsante_ondata)."""
    # Usa le nuove funzioni dal secondo codice
    disegna_sfondo(schermo)
    disegna_percorso(schermo)
    
    mostra_raggio = stato['torre_selezionata'] is not None
    for t in stato['torri']:
        disegna_torre(schermo, t, immagini, mostra_raggio)
    for n in stato['nemici']:
        disegna_nemico(schermo, n, immagini)
    for p in stato['proiettili']:
        disegna_proiettile(schermo, p, immagini)
    disegna_monete(schermo, stato['monete_anim'], immagini, font_piccolo)
    if stato['torre_selezionata']:
        mx, my = pygame.mouse.get_pos()
        if mx < LARGHEZZA_GIOCO:
            disegna_preview(schermo, stato, *pixel_a_griglia(mx, my))
    disegna_pannello(schermo, stato, immagini, font_grande, font_medio, font_piccolo)
    pulsanti_torri  = disegna_pulsanti_torri(schermo, stato, immagini, font_medio)
    pulsante_ondata = disegna_pulsante_ondata(schermo, stato['ondata_in_corso'], font_medio)
    disegna_legenda(schermo, font_piccolo)
    if stato['game_over']:
        disegna_game_over(schermo, stato, classifica, font_grande, font_medio, font_piccolo)
    return pulsanti_torri, pulsante_ondata


# =============================================================================
# SCHERMATA INIZIALE
# =============================================================================

def disegna_menu(schermo, immagini):
    sfondo = immagini.get('schermata_iniziale')
    if sfondo:
        schermo.blit(sfondo, (0, 0))
    else:
        schermo.fill((20,20,40))

    def rect_centrato(cy, w, h):
        r = pygame.Rect(0, 0, w, h)
        r.centerx = LARGHEZZA_SCHERMO // 2
        r.centery = cy
        return r

    r_avvia = rect_centrato(575, 220, 58)
    r_imp   = rect_centrato(636, 180, 34)
    r_esci  = rect_centrato(674, 120, 34)
    return r_avvia, r_imp, r_esci

def loop_menu(schermo, immagini, clock):
    while True:
        r_avvia, r_imp, r_esci = disegna_menu(schermo, immagini)
        pygame.display.flip()
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return 'gioca'
                if evento.key == pygame.K_ESCAPE:
                    return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                if r_avvia.collidepoint(mx, my): return 'gioca'
                if r_imp.collidepoint(mx, my):   return 'impostazioni'
                if r_esci.collidepoint(mx, my):  return False


# =============================================================================
# SCHERMATA IMPOSTAZIONI
# =============================================================================

def loop_impostazioni(schermo, immagini, font_grande, font_medio, font_piccolo, clock):
    istruzioni = [
        ("TORRI", ""),
        ("Arciere  $100", "Raggio 120, danno 15, fuoco medio"),
        ("Magia    $150", "Raggio 100, danno 8,  fuoco rapido"),
        ("Cannone  $200", "Raggio 200, danno 40, fuoco lento"),
        ("", ""),
        ("CONTROLLI", ""),
        ("Clic torre",   "Seleziona tipo di torre"),
        ("Clic campo",   "Piazza torre (non sul sentiero)"),
        ("Avvia Ondata", "Fa partire i nemici"),
        ("ESC",          "Deseleziona torre"),
        ("R",            "Riavvia dopo Game Over"),
        ("", ""),
        ("PUNTEGGIO", ""),
        ("Nemici",   "x 100 punti"),
        ("Ondate",   "x 500 punti"),
        ("Vite",     "x 200 punti"),
        ("Vittoria", "+ 2000 bonus"),
    ]

    while True:
        sfondo = immagini.get('schermata_iniziale')
        if sfondo: schermo.blit(sfondo, (0, 0))
        else: schermo.fill((20,20,40))

        overlay = pygame.Surface((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        schermo.blit(overlay, (0, 0))

        box = pygame.Rect(150, 40, 700, 590)
        pygame.draw.rect(schermo, (30,30,45), box, border_radius=16)
        pygame.draw.rect(schermo, GIALLO, box, 3, border_radius=16)

        t = font_grande.render("ISTRUZIONI", True, GIALLO)
        schermo.blit(t, (LARGHEZZA_SCHERMO//2 - t.get_width()//2, 58))
        pygame.draw.line(schermo, GIALLO, (200, 108), (800, 108), 1)

        y = 122
        for chiave, valore in istruzioni:
            if not chiave:
                y += 8; continue
            if not valore:
                schermo.blit(font_medio.render(chiave, True, GIALLO), (220, y))
            else:
                schermo.blit(font_medio.render(chiave, True, BIANCO), (220, y))
                schermo.blit(font_piccolo.render(valore, True, (180,180,180)), (430, y+4))
            y += 28

        r_ind = pygame.Rect(400, 570, 200, 44)
        pygame.draw.rect(schermo, (60,20,20), r_ind, border_radius=10)
        pygame.draw.rect(schermo, ROSSO, r_ind, 2, border_radius=10)
        t_ind = font_medio.render("← INDIETRO", True, BIANCO)
        schermo.blit(t_ind, (r_ind.x + (200-t_ind.get_width())//2,
                              r_ind.y + (44-t_ind.get_height())//2))

        pygame.display.flip()
        clock.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return True
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if r_ind.collidepoint(evento.pos):
                    return True


# =============================================================================
# GESTIONE INPUT GIOCO
# =============================================================================

def gestisci_click(stato, mx, my, pulsanti_torri, pulsante_ondata):
    if stato['game_over']:
        return
    for tipo, r in pulsanti_torri.items():
        if r.collidepoint(mx, my):
            if stato['soldi'] >= COSTI_TORRI[tipo]:
                stato['torre_selezionata'] = (None if stato['torre_selezionata'] == tipo else tipo)
            return
    if pulsante_ondata and pulsante_ondata.collidepoint(mx, my):
        avvia_ondata(stato)
        return
    if mx < LARGHEZZA_GIOCO and stato['torre_selezionata']:
        if piazza_torre(stato, *pixel_a_griglia(mx, my)):
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
    font_medio   = pygame.font.Font(None, 32)
    font_piccolo = pygame.font.Font(None, 22)

    immagini   = carica_immagini()
    classifica = []

    while True:
        risultato = loop_menu(schermo, immagini, clock)

        if risultato is False:
            break

        if risultato == 'impostazioni':
            if not loop_impostazioni(schermo, immagini, font_grande, font_medio, font_piccolo, clock):
                break
            continue

        if risultato == 'gioca':
            stato           = inizializza_gioco()
            pulsanti_torri  = {}
            pulsante_ondata = None

            in_gioco = True
            while in_gioco:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit(); return
                    if evento.type == pygame.MOUSEBUTTONDOWN:
                        gestisci_click(stato, *evento.pos, pulsanti_torri, pulsante_ondata)
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_r and stato['game_over']:
                            score = stato['punteggio_finale']
                            if score > 0:
                                classifica.append(score)
                                classifica.sort(reverse=True)
                                classifica[:] = classifica[:5]
                            stato = inizializza_gioco()
                        elif evento.key == pygame.K_ESCAPE:
                            if stato['game_over']:
                                in_gioco = False  # torna al menu
                            else:
                                stato['torre_selezionata'] = None

                if in_gioco:
                    aggiorna_gioco(stato)
                    pulsanti_torri, pulsante_ondata = disegna_gioco(
                        schermo, stato, immagini, classifica,
                        font_grande, font_medio, font_piccolo)
                    pygame.display.flip()
                    clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
