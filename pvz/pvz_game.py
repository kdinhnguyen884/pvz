import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PvZ Smooth Edition")
clock = pygame.time.Clock()

GRID = 80
OX, OY = 100, 120

WHITE = (255,255,255)
GREEN = (50,180,50)
DARK_GREEN = (30,120,30)
YELLOW = (255,255,0)
RED = (200,50,50)
BROWN = (139,69,19)
GRAY = (120,120,120)
PURPLE = (160,0,200)
ORANGE = (255,140,0)

font = pygame.font.SysFont("Arial",18,True)
big_font = pygame.font.SysFont("Arial",40,True)

# --- SUN ---
class Sun:
    def __init__(self,x=None,y=None):
        self.x = x if x else random.randint(OX,WIDTH-50)
        self.y = y if y else -50
        self.target = y if y else random.randint(OY+80,HEIGHT-50)
        self.rect = pygame.Rect(self.x,self.y,40,40)
        self.life = 300

    def update(self):
        if self.y < self.target:
            self.y += 2
        self.rect.y = self.y
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen,YELLOW,self.rect.center,18)
        pygame.draw.circle(screen,ORANGE,self.rect.center,18,3)

# --- BULLET ---
class Bullet:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x+50,y+25,8,8)

    def move(self): self.rect.x += 7

    def draw(self):
        pygame.draw.circle(screen,YELLOW,self.rect.center,5)

# --- PLANT BASE ---
class Plant:
    def __init__(self,x,y,hp):
        self.rect = pygame.Rect(x,y,60,60)
        self.hp = hp
        self.max_hp = hp
        self.timer = 0
        self.anim = random.random()*10

    def draw_hp(self):
        if self.hp < self.max_hp:
            pygame.draw.rect(screen,(0,255,255),
                (self.rect.x,self.rect.y-6,
                 (self.hp/self.max_hp)*60,5))

# --- PLANTS ---
class Shooter(Plant):
    def __init__(self,x,y): super().__init__(x,y,100)

    def update(self,bullets,suns):
        self.timer+=1
        if self.timer>=80:
            bullets.append(Bullet(self.rect.x,self.rect.y))
            self.timer=0

    def draw(self):
        self.anim += 0.1
        offset = int(3 * math.sin(self.anim))

        pygame.draw.circle(screen,(0,200,0),
            (self.rect.centerx, self.rect.centery + offset),25)
        pygame.draw.circle(screen,(0,100,0),
            (self.rect.centerx, self.rect.centery + offset),25,3)

        self.draw_hp()

class WallNut(Plant):
    def __init__(self,x,y): super().__init__(x,y,500)

    def update(self,b,s): pass

    def draw(self):
        self.anim += 0.05
        offset = int(2 * math.sin(self.anim))

        pygame.draw.ellipse(screen,BROWN,
            (self.rect.x, self.rect.y+offset,60,60))
        pygame.draw.ellipse(screen,(90,40,0),
            (self.rect.x, self.rect.y+offset,60,60),3)

        self.draw_hp()

class SunFlower(Plant):
    def __init__(self,x,y): super().__init__(x,y,80)

    def update(self,bullets,suns):
        self.timer+=1
        if self.timer>=350:
            suns.append(Sun(self.rect.centerx,self.rect.centery))
            self.timer=0

    def draw(self):
        self.anim += 0.1
        offset = int(4 * math.sin(self.anim))

        pygame.draw.circle(screen,YELLOW,
            (self.rect.centerx,self.rect.centery+offset),25)
        pygame.draw.circle(screen,ORANGE,
            (self.rect.centerx,self.rect.centery+offset),10)

        self.draw_hp()

class Bomb(Plant):
    def __init__(self,x,y):
        super().__init__(x,y,60)
        self.explode_radius = 0

    def update(self,bullets,suns):
        self.timer += 1
        if self.timer >= 120:
            self.explode_radius += 8

    def explode(self,zombies):
        for z in zombies[:]:
            if abs(z.rect.x - self.rect.x) < 120:
                z.hp -= 10

    def draw(self):
        if self.timer < 120:
            pygame.draw.circle(screen,RED,self.rect.center,25)
        else:
            pygame.draw.circle(screen,(255,200,0),
                self.rect.center,self.explode_radius,3)

        self.draw_hp()

# --- ZOMBIE ---
class Zombie:
    def __init__(self,speed,hp,color,size=50,bucket=False):
        self.x = WIDTH
        self.y = random.randint(1,5)*GRID + OY + 10
        self.rect = pygame.Rect(self.x,self.y,size,size)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.bucket = bucket
        self.anim = random.random()*10

    def move(self,plants):
        eating=False
        for p in plants:
            if self.rect.colliderect(p.rect):
                p.hp -= 0.4
                eating=True
                break

        if not eating:
            self.x -= self.speed
            self.rect.x = int(self.x)

        self.anim += 0.2

    def draw(self):
        offset = int(4 * math.sin(self.anim))

        pygame.draw.rect(screen,self.color,
            (self.rect.x,self.rect.y+offset,
             self.rect.w,self.rect.h),border_radius=6)

        if self.bucket:
            pygame.draw.rect(screen,GRAY,
                (self.rect.x+5,self.rect.y-15,40,20))

        pygame.draw.rect(screen,(0,255,0),
            (self.rect.x,self.rect.y-20,
             (self.hp/self.max_hp)*50,5))

# --- MENU ---
def menu():
    while True:
        screen.fill(DARK_GREEN)
        title = big_font.render("PVZ MINI",True,WHITE)
        screen.blit(title,(WIDTH//2-120,200))

        btn = pygame.Rect(WIDTH//2-100,300,200,60)
        pygame.draw.rect(screen,(0,200,0),btn,border_radius=10)
        screen.blit(font.render("START",True,WHITE),(btn.x+70,btn.y+20))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(pygame.mouse.get_pos()):
                    return

        pygame.display.flip()

# --- GAME ---
def game():
    plants=[]
    zombies=[]
    bullets=[]
    suns=[]

    total_sun=100
    selected="SHOOTER"

    # mower
    mowers=[]
    for row in range(5):
        y = (row+1)*GRID + OY + 10
        rect = pygame.Rect(OX-60,y,50,50)
        mowers.append({"rect":rect,"active":False})

    # cards
    cards = [
        {"type":"SHOOTER","cost":100,"color":(0,200,0)},
        {"type":"WALL","cost":50,"color":BROWN},
        {"type":"SUN","cost":50,"color":YELLOW},
        {"type":"BOMB","cost":125,"color":RED},
    ]

    start = pygame.time.get_ticks()

    while True:
        screen.fill(DARK_GREEN)

        # grid
        for r in range(1,6):
            for c in range(9):
                pygame.draw.rect(screen,GREEN,
                    (c*GRID+OX,r*GRID+OY,GRID,GRID),1)

        # cards UI
        for i,card in enumerate(cards):
            x = 20 + i*90
            y = 20
            rect = pygame.Rect(x,y,80,80)

            pygame.draw.rect(screen,(60,60,60),rect,border_radius=10)
            pygame.draw.circle(screen,card["color"],rect.center,25)

            txt = font.render(str(card["cost"]),True,WHITE)
            screen.blit(txt,(x+25,y+55))

            if selected == card["type"]:
                pygame.draw.rect(screen,(255,255,0),rect,3,border_radius=10)

            card["rect"]=rect

        # events
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); exit()

            if e.type==pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()

                for card in cards:
                    if card["rect"].collidepoint(mx,my):
                        selected = card["type"]

                for s in suns[:]:
                    if s.rect.collidepoint(mx,my):
                        total_sun+=25
                        suns.remove(s)

                if OX<mx<OX+GRID*9:
                    if OY+GRID<my<OY+GRID*6:
                        gx=((mx-OX)//GRID)*GRID+OX+10
                        gy=((my-OY)//GRID)*GRID+OY+10

                        if not any(p.rect.x==gx and p.rect.y==gy for p in plants):
                            if selected=="SHOOTER" and total_sun>=100:
                                plants.append(Shooter(gx,gy)); total_sun-=100
                            elif selected=="WALL" and total_sun>=50:
                                plants.append(WallNut(gx,gy)); total_sun-=50
                            elif selected=="SUN" and total_sun>=50:
                                plants.append(SunFlower(gx,gy)); total_sun-=50
                            elif selected=="BOMB" and total_sun>=125:
                                plants.append(Bomb(gx,gy)); total_sun-=125

        # spawn
        seconds=(pygame.time.get_ticks()-start)//1000
        spawn_rate = max(60,200 - (seconds//30)*20)

        if random.randint(1,spawn_rate)==1:
            r=random.random()
            if r<0.2:
                zombies.append(Zombie(0.3,20,(150,75,0),60,True))
            elif r<0.4:
                zombies.append(Zombie(1.5,3,PURPLE))
            else:
                zombies.append(Zombie(0.6,5,RED))

        if random.randint(1,250)==1:
            suns.append(Sun())

        # update
        for s in suns[:]:
            s.update(); s.draw()
            if s.life<=0: suns.remove(s)

        for p in plants[:]:
            if p.hp<=0:
                plants.remove(p)
                continue

            p.update(bullets,suns)

            if isinstance(p,Bomb) and p.timer>=120:
                p.explode(zombies)
                if p.explode_radius > 80:
                    plants.remove(p)
                    continue

            p.draw()

        for z in zombies[:]:
            z.move(plants)
            z.draw()
            if z.x < OX:
                return

        for b in bullets[:]:
            b.move(); b.draw()
            for z in zombies[:]:
                if b.rect.colliderect(z.rect):
                    z.hp-=1
                    pygame.draw.circle(screen,(255,255,255),z.rect.center,8,2)
                    if b in bullets: bullets.remove(b)
                    if z.hp<=0: zombies.remove(z)

        # mower
        for mower in mowers:
            row = (mower["rect"].y - OY) // GRID

            if mower["active"]:
                mower["rect"].x += 10
                shake = random.randint(-2,2)
                draw_rect = mower["rect"].copy()
                draw_rect.y += shake

                pygame.draw.rect(screen,(220,220,220),draw_rect, border_radius=5)

                for z in zombies[:]:
                    if abs(z.rect.y - mower["rect"].y) < 40:
                        if mower["rect"].colliderect(z.rect):
                            zombies.remove(z)
            else:
                pygame.draw.rect(screen,(180,180,180),mower["rect"], border_radius=5)
                for z in zombies:
                    z_row = (z.rect.y - OY) // GRID
                    if z_row == row and z.rect.x < OX:
                        mower["active"] = True

        screen.blit(font.render(f"SUN:{total_sun}",True,WHITE),(20,110))

        pygame.display.flip()
        clock.tick(60)

# RUN
while True:
    menu()
    game()