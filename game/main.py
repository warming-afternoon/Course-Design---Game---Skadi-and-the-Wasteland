import sys
import pygame
from pygame.locals import *
import Controller
from map_edit import start

# 定义游戏变量
screen_width,screen_height= 1280,720
main_menu = True
help_menu = False
FPS=60
SCORE=0
# 加载图片
start_btn_img = pygame.image.load("image/bottom/start_btn.png")
help_btn_img = pygame.image.load("image/bottom/help_btn.png")
return_btn_img = pygame.image.load("image/bottom/return_btn.png")
main_back_img=pygame.image.load("image/main_back.png")
help_back_img=pygame.image.load("image/help_back.png")
#启动
pygame.init()
clock=pygame.time.Clock()
#主窗口
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("斯卡蒂与荒芜之原")
pygame.mixer.music.load("music/Call_of_silence.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
# 实例化按钮
start_button = Controller.Button(screen_width // 2-93 , screen_height // 2-10, start_btn_img)
help_button = Controller.Button(screen_width // 2 -93, screen_height // 2+ 80, help_btn_img)
return_button = Controller.Button(screen_width // 2 -93, screen_height // 2+ 200, return_btn_img)
RUN=True
while RUN:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN=False

    if main_menu == True:
        screen.blit(main_back_img,(0,0))
        if help_button.draw(screen):
            main_menu = False
            help_menu = True
        if start_button.draw(screen):
            main_menu = False
            help_menu = False
    elif help_menu == True:
        screen.blit(help_back_img,(0,0))
        if return_button.draw(screen):
            main_menu = True
            help_menu = False
    else:
        start()
            
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
