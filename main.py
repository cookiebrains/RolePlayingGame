import pygame
from pygame.locals import *
import sys
import random
import time
from tkinter import filedialog
from tkinter import *

pygame.init()

vec = pygame.math.Vector2
HEIGHT = 350
WIDTH = 700
ACC = 0.3
FRIC = -0.10
FPS = 60
FPS_CLOCK = pygame.time.Clock()
COUNT = 0

display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

run_ani_R = [pygame.image.load("Player_Sprite_R.png"), pygame.image.load("Player_Sprite2_R.png"),
             pygame.image.load("Player_Sprite3_R.png"), pygame.image.load("Player_Sprite4_R.png"),
             pygame.image.load("Player_Sprite5_R.png"), pygame.image.load("Player_Sprite6_R.png"),
             pygame.image.load("Player_Sprite_R.png")]

run_ani_L = [pygame.image.load("Player_Sprite_L.png"), pygame.image.load("Player_Sprite2_L.png"),
             pygame.image.load("Player_Sprite3_L.png"), pygame.image.load("Player_Sprite4_L.png"),
             pygame.image.load("Player_Sprite5_L.png"), pygame.image.load("Player_Sprite6_L.png"),
             pygame.image.load("Player_Sprite_L.png")]

# Attack animation for the RIGHT
attack_ani_R = [pygame.image.load("Player_Sprite_R.png"), pygame.image.load("Player_Attack_R.png"),
                pygame.image.load("Player_Attack2_R.png"), pygame.image.load("Player_Attack2_R.png"),
                pygame.image.load("Player_Attack3_R.png"), pygame.image.load("Player_Attack3_R.png"),
                pygame.image.load("Player_Attack4_R.png"), pygame.image.load("Player_Attack4_R.png"),
                pygame.image.load("Player_Attack5_R.png"), pygame.image.load("Player_Attack5_R.png"),
                pygame.image.load("Player_Sprite_R.png")]

# Attack animation for the LEFT
attack_ani_L = [pygame.image.load("Player_Sprite_L.png"), pygame.image.load("Player_Attack_L.png"),
                pygame.image.load("Player_Attack2_L.png"), pygame.image.load("Player_Attack2_L.png"),
                pygame.image.load("Player_Attack3_L.png"), pygame.image.load("Player_Attack3_L.png"),
                pygame.image.load("Player_Attack4_L.png"), pygame.image.load("Player_Attack4_L.png"),
                pygame.image.load("Player_Attack5_L.png"), pygame.image.load("Player_Attack5_L.png"),
                pygame.image.load("Player_Sprite_L.png")]


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgimage = pygame.image.load("Background.png")
        self.bgY = 0
        self.bgX = 0

    def render(self):
        display_surface.blit(self.bgimage, (self.bgX, self.bgY))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Ground.png")
        self.rect = self.image.get_rect(center=(350, 350))

    def render(self):
        display_surface.blit(self.image, (self.rect.x, self.rect.y))


class Castle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hide = False
        self.image = pygame.image.load("castle.png")

    def update(self):
        if not self.hide:
            display_surface.blit(self.image, (400, 80))


class EventHandler:
    def __init__(self):
        self.enemy_count = 0
        self.battle = False
        self.enemy_generation = pygame.USEREVENT + 1
        self.stage = 1

        self.stage_enemies = []
        for x in range(1, 21):
            self.stage_enemies.append(int((x ** 2 / 2) + 1))

    def stage_handler(self):
        # Code for the Tkinter stage selection window
        self.root = Tk()
        self.root.geometry('200x170')

        button1 = Button(self.root, text="Twilight Dungeon", width=18, height=2,
                         command=self.world1)
        button2 = Button(self.root, text="Skyward Dungeon", width=18, height=2,
                         command=self.world2)
        button3 = Button(self.root, text="Hell Dungeon", width=18, height=2,
                         command=self.world3)

        button1.place(x=40, y=15)
        button2.place(x=40, y=65)
        button3.place(x=40, y=115)

        self.root.mainloop()

    def world1(self):
        self.root.destroy()
        pygame.time.set_timer(self.enemy_generation, 2000)
        castle.hide = True
        self.battle = True

    def world2(self):
        self.battle = True

    def world3(self):
        self.battle = True

    def next_stage(self):  # Code for when the next stage is clicked
        self.stage += 1
        print("Stage: " + str(self.stage))
        self.enemy_count = 0
        pygame.time.set_timer(self.enemy_generation, 1500 - (50 * self.stage))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player_Sprite_R.png")
        self.rect = self.image.get_rect()

        # Position and direction
        self.vx = 0
        self.pos = vec((340, 240))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.jumping = False
        self.running = False
        self.move_frame = 0
        self.attacking = False
        self.cooldown = False
        self.attack_frame = 0

    def move(self):
        # Keep a constant acceleration of 0.5 in the downwards direction (gravity)
        self.acc = vec(0, 0.5)

        # Sets running to False if the player has slowed down to a certain extent
        if abs(self.vel.x) > 0.3:
            self.running = True
        else:
            self.running = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # This causes character warping from one point of the screen to the other
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos  # Update rect with new pos

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(player, ground_group, False)
        if self.vel.y > 0:
            if hits:
                lowest = hits[0]
                if self.pos.y < lowest.rect.bottom:
                    self.pos.y = lowest.rect.top + 1
                    self.vel.y = 0
                    self.jumping = False

    def update(self):
        if self.move_frame > 6:
            self.move_frame = 0
            return

        if self.jumping == False and self.running == True:
            if self.vel.x > 0:
                self.image = run_ani_R[self.move_frame]
                self.direction = "RIGHT"
            elif self.vel.x < 0:
                self.image = run_ani_L[self.move_frame]
                self.direction = "LEFT"
            self.move_frame += 1

        if abs(self.vel.x) < 0.2 and self.move_frame != 0:
            self.move_frame = 0
            if self.direction == "RIGHT":
                self.image = run_ani_R[self.move_frame]
            elif self.direction == "LEFT":
                self.image = run_ani_L[self.move_frame]

    def attack(self):
        # If attack frame has reached end of sequence, return to base frame
        if self.attack_frame > 10:
            self.attack_frame = 0
            self.attacking = False

        # Check direction for correct animation to display
        if self.direction == "RIGHT":
            self.image = attack_ani_R[self.attack_frame]
        elif self.direction == "LEFT":
            self.correction()
            self.image = attack_ani_L[self.attack_frame]

            # Update the current attack frame
        self.attack_frame += 1

    def jump(self):
        self.rect.x += 1

        # Check to see if payer is in contact with the ground
        hits = pygame.sprite.spritecollide(self, ground_group, False)

        self.rect.x -= 1

        # If touching the ground, and not currently jumping, cause the player to jump.
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12

    def correction(self):
        # Function is used to correct an error
        # with character position on left attack frames
        if self.attack_frame == 1:
            self.pos.x -= 20
        if self.attack_frame == 10:
            self.pos.x += 20

    def player_hit(self):
        if self.cooldown == False:
            self.cooldown = True  # Enable the cooldown
            pygame.time.set_timer(hit_cooldown, 1000)  # Resets cooldown in 1 second

            print("hit")
            pygame.display.update()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.direction = random.randint(0, 1)  # 0 for Right, 1 for Left
        self.vel.x = random.randint(2, 6) / 2  # Randomized velocity of the generated enemy
        self.pos.x = 0
        self.pos.y = 235

        if self.direction == 0:
            self.pos.x = 0
            self.pos.y = 235
        if self.direction == 1:
            self.pos.x = 700
            self.pos.y = 235

    def move(self):
        # Causes the enemy to change directions upon reaching the end of screen
        if self.pos.x >= (WIDTH - 20):
            self.direction = 1
        elif self.pos.x <= 0:
            self.direction = 0
        if self.direction == 0:
            self.pos.x += self.vel.x
        if self.direction == 1:
            self.pos.x -= self.vel.x

        self.rect.center = self.pos  # Updates rect

    def render(self):
        # Displayed the enemy on screen
        display_surface.blit(self.image, (self.pos.x, self.pos.y))

    def update(self):
        # Checks for collision with the Player
        hits = pygame.sprite.spritecollide(self, Playergroup, False)

        # Activates upon either of the two expressions being true
        if hits and player.attacking == True:
            self.kill()
            print("Enemy killed")

        # If collision has occured and player not attacking, call "hit" function
        elif hits and player.attacking == False:
            player.player_hit()


Enemies = pygame.sprite.Group()

player = Player()
Playergroup = pygame.sprite.Group()
Playergroup.add(player)

background = Background()

ground = Ground()
ground_group = pygame.sprite.Group()
ground_group.add(ground)

castle = Castle()
handler = EventHandler()
# health = HealthBar()

hit_cooldown = pygame.USEREVENT + 1

while True:
    player.gravity_check()

    for event in pygame.event.get():
        if event.type == hit_cooldown:
            player.cooldown = False
        # Will run when the close window button is clicked
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == handler.enemy_generation:
            if handler.enemy_count < handler.stage_enemies[handler.stage - 1]:
                # print(handler.enemy_count)
                # print(handler.stage_enemies[handler.stage - 1])
                enemy = Enemy()
                Enemies.add(enemy)
                handler.enemy_count += 1

                # For events that occur upon clicking the mouse (left click)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass

        # Event handling for a range of different key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                if handler.battle == True and len(Enemies) == 0:
                    handler.next_stage()
            if event.key == pygame.K_e and 450 < player.rect.x < 550:
                handler.stage_handler()
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_RETURN:
                if player.attacking == False:
                    player.attack()
                    player.attacking = True

    background.render()
    ground.render()

    for entity in Enemies:
        entity.update()
        entity.move()
        entity.render()

    castle.update()
    player.update()
    if player.attacking:
        player.attack()
    player.move()
    display_surface.blit(player.image, player.rect)

    pygame.display.update()
    FPS_CLOCK.tick(FPS)
