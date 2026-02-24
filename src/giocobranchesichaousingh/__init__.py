def main() -> None:
    print("Hello from giocobranchesichaousingh!")
    
import pygame
import math
import os

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
pygame.display.set_caption("Tower Defense - Sprite Edition")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Percorso dei nemici
PATH = [
    (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
    (6, 4), (6, 3), (6, 2), (6, 1),
    (7, 1), (8, 1), (9, 1), (10, 1),
    (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
    (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7)
]

# Carica sprites
SPRITES = {}

def load_sprites():
    """Carica tutte le immagini degli sprites"""
    sprite_dir = '/home/claude/sprites'
    
    # Torri
    SPRITES['tower_archer'] = pygame.image.load(f'{sprite_dir}/tower_archer.png').convert_alpha()
    SPRITES['tower_cannon'] = pygame.image.load(f'{sprite_dir}/tower_cannon.png').convert_alpha()
    SPRITES['tower_magic'] = pygame.image.load(f'{sprite_dir}/tower_magic.png').convert_alpha()
    
    # Mostri
    SPRITES['monster_goblin'] = pygame.image.load(f'{sprite_dir}/monster_goblin.png').convert_alpha()
    SPRITES['monster_orc'] = pygame.image.load(f'{sprite_dir}/monster_orc.png').convert_alpha()
    SPRITES['monster_demon'] = pygame.image.load(f'{sprite_dir}/monster_demon.png').convert_alpha()
    
    # Proiettili
    SPRITES['projectile_arrow'] = pygame.image.load(f'{sprite_dir}/projectile_arrow.png').convert_alpha()
    SPRITES['projectile_cannonball'] = pygame.image.load(f'{sprite_dir}/projectile_cannonball.png').convert_alpha()
    SPRITES['projectile_magic'] = pygame.image.load(f'{sprite_dir}/projectile_magic.png').convert_alpha()
    
    # Tiles terreno
    SPRITES['tile_grass'] = pygame.image.load(f'{sprite_dir}/tile_grass.png').convert()
    SPRITES['tile_path'] = pygame.image.load(f'{sprite_dir}/tile_path.png').convert()
    
    print("✅ Sprites caricati con successo!")


# Funzioni di utilità
def grid_to_pixel(grid_x, grid_y):
    """Converte coordinate griglia in pixel"""
    return (grid_x * GRID_SIZE + GRID_SIZE // 2, grid_y * GRID_SIZE + GRID_SIZE // 2)


def get_path_pixels():
    """Converte il percorso in coordinate pixel"""
    return [grid_to_pixel(x, y) for x, y in PATH]


# Funzioni per i nemici
def create_enemy(health, speed, reward, enemy_type='goblin'):
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
        'type': enemy_type,
        'sprite': SPRITES[f'monster_{enemy_type}']
    }


def move_enemy(enemy):
    """Muove un nemico lungo il percorso"""
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
    """Infligge danno a un nemico"""
    enemy['health'] -= damage
    return enemy['health'] <= 0


def draw_enemy(screen, enemy):
    """Disegna un nemico usando lo sprite"""
    sprite = enemy['sprite']
    x = int(enemy['x'])
    y = int(enemy['y'])
    
    # Centra lo sprite
    sprite_rect = sprite.get_rect()
    sprite_rect.center = (x, y)
    screen.blit(sprite, sprite_rect)
    
    # Barra vita
    bar_width = 30
    bar_height = 4
    bar_x = x - bar_width // 2
    bar_y = y - sprite_rect.height // 2 - 10
    health_percentage = enemy['health'] / enemy['max_health']
    
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_percentage, bar_height))


# Funzioni per i proiettili
def create_projectile(x, y, target, damage, speed, proj_type):
    """Crea un nuovo proiettile"""
    return {
        'x': x,
        'y': y,
        'target': target,
        'damage': damage,
        'speed': speed,
        'type': proj_type,
        'sprite': SPRITES[f'projectile_{proj_type}'],
        'angle': 0
    }


def move_projectile(projectile):
    """Muove un proiettile verso il target"""
    target = projectile['target']
    
    if target and target['health'] > 0:
        dx = target['x'] - projectile['x']
        dy = target['y'] - projectile['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calcola angolo per rotazione
        projectile['angle'] = math.degrees(math.atan2(-dy, -dx))
        
        if distance < projectile['speed']:
            return True
        
        projectile['x'] += (dx / distance) * projectile['speed']
        projectile['y'] += (dy / distance) * projectile['speed']
        return False
    
    return True


def draw_projectile(screen, projectile):
    """Disegna un proiettile usando lo sprite"""
    sprite = projectile['sprite']
    x = int(projectile['x'])
    y = int(projectile['y'])
    
    # Ruota sprite in base alla direzione
    if projectile['type'] == 'arrow':
        rotated_sprite = pygame.transform.rotate(sprite, projectile['angle'])
    else:
        rotated_sprite = sprite
    
    # Centra lo sprite
    sprite_rect = rotated_sprite.get_rect()
    sprite_rect.center = (x, y)
    screen.blit(rotated_sprite, sprite_rect)


# Funzioni per le torri
def create_tower(grid_x, grid_y, tower_type):
    """Crea una nuova torre"""
    px, py = grid_to_pixel(grid_x, grid_y)
    
    stats = {
        'archer': {
            'range': 120, 'damage': 15, 'fire_rate': 60,
            'color': BLUE, 'cost': 100, 'projectile': 'arrow'
        },
        'cannon': {
            'range': 200, 'damage': 40, 'fire_rate': 120,
            'color': PURPLE, 'cost': 200, 'projectile': 'cannonball'
        },
        'magic': {
            'range': 100, 'damage': 8, 'fire_rate': 20,
            'color': ORANGE, 'cost': 150, 'projectile': 'magic'
        }
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
        'projectile_type': tower_stats['projectile'],
        'cooldown': 0,
        'target': None,
        'sprite': SPRITES[f'tower_{tower_type}']
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
    """Fa sparare la torre"""
    tower['cooldown'] = tower['fire_rate']
    
    # Posizione di partenza del proiettile (in cima alla torre)
    sprite_height = tower['sprite'].get_height()
    start_y = tower['y'] - sprite_height // 2
    
    return create_projectile(
        tower['x'], start_y, tower['target'],
        tower['damage'], 8, tower['projectile_type']
    )


def draw_tower(screen, tower, show_range=False):
    """Disegna una torre usando lo sprite"""
    sprite = tower['sprite']
    x = int(tower['x'])
    y = int(tower['y'])
    
    # Raggio (opzionale)
    if show_range:
        pygame.draw.circle(screen, (*tower['color'], 50), (x, y), tower['range'], 1)
    
    # Centra lo sprite
    sprite_rect = sprite.get_rect()
    sprite_rect.center = (x, y)
    screen.blit(sprite, sprite_rect)


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
        {'type': 'archer', 'cost': 100, 'rect': pygame.Rect(820, 100, 150, 60), 'name': 'Archer'},
        {'type': 'magic', 'cost': 150, 'rect': pygame.Rect(820, 170, 150, 60), 'name': 'Magic'},
        {'type': 'cannon', 'cost': 200, 'rect': pygame.Rect(820, 240, 150, 60), 'name': 'Cannon'},
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
    
    # Determina tipo di nemico in base all'ondata
    if wave <= 3:
        enemy_type = 'goblin'
        health = 50 + wave * 20
    elif wave <= 7:
        enemy_type = 'orc'
        health = 80 + wave * 25
    else:
        enemy_type = 'demon'
        health = 120 + wave * 30
    
    speed = 1 + wave * 0.1
    reward = 20 + wave * 5
    game_state['enemies'].append(create_enemy(health, min(speed, 3), reward, enemy_type))


def can_place_tower(game_state, grid_x, grid_y):
    """Controlla se si può piazzare una torre"""
    if (grid_x, grid_y) in PATH:
        return False
    
    for tower in game_state['towers']:
        if tower['grid_x'] == grid_x and tower['grid_y'] == grid_y:
            return False
    
    return True


def place_tower(game_state, grid_x, grid_y, tower_buttons):
    """Piazza una torre se possibile"""
    if game_state['selected_tower_type']:
        if not can_place_tower(game_state, grid_x, grid_y):
            return False
        
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
        if game_state['spawn_timer'] >= 60:
            spawn_enemy(game_state)
            game_state['enemies_to_spawn'] -= 1
            game_state['spawn_timer'] = 0
    
    # Controlla fine ondata
    if (game_state['enemies_to_spawn'] == 0 and
        len(game_state['enemies']) == 0 and
        game_state['wave_in_progress']):
        game_state['wave_in_progress'] = False
        game_state['money'] += 50
    
    # Controlla vittoria
    if (game_state['wave'] >= 10 and
        not game_state['wave_in_progress'] and
        len(game_state['enemies']) == 0):
        game_state['won'] = True
        game_state['game_over'] = True
    
    # Aggiorna nemici
    for enemy in game_state['enemies'][:]:
        if move_enemy(enemy):
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
            target = projectile['target']
            if target and target['health'] > 0:
                if damage_enemy(target, projectile['damage']):
                    game_state['money'] += target['reward']
                    if target in game_state['enemies']:
                        game_state['enemies'].remove(target)
            game_state['projectiles'].remove(projectile)


def draw_game(screen, game_state, tower_buttons):
    """Disegna il gioco"""
    # Disegna il terreno con tiles realistici
    grass_tile = SPRITES['tile_grass']
    path_tile = SPRITES['tile_path']
    
    # Riempi tutto con erba
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            screen.blit(grass_tile, (x * GRID_SIZE, y * GRID_SIZE))
    
    # Disegna il percorso
    for gx, gy in PATH:
        screen.blit(path_tile, (gx * GRID_SIZE, gy * GRID_SIZE))
    
    # Griglia leggera (opzionale, meno visibile)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (0, 0, 0, 30), rect, 1)
    
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
    
    # Pulsanti torri con preview sprite
    for btn in tower_buttons:
        color = GREEN if game_state['money'] >= btn['cost'] else GRAY
        if game_state['selected_tower_type'] == btn['type']:
            color = YELLOW
        pygame.draw.rect(screen, color, btn['rect'])
        pygame.draw.rect(screen, BLACK, btn['rect'], 2)
        
        # Mini preview sprite
        tower_sprite = SPRITES[f"tower_{btn['type']}"]
        mini_sprite = pygame.transform.scale(tower_sprite, (40, 50))
        screen.blit(mini_sprite, (btn['rect'].x + 5, btn['rect'].y + 5))
        
        name_text = small_font.render(btn['name'], True, BLACK)
        cost_text = small_font.render(f"${btn['cost']}", True, BLACK)
        screen.blit(name_text, (btn['rect'].x + 50, btn['rect'].y + 10))
        screen.blit(cost_text, (btn['rect'].x + 50, btn['rect'].y + 35))
    
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
            
            # Mostra preview sprite della torre
            tower_sprite = SPRITES[f"tower_{game_state['selected_tower_type']}"]
            preview_sprite = tower_sprite.copy()
            preview_sprite.set_alpha(150)
            px, py = grid_to_pixel(grid_x, grid_y)
            sprite_rect = preview_sprite.get_rect()
            sprite_rect.center = (px, py)
            screen.blit(preview_sprite, sprite_rect)
    
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
    # Carica sprites
    load_sprites()
    
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