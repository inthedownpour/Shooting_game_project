from __future__ import division
import pygame
import random
import time
import sqlite3
from os import path

############ 전역변수 선언 ############

WIDTH = 1000
HEIGHT = 700
FPS = 1400

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
pygame.display.set_caption("Shooting Game")
clock = pygame.time.Clock()

start_img = pygame.image.load("start_img.png")
start_img = pygame.transform.scale(start_img, (WIDTH, HEIGHT))

manual_img = pygame.image.load("manual_img.png")
manual_img = pygame.transform.scale(manual_img, (WIDTH, HEIGHT))

choose_img = pygame.image.load("choose_img.png")
choose_img = pygame.transform.scale(choose_img, (WIDTH, HEIGHT))

ranking_img = pygame.image.load("ranking_img.png")
ranking_img = pygame.transform.scale(ranking_img, (WIDTH, HEIGHT))

gameover_img = pygame.image.load("gameover_img.png")
gameover_img = pygame.transform.scale(gameover_img, (WIDTH, HEIGHT))

nextlevel_img = pygame.image.load("nextlevel_img.png")
nextlevel_img = pygame.transform.scale(nextlevel_img, (WIDTH, HEIGHT))

saveranking_img = pygame.image.load("saveranking_img.png")
saveranking_img = pygame.transform.scale(saveranking_img, (WIDTH, HEIGHT))

main_text = pygame.image.load("main_text.png")

######### 버튼 이미지
b_end = pygame.image.load("b_end.png")
b_end = pygame.transform.scale(b_end, (140, 50))
b_main = pygame.image.load("b_main.png")
b_main = pygame.transform.scale(b_main, (140, 50))
b_manual = pygame.image.load("b_manual.png")
b_manual = pygame.transform.scale(b_manual, (140, 50))
b_ranking = pygame.image.load("b_ranking.png")
b_ranking = pygame.transform.scale(b_ranking, (140, 50))
b_start = pygame.image.load("b_start.png")
b_start = pygame.transform.scale(b_start, (140, 50))
b_solo = pygame.image.load("b_solo.png")
b_solo = pygame.transform.scale(b_solo, (140, 50))
b_team = pygame.image.load("b_team.png")
b_team= pygame.transform.scale(b_team, (140, 50))

######### 아이템 이미지
items_set = {}
items_set['item1'] = pygame.image.load("item_1.png")
items_set['item2'] = pygame.image.load("item_2.png")
items_set['item3'] = pygame.image.load("item_3.png")

####### 플레이어 1, 2
player1_img = pygame.image.load("player1.png")
player2_img = pygame.image.load("player2.png")

min_player1 = pygame.image.load("min_player1.png")
min_player1 = pygame.transform.scale(min_player1, (20, 20))

min_player2 = pygame.image.load("min_player2.png")
min_player2 = pygame.transform.scale(min_player2, (20, 20))

background = pygame.image.load("background.png")
background_img = pygame.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background_img.get_rect()

shot = pygame.image.load("shot.png")
shot = pygame.transform.scale(shot, (45, 50))
shot2 = pygame.image.load("shot2.png")
shot2 = pygame.transform.scale(shot2, (20, 20))

enemy_shot = pygame.image.load("enemy_shot.png")
enemy_shot = pygame.transform.scale(enemy_shot, (10, 10))

enemy_img = pygame.image.load("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (100, 80))


############ 데이터베이스 ############
con, cur = None, None
data1, data2, data3 = "","",""
sql = ""
con = sqlite3.connect("RANKING_CHART")
cur = con.cursor()
#cur.execute("CREATE TABLE scoreTable (id char(4), score INT)")

def DB_insert(id, score):
    DB_id = id
    DB_score = score
    sql = "INSERT INTO scoreTable VALUES('" + DB_id + "','" + DB_score + "')"
    cur.execute(sql)
    con.commit()

def DB_check():

    cur.execute("SELECT id, score FROM scoreTable ORDER BY CAST (score AS INTEGER) DESC")
    con.commit()

    draw_text(screen, "Player ID", 20, WIDTH / 2 - 110, 200, BLACK)
    draw_text(screen, "SCORE", 20, WIDTH / 2 + 140, 200, BLACK)


    for i in range(10):
        row = cur.fetchone()
        if row == None:
            break
        DB_id = row[0]
        DB_score = row[1]
        draw_text(screen, str(i+1), 20, WIDTH / 2 -  250, 250 + i * 30, BLACK)
        draw_text(screen, str(DB_id), 20, WIDTH / 2 -  110, 250 + i * 30, BLACK)
        draw_text(screen, str(DB_score), 20, WIDTH / 2 +  140, 250 + i * 30, BLACK)

        #print("%5s %15s" % (data1, data2))
    #con.close() #종료할 때 넣어야 함!!!!!!!!!!!!!!!!!!!!!!!!!!!



############ 클래스 선언 ############
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image = pygame.transform.scale(self.image, (60, 80))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedx = 0
        self.speedy = 0
        self.top_shot_delay = 150
        self.bottom_shot_delay = 300
        self.last_shot = pygame.time.get_ticks()
        self.lives = 4
        self.HP = 100
        self.power = 1
        self.power_time = pygame.time.get_ticks()

        self.item1 = 0 #가지고 있는 아이템 개수 저장
        self.item2 = 0
        self.item3 = 0
        if self.item1 >= 5: self.item1 = 5 #아이템 하나당 최대 5개까지 보관 가능
        if self.item2 >= 5: self.item2 = 5
        if self.item3 >= 5: self.item3 = 5

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

        now = pygame.time.get_ticks()
        if self.power >= 2 and now - self.power_time > 10000: #10초 동안 아이템2 효과 지속
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shot_top(self): ############레벨 1,2에서는 아래쪽 총알이 나오지 않도록 수정 필요 # 위쪽 총알 발사
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.top_shot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet_top = Bullet(self.rect.centerx, self.rect.top, 1)
                all_sprites.add(bullet_top)
                bullets.add(bullet_top)
            if self.power == 2:
                bullet_top1 = Bullet(self.rect.centerx - 5, self.rect.top, 1)
                bullet_top2 = Bullet(self.rect.centerx + 5, self.rect.top, 1)
                all_sprites.add(bullet_top1)
                bullets.add(bullet_top1)
                all_sprites.add(bullet_top2)
                bullets.add(bullet_top2)
            if self.power == 3:
                bullet_top1 = Bullet(self.rect.centerx - 10, self.rect.top, 1)
                bullet_top2 = Bullet(self.rect.centerx, self.rect.top, 1)
                bullet_top3 = Bullet(self.rect.centerx + 10, self.rect.top, 1)
                all_sprites.add(bullet_top1)
                bullets.add(bullet_top1)
                all_sprites.add(bullet_top2)
                bullets.add(bullet_top2)
                all_sprites.add(bullet_top3)
                bullets.add(bullet_top3)

    def shot_bottom(self): # 아래쪽 총알 발사
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.bottom_shot_delay:
            self.last_shot = now
            if self.power <= 2:
                bullet_bottom = Bullet(self.rect.centerx, self.rect.bottom, 2)
                all_sprites.add(bullet_bottom)
                bullets.add(bullet_bottom)
            if self.power == 3:
                bullet_bottom1 = Bullet(self.rect.centerx - 6, self.rect.bottom, 2)
                bullet_bottom2 = Bullet(self.rect.centerx + 6, self.rect.bottom, 2)
                all_sprites.add(bullet_bottom1)
                bullets.add(bullet_bottom1)
                all_sprites.add(bullet_bottom2)
                bullets.add(bullet_bottom2)

    def item(self, inventory_key):
        if inventory_key == 1 and self.item1 != 0:
            self.item1 -= 1
            if player.HP >= 50:
                player.HP = 100
            else: player.HP += 50
        if inventory_key == 2 and self.item2 != 0:
            self.item2 -= 1
            if self.power < 3:
                self.power += 1

        # 세 번째 아이템 구현해야 함

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
            self.image = shot2
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.top = y
            self.speedy = 4

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
            self.bullet_speed = 2
            self.rect.y = random.randrange(-700, -300)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.speedx = random.randrange(-2, 2)
            self.speedy = random.randrange(3, 5)
            self.shot_delay = random.randrange(1000, 2000)
        if level == 2: #x속도, y속도, 샷 딜레이 조정
            self.bullet_speed = 2.5
            self.rect.y = random.randrange(-700, -300)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.speedx = random.randrange(-2, 2)
            self.speedy = random.randrange(4, 6)
            self.shot_delay = random.randrange(1000, 2000)
        if level == 3:
            self.bullet_speed = 3
            self.shot_delay = random.randrange(1000, 2000)
            self.speedx = random.randrange(-2, 2)
            if random.random() > 0.5:
                self.rect.y = random.randrange(-700, -300)
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(5, 7)
            else:
                self.rect.y = random.randrange(HEIGHT + 300,
                                               HEIGHT + 700)  # 밑에서도 적들이 나오게 하려면 플레이어 총알을 아래로도 발사시킬 수 있어야 함
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(-5, -4)
        if level == 4: #보스전
            self.bullet_speed = 1.3
            self.shot_delay = random.randrange(1000, 2000)
            self.speedx = random.randrange(-2, 2)
            if random.random() > 0.5:
                self.rect.y = random.randrange(-700, -300)
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.speedy = random.randrange(5, 7)
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

def draw_inventory(p1_inventory_key, p2_inventory_key):
    inventoryWIDTH = shieldWIDHT / 3
    for i in range (0, 3):
        if i == p2_inventory_key - 1: #지정된 키의 색과 두께를 다르게 함
            color = RED
            size = 4
        else:
            color = BLACK
            size = 2
        outline_rect2 = pygame.Rect(15 + inventoryWIDTH * i, HEIGHT - 55, inventoryWIDTH, inventoryWIDTH)  # 인벤토리 3칸 그려줌
        pygame.draw.rect(screen, color, outline_rect2, size)

    for i in range (0, 3):
        if i == p1_inventory_key - 4:
            color = RED
            size = 4
        else:
            color = BLACK
            size = 2
        outline_rect2 = pygame.Rect(865 + inventoryWIDTH * i, HEIGHT - 55, inventoryWIDTH, inventoryWIDTH)  # 인벤토리 3칸 그려줌
        pygame.draw.rect(screen, color, outline_rect2, size)

def draw_text(surf, text, size, x, y, color):
    if color == BLACK:
        font = pygame.font.Font(font_name, size)

    if color == RED:
        font = pygame.font.Font(font_name, size + 2)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_lives(surf, x, lives, image):
    for i in range(lives):
        img_rect = image.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = 35
        surf.blit(image, img_rect)

def draw_item(item1, item2, item3, x, y):
    if item1 > 0:
        item1_img = items_set['item1']
        item1_img_rect = item1_img.get_rect()
        item1_img_rect.x = x + 5
        item1_img_rect.y = y + 5
        screen.blit(item1_img, item1_img_rect)

    if item2 > 0:
        item2_img = items_set['item2']
        item2_img_rect = item2_img.get_rect()
        item2_img_rect.x = x + 50
        item2_img_rect.y = y + 6
        screen.blit(item2_img, item2_img_rect)

    if item3 > 0:
        item3_img = items_set['item3']
        item3_img_rect = item3_img.get_rect()
        item3_img_rect.x = x + 83
        item3_img_rect.y = y + 5
        screen.blit(item3_img, item3_img_rect)

def draw_button(image, x, y):
    image_rect = image.get_rect()
    if x == 0: # x값이 0이면 중앙에 출력
        screen.blit(image, (WIDTH / 2 - image_rect.width /2, y))
    else: # x값이 0이 아니면 x, y에 출력
        screen.blit(image, (x, y))

def collide(mouseX, mouseY, rect, y): #버튼 클릭
    rectX = WIDTH / 2 - rect.width / 2

    if (mouseX >= rectX and mouseX <= rectX + rect.width and mouseY >= y and mouseY <= y + rect.height):
        return True
    else:
        return False

def main_menu():
    global screen

    screen.blit(background_img, (0, 0))
    draw_button(main_text, 0, 100)
    draw_button(b_start, 0, 300)
    draw_button(b_manual, 0, 380)
    draw_button(b_ranking, 0, 460)
    draw_button(b_end, 0, 540)

    #DB_insert(str(100), str(400))

    b_start_rect = b_start.get_rect()
    b_manual_rect = b_manual.get_rect()
    b_ranking_rect = b_ranking.get_rect()
    b_end_rect = b_end.get_rect()

    pygame.display.update()

    while True:
        if pygame.mouse.get_pressed()[0]: #마우스 왼쪽 버튼 클릭
            mouse_pos = pygame.mouse.get_pos()
            if collide(mouse_pos[0], mouse_pos[1], b_start_rect, 300) == True: # b_end
                return 2
            elif collide(mouse_pos[0], mouse_pos[1], b_manual_rect, 380) == True: # b_end
                return 3
            elif collide(mouse_pos[0], mouse_pos[1], b_ranking_rect, 460) == True: # b_end
                return 4
            elif collide(mouse_pos[0], mouse_pos[1], b_end_rect, 540) == True: # b_end
                quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def manual():
    global screen

    screen.blit(manual_img, (0, 0))
    draw_button(b_main, 0, 600)
    b_main_rect = b_main.get_rect()

    pygame.display.update()

    while True:
        if pygame.mouse.get_pressed()[0]: #마우스 왼쪽 버튼 클릭
            mouse_pos = pygame.mouse.get_pos()
            if collide(mouse_pos[0], mouse_pos[1], b_main_rect, 600) == True:
                return 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def game_choose(): #게임 시작 누른후 게임 선택
    global screen

    screen.blit(choose_img, (0, 0))
    draw_button(b_solo, 0, 200)
    draw_button(b_team, 0, 380)
    draw_button(b_main, 0, 600)
    b_solo_rect = b_solo.get_rect()
    b_team_rect = b_team.get_rect()
    b_main_rect = b_main.get_rect()

    pygame.display.update()

    while True:
        if pygame.mouse.get_pressed()[0]: #마우스 왼쪽 버튼 클릭
            mouse_pos = pygame.mouse.get_pos()
            if collide(mouse_pos[0], mouse_pos[1], b_solo_rect, 200) == True:
                return 5 #개인모드
            elif collide(mouse_pos[0], mouse_pos[1], b_team_rect, 380) == True:
                return 6 #협동모드
            elif collide(mouse_pos[0], mouse_pos[1], b_main_rect, 600) == True:
                return 1 #manual 함수가 1반환 즉 메인메뉴 함수에서 메인메뉴 처음으로? 돌아감

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def ranking():
    global screen
    screen.blit(ranking_img, (0, 0))
    draw_button(b_main, 0, 600)
    b_main_rect = b_main.get_rect()

    DB_check()

    pygame.display.update()


    while True:
        if pygame.mouse.get_pressed()[0]: #마우스 왼쪽 버튼 클릭
            mouse_pos = pygame.mouse.get_pos()
            if collide(mouse_pos[0], mouse_pos[1], b_main_rect, 600) == True:
                return 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()



def DB_inputdata():
    global screen
    screen.blit(saveranking_img, (0, 0))

    pygame.display.update()

    id = ''
    input_box = pygame.Rect(WIDTH/2 + 50, 400, 60, 40)
    font = pygame.font.Font(font_name, 30)
    color = BLACK
    active = False
    while True:
        if pygame.mouse.get_pressed()[0]:  # 마우스 왼쪽 버튼 클릭
            mouse_pos = pygame.mouse.get_pos()
            if collide(mouse_pos[0], mouse_pos[1], b_main_rect, 600) == True:
                return 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active ## True????
                    color = RED # 칸 클릭하면 색깔 바뀜
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return id
                    elif event.key == pygame.K_BACKSPACE:
                        id = id[:-1]
                    else:
                        id += event.unicode


        screen.blit(ranking_img, (0, 0))
        draw_text(screen, "Click on the SQUARE and enter your ID", 25, WIDTH / 2, 170, BLACK)
        draw_text(screen, "press ENTER to SAVE", 25, WIDTH / 2, 220, BLACK)
        draw_text(screen, "YOUR SCORE: ", 30, WIDTH / 2 - 100, 330, BLACK)
        draw_text(screen, str(score), 30, WIDTH / 2 + 100, 330, BLACK)
        draw_text(screen, "ENTER YOUR ID: ", 30, WIDTH / 2 - 100, 400, BLACK)
        #draw_text(screen, id, 30, WIDTH / 2 + 100, 300, BLACK)  # print(a)
        draw_button(b_main, 0, 600)
        txt_surface = font.render(id, True, BLACK)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        # Blit the text.
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5)) # 글자 쓰기

        pygame.draw.rect(screen, color, input_box, 2) # 사각형 그리기
        b_main_rect = b_main.get_rect()

        pygame.display.flip()
        clock.tick(30)

def saveranking(score):
    global screen
    screen.blit(saveranking_img, (0, 0))
    draw_button(b_main, 0, 600)
    b_main_rect = b_main.get_rect()
    word = DB_inputdata()
    #draw_text(screen, word, 30, WIDTH/2 + 50, 400, BLACK)
    draw_text(screen, "SAVED", 30, WIDTH/2, 500, BLACK)

    #DB_insert(word, str(score))
    DB_insert(word, str(score))

    pygame.display.update()

    while True:
        if pygame.mouse.get_pressed()[0]:  # 마우스 왼쪽 버튼 클릭
            mouse_pos = pygame.mouse.get_pos()
            if collide(mouse_pos[0], mouse_pos[1], b_main_rect, 600) == True:
                return 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


def gameover(time):
    global screen

    screen.blit(gameover_img, (0, 0))
    pygame.display.update()

    while True:
        now = pygame.time.get_ticks()
        if time + 2000 <= now:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def nextlevel(time):
    global screen

    screen.blit(nextlevel_img, (0, 0))
    pygame.display.update()

    while True:
        now = pygame.time.get_ticks()
        if time + 2000 <= now:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()



############ 게임 메인 루프 ############
running = True
menu = True
game = False
reset = False
#now = 0
start = 0
score = 0

level = 1
level_time = 30000

p1_inventory_key = 4
p2_inventory_key = 1

while running:
    if menu:
        while (1):
            if main_menu() == 2:  # 게임 시작 선택
                break
            elif main_menu() == 3:  # 게임 방법 선택
                if manual() == 1:  # 여기서 메뉴얼 함수 실행함
                    pass  # 마우스로 메인메뉴 버튼 눌렀을때 1반환함, 밑에문장 계속 실행하고 와일문 반복 즉 다시 메인메뉴 함수 실행
            elif main_menu() == 4:  # 랭킹 확인 선택
                if ranking() == 1:
                    pass
        game = True
        menu = False
        reset = True

        start_time = pygame.time.get_ticks() #게임 시작 시간

        all_sprites = pygame.sprite.Group()
        player2 = Player(WIDTH / 2 - 80, HEIGHT, player2_img)
        player = Player(WIDTH / 2 + 80, HEIGHT, player1_img)
        all_sprites.add(player)
        all_sprites.add(player2)

        enemys = pygame.sprite.Group()
        #enemyHPs = pygame.sprite.Group()
        for i in range(10):
            make_new_enemy(level)

        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        items = pygame.sprite.Group()

    clock.tick(FPS)

    if game:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC키 눌리면
                    pygame.quit()
                    quit()
            if event.type == pygame.KEYDOWN:  # key down일때
                if event.key == pygame.K_o:
                    player.shot_top()
                    score += 1
                if event.key == pygame.K_p:
                    player.shot_bottom()
                    score += 1
                if event.key == pygame.K_LEFT:
                    player.speedx = -5
                if event.key == pygame.K_RIGHT:
                    player.speedx = 5
                if event.key == pygame.K_UP:
                    player.speedy = -5
                if event.key == pygame.K_DOWN:
                    player.speedy = +5

                if event.key == pygame.K_r:
                    player2.shot_top()
                    score += 1
                if event.key == pygame.K_t:
                    player2.shot_bottom()
                    score += 1
                if event.key == pygame.K_a:
                    player2.speedx = -5
                if event.key == pygame.K_d:
                    player2.speedx = 5
                if event.key == pygame.K_w:
                    player2.speedy = -5
                if event.key == pygame.K_s:
                    player2.speedy = +5

                if event.key == pygame.K_k: # SPACE 키로 아이템 인벤토리 조작
                    p1_inventory_key += 1
                    if p1_inventory_key > 6:
                        p1_inventory_key = 4
                if event.key == pygame.K_f: # SPACE 키로 아이템 인벤토리 조작
                    p2_inventory_key += 1
                    if p2_inventory_key > 3:
                        p2_inventory_key = 1

                if event.key == pygame.K_g: # ENTER 키를 누르면 지정된 칸의 아이템이 사용됨
                    player2.item(p2_inventory_key)
                if event.key == pygame.K_l: # ENTER 키를 누르면 지정된 칸의 아이템이 사용됨
                    player.item(p1_inventory_key - 3)

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.speedx = 0
                if event.key == pygame.K_RIGHT:
                    player.speedx = 0
                if event.key == pygame.K_UP:
                    player.speedy = 0
                if event.key == pygame.K_DOWN:
                    player.speedy = 0

                if event.key == pygame.K_a:
                    player2.speedx = 0
                if event.key == pygame.K_d:
                    player2.speedx = 0
                if event.key == pygame.K_w:
                    player2.speedy = 0
                if event.key == pygame.K_s:
                    player2.speedy = 0

        # 레벨 변경
        if now - start_time > level_time: #임시 - 30초마다 레벨 변경
            nextlevel(now)
            if level == 4:
                game = False
                #######################################################엔딩크레딧 출력
            else:
                level += 1

            #enemys.empty() #스프라이트는 없어지는데 그림은 안없어짐 다시 덮어야할듯

            #screen.blit(background_img, background_rect)
            #pygame.display.flip()
            start_time = now + 2000

        # 업데이트
        all_sprites.update()

        #충돌 체크
        hits = pygame.sprite.groupcollide(enemys, bullets, True, True)
        for hit in hits:
            make_new_enemy(level)
            score += random.randrange(20, 50)
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
            score += random.randrange(20, 40)
            if hit.type == 'item1':
                player.item1 += 1
            if hit.type == 'item2':
                player.item2 += 1
            if hit.type == 'item3':
                player.item3 += 1
        hits = pygame.sprite.spritecollide(player2, items, True)
        for hit in hits:
            score += random.randrange(20, 40)
            if hit.type == 'item1':
                player2.item1 += 1
            if hit.type == 'item2':
                player2.item2 += 1
            if hit.type == 'item3':
                player2.item3 += 1

        # 게임 종료 조건
        if player.lives == 0 and player.HP == 0:
            player.kill()
        if player2.lives == 0 and player2.HP == 0:
            player2.kill()
        if (player.lives == 0 and player.HP == 0) or \
                (player2.lives <= 0 and player2.HP == 0):
            game = False
            #now = pygame.time.get_ticks()
            gameover(now) # 게임 오버 출력
            saveranking(score)

            score = 0 # 점수, 레벨, 인벤토리 위치 표시 초기화
            level = 1
            p1_inventory_key = 4
            p2_inventory_key = 1

    if game == False: #수정 필요
        #랭킹 입력
        #saveranking(score)
        menu = True

    screen.blit(background_img, background_rect)

    all_sprites.draw(screen)

    draw_text(screen, "SCORE: ", 20, WIDTH / 2 - 30, 30, BLACK)
    draw_text(screen, str(score), 20, WIDTH / 2 + 30, 30, BLACK)
    draw_HP(screen, 15, 15, player2.HP, BLUE)
    draw_HP(screen, WIDTH - 135, 15, player.HP, RED)

    draw_inventory(p1_inventory_key, p2_inventory_key)
    #draw_inventory(p2_inventory_key)


    draw_item(player.item1, player.item2, player.item3, WIDTH -15 - shieldWIDHT, HEIGHT - 55) # player1 아이템 그리기
    draw_item(player2.item1, player2.item2, player2.item3, 15, HEIGHT - 55) # player2 아이템 그리기
    draw_text(screen, str(player.item1), 15, WIDTH - 100, HEIGHT - 32, BLACK) # player1 아이템 개수 표시
    draw_text(screen, str(player.item2), 15, WIDTH - 60, HEIGHT - 32, BLACK)
    draw_text(screen, str(player.item3), 15, WIDTH - 20, HEIGHT - 32, BLACK)
    draw_text(screen, str(player2.item1), 15, 50, HEIGHT - 32, BLACK) # plyaer2 아이템 개수 표시
    draw_text(screen, str(player2.item2), 15, 90, HEIGHT - 32, BLACK)
    draw_text(screen, str(player2.item3), 15, 130, HEIGHT - 32, BLACK)

    draw_lives(screen, 10, player2.lives, min_player1)
    draw_lives(screen, WIDTH - 145, player.lives, min_player2)

    draw_text(screen, "LEVEL:  ", 20, WIDTH / 2 - 30, 5, BLACK)
    draw_text(screen, str(level), 20, WIDTH/2 + 30, 5, BLACK)

    draw_text(screen, "TIME:    ", 20, WIDTH / 2 - 30, 55, BLACK)
    if level_time - (now - start_time) > 4000 : # 남은 시간이 4초 이상이면 검정색으로 시간 표시
        draw_text(screen, str("%0.2f" % float((level_time - (now - start_time))/ 1000)), 20, WIDTH / 2 + 30, 55, BLACK)
    else: # 남은 이간이 4초 이하라면 빨간색 굵은 글씨로 시간 표시
        draw_text(screen, str("%0.2f" % float((level_time - (now - start_time)) / 1000)), 20, WIDTH / 2 + 30, 55, RED)

    pygame.display.flip()

pygame.quit()



