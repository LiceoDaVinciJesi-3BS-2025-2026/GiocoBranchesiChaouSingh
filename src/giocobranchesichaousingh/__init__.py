def main() -> None:
    print("Hello from giocobranchesichaousingh!")
    
import pygame
import math
import random
from pathlib import Path

# Inizializzazione Pygame
pygame.init()

# Costanti
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GRID_SIZE = 50
GRID_WIDTH = 16
GRID_HEIGHT = 12
FPS = 60

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 90, 43)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)

# Setup schermo
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# ── CARICAMENTO IMMAGINI TORRI ──────────────────────────────────────────────
def _load_tower_image(filename):
    """Carica e scala l'immagine di una torre; ritorna None se il file manca."""
    try:
        path = Path(__file__).parent / filename
        return pygame.transform.scale(pygame.image.load(str(path)).convert_alpha(), (80, 80))
    except Exception:
        return None

TOWER_IMAGES = {
    'basic':  _load_tower_image('torre_basic.png'),
    'rapid':  _load_tower_image('torre_rapid.png'),
    'sniper': _load_tower_image('torre_sniper.png'),
}
# DEBUG - aggiungi queste righe temporanee
print("Cartella cercata:", Path(__file__).parent)
print("basic trovata:", TOWER_IMAGES['basic'] is not None)
print("rapid trovata:", TOWER_IMAGES['rapid'] is not None)
print("sniper trovata:", TOWER_IMAGES['sniper'] is not None)
def _load_projectile_image(filename):
    """Carica e scala l'immagine di un proiettile piccolo."""
    try:
        path = Path(__file__).parent / filename
        return pygame.transform.scale(pygame.image.load(str(path)).convert_alpha(), (50, 50))
    except Exception:
        return None

PROJECTILE_IMAGES = {
    'basic':  _load_projectile_image('freccia_basic.png'),
    'rapid':  _load_projectile_image('freccia_rapid.png'),
    'sniper': _load_projectile_image('freccia_sniper.png'),
}
# ────────────────────────────────────────────────────────────────────────────

# Percorso dei nemici (coordinate griglia)
PATH = [
    (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
    (6, 4), (6, 3), (6, 2), (6, 1),
    (7, 1), (8, 1), (9, 1), (10, 1),
    (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
    (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7)
]


# Funzioni di utilità
def grid_to_pixel(grid_x, grid_y):
    """Converte coordinate griglia in pixel"""
    return (grid_x * GRID_SIZE + GRID_SIZE // 2, grid_y * GRID_SIZE + GRID_SIZE // 2)


def get_path_pixels():
    """Converte il percorso in coordinate pixel"""
    return [grid_to_pixel(x, y) for x, y in PATH]


# Funzioni per i nemici
def create_enemy(health, speed, reward):
    """Crea un nuovo nemico"""
    path_pixels = get_path_pixels()
    return {
        'max_health': health,
        'health': health,
        'speed': speed,
        'reward': reward,
        'path_index': 0,
        'x': path_pixels[0][0],
        'y': path_pixels[0][1],
        'radius': 8
    }


def move_enemy(enemy):
    """Muove un nemico lungo il percorso. Ritorna True se ha raggiunto la fine"""
    path_pixels = get_path_pixels()
    
    if enemy['path_index'] < len(path_pixels) - 1:
        target_x, target_y = path_pixels[enemy['path_index'] + 1]
        dx = target_x - enemy['x']
        dy = target_y - enemy['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < enemy['speed']:
            enemy['path_index'] += 1
            if enemy['path_index'] < len(path_pixels):
                enemy['x'], enemy['y'] = path_pixels[enemy['path_index']]
        else:
            enemy['x'] += (dx / distance) * enemy['speed']
            enemy['y'] += (dy / distance) * enemy['speed']
            
    return enemy['path_index'] >= len(path_pixels) - 1


def damage_enemy(enemy, damage):
    """Infligge danno a un nemico. Ritorna True se è morto"""
    enemy['health'] -= damage
    return enemy['health'] <= 0


def draw_enemy(screen, enemy):
    """Disegna un nemico"""
    # Corpo
    pygame.draw.circle(screen, RED, (int(enemy['x']), int(enemy['y'])), enemy['radius'])
    
    # Barra vita
    bar_width = 30
    bar_height = 4
    bar_x = enemy['x'] - bar_width // 2
    bar_y = enemy['y'] - enemy['radius'] - 8
    health_percentage = enemy['health'] / enemy['max_health']
    
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_percentage, bar_height))


# Funzioni per i proiettili
def create_projectile(x, y, target, damage, speed=8):
    """Crea un nuovo proiettile"""
    return {
        'x': x,
        'y': y,
        'target': target,
        'damage': damage,
        'speed': speed,
        'radius': 4
        'type': tower_type 
    }


def move_projectile(projectile):
    """Muove un proiettile verso il target. Ritorna True se ha colpito o il target è morto"""
    target = projectile['target']
    
    if target and target['health'] > 0:
        dx = target['x'] - projectile['x']
        dy = target['y'] - projectile['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < projectile['speed']:
            return True  # Ha colpito
        
        projectile['x'] += (dx / distance) * projectile['speed']
        projectile['y'] += (dy / distance) * projectile['speed']
        return False
    
    return True  # Target morto, rimuovi proiettile


def draw_projectile(screen, projectile):
    img = PROJECTILE_IMAGES.get(projectile.get('type', 'basic'))
    if img:
        rect = img.get_rect(center=(int(projectile['x']), int(projectile['y'])))
        screen.blit(img, rect)
    else:
        pygame.draw.circle(screen, YELLOW, (int(projectile['x']), int(projectile['y'])),
                           projectile['radius'])


# Funzioni per le torri
def create_tower(grid_x, grid_y, tower_type):
    """Crea una nuova torre"""
    px, py = grid_to_pixel(grid_x, grid_y)
    
    # Statistiche in base al tipo
    stats = {
        'basic': {'range': 120, 'damage': 15, 'fire_rate': 60, 'color': BLUE, 'cost': 100},
        'sniper': {'range': 200, 'damage': 40, 'fire_rate': 120, 'color': PURPLE, 'cost': 200},
        'rapid': {'range': 100, 'damage': 8, 'fire_rate': 20, 'color': ORANGE, 'cost': 150}
    }
    
    tower_stats = stats[tower_type]
    
    return {
        'grid_x': grid_x,
        'grid_y': grid_y,
        'x': px,
        'y': py,
        'type': tower_type,
        'range': tower_stats['range'],
        'damage': tower_stats['damage'],
        'fire_rate': tower_stats['fire_rate'],
        'color': tower_stats['color'],
        'cooldown': 0,
        'target': None
    }


def find_tower_target(tower, enemies):
    """Trova un nemico nel raggio della torre"""
    tower['target'] = None
    for enemy in enemies:
        distance = math.sqrt((enemy['x'] - tower['x'])**2 + (enemy['y'] - tower['y'])**2)
        if distance <= tower['range']:
            tower['target'] = enemy
            break


def update_tower(tower):
    """Aggiorna il cooldown della torre"""
    if tower['cooldown'] > 0:
        tower['cooldown'] -= 1


def can_tower_shoot(tower):
    """Controlla se la torre può sparare"""
    target = tower['target']
    if target and target['health'] > 0 and tower['cooldown'] == 0:
        distance = math.sqrt((target['x'] - tower['x'])**2 + (target['y'] - tower['y'])**2)
        if distance <= tower['range']:
            return True
    return False


def tower_shoot(tower):
    tower['cooldown'] = tower['fire_rate']
    return create_projectile(tower['x'], tower['y'], tower['target'],
                             tower['damage'], tower_type=tower['type'])


def draw_tower(screen, tower, show_range=False):
    if show_range:
        pygame.draw.circle(screen, (*tower['color'], 50), 
                         (int(tower['x']), int(tower['y'])), tower['range'], 1)
    
    img = TOWER_IMAGES.get(tower['type'])
    if img:
        rect = img.get_rect(center=(int(tower['x']), int(tower['y'])))
        screen.blit(img, rect)
    else:
        size = 20
        pygame.draw.rect(screen, tower['color'],
                        (tower['x'] - size//2, tower['y'] - size//2, size, size))
        pygame.draw.rect(screen, BLACK,
                        (tower['x'] - size//2, tower['y'] - size//2, size, size), 2)


# Funzioni di gioco
def init_game():
    """Inizializza lo stato del gioco"""
    return {
        'money': 300,
        'lives': 20,
        'wave': 0,
        'enemies': [],
        'towers': [],
        'projectiles': [],
        'selected_tower_type': None,
        'game_over': False,
        'won': False,
        'spawn_timer': 0,
        'enemies_to_spawn': 0,
        'wave_in_progress': False
    }


def get_tower_buttons():
    """Ritorna i pulsanti delle torri"""
    return [
        {'type': 'basic', 'cost': 100, 'rect': pygame.Rect(820, 100, 150, 60), 'name': 'Basic'},
        {'type': 'rapid', 'cost': 150, 'rect': pygame.Rect(820, 170, 150, 60), 'name': 'Rapid'},
        {'type': 'sniper', 'cost': 200, 'rect': pygame.Rect(820, 240, 150, 60), 'name': 'Sniper'},
    ]


def start_wave(game_state):
    """Avvia una nuova ondata"""
    if not game_state['wave_in_progress'] and not game_state['game_over']:
        game_state['wave'] += 1
        game_state['wave_in_progress'] = True
        game_state['enemies_to_spawn'] = 5 + game_state['wave'] * 3
        game_state['spawn_timer'] = 0


def spawn_enemy(game_state):
    """Spawna un nemico"""
    wave = game_state['wave']
    health = 50 + wave * 20
    speed = 1 + wave * 0.1
    reward = 20 + wave * 5
    game_state['enemies'].append(create_enemy(health, min(speed, 3), reward))


def can_place_tower(game_state, grid_x, grid_y):
    """Controlla se si può piazzare una torre in una posizione"""
    # Controlla se è sul percorso
    if (grid_x, grid_y) in PATH:
        return False
    
    # Controlla se c'è già una torre
    for tower in game_state['towers']:
        if tower['grid_x'] == grid_x and tower['grid_y'] == grid_y:
            return False
    
    return True


def place_tower(game_state, grid_x, grid_y, tower_buttons):
    """Piazza una torre se possibile"""
    if game_state['selected_tower_type']:
        if not can_place_tower(game_state, grid_x, grid_y):
            return False
        
        # Trova costo
        cost = 0
        for btn in tower_buttons:
            if btn['type'] == game_state['selected_tower_type']:
                cost = btn['cost']
                break
        
        if game_state['money'] >= cost:
            tower = create_tower(grid_x, grid_y, game_state['selected_tower_type'])
            game_state['towers'].append(tower)
            game_state['money'] -= cost
            return True
    
    return False


def update_game(game_state):
    """Aggiorna lo stato del gioco"""
    if game_state['game_over']:
        return
    
    # Spawn nemici
    if game_state['wave_in_progress'] and game_state['enemies_to_spawn'] > 0:
        game_state['spawn_timer'] += 1
        if game_state['spawn_timer'] >= 60:  # Ogni secondo
            spawn_enemy(game_state)
            game_state['enemies_to_spawn'] -= 1
            game_state['spawn_timer'] = 0
    
    # Controlla fine ondata
    if (game_state['enemies_to_spawn'] == 0 and 
        len(game_state['enemies']) == 0 and 
        game_state['wave_in_progress']):
        game_state['wave_in_progress'] = False
        game_state['money'] += 50  # Bonus
    
    # Controlla vittoria
    if (game_state['wave'] >= 10 and 
        not game_state['wave_in_progress'] and 
        len(game_state['enemies']) == 0):
        game_state['won'] = True
        game_state['game_over'] = True
    
    # Aggiorna nemici
    for enemy in game_state['enemies'][:]:
        if move_enemy(enemy):  # Raggiunto fine
            game_state['lives'] -= 1
            game_state['enemies'].remove(enemy)
            if game_state['lives'] <= 0:
                game_state['game_over'] = True
    
    # Aggiorna torri
    for tower in game_state['towers']:
        update_tower(tower)
        find_tower_target(tower, game_state['enemies'])
        if can_tower_shoot(tower):
            projectile = tower_shoot(tower)
            game_state['projectiles'].append(projectile)
    
    # Aggiorna proiettili
    for projectile in game_state['projectiles'][:]:
        if move_projectile(projectile):
            # Colpito o target morto
            target = projectile['target']
            if target and target['health'] > 0:
                if damage_enemy(target, projectile['damage']):
                    game_state['money'] += target['reward']
                    if target in game_state['enemies']:
                        game_state['enemies'].remove(target)
            game_state['projectiles'].remove(projectile)


def draw_game(screen, game_state, tower_buttons):
    """Disegna il gioco"""
    screen.fill(GREEN)
    
    # Griglia
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, DARK_GREEN, rect, 1)
    
    # Percorso
    for gx, gy in PATH:
        pygame.draw.rect(screen, BROWN, (gx * GRID_SIZE, gy * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    
    # Torri
    show_range = game_state['selected_tower_type'] is not None
    for tower in game_state['towers']:
        draw_tower(screen, tower, show_range)
    
    # Nemici
    for enemy in game_state['enemies']:
        draw_enemy(screen, enemy)
    
    # Proiettili
    for projectile in game_state['projectiles']:
        draw_projectile(screen, projectile)
    
    # UI Panel
    pygame.draw.rect(screen, GRAY, (800, 0, 200, SCREEN_HEIGHT))
    
    # Info
    money_text = font.render(f"Soldi: ${game_state['money']}", True, YELLOW)
    lives_text = font.render(f"Vite: {game_state['lives']}", True, RED)
    wave_text = font.render(f"Ondata: {game_state['wave']}/10", True, WHITE)
    
    screen.blit(money_text, (810, 10))
    screen.blit(lives_text, (810, 40))
    screen.blit(wave_text, (810, 70))
    
    # Pulsanti torri
    for btn in tower_buttons:
        color = GREEN if game_state['money'] >= btn['cost'] else GRAY
        if game_state['selected_tower_type'] == btn['type']:
            color = YELLOW
        pygame.draw.rect(screen, color, btn['rect'])
        pygame.draw.rect(screen, BLACK, btn['rect'], 2)
        
        name_text = small_font.render(btn['name'], True, BLACK)
        cost_text = small_font.render(f"${btn['cost']}", True, BLACK)
        screen.blit(name_text, (btn['rect'].x + 10, btn['rect'].y + 10))
        screen.blit(cost_text, (btn['rect'].x + 10, btn['rect'].y + 35))
    
    # Pulsante avvia ondata
    start_wave_button = pygame.Rect(820, 350, 150, 60)
    if not game_state['wave_in_progress'] and not game_state['game_over']:
        pygame.draw.rect(screen, BLUE, start_wave_button)
        pygame.draw.rect(screen, BLACK, start_wave_button, 2)
        start_text = small_font.render("Avvia Ondata", True, WHITE)
        screen.blit(start_text, (start_wave_button.x + 15, start_wave_button.y + 20))
    
    # Preview torre selezionata
    if game_state['selected_tower_type']:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x < 800:
            grid_x = mouse_x // GRID_SIZE
            grid_y = mouse_y // GRID_SIZE
            
            valid = can_place_tower(game_state, grid_x, grid_y)
            color = GREEN if valid else RED
            pygame.draw.rect(screen, (*color, 100), 
                           (grid_x * GRID_SIZE, grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    
    # Game Over
    if game_state['game_over']:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        if game_state['won']:
            end_text = font.render("VITTORIA!", True, YELLOW)
        else:
            end_text = font.render("GAME OVER", True, RED)
        
        restart_text = small_font.render("Premi R per ricominciare", True, WHITE)
        screen.blit(end_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))


def handle_click(game_state, mouse_x, mouse_y, tower_buttons):
    """Gestisce i click del mouse"""
    if game_state['game_over']:
        return
    
    # Click su pulsanti torri
    for btn in tower_buttons:
        if btn['rect'].collidepoint(mouse_x, mouse_y):
            if game_state['money'] >= btn['cost']:
                if game_state['selected_tower_type'] == btn['type']:
                    game_state['selected_tower_type'] = None
                else:
                    game_state['selected_tower_type'] = btn['type']
            return
    
    # Click su avvia ondata
    start_wave_button = pygame.Rect(820, 350, 150, 60)
    if start_wave_button.collidepoint(mouse_x, mouse_y):
        start_wave(game_state)
        return
    
    # Piazza torre
    if mouse_x < 800 and game_state['selected_tower_type']:
        grid_x = mouse_x // GRID_SIZE
        grid_y = mouse_y // GRID_SIZE
        if place_tower(game_state, grid_x, grid_y, tower_buttons):
            game_state['selected_tower_type'] = None


def main():
    """Funzione principale"""
    game_state = init_game()
    tower_buttons = get_tower_buttons()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                handle_click(game_state, mouse_x, mouse_y, tower_buttons)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state['game_over']:
                    game_state = init_game()
                if event.key == pygame.K_ESCAPE:
                    game_state['selected_tower_type'] = None
        
        update_game(game_state)
        draw_game(screen, game_state, tower_buttons)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
