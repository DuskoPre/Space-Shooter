#!/usr/bin/env python3.11

#  Copyright (c) 26.12.2024 [D. P.] aka duskop; after the call a day after from a Japanese IPO-agency, i'm adding my patreon ID: https://www.patreon.com/florkz_com
#  All rights reserved.

import pygame
import random
import os
from typing import List, Tuple, Dict, Any

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Load all game graphics
png_folder = "."
background = pygame.image.load(os.path.join(png_folder, "starfield.png")).convert()
player_img = pygame.image.load(os.path.join(png_folder, "spaceship.png")).convert()
enemy_img = pygame.image.load(os.path.join(png_folder, "enemy.png")).convert()
bullet_img = pygame.image.load(os.path.join(png_folder, "bullet.png")).convert()
player_mini_img = pygame.image.load(os.path.join(png_folder, 'spaceship_mini.png')).convert()

player_img = pygame.transform.scale(player_img, (50, 50))  # Resize to 50x50 pixels
enemy_img = pygame.transform.scale(enemy_img, (40, 40))    # Resize to 40x40 pixels
bullet_img = pygame.transform.scale(bullet_img, (40, 40))
player_mini_img = pygame.transform.scale(player_img, (30, 30))

# Explosion animations
def load_explosion_anim() -> Dict[str, List[pygame.Surface]]:
    #explosion_anim: Dict[str, List[pygame.Surface]] = {"lg": [], "sm": []}
    explosion_anim: Dict[str, List[pygame.Surface]] = {"lg": [], "sm": [], "player": []}
    for i in range(9):
        filename = f"explosion.png"
        img = pygame.image.load(os.path.join(png_folder, filename)).convert()
        img.set_colorkey((0, 0, 0))
        img_lg = pygame.transform.scale(img, (75, 75))
        explosion_anim["lg"].append(img_lg)
        img_sm = pygame.transform.scale(img, (32, 32))
        explosion_anim["sm"].append(img_sm)
        img_player = pygame.transform.scale(img, (100, 100)) #fixed
        explosion_anim["player"].append(img_player) #fixed
    return explosion_anim


explosion_anim = load_explosion_anim()

# Sound effects
shoot_sound = pygame.mixer.Sound(os.path.join(png_folder, "laser.wav"))
explosion_sounds: List[pygame.mixer.Sound] = [
    pygame.mixer.Sound(os.path.join(png_folder, "explosion.wav")),
    pygame.mixer.Sound(os.path.join(png_folder, "laser.wav")),
]
pygame.mixer.music.load(os.path.join(png_folder, "music.ogg"))
pygame.mixer.music.set_volume(0.4)

all_sprites: pygame.sprite.Group = pygame.sprite.Group()
enemies: pygame.sprite.Group = pygame.sprite.Group()
bullets: pygame.sprite.Group = pygame.sprite.Group()
powerups: pygame.sprite.Group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = player_img
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.fire_rate = 1.0

    def update(self) -> None:
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_SPACE] and not self.hidden:
            self.shoot()

        self.rect.x += self.speedx * self.fire_rate
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self) -> None:
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def powerup(self) -> None:
        self.power += 1
        self.fire_rate *= 0.9


class Enemy(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = enemy_img
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self) -> None:
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if (
            self.rect.top > HEIGHT + 10
            or self.rect.left < -25
            or self.rect.right > WIDTH + 20
        ):
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        self.image = bullet_img
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self) -> None:
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center: Tuple[float, float], size: str) -> None:
        super().__init__()
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


def draw_text(surf: pygame.Surface, text: str, size: int, x: float, y: float) -> None:
    font_name = pygame.font.match_font("arial")
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf: pygame.Surface, x: float, y: float, pct: float) -> None:
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(
    surf: pygame.Surface, x: float, y: float, lives: int, img: pygame.Surface
) -> None:
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen() -> None:
    screen.blit(background, background.get_rect())
    draw_text(screen, "Space Shooter", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


player = Player()
all_sprites.add(player)
for i in range(8):
    m = Enemy()
    all_sprites.add(m)
    enemies.add(m)

score = 0
pygame.mixer.music.play(loops=-1)

running = True
game_over = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            m = Enemy()
            all_sprites.add(m)
            enemies.add(m)
        score = 0

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(explosion_sounds).play()
        expl = Explosion(hit.rect.center, "lg")
        all_sprites.add(expl)
        m = Enemy()
        all_sprites.add(m)
        enemies.add(m)

    hits = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, "sm")
        all_sprites.add(expl)
        m = Enemy()
        all_sprites.add(m)
        enemies.add(m)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, "player")
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    screen.fill(BLACK)
    #screen.blit(background, background_rect)
    screen.blit(background, background.get_rect())
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    pygame.display.flip()

pygame.quit()
