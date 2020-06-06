from __future__ import division
import pygame
import pygame_menu
import random
import time
import sqlite3
from os import path

############ 전역변수 선언 ############
WIDTH = 550
HEIGHT = 700
FPS = 120

shieldWIDHT = 120
shieldHEIGHT = 10
enemy_shieldWIDTH = 40
enemy_shieldHEIGHT = 10

font_name = pygame.font.match_font('arial')
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (124, 252, 0)
BLUE = (24, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

start_img = pygame.image.load("start_img.png")
start_img = pygame.transform.scale(start_img, (WIDTH, HEIGHT))

manual_img = pygame.image.load("manual_img.png")
manual_img = pygame.transform.scale(manual_img, (WIDTH, HEIGHT))


######### 아이템 이미지
items_set = {}
items_set['item1'] = pygame.image.load("item_1.png")  ######크기조절 해야함!!
items_set['item2'] = pygame.image.load("item_2.png")
items_set['item3'] = pygame.image.load("item_3.png")

####### 플레이어 1, 2
player1_img = pygame.image.load("player1.png")
player2_img = pygame.image.load("player2.png")

min_player1 = pygame.image.load("min_player1.png")
min_player1 = pygame.transform.scale(min_player1, (40, 40))

min_player2 = pygame.image.load("min_player2.png")
min_player2 = pygame.transform.scale(min_player2, (40, 40))

background = pygame.image.load("background.png")
background_img = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background_img.get_rect()

shot = pygame.image.load("shot.png")
shot = pygame.transform.scale(shot, (24, 24))

enemy_shot = pygame.image.load("enemy_shot.png")
enemy_shot = pygame.transform.scale(enemy_shot, (15, 15))

enemy_img = pygame.image.load("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (100, 80))

score = 0

############ 클래스 선언 ############
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image = pygame.transform.scale(self.image, (60, 120))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedx = 0
        self.speedy = 0
        self.shot_delay = 100
        self.last_shot = pygame.time.get_ticks()
        self.lives = 4
        self.HP = 100

    def update(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shot(self): ############레벨 1,2에서는 아래쪽 총알이 나오지 않도록 수정 필요
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            bullet_top = Bullet(self.rect.centerx, self.rect.top, 1) # 아래쪽 총알
            all_sprites.add(bullet_top)
            bullets.add(bullet_top)

            bullet_bottom = Bullet(self.rect.centerx, self.rect.bottom, 2) # 위쪽 총알
            all_sprites.add(bullet_bottom)
            bullets.add(bullet_bottom)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = shot
        self.rect = self.image.get_rect()
        self.rect.centerx = x

        if type == 1: # 위쪽 총알
            self.rect.bottom = y
            self.speedy = -7
        if type == 2: # 아래쪽 총알
            self.rect.top = y
            self.speedy = 7


    def update(self):
        self.rect.y += self.speedy
        if self.rect.y < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        if level == 1:
            self.bullet_speed = 0.7
            self.rect.y = random.randrange(-700, -300)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.speedx = random.randrange(-3, 3)
            self.speedy = random.randrange(1, 4)
            self.shot_delay = random.randrange(1000, 2000)

        if level == 2: #x속도, y속도, 샷 딜레이 조정
            self.bullet_speed = 1
            self.rect.y = random.randrange(-700, -300)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.speedx = random.randrange(-3, 3)
            self.speedy = random.randrange(2, 5)
            self.shot_delay = random.randrange(1000, 2000)

        if level == 3:
            self.bullet_speed = 1
            self.shot_delay = random.randrange(1000, 2000)
            self.speedx = random.randrange(-3, 3)
            if random.random() > 0.5:
                self.rect.y = random.randrange(-700, -300)
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(2, 6)
            else:
                self.rect.y = random.randrange(HEIGHT + 300,
                                               HEIGHT + 700)  # 밑에서도 적들이 나오게 하려면 플레이어 총알을 아래로도 발사시킬 수 있어야 함
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(-5, -1)

        if level == 4: #보스전
            self.bullet_speed = 1.3
            self.shot_delay = random.randrange(1000, 2000)
            self.speedx = random.randrange(-3, 3)
            if random.random() > 0.5:
                self.rect.y = random.randrange(-700, -300)
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(2, 7)
            else:
                self.rect.y = random.randrange(HEIGHT + 300,
                                               HEIGHT + 700)
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(-5, -1)

        self.last_shot = pygame.time.get_ticks()
        self.HP = 100

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # 적이 보이는 범위를 벗어나면 삭제하고 새로운 적을 만들어줌
        # 아래쪽으로 내려가는 적 삭제
        if (self.speedy > 0) and ((self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20)):
            self.kill()
            make_new_enemy(level)
        # 위로 올라가는 적 삭제
        if (self.speedy < 0) and ((self.rect.bottom < 0) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20)):
            self.kill()
            make_new_enemy(level)

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay and random.random() > 0.7: #샷 딜레이 시간 후, 일정 확률로 총알 발사
            self.last_shot = now

            ####################################### 총알 각도 수정 필요
            if level == 1: # 레벨 1에서 총알 1개씩 발사
                enemy_bullet1 = Enemy_Bullet(self.speedx, self.speedy, self.rect.centerx, self.rect.bottom, self.bullet_speed)
                all_sprites.add(enemy_bullet1)
                enemy_bullets.add(enemy_bullet1)

            if level == 2: # 레벨 2에서 총알 2개씩 발사
                enemy_bullet1 = Enemy_Bullet(self.speedx, self.speedy, self.rect.centerx, self.rect.bottom,
                                             self.bullet_speed)
                all_sprites.add(enemy_bullet1)
                enemy_bullets.add(enemy_bullet1)

                enemy_bullet2 = Enemy_Bullet(0, self.speedy, self.rect.centerx, self.rect.bottom, self.bullet_speed)
                all_sprites.add(enemy_bullet2)
                enemy_bullets.add(enemy_bullet2)

            if level >= 3: # 레벨 3, 보스전에서 총알 3개씩 발사
                enemy_bullet1 = Enemy_Bullet(self.speedx, self.speedy, self.rect.centerx, self.rect.bottom, self.bullet_speed)
                all_sprites.add(enemy_bullet1)
                enemy_bullets.add(enemy_bullet1)

                enemy_bullet2 = Enemy_Bullet(0, self.speedy, self.rect.centerx, self.rect.bottom, self.bullet_speed)
                all_sprites.add(enemy_bullet2)
                enemy_bullets.add(enemy_bullet2)

                enemy_bullet3 = Enemy_Bullet(-self.speedx, self.speedy, self.rect.centerx, self.rect.bottom, self.bullet_speed)
                all_sprites.add(enemy_bullet3)
                enemy_bullets.add(enemy_bullet3)



class Enemy_Bullet(pygame.sprite.Sprite):
    def __init__(self, speedx, speedy, x, y, bullet_speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_shot
        self.rect = self.image.get_rect()
        #self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = 0#speedx
        if speedy > 0:
            self.rect.bottom = y
            self.speedy = speedy + bullet_speed
        else:
            self.rect.bottom = y - 20
            self.speedy = speedy - bullet_speed

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.y < 0:
            self.kill()
        if self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['item1', 'item2', 'item3'])
        self.image = items_set[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


############ 함수 선언 ############

def make_new_enemy(level): #새로운 적을 만드는 함수
    enemy_element = Enemy(level)
    all_sprites.add(enemy_element)
    enemys.add(enemy_element)

def draw_HP(surf, x, y, HP, color):
    HP = max(HP, 0)
    fill = (HP / 100) * shieldWIDHT
    outline_rect = pygame.Rect(x, y, shieldWIDHT, shieldHEIGHT)
    fill_rect = pygame.Rect(x, y, fill, shieldHEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, BLACK, outline_rect, 2)

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_lives(surf, x, lives, image):
    for i in range(lives):
        img_rect = image.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = 35
        surf.blit(image, img_rect)

def main_menu():
    global screen

    screen.blit(start_img, (0, 0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                return 2
                #manual()
                #break
            elif ev.key == pygame.K_h:
                return 1
                #manual()
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()

def manual():
    global screen
    screen.blit(manual_img, (0, 0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                return 1
                #main_menu()

                #break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()


############ 게임 메인 루프 ############
running = True
menu = True
game = False
now = 0
start = 0

level = 2 # 레벨 어떻게 바꿀 건지 수정해야 함

while running:
    if menu:
        while (1): #수정 필요
            if main_menu() == 1:
                if manual() == 1:
                    pass
            elif main_menu() == 2:
                break

        game = True
        menu = False
        start = pygame.time.get_ticks()

        all_sprites = pygame.sprite.Group()
        player2 = Player(WIDTH / 2 - 80, HEIGHT, player1_img)
        player = Player(WIDTH / 2 + 80, HEIGHT, player2_img)
        all_sprites.add(player)
        all_sprites.add(player2)
        enemys = pygame.sprite.Group()
        enemyHPs = pygame.sprite.Group()
        for i in range(10):
            make_new_enemy(level)

        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        items = pygame.sprite.Group()

    clock.tick(FPS)
    now = pygame.time.get_ticks()

    if game:
        # while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC키 눌리면
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN:  # key down일때
                if event.key == pygame.K_SPACE:
                    player.shot()
                if event.key == pygame.K_LEFT:
                    player.speedx = -5
                if event.key == pygame.K_RIGHT:
                    player.speedx = 5
                if event.key == pygame.K_UP:
                    player.speedy = -5
                if event.key == pygame.K_DOWN:
                    player.speedy = +5

                if event.key == pygame.K_TAB:
                    player2.shot()
                if event.key == pygame.K_a:
                    player2.speedx = -5
                if event.key == pygame.K_d:
                    player2.speedx = 5
                if event.key == pygame.K_w:
                    player2.speedy = -5
                if event.key == pygame.K_s:
                    player2.speedy = +5

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    pass
                if event.key == pygame.K_LEFT:
                    player.speedx = 0
                if event.key == pygame.K_RIGHT:
                    player.speedx = 0
                if event.key == pygame.K_UP:
                    player.speedy = 0
                if event.key == pygame.K_DOWN:
                    player.speedy = 0

                if event.key == pygame.K_SPACE:
                    pass
                if event.key == pygame.K_a:
                    player2.speedx = 0
                if event.key == pygame.K_d:
                    player2.speedx = 0
                if event.key == pygame.K_w:
                    player2.speedy = 0
                if event.key == pygame.K_s:
                    player2.speedy = 0

        # 업데이트
        all_sprites.update()

        hits = pygame.sprite.groupcollide(enemys, bullets, True, True)
        for hit in hits:
            make_new_enemy(level)
            score += random.randrange(10, 50)
            if random.random() > 0.7:
                item = Item(hit.rect.center)
                all_sprites.add(item)
                items.add(item)

        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            player.HP -= 20
            if player.HP <= 0 and player.lives > 0:
                player.HP = 100
                player.lives -= 1
            elif player.HP <= 0 and player.lives == 0:
                player.HP = 0
                player.lives = 0
        hits = pygame.sprite.spritecollide(player2, enemy_bullets, True)
        for hit in hits:
            player2.HP -= 20
            if player2.HP <= 0 and player2.lives > 0:
                player2.HP = 100
                player2.lives -= 1
            elif player2.HP <= 0 and player2.lives == 0:
                player2.HP = 0
                player2.lives = 0

        hits = pygame.sprite.spritecollide(player, enemys, True)
        for hit in hits:
            player.HP -= 50
            if player.HP <= 0 and player.lives > 0:
                player.HP = 100
                player.lives -= 1
            elif player.HP <= 0 and player.lives == 0:
                player.HP = 0
                player.lives = 0
            make_new_enemy(level)
        hits = pygame.sprite.spritecollide(player2, enemys, True)
        for hit in hits:
            player2.HP -= 50
            player2.HP -= 20
            if player2.HP <= 0 and player2.lives > 0:
                player2.HP = 100
                player2.lives -= 1
            elif player2.HP <= 0 and player2.lives == 0:
                player2.HP = 0
                player2.lives = 0
            make_new_enemy(level)

        hits = pygame.sprite.spritecollide(player, items, True)
        for hit in hits:
            if hit.type == 'item1':
                player.HP += 40
                if player.HP >= 100:
                    player.HP = 100
            if hit.type == 'item2':
                if player.lives == 4:
                    player.HP = 100
                else:
                    player.lives += 1
        hits = pygame.sprite.spritecollide(player2, items, True)
        for hit in hits:
            if hit.type == 'item1':
                player2.HP += 40
                if player2.HP >= 100:
                    player2.HP = 100
            if hit.type == 'item2':
                if player2.lives == 4:
                    player2.HP = 100
                else:
                    player2.lives += 1

        if (player.lives == 0 and player.HP == 0) or \
                (player2.lives <= 0 and player2.HP == 0):
            game = False
            score = 0

    if game == False: #수정 필요
        menu = True
        game = False

    screen.blit(background_img, background_rect)

    all_sprites.draw(screen)

    draw_text(screen, "SCORE: ", 20, WIDTH / 2 - 30, 10)
    draw_text(screen, str(score), 20, WIDTH / 2 + 30, 10)
    draw_HP(screen, 15, 15, player2.HP, BLUE)
    draw_HP(screen, WIDTH - 135, 15, player.HP, RED)

    draw_lives(screen, 10, player2.lives, min_player1)
    draw_lives(screen, WIDTH - 145, player.lives, min_player2)

    pygame.display.flip()

pygame.quit()

