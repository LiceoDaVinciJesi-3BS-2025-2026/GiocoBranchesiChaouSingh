def main() -> None:
    print("Hello from giocobranchesichaousingh!")
    
import pygame
import math

# =======================
# INIZIALIZZAZIONE
# =======================
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Semplice - No Classi")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# =======================
# VARIABILI DI GIOCO
# =======================
gold = 200
lives = 10
level = 1

towers = []
enemies = []
ondata_corrente = []

spawn_timer = 0
spawn_delay = 1000  # millisecondi

# =======================
# FUNZIONI DI SUPPORTO
# =======================
def distanza(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# =======================
# CREAZIONE TORRE
# =======================
def crea_torre(x, y):
    return {
        "x": x,
        "y": y,
        "range": 120,
        "damage": 25,
        "cooldown": 800,
        "last_shot": 0
    }

# =======================
# CREAZIONE NEMICO
# =======================
def crea_nemico(level):
    return {
        "x": 0,
        "y": 300,
        "hp": 80 + level * 20,
        "speed": 1 + level * 0.2,
        "reward": 10,
        "reached_goal": False
    }

# =======================
# CREAZIONE ONDATA
# =======================
def crea_ondata(level):
    ondata = []
    for i in range(5 + level * 2):
        ondata.append(crea_nemico(level))
    return ondata

# =======================
# ATTACCO TORRI
# =======================
def torri_attaccano(tempo):
    for torre in towers:
        if tempo - torre["last_shot"] < torre["cooldown"]:
            continue

        for nemico in enemies:
            if distanza(torre["x"], torre["y"], nemico["x"], nemico["y"]) <= torre["range"]:
                nemico["hp"] -= torre["damage"]
                torre["last_shot"] = tempo
                break

# =======================
# MOVIMENTO NEMICI
# =======================
def muovi_nemici():
    for nemico in enemies:
        nemico["x"] += nemico["speed"]
        if nemico["x"] > WIDTH:
            nemico["reached_goal"] = True

# =======================
# RIMOZIONE NEMICI
# =======================
def pulizia_nemici():
    global gold, lives
    for nemico in enemies[:]:
        if nemico["hp"] <= 0:
            gold += nemico["reward"]
            enemies.remove(nemico)
        elif nemico["reached_goal"]:
            lives -= 1
            enemies.remove(nemico)

# =======================
# GESTIONE SPAWN
# =======================
def gestisci_spawn(dt):
    global spawn_timer
    spawn_timer += dt
    if ondata_corrente and spawn_timer >= spawn_delay:
        enemies.append(ondata_corrente.pop(0))
        spawn_timer = 0

# =======================
# CONTROLLO LIVELLO
# =======================
def controlla_livello():
    global level, ondata_corrente
    if not enemies and not ondata_corrente:
        level += 1
        ondata_corrente = crea_ondata(level)

# =======================
# DISEGNO
# =======================
def disegna():
    screen.fill((30, 30, 30))

    pygame.draw.rect(screen, (60, 120, 60), (0, 280, WIDTH, 80))

    for torre in towers:
        pygame.dr
ù
