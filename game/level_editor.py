import sys
import pygame
import pickle
from os import path
from pygame.locals import *
from map_edit import *

#颜色
BLACK=(0,0,0) 
BLUE=(0,0,255)
RED=(255,0,0)
WHITE=(255,255,255)
RUN=True

# 定义游戏变量
screen_width,screen_height= 1280,720
main_menu = True
FPS=60
grid_width, grid_height=64,36
clicked = False
level = 0

# 加载图片
back_img=pygame.image.load("image/back_night.png")
dirt_img=pygame.image.load("image/dirt.png")
dirt_in_img=pygame.image.load("image/dirt_in.png")
platform_img=pygame.image.load("image/platform.png")
lucency_platform_img=pygame.image.load("image/lucency_platform.png")
double_swordsman_img=pygame.image.load("image/double_swordsman/move/Move-1.png")
skadi_img=pygame.image.load("image/skadi/default-1.png")
lava_img = pygame.image.load('image/lava.png')
restart_img = pygame.image.load("image/bottom/restart_btn.png")
start_img = pygame.image.load("image/bottom/start_btn.png")
exit_img = pygame.image.load("image/exit.png")
save_img = pygame.image.load("image/bottom/save_btn.png")
load_img = pygame.image.load("image/bottom/load_btn.png")
#创建空列表
world_data = []
for row in range(20):
	r = [0] * 20
	world_data.append(r)

def draw_grid():
	for c in range(21):
		pygame.draw.line(screen, WHITE, (c * grid_width, 0), (c * grid_width, screen_height))
		pygame.draw.line(screen, WHITE, (0, c * grid_height), (screen_width, c * grid_height))
def draw_world():
    row_count=0
    for row in world_data:
            col_count = 0
            for tile in row:
                if tile == 1:    #深层土
                    img = pygame.transform.scale(dirt_in_img, (grid_width, grid_height))
                    screen.blit(img, (col_count * grid_width, row_count * grid_height))
                if tile == 2:    #浅层土
                    img = pygame.transform.scale(dirt_img, (grid_width, grid_height))
                    screen.blit(img, (col_count * grid_width, row_count * grid_height))               
                if tile == 3:    #怪物
                    img_rect=double_swordsman_img.get_rect()
                    img = pygame.transform.scale(double_swordsman_img, (img_rect.width/4,img_rect.height/4))
                    screen.blit(img, (col_count * grid_width-93, row_count * grid_height-108))
                if tile == 4:    #左右移动平台
                    img = pygame.transform.scale(platform_img, (grid_width, grid_height // 2))
                    screen.blit(img, (col_count * grid_width, row_count * grid_height))
                    pygame.draw.rect(screen,(255, 255, 255), (col_count * grid_width+45, row_count * grid_height+10,20,4))
                if tile == 5:    #上下移动平台
                    img = pygame.transform.scale(platform_img, (grid_width, grid_height // 2))
                    screen.blit(img, (col_count * grid_width, row_count * grid_height))
                    pygame.draw.rect(screen,(255, 255, 255), (col_count * grid_width+50, row_count * grid_height+5, 4, 20))
                if tile == 6:
                    img=lava_img
                    screen.blit(img, (col_count * grid_width, row_count * grid_height))
                if tile == 7:
                    pygame.draw.rect(screen,(255, 255, 255), (col_count * grid_width, row_count * grid_height,64,36))
                if tile == 8:    #出口
                    img=exit_img
                    screen.blit(img, (col_count * grid_width, row_count * grid_height+8))
                if tile == 9:    #玩家
                    img_rect=skadi_img.get_rect()
                    img = pygame.transform.scale(skadi_img, (img_rect.width/4,img_rect.height/4))
                    screen.blit(img, (col_count * grid_width-100, row_count * grid_height-97))
                col_count += 1
            row_count += 1

#启动
pygame.init()
clock=pygame.time.Clock()
#主窗口
screen = pygame.display.set_mode((screen_width,screen_height+100))
pygame.display.set_caption("关卡编辑器") 

#在屏幕上输出文字
font = pygame.font.SysFont("Microsoft YaHei",24)
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

# 实例化按钮
save_button = Button(screen_width // 2 - 150, screen_height + 40, save_img)
load_button = Button(screen_width // 2 + 50, screen_height + 40, load_img)
    
RUN=True
while RUN:
    screen.fill((144, 201, 120))
    screen.blit(back_img, (0, 0))
    if save_button.draw(screen):
        #保持关卡数据
        pickle_out = open(f'level{level}_data', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out.close()
    if load_button.draw(screen):
        #加载关卡数据
        if path.exists(f'level{level}_data'):
            pickle_in = open(f'level{level}_data', 'rb')
            world_data = pickle.load(pickle_in)
    draw_grid()
    draw_world()
    draw_text(f'Level: {level}', font, WHITE, grid_width, screen_height +40)
    draw_text('Press UP or DOWN to change level', font, WHITE, grid_width, screen_height + 60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                RUN = False
        #检测鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
            pos = pygame.mouse.get_pos()
            x = int(pos[0] // grid_width)
            y = int(pos[1] // grid_height)
            if x < 20 and y < 20:
                #更新关卡数据
                if pygame.mouse.get_pressed()[0] == 1:
                    world_data[y][x] += 1
                    if world_data[y][x] > 9:
                        world_data[y][x] = 0
                elif pygame.mouse.get_pressed()[2] == 1:
                    world_data[y][x] -= 1
                    if world_data[y][x] < 0:
                        world_data[y][x] = 9
        if event.type == pygame.MOUSEBUTTONUP:
            clicked = False
        #更改关卡号
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            elif event.key == pygame.K_DOWN and level > 0:
                level -= 1

    pygame.display.update()
    clock.tick(FPS)
    
pygame.quit()
sys.exit()
    