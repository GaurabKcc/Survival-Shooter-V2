import pygame
from sys import exit
import math
import random
from settings import *

pygame.init()

menu_active = True
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Shooter")
clock = pygame.time.Clock()

background = pygame.transform.scale(pygame.image.load("grass.png").convert(), (WIDTH, HEIGHT))

all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

player_health = 100
game_over = False
start_ticks = pygame.time.get_ticks()
spawn_radius = 150
spawn_rate = 0.015

ENEMY_SIZE = 50

enemies_killed = 0
game_time = 0

enemy_speed_factor = 2.0

def main_menu():
    global menu_active, spawn_rate, game_over, enemy_speed_factor
    screen.fill((0, 0, 0))

    menu_image = pygame.image.load("menu.webp").convert_alpha()
    menu_image = pygame.transform.scale(menu_image, (WIDTH, HEIGHT))
    screen.blit(menu_image, (0, 0))

    font = pygame.font.Font("Exquisite Corpse.ttf", 120)
    title_text = font.render("Zombiecide Survival", True, (255, 0, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 + 100))
    
    button_width = 300
    button_height = 75
    casual_button = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2, button_width, button_height)
    hardcore_button = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 90, button_width, button_height)

    pygame.draw.rect(screen, (0, 255, 0), casual_button)
    pygame.draw.rect(screen, (255, 0, 0), hardcore_button)

    font = pygame.font.Font("Exquisite Corpse.ttf", 54)
    casual_text = font.render("Casual", True, (0, 0, 0))
    hardcore_text = font.render("Hardcore", True, (0, 0, 0))

    screen.blit(casual_text, (WIDTH // 2 - casual_text.get_width() // 2, HEIGHT // 2 + 20))
    screen.blit(hardcore_text, (WIDTH // 2 - hardcore_text.get_width() // 2, HEIGHT // 2 + 110))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if casual_button.collidepoint(event.pos):
                spawn_rate = 0.030
                enemy_speed_factor = 1.5
                menu_active = False
                start_game()
            if hardcore_button.collidepoint(event.pos):
                spawn_rate = 0.050
                enemy_speed_factor = 2
                menu_active = False
                start_game()


def start_game():
    global game_over, start_ticks, player, enemies_killed, menu_active, game_time
    all_sprites_group.empty()
    enemy_group.empty()

    game_time = 0
    enemies_killed = 0  # Reset score when starting a new game
    game_over = False

    start_ticks = pygame.time.get_ticks()  # Track the start time

    player = Player()
    all_sprites_group.add(player)

    for _ in range(5):
        spawn_enemy()

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if keys[pygame.K_m]:
            menu_active = True
            return

        if not game_over and random.random() < spawn_rate:
            spawn_enemy()

        if not game_over:
            player_hits = pygame.sprite.spritecollide(player, enemy_group, False)
            for enemy in player_hits:
                if player.take_damage(1):
                    game_over = True
                    end_ticks = pygame.time.get_ticks()
                    game_time = (end_ticks - start_ticks) // 1000

        if game_over:
            font = pygame.font.Font("Exquisite Corpse.ttf", 74)
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

            font = pygame.font.Font("Exquisite Corpse.ttf", 36)
            time_text = font.render(f"Time played: {game_time} seconds", True, (255, 255, 255))
            screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2))

            kill_text = font.render(f"Enemies killed: {enemies_killed}", True, (255, 255, 255))
            screen.blit(kill_text, (WIDTH // 2 - kill_text.get_width() // 2, HEIGHT // 2 + 50))

            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 120))

            menu_prompt = font.render("Press M to Return to Menu", True, (255, 255, 255))
            screen.blit(menu_prompt, (WIDTH // 2 - menu_prompt.get_width() // 2, HEIGHT // 2 + 180))

            pygame.display.update()

            if keys[pygame.K_r]:
                player.health = player_health
                player.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
                game_over = False
                start_ticks = pygame.time.get_ticks()  # Reset start time
                all_sprites_group.empty()
                enemy_group.empty()
                player = Player()
                all_sprites_group.add(player)
                for _ in range(5):
                    spawn_enemy()

                # Reset the score when restarting the game
                enemies_killed = 0

            continue

        screen.blit(background, (0, 0))
        player.draw_health_bar(screen)
        all_sprites_group.draw(screen)
        all_sprites_group.update()

        # Only update game time if the game is not over
        if not game_over:
            game_time = (pygame.time.get_ticks() - start_ticks) // 1000

        font = pygame.font.Font("Exquisite Corpse.ttf", 36)
        score_text = font.render(f"Score: {enemies_killed}", True, (255, 0, 0))

        score_rect = score_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(score_text, score_rect)

        pygame.display.update()
        clock.tick(FPS)


def spawn_enemy():
    global enemies_killed
    valid_position = False
    while not valid_position:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        distance_to_player = math.sqrt((x - player.rect.centerx) ** 2 + (y - player.rect.centery) ** 2)
        if distance_to_player > spawn_radius:
            valid_position = True
    new_enemy = Enemy((x, y))
    enemy_group.add(new_enemy)
    all_sprites_group.add(new_enemy)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("player/0.png").convert_alpha(), 0, PLAYER_SIZE)
        self.base_player_image = self.image
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)
        self.health = player_health
        self.angle = 0

    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coords[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)

    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed

        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self): 
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.pos.x = max(0, min(self.pos.x, WIDTH - self.rect.width))
        self.pos.y = max(0, min(self.pos.y, HEIGHT - self.rect.height))
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        if not game_over:
            self.user_input()
            self.move()
            self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True
        return False

    def increase_health(self, amount):
        self.health += amount
        self.health = min(self.health, 100)

    def draw_health_bar(self, surface):
        health_bar_width = 200
        health_bar_height = 20
        health_ratio = self.health / 100
        pygame.draw.rect(surface, (255, 0, 0), (10, 10, health_bar_width, health_bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (10, 10, health_bar_width * health_ratio, health_bar_height))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("bullet/1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):  
        self.x += self.x_vel
        self.y += self.y_vel
        self.rect.center = (self.x, self.y)
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def update(self):
        self.bullet_movement()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.image.load("2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (ENEMY_SIZE, ENEMY_SIZE))
        self.rect = self.image.get_rect(center=position)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = random.uniform(1, 2) * enemy_speed_factor

    def update(self):
        vector_to_player = pygame.math.Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y)
        distance_to_player = vector_to_player.length()
        vector_to_player.normalize_ip()
        self.pos += vector_to_player * self.speed
        self.rect.center = self.pos
        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.kill()
            global enemies_killed
            enemies_killed += 1


while menu_active:
    main_menu()
pygame.quit()
