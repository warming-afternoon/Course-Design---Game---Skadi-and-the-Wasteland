import sys
from pygame.locals import *
from Controller import *

#主界面
def start():
    # 定义游戏变量
    screen_width,screen_height= 1280,720
    game_over=0
    FPS=60
    level=0
    max_levels=4 
    cut_down=0
    # 加载图片
    back_img=pygame.image.load("image/back_night.png")
    restart_img = pygame.image.load("image/bottom/restart_btn.png")
    background_img=pygame.image.load("image/background.png")
    #启动
    pygame.init()
    clock=pygame.time.Clock()
    #主窗口
    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption("斯卡蒂与荒芜之原")
    screen.blit(background_img, (0,0))
    if os.path.exists(f"./level{level}_data"):
        pickle_in = open(f"level{level}_data", "rb")
        world_data = pickle.load(pickle_in)
    map = Map(world_data,screen)
    if map.player_y!=None and map.player_x!=None:
        player_x,player_y=map.player_x,map.player_y
    else:
        player_x,player_y=100,100
    player=Player(map,player_x,player_y)
    restart_button = Button(screen_width // 2 - 50, screen_height // 2, restart_img)
    #背景音乐
    pygame.mixer.music.load("music/蔓延.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    #设置字体和文字
    font_big = pygame.font.SysFont("Microsoft YaHei",60)
    #主程序
    RUN=True
    while RUN:
        screen.blit(back_img,(0,0))
        map.draw()
        map.enemy_group.update()
        map.platform_group.update()
        map.platform_group.draw(screen)
        map.lava_group.draw(screen)
        map.TL_platform_group.draw(screen)
        map.exit_group.draw(screen)     
        game_over = player.update(game_over)
        player.draw(screen)
        cut_down+=1
        if cut_down >= 30:
            cut_down=0
            map.material_reset()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN=False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    player.jump()
                if event.key == K_j:
                    player.attack()

        if game_over == -1:
            if restart_button.draw(screen):
                player.restart()
                map.enemy_restart()
                game_over = 0
        if game_over == 1:
            level += 1
            if level <= max_levels:
               screen.blit(background_img, (0,0))
               world_data = []
               map.reset_level(level,player)
               game_over = 0
            else:
                img = font_big.render("YOU WIN!", True, WHITE)
                screen.blit(img, ((screen_width // 2) - 142, screen_height // 2-100))
                if restart_button.draw(screen):
                    level = 0
                    world_data = []
                    map.reset_level(level,player)
                    game_over = 0

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    start()