import time
import pygame
import os
import pickle
from pygame.locals import *

#颜色
BLACK=(0,0,0) 
WHITE=(255,255,255)

dirt_img=pygame.image.load("image/dirt.png")
dirt_in_img=pygame.image.load("image/dirt_in.png")
platform_img=pygame.image.load("image/platform.png")
lava_img = pygame.image.load("image/lava.png")
lucency_platform_img=pygame.image.load("image/lucency_platform.png")
background_img=pygame.image.load("image/background.png")
def draw_grid(surf):
    rect=surf.get_rect()
    surf_width,surf_height=rect.width,rect.height
    grid_width=surf_width/20
    grid_height=surf_height/20  
    for line in range(0,20):
        pygame.draw.line(surf,WHITE,(0,line*grid_height),(surf_width,line*grid_height))
        pygame.draw.line(surf,WHITE,(line*grid_width,0),(line*grid_width,surf_height))

def show_rect(surf):
    rect=surf.get_rect()
    print("left= %d,right= %d" % (rect.left,rect.right))
    print("top= %d,bottom= %d" % (rect.top,rect.bottom))

# 创建按钮
class Button():
    def __init__(self, xi, yi, image):
        self.image = image
        self.rect = self.image.get_rect(x=xi,y=yi)
        self.clicked = False

    def draw(self,surf):
        action = False
        # 得到鼠标的位置
        pos = pygame.mouse.get_pos()
        # 检测鼠标是否经过按钮位置和是否已点击
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # 将按钮画到屏幕上
        surf.blit(self.image, self.rect)

        return action

#地图类
class Map():
    def __init__(self,data,surf):
        self.surf=surf
        self.tile_list=[]
        rect=surf.get_rect()
        self.surf_width,self.surf_height=rect.width,rect.height
        grid_width=self.surf_width/20
        grid_height=self.surf_height/20
        self.enemies=[]
        self.TL_platforms=[]
        self.player_x,self.player_y=None,None
        #创建碰撞组
        self.enemy_group = pygame.sprite.Group()
        self.platform_group= pygame.sprite.Group()
        self.lava_group = pygame.sprite.Group()
        self.exit_group=pygame.sprite.Group()
        self.TL_platform_group=pygame.sprite.Group()
        #加载图片
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:    #深层土
                    img = pygame.transform.scale(dirt_in_img, (grid_width, grid_height))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * grid_width
                    img_rect.y = row_count * grid_height
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 2:  #浅层土
                    img = pygame.transform.scale(dirt_img, (grid_width, grid_height))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * grid_width
                    img_rect.y = row_count * grid_height
                    tile = (img, img_rect)
                    self.tile_list.append(tile)                
                elif tile == 3:  #怪物
                    shield_soldier = Enemy(self,col_count * grid_width, row_count * grid_height + 8)
                    self.enemy_group.add(shield_soldier)
                    self.enemies.append(shield_soldier)
                elif tile == 4:  #上下移动平台
                    platform = Platform(self.surf,col_count * grid_width, row_count * grid_height, 1, 0)
                    self.platform_group.add(platform)
                elif tile == 5:  #左右移动平台
                    platform = Platform(self.surf,col_count * grid_width, row_count * grid_height, 0, 1)
                    self.platform_group.add(platform)
                elif tile == 6:  #岩浆
                    lava = Lava(self.surf,col_count * grid_width, row_count * grid_height)
                    self.lava_group.add(lava)
                elif tile == 7:  #限时平台
                    TL_platform = Time_limited_platform(self.surf,col_count * grid_width, row_count * grid_height)
                    self.TL_platform_group.add(TL_platform)
                    self.TL_platforms.append(TL_platform)
                elif tile == 8:  #出口
                    exit = Exit(col_count * grid_width, row_count * grid_height+8)
                    self.exit_group.add(exit)  
                elif tile == 9:  #玩家
                    if self.player_x==None and self.player_y==None:
                        self.player_x,self.player_y = col_count * grid_width, row_count * grid_height
                col_count += 1
            row_count += 1
    def enemy_restart(self):
        for enemy in self.enemies:
            if enemy.alive and enemy.groups()!=[]:
                pass
            else:
                enemy.restart()
                self.enemy_group.add(enemy)
    def material_reset(self):
        current_time=time.time()
        for enemy in self.enemies:
            enemy_alive=enemy.alive and enemy.groups()!=[]
            if enemy_alive!=True and current_time-enemy.die_time>=10:
                enemy.restart()
                self.enemy_group.add(enemy)
        for TL_platform in self.TL_platforms:
            TL_platform.update()
            TL_platform_alive=TL_platform.alive and TL_platform.groups()!=[]
            if TL_platform_alive!=True and current_time-TL_platform.die_time>=6:
                TL_platform.restart()
                self.TL_platform_group.add(TL_platform)
    def reset_level(self,level,player):
        self.enemy_group.empty()
        self.platform_group.empty()
        self.lava_group.empty()
        self.exit_group.empty()
        if os.path.exists(f"./level{level}_data"):
            pickle_in = open(f"level{level}_data", "rb")
            map_data = pickle.load(pickle_in)
        self.__init__(map_data,self.surf)
        if self.player_y!=None and self.player_x!=None:
            player_x,player_y=self.player_x,self.player_y
        else:
            player_x,player_y=100,100
        player.restart(player_x,player_y)
    
    def draw(self):
        for tile in self.tile_list:
            self.surf.blit(tile[0], tile[1])

#角色类
class Player(pygame.sprite.Sprite):
    images_right = []
    images_left = []
    imgs_right_mask = []
    imgs_left_mask = []
    die_right = []
    die_left = []
    attack_right=[]
    attack_left=[]
    attack_right_mask=[]
    attack_left_mask=[]
    image_exist=False
    
    def __init__(self,map,xi,yi)-> None:
        super(Player,self).__init__()   #调用父类__init__方法初始化对象
        self.map=map
        if Player.image_exist==False:
            #加载动画图片       
            default_left,default_right,default_left_mask,default_right_mask=self.get_img("image/skadi/default")
            Player.images_left.extend(default_left)
            Player.images_right.extend(default_right)
            Player.imgs_left_mask.extend(default_left_mask)
            Player.imgs_right_mask.extend(default_right_mask)       
            move_left,move_right,move_left_mask,move_right_mask=self.get_img("image/skadi/move/Move",45)
            Player.images_left.extend(move_left)
            Player.images_right.extend(move_right)
            Player.imgs_left_mask.extend(move_left_mask)
            Player.imgs_right_mask.extend(move_right_mask)
            die_left,die_right=self.get_img("image/skadi/die/die",46,False)
            Player.die_left.extend(die_left)
            Player.die_right.extend(die_right)
            att_begin_left,att_begin_right,att_begin_left_mask,att_begin_right_mask=self.get_img("image/skadi/attack/Attack_Begin",7)
            Player.attack_left.extend(att_begin_left)
            Player.attack_right.extend(att_begin_right)
            Player.attack_left_mask.extend(att_begin_left_mask)
            Player.attack_right_mask.extend(att_begin_right_mask)
            att_left,att_right,att_left_mask,att_right_mask=self.get_img("image/skadi/attack/Attack",75)
            Player.attack_left.extend(att_left)
            Player.attack_right.extend(att_right)
            Player.attack_left_mask.extend(att_left_mask)
            Player.attack_right_mask.extend(att_right_mask)
            att_begin_left.reverse(),att_begin_right.reverse(),att_begin_left_mask.reverse(),att_begin_right_mask.reverse()
            Player.attack_left.extend(att_begin_left)
            Player.attack_right.extend(att_begin_right)
            Player.attack_left_mask.extend(att_begin_left_mask)
            Player.attack_right_mask.extend(att_begin_right_mask)
        #设置人物属性
        self.image = Player.images_right[0]
        self.mask=Player.imgs_right_mask[0]  
        self.in_air = True
        self.jump_num = 0
        self.direction = 1
        self.o_x,self.o_y=xi,yi
        self.vel_x,self.vel_y=0,0
        self.index = 0
        self.counter=0
        self.blood=100
        self.retract_x,self.retract_y=100,97
        self.rect=pygame.Rect((xi-self.retract_x,yi-self.retract_x),(48,102))
        self.true_rect=pygame.Rect((xi,yi),(48,102))
        self.walk_cooldown = 1
        self.hit_time= None
        self.is_attack =False
    def restart(self,xi=None,yi=None) -> None:
        self.image = self.images_right[0]
        self.mask=self.imgs_right_mask[0]  
        if xi!=None and yi!=None:
            self.o_x,self.o_y=xi,yi
            self.rect=pygame.Rect((xi-self.retract_x,yi-self.retract_x),(48,102))
            self.true_rect=pygame.Rect((xi,yi),(48,102))
        else:
            self.rect=pygame.Rect((self.o_x-self.retract_x,self.o_y-self.retract_y),(48,102))
            self.true_rect=pygame.Rect((self.o_x,self.o_y),(48,102))
        self.in_air = True
        self.jump_num = 0
        self.direction = 1
        self.vel_x,self.vel_y=0,0
        self.index = 0
        self.counter=0
        self.blood=100
        self.hit_time= None
        self.is_attack =False
        
    def update(self,game_over):
        dx = 0
        dy =  0
        col_thresh=15
        current_time=time.time()
        if self.blood>0:
            pressed_keys=pygame.key.get_pressed()
            self.counter += 1
            if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
                dx += 4
                self.direction = 1
            elif pressed_keys[K_LEFT] or pressed_keys[K_a]:
                dx -= 4
                self.direction = -1
            else :
                if self.is_attack:
                    pass
                else:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                        self.mask = self.imgs_right_mask[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]
                        self.mask=self.imgs_right_mask[self.index]
            # 播放动画
            if self.counter >= self.walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.is_attack:
                    if self.index >= len(self.attack_right)-1:
                        self.is_attack=False
                        self.index = 1
                    else:
                        if self.direction == 1:
                            self.image = self.attack_right[self.index]
                            self.mask = self.attack_right_mask[self.index]
                        if self.direction == -1:
                            self.image = self.attack_left[self.index]
                            self.mask = self.attack_left_mask[self.index]
                else:
                    if self.index >= len(self.images_right):
                        self.index = 1
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                        self.mask = self.imgs_right_mask[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]
                        self.mask = self.imgs_left_mask[self.index]
            # 玩家与敌人的碰撞
            uninvincible= self.hit_time==None or current_time-self.hit_time>=1.5
            for enemy in self.map.enemy_group:
                both_distance_y=self.true_rect.centery-enemy.true_rect.centery
                both_distance_x=self.true_rect.centerx-enemy.true_rect.centerx
                in_y_ken= -enemy.ken<both_distance_y and both_distance_y<enemy.ken
                in_x_ken= -enemy.ken<both_distance_x and both_distance_x<enemy.ken
                if in_y_ken and in_x_ken:
                    enemy.player_distance_x=both_distance_x
                else:
                    enemy.player_distance_x=None
                collision_point=pygame.sprite.collide_mask(self, enemy)
                if collision_point != None  and enemy.die_time==None:
                    if self.is_attack and self.index>6 and self.index<80:
                        hit_left=self.true_rect.width/2 <= collision_point[0]
                        hit_down=self.true_rect.height/2 <= collision_point[1]
                        enemy.be_attacked(30,hit_left,hit_down)
                    elif uninvincible:
                        self.hit_time=current_time
                        self.be_attacked(40)
                        if self.true_rect.width/2 <= collision_point[0]:
                            self.vel_x = -10
                        else:
                            self.vel_x = 10
                        if self.true_rect.height/2 < collision_point[1]:
                            self.vel_y= -10
            
            #检测血量
            if self.blood<=0:
                self.index=0
                self.counter=0
                self.vel_y=0               
            #向左击退或向右击退
            if self.vel_x <0:
                self.vel_x += 1   
            if self.vel_x > 0:
                self.vel_x -= 1
            dx += self.vel_x
            #下落或上升
            self.vel_y += 1   
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            if self.in_air == False:
                self.jump_num = 0
            # 检测玩家与每个泥块与草地的碰撞
            self.in_air = True
            for tile in self.map.tile_list:
                #判断玩家在x方向上的碰撞
                if tile[1].colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    dx = 0
                #检测玩家在y方向的碰撞
                if tile[1].colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                    #检测玩家顶部与泥块底部碰撞
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.true_rect.top
                        self.vel_y = 0
                    #检测玩家底部与泥块顶部的碰撞
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.true_rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #玩家与熔岩的碰撞
            for lava in self.map.lava_group:                
                if lava.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    if lava.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                        self.be_attacked(100)

            # 玩家与出口的碰撞
            for exit in self.map.exit_group:
                if exit.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    if exit.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                        game_over = 1     
            # 玩家与移动平台的碰撞
            for platform in self.map.platform_group:
                # 检测玩家与块x方向上的碰撞
                if platform.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    dx = 0
                # 检测人员与块y方向上的碰撞
                if platform.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                    # 检测玩家顶部与平台底部的碰撞
                    if abs((self.true_rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.true_rect.top
                    # 检测玩家底部与平台顶部的碰撞
                    elif abs((self.true_rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.true_rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # 判断是否与平台一起动
                    if platform.move_x != 0:
                        self.true_rect.x += platform.move_direction
            # 玩家与限时平台的碰撞
            for TL_platform in self.map.TL_platform_group:
                # 检测玩家与块x方向上的碰撞
                if TL_platform.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    dx = 0
                # 检测人员与块y方向上的碰撞
                if TL_platform.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                    # 检测玩家顶部与平台底部的碰撞
                    if abs((self.true_rect.top + dy) - TL_platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = TL_platform.rect.bottom - self.true_rect.top
                    # 检测玩家底部与平台顶部的碰撞
                    elif abs((self.true_rect.bottom + dy) - TL_platform.rect.top) < col_thresh:
                        TL_platform.be_hit(current_time)
                        self.true_rect.bottom = TL_platform.rect.top - 1
                        self.in_air = False
                        dy = 0
            # 更新玩家的位置
            self.true_rect.move_ip(dx,dy)
            #画面边界检测
            if self.true_rect.top <=0 :
                self.true_rect.top=0
            if self.true_rect.bottom >= self.map.surf_height :
                self.true_rect.bottom=self.map.surf_height          
            if self.true_rect.left <=0 :
                self.true_rect.left=0
            if self.true_rect.right >= self.map.surf_width:
                self.true_rect.right=self.map.surf_width    
            self.rect.x,self.rect.y=self.true_rect.x-self.retract_x,self.true_rect.y-self.retract_y
        elif  self.blood<=0:
            # 播放动画
            if self.index < len(self.die_right)-1:
                self.counter += 1
            if self.counter >= 1:
                self.counter = 0
                self.index += 1
                if self.direction == 1:
                    self.image = self.die_right[self.index]
                if self.direction == -1:
                    self.image = self.die_left[self.index] 
            else:
                game_over=-1    
        
        return game_over
    
    def jump(self):
        if self.jump_num <1 :
            self.vel_y = -12
            self.jump_num +=1
    def attack(self):
        self.is_attack=True
    def get_img(self,str,num=2,get_mask=True):    
        if get_mask==True:
            images_left=[]
            images_right=[]
            left_masks=[]
            right_masks=[]
            for num in range(1,num):
                img_right = pygame.image.load(str+f"-{num}.png")
                img_rect=img_right.get_rect()
                img_right = pygame.transform.scale(img_right, (img_rect.width/4,img_rect.height/4))
                img_left = pygame.transform.flip(img_right, True, False)
                images_left.append(img_left)
                images_right.append(img_right)
                left_mask=pygame.mask.from_surface(img_left)
                right_mask=pygame.mask.from_surface(img_right)
                left_masks.append(left_mask)
                right_masks.append(right_mask)
            return images_left,images_right,left_masks,right_masks
        else:
            images_left=[]
            images_right=[]
            for num in range(1,num):
                img_right = pygame.image.load(str+f"-{num}.png")
                img_rect=img_right.get_rect()
                img_right = pygame.transform.scale(img_right, (img_rect.width/4,img_rect.height/4))
                img_left = pygame.transform.flip(img_right, True, False)
                images_left.append(img_left)
                images_right.append(img_right)
            return images_left,images_right
    def be_attacked(self,hurt):
        self.blood -= hurt
        if self.blood < 0:
            self.blood = 0
    def draw(self,surf):
        surf.blit(self.image,(self.rect.x,self.rect.y))
        #pygame.draw.rect(self.map.surf, (255, 255, 255), (self.true_rect.x, self.true_rect.y, self.rect.width, self.rect.height),width=1)
        #pygame.draw.rect(self.map.surf, (255, 255, 255), (self.rect.x, self.rect.y, self.rect.width, self.rect.height),width=1)
        #人物上方血条
        pygame.draw.rect(surf, (128, 128, 128), (self.true_rect.x+2, self.true_rect.y - 20, 52, 8),width=1)
        pygame.draw.rect(surf, (255, 0, 0),(self.true_rect.x + 3, self.true_rect.y - 19, self.blood /2, 6))  

#敌人类
class Enemy(pygame.sprite.Sprite):
    images_right = []
    images_left = []
    imgs_right_mask = []
    imgs_left_mask = []
    die_right = []
    die_left = []
    attack_right=[]
    attack_left=[]
    attack_right_mask=[]
    attack_left_mask=[]
    image_exist=False
    def __init__(self,map,xi,yi) -> None:
        super(Enemy,self).__init__()   #调用父类__init__方法初始化对象
        self.map=map
        #加载图片
        if Enemy.image_exist==False:
            move_left,move_right,move_left_mask,move_right_mask=self.get_img("image/double_swordsman/move/Move",42)
            Enemy.images_left.extend(move_left)
            Enemy.images_right.extend(move_right)
            Enemy.imgs_left_mask.extend(move_left_mask)
            Enemy.imgs_right_mask.extend(move_right_mask)
            die_left,die_right=self.get_img("image/double_swordsman/die/die",49,False)
            Enemy.die_left.extend(die_left)
            Enemy.die_right.extend(die_right)
            att_left,att_right,att_left_mask,att_right_mask=self.get_img("image/double_swordsman/attack/Attack",53)
            Enemy.attack_left.extend(att_left)
            Enemy.attack_right.extend(att_right)
            Enemy.attack_left_mask.extend(att_left_mask)
            Enemy.attack_right_mask.extend(att_right_mask)
            Enemy.image_exist=True
        #变量
        self.image = Enemy.images_right[0]
        self.mask=Enemy.imgs_right_mask[0]
        self.in_air = True
        self.direction = 1
        self.vel_x,self.vel_y=0,0
        self.index = 0
        self.counter=0
        self.retract_x=93
        self.retract_y=108
        self.o_x,self.o_y=xi,yi
        self.rect=pygame.Rect((xi-self.retract_x,yi-self.retract_y),(63,91))
        self.true_rect=pygame.Rect((xi,yi),(63,91))
        self.move_counter=0
        self.walk_cooldown = 1
        self.blood=100
        self.die_time=None
        self.hit_time= None
        self.is_attack =False
        self.attack_distance=150
        self.player_distance_x=None
        self.ken=250
    def restart(self) -> None:
        self.direction = 1
        self.vel_x,self.vel_y=0,0
        self.index = 0
        self.counter=0
        self.rect=pygame.Rect((self.o_x-self.retract_x,self.o_y-self.retract_y),(60,94))
        self.true_rect=pygame.Rect((self.o_x,self.o_y),(60,94))
        self.move_counter=0
        self.blood=100
        self.die_time=None
        self.hit_time= None
        self.is_attack =False
        self.player_distance_x=None
    def update(self):
        dx = 0
        dy =  0
        col_thresh=18
        if self.blood>0:
            if self.player_distance_x!=None:
                if -self.attack_distance<self.player_distance_x and self.player_distance_x> self.attack_distance:
                    self.is_attack =True
                if self.player_distance_x>=0:
                    self.direction=1
                else:
                    self.direction=-1
            else:
                self.is_attack =False
                self.move_counter+=1
            dx += self.direction
            self.counter += 1
            # 播放动画
            if self.counter >= self.walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.is_attack:
                    if self.index >= len(self.attack_right)-1:
                        self.index = 0
                    else:
                        if self.direction == 1:
                            self.image = self.attack_right[self.index]
                            self.mask = self.attack_right_mask[self.index]
                        if self.direction == -1:
                            self.image = self.attack_left[self.index]
                            self.mask = self.attack_left_mask[self.index]
                else:
                    if self.index >= len(self.images_right)-1:
                        self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                        self.mask = self.imgs_right_mask[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]
                        self.mask = self.imgs_left_mask[self.index]    
            #向左击退或向右击退
            if self.vel_x <0:
                self.vel_x += 1   
            if self.vel_x > 0:
                self.vel_x -= 1
            dx += self.vel_x
            #下落或上升
            self.vel_y += 1   
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            
            if self.in_air == False:
                self.jump_num = 0
            # 检测怪物与每个泥块与草地的碰撞
            self.in_air = True
            for tile in self.map.tile_list:
                #判断怪物在x方向上的碰撞
                if tile[1].colliderect(self.true_rect.x + dx , self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    dx = 0
                #检测怪物在y方向的碰撞
                if tile[1].colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                    #检测怪物顶部与泥块底部碰撞
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.true_rect.top
                        self.vel_y = 0
                    #检测怪物底部与泥块顶部的碰撞
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.true_rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #怪物与熔岩的碰撞
            for lava in self.map.lava_group:                
                if lava.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    if lava.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                        self.be_attacked(100)
                       
            #怪物与移动平台的碰撞
            for platform in self.map.platform_group:
                # 检测怪物与块x方向上的碰撞
                if platform.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    dx = 0
                # 检测怪物与块y方向上的碰撞
                if platform.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                    # 检测底部的碰撞
                    if abs((self.true_rect.top+ dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.true_rect.top
                    # 检测顶部的碰撞
                    elif abs((self.true_rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.true_rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #判断是否与平台一起动
                    if platform.move_x != 0:
                        self.true_rect.x += platform.move_direction
            # 怪物与限时平台的碰撞
            for TL_platform in self.map.TL_platform_group:
                if TL_platform.rect.colliderect(self.true_rect.x + dx, self.true_rect.y, self.true_rect.width, self.true_rect.height):
                    dx = 0
                if TL_platform.rect.colliderect(self.true_rect.x, self.true_rect.y + dy, self.true_rect.width, self.true_rect.height):
                    if abs((self.true_rect.top + dy) - TL_platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = TL_platform.rect.bottom - self.true_rect.top
                    elif abs((self.true_rect.bottom + dy) - TL_platform.rect.top) < col_thresh:
                        self.true_rect.bottom = TL_platform.rect.top - 1
                        self.in_air = False
                        dy = 0
            #换向            
            if abs(self.move_counter) > 50:
                self.direction *= -1
                self.move_counter *= -1
            # 更新怪物的位置
            self.true_rect.move_ip(dx,dy)  
            #画面边界检测
            if self.true_rect.top <=0 :
                self.true_rect.top=0
            if self.true_rect.bottom >= self.map.surf_height :
                self.true_rect.bottom=self.map.surf_height           
            if self.true_rect.left <=0:
                self.true_rect.left=0
            if self.true_rect.right >= self.map.surf_width:
                self.true_rect.right=self.map.surf_width    
            self.rect.x,self.rect.y=self.true_rect.x-self.retract_x,self.true_rect.y-self.retract_y
        elif  self.blood<=0:
            # 播放死亡动画
            if self.index < len(self.die_right)-1:
                self.counter += 1
            if self.counter >= 1:
                self.counter = 0
                self.index += 1
                if self.direction == 1:
                    self.image = self.die_right[self.index]
                if self.direction == -1:
                    self.image = self.die_left[self.index] 
            else:
                self.kill()
        #显示画面
        self.map.surf.blit(self.image,self.rect)
        # pygame.draw.rect(self.map.surf, (255, 255, 255), (self.true_rect.x, self.true_rect.y, self.rect.width, self.rect.height),width=1)
        # pygame.draw.rect(self.map.surf, (255, 255, 255), (self.rect.x, self.rect.y, self.rect.width, self.rect.height),width=1)
        pygame.draw.rect(self.map.surf, (128, 128, 128), (self.true_rect.x + 6, self.true_rect.y - 20, 52, 8),width=1)
        pygame.draw.rect(self.map.surf, (255, 0, 0),(self.true_rect.x + 7, self.true_rect.y - 19, self.blood /2, 6))

    def be_attacked(self,hurt,hit_left=True,hit_down=True):
        current_time=time.time()
        uninvincible= self.hit_time==None or current_time-self.hit_time>=0.4
        if uninvincible:
            self.hit_time=current_time
            self.blood -= hurt
            if hit_left:
                self.vel_x = 10
            else:
                self.vel_x = -10
            if hit_down:
                self.vel_y= -10
        #检测血量
            if self.blood<=0:
                self.die_time=time.time()
                self.index=0
                self.counter=0
                self.vel_y=0   
    
    def get_img(self,str,num=2,get_mask=True):    
        if get_mask==True:
            images_left=[]
            images_right=[]
            left_masks=[]
            right_masks=[]
            for num in range(1,num):
                img_right = pygame.image.load(str+f"-{num}.png")
                img_rect=img_right.get_rect()
                img_right = pygame.transform.scale(img_right, (img_rect.width/4,img_rect.height/4))
                img_left = pygame.transform.flip(img_right, True, False)
                images_left.append(img_left)
                images_right.append(img_right)
                left_mask=pygame.mask.from_surface(img_left)
                right_mask=pygame.mask.from_surface(img_right)
                left_masks.append(left_mask)
                right_masks.append(right_mask)
            return images_left,images_right,left_masks,right_masks
        else:
            images_left=[]
            images_right=[]
            for num in range(1,num):
                img_right = pygame.image.load(str+f"-{num}.png")
                img_rect=img_right.get_rect()
                img_right = pygame.transform.scale(img_right, (img_rect.width/4,img_rect.height/4))
                img_left = pygame.transform.flip(img_right, True, False)
                images_left.append(img_left)
                images_right.append(img_right)
            return images_left,images_right

class Platform(pygame.sprite.Sprite):
    def __init__(self,surf, x, y, move_x, move_y):
        super().__init__()
        rect=surf.get_rect()
        surf_width,surf_height=rect.width,rect.height
        grid_width=surf_width/20
        grid_height=surf_height/20
        self.image = pygame.transform.scale(dirt_img, (grid_width, grid_height // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1        

class Time_limited_platform(pygame.sprite.Sprite):
    def __init__(self,surf, xi, yi):
        super(Time_limited_platform,self).__init__()
        rect=surf.get_rect()
        surf_width,surf_height=rect.width,rect.height
        grid_width=surf_width/20
        grid_height=surf_height/20        
        self.common_image = pygame.transform.scale(platform_img, (grid_width, grid_height // 2))
        self.lucency_image=pygame.transform.scale(lucency_platform_img, (grid_width, grid_height // 2))
        self.image=self.common_image
        self.rect = self.image.get_rect(x=xi,y=yi)
        self.hit_time=None
        self.die_time=None
        self.keep_time=3
    def update(self):
        if self.hit_time!=None:
            self.image=self.lucency_image
            current_time=time.time()
            if current_time-self.hit_time >self.keep_time and self.die_time==None:
                self.die_time=current_time
                self.kill()
    def restart(self) -> None:
        self.image=self.common_image
        self.hit_time=None
        self.die_time=None
    def be_hit(self,current_time):
        if self.hit_time==None:
            self.hit_time=current_time
     
class Lava(pygame.sprite.Sprite):
    def __init__(self,surf, xi, yi):
        super().__init__()
        rect=surf.get_rect()
        surf_width,surf_height=rect.width,rect.height
        grid_width=surf_width/20
        grid_height=surf_height/20
        self.image = pygame.transform.scale(lava_img, (grid_width, grid_height // 2))
        self.rect = self.image.get_rect(x=xi,y=yi+grid_height // 2)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("image/exit.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y