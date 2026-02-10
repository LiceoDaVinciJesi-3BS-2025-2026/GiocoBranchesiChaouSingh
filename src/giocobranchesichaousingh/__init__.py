def main() -> None:
    print("Hello from giocobranchesichaousingh!")
    
# blablabla prova
# facciamo un gioco simile a Minesweeper
import pygame
import math
import random

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

# Percorso dei nemici (coordinate griglia)
PATH = [
    (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
    (6, 4), (6, 3), (6, 2), (6, 1),
    (7, 1), (8, 1), (9, 1), (10, 1),
    (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
    (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7)
]

# Convertire percorso in coordinate pixel
def grid_to_pixel(grid_x, grid_y):
    return (grid_x * GRID_SIZE + GRID_SIZE // 2, grid_y * GRID_SIZE + GRID_SIZE // 2)

PATH_PIXELS = [grid_to_pixel(x, y) for x, y in PATH]


class Enemy:
    def __init__(self, health, speed, reward):
        self.max_health = health
        self.health = health
        self.speed = speed
        self.reward = reward
        self.path_index = 0
        self.x, self.y = PATH_PIXELS[0]
        self.radius = 8
        
    def move(self):
        if self.path_index < len(PATH_PIXELS) - 1:
            target_x, target_y = PATH_PIXELS[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                self.path_index += 1
                if self.path_index < len(PATH_PIXELS):
                    self.x, self.y = PATH_PIXELS[self.path_index]
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                
        return self.path_index >= len(PATH_PIXELS) - 1
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        # Corpo nemico
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        
        # Barra vita
        bar_width = 30
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 8
        health_percentage = self.health / self.max_health
        
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_percentage, bar_height))


class Projectile:
    def __init__(self, x, y, target, damage, speed=8):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.radius = 4
        
    def move(self):
        if self.target and self.target.health > 0:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                return True  # Hit target
            
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            return False
        return True  # Target dead, remove projectile
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)


class Tower:
    def __init__(self, grid_x, grid_y, tower_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x, self.y = grid_to_pixel(grid_x, grid_y)
        self.type = tower_type
        
        # Statistiche torre in base al tipo
        if tower_type == "basic":
            self.range = 120
            self.damage = 15
            self.fire_rate = 60  # frame tra spari
            self.color = BLUE
            self.cost = 100
        elif tower_type == "sniper":
            self.range = 200
            self.damage = 40
            self.fire_rate = 120
            self.color = PURPLE
            self.cost = 200
        elif tower_type == "rapid":
            self.range = 100
            self.damage = 8
            self.fire_rate = 20
            self.color = ORANGE
            self.cost = 150
            
        self.cooldown = 0
        self.target = None
        
    def find_target(self, enemies):
        self.target = None
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance <= self.range:
                self.target = enemy
                break
                
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            
    def can_shoot(self):
        if self.target and self.target.health > 0 and self.cooldown == 0:
            distance = math.sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
            if distance <= self.range:
                return True
        return False
    
    def shoot(self):
        self.cooldown = self.fire_rate
        return Projectile(self.x, self.y, self.target, self.damage)
    
    def draw(self, screen, show_range=False):
        # Raggio (opzionale)
        if show_range:
            pygame.draw.circle(screen, (*self.color, 50), (int(self.x), int(self.y)), 
                             self.range, 1)
        
        # Torre
        size = 20
        pygame.draw.rect(screen, self.color, 
                        (self.x - size//2, self.y - size//2, size, size))
        pygame.draw.rect(screen, BLACK, 
                        (self.x - size//2, self.y - size//2, size, size), 2)


class Game:
    def __init__(self):
        self.money = 300
        self.lives = 20
        self.wave = 0
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.selected_tower_type = None
        self.game_over = False
        self.won = False
        self.spawn_timer = 0
        self.enemies_to_spawn = 0
        self.wave_in_progress = False
        
        # UI
        self.tower_buttons = [
            {"type": "basic", "cost": 100, "rect": pygame.Rect(820, 100, 150, 60), "name": "Basic"},
            {"type": "rapid", "cost": 150, "rect": pygame.Rect(820, 170, 150, 60), "name": "Rapid"},
            {"type": "sniper", "cost": 200, "rect": pygame.Rect(820, 240, 150, 60), "name": "Sniper"},
        ]
        self.start_wave_button = pygame.Rect(820, 350, 150, 60)
        
    def start_wave(self):
        if not self.wave_in_progress and not self.game_over:
            self.wave += 1
            self.wave_in_progress = True
            # Aumenta nemici e difficoltà per ondata
            self.enemies_to_spawn = 5 + self.wave * 3
            self.spawn_timer = 0
            
    def spawn_enemy(self):
        health = 50 + self.wave * 20
        speed = 1 + self.wave * 0.1
        reward = 20 + self.wave * 5
        self.enemies.append(Enemy(health, min(speed, 3), reward))
        
    def update(self):
        if self.game_over:
            return
            
        # Spawn nemici
        if self.wave_in_progress and self.enemies_to_spawn > 0:
            self.spawn_timer += 1
            if self.spawn_timer >= 60:  # Ogni secondo
                self.spawn_enemy()
                self.enemies_to_spawn -= 1
                self.spawn_timer = 0
                
        # Controlla fine ondata
        if self.enemies_to_spawn == 0 and len(self.enemies) == 0 and self.wave_in_progress:
            self.wave_in_progress = False
            self.money += 50  # Bonus per ondata completata
            
        # Controlla vittoria
        if self.wave >= 10 and not self.wave_in_progress and len(self.enemies) == 0:
            self.won = True
            self.game_over = True
            
        # Aggiorna nemici
        for enemy in self.enemies[:]:
            if enemy.move():  # Raggiunto la fine
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
                    
        # Aggiorna torri
        for tower in self.towers:
            tower.update()
            tower.find_target(self.enemies)
            if tower.can_shoot():
                self.projectiles.append(tower.shoot())
                
        # Aggiorna proiettili
        for projectile in self.projectiles[:]:
            if projectile.move():
                # Colpito o target morto
                if projectile.target and projectile.target.health > 0:
                    if projectile.target.take_damage(projectile.damage):
                        self.money += projectile.target.reward
                        if projectile.target in self.enemies:
                            self.enemies.remove(projectile.target)
                self.projectiles.remove(projectile)
                
    def place_tower(self, grid_x, grid_y):
        if self.selected_tower_type:
            # Controlla se posizione valida
            if (grid_x, grid_y) in PATH:
                return False
                
            for tower in self.towers:
                if tower.grid_x == grid_x and tower.grid_y == grid_y:
                    return False
                    
            # Trova costo
            cost = 0
            for btn in self.tower_buttons:
                if btn["type"] == self.selected_tower_type:
                    cost = btn["cost"]
                    break
                    
            if self.money >= cost:
                self.towers.append(Tower(grid_x, grid_y, self.selected_tower_type))
                self.money -= cost
                return True
        return False
    
    def draw(self, screen):
        screen.fill(GREEN)
        
        # Griglia
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, DARK_GREEN, rect, 1)
                
        # Percorso
        for i, (gx, gy) in enumerate(PATH):
            pygame.draw.rect(screen, BROWN, 
                           (gx * GRID_SIZE, gy * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
        # Torri
        for tower in self.towers:
            tower.draw(screen, self.selected_tower_type is not None)
            
        # Nemici
        for enemy in self.enemies:
            enemy.draw(screen)
            
        # Proiettili
        for projectile in self.projectiles:
            projectile.draw(screen)
            
        # UI Panel
        pygame.draw.rect(screen, GRAY, (800, 0, 200, SCREEN_HEIGHT))
        
        # Info
        money_text = font.render(f"Soldi: ${self.money}", True, YELLOW)
        lives_text = font.render(f"Vite: {self.lives}", True, RED)
        wave_text = font.render(f"Ondata: {self.wave}/10", True, WHITE)
        
        screen.blit(money_text, (810, 10))
        screen.blit(lives_text, (810, 40))
        screen.blit(wave_text, (810, 70))
        
        # Pulsanti torri
        for btn in self.tower_buttons:
            color = GREEN if self.money >= btn["cost"] else GRAY
            if self.selected_tower_type == btn["type"]:
                color = YELLOW
            pygame.draw.rect(screen, color, btn["rect"])
            pygame.draw.rect(screen, BLACK, btn["rect"], 2)
            
            name_text = small_font.render(btn["name"], True, BLACK)
            cost_text = small_font.render(f"${btn['cost']}", True, BLACK)
            screen.blit(name_text, (btn["rect"].x + 10, btn["rect"].y + 10))
            screen.blit(cost_text, (btn["rect"].x + 10, btn["rect"].y + 35))
            
        # Pulsante avvia ondata
        if not self.wave_in_progress and not self.game_over:
            pygame.draw.rect(screen, BLUE, self.start_wave_button)
            pygame.draw.rect(screen, BLACK, self.start_wave_button, 2)
            start_text = small_font.render("Avvia Ondata", True, WHITE)
            screen.blit(start_text, (self.start_wave_button.x + 15, 
                                    self.start_wave_button.y + 20))
        
        # Preview torre selezionata
        if self.selected_tower_type:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x < 800:
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE
                px, py = grid_to_pixel(grid_x, grid_y)
                
                # Controlla se valido
                valid = (grid_x, grid_y) not in PATH
                for tower in self.towers:
                    if tower.grid_x == grid_x and tower.grid_y == grid_y:
                        valid = False
                        
                color = GREEN if valid else RED
                pygame.draw.rect(screen, (*color, 100), 
                               (grid_x * GRID_SIZE, grid_y * GRID_SIZE, 
                                GRID_SIZE, GRID_SIZE))
                                
        # Game Over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            if self.won:
                end_text = font.render("VITTORIA!", True, YELLOW)
            else:
                end_text = font.render("GAME OVER", True, RED)
                
            restart_text = small_font.render("Premi R per ricominciare", True, WHITE)
            screen.blit(end_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))


def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                if game.game_over:
                    continue
                    
                # Click su pulsanti torri
                for btn in game.tower_buttons:
                    if btn["rect"].collidepoint(mouse_x, mouse_y):
                        if game.money >= btn["cost"]:
                            if game.selected_tower_type == btn["type"]:
                                game.selected_tower_type = None
                            else:
                                game.selected_tower_type = btn["type"]
                        break
                        
                # Click su avvia ondata
                if game.start_wave_button.collidepoint(mouse_x, mouse_y):
                    game.start_wave()
                    
                # Piazza torre
                if mouse_x < 800 and game.selected_tower_type:
                    grid_x = mouse_x // GRID_SIZE
                    grid_y = mouse_y // GRID_SIZE
                    if game.place_tower(grid_x, grid_y):
                        game.selected_tower_type = None
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game = Game()
                if event.key == pygame.K_ESCAPE:
                    game.selected_tower_type = None
                    
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()


if __name__ == "__main__":
    main()