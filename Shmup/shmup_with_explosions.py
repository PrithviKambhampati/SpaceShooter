#Shmup
# attribute instructions for railjet music http://www.nosoapradio.us
#art from kenney.nl

import pygame
import random
import os
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 480
HEIGHT = 600
FPS = 60

#define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#set up assets(art and sound)
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")


pygame.init() #initializing pygame
pygame.mixer.init() #for the sound
screen = pygame.display.set_mode((WIDTH, HEIGHT)) #create window
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial') #python finds a font in the computer closest to the name given
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size) #creating font
    text_surface = font.render(text, True, WHITE) #text is aliased(one color) or anti-aliased(shades of a color for smoothness)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect) #blit the text surface at the location of the text rectangle

def new_mob():
    m = Mob() #spawn a Mob
    all_sprites.add(m) #add to all sprites
    mobs.add(m) #add to mobs groupcollide

def draw_shield_bar(surface, x, y, percentage):
    if percentage < 0:
        percentage = 0
    BAR_LENGTH = 40
    BAR_HEIGHT = 10
    fill = (percentage/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2) #2 is the thickness of the outline, if not mentioned it fills the whole rectangle

class Player(pygame.sprite.Sprite):
    #sprite for the Player
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #for the sprite to work
        self.image = pygame.transform.scale(player_img, (50, 38)) #making the graphic smaller(scaling)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 21
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250 #ms
        self.last_shot = pygame.time.get_ticks()
    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -10
        if keystate[pygame.K_RIGHT]:
            self.speedx = 10
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image_orig = pygame.transform.scale(meteor_img, (33,28))
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*(0.4)) #or use a number (eg. 14)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1,8)
        self.speedx = random.randrange(-3,3)
        self.rot = 0 #how far in degrees the sprite should be rotated
        self.rot_speed = random.randrange(-10,10) #how fast is it rotated
        self.last_update = pygame.time.get_ticks() #time last updated
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50: #milli seconds
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360 #self.rot it the total rotation, self.rot_speedis the angle by which it is rotated
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.right > WIDTH + 20 or self.rect.left < -20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1,8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (5,30))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    def update(self):
        self.rect.y += self.speedy
        #kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size): #explosion at the center of the meteor and small or large explosion
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 #keep track of frame, we start at frame 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50 #how fast the animation changes
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_animation[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center



#load game graphics
background = pygame.image.load(path.join(img_dir, "background.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_blue.png")).convert()
meteor_img = pygame.image.load(path.join(img_dir, "meteorGrey_big1.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "laserBlue01.png")).convert()
meteor_images = []
meteor_list = ['meteorGrey_big2.png', 'meteorGrey_big2.png', 'meteorGrey_big3.png',
                'meteorGrey_big4.png', 'meteorGrey_med1.png', 'meteorGrey_med2.png',
                'meteorGrey_small1.png', 'meteorGrey_small2.png', 'meteorGrey_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())
#explosion list
explosion_animation = {}
explosion_animation['large'] = []
explosion_animation['small'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_large = pygame.transform.scale(img, (75,75))
    explosion_animation['large'].append(img_large)
    img_small = pygame.transform.scale(img, (32,32))
    explosion_animation['small'].append(img_small)
#load game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "Shoot.wav"))
shoot_sound.set_volume(0.5)
explosion_sounds = []
for snd in ['Explosion1.wav', 'Explosion2.wav']:
    explosion_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
for explosion_sound in explosion_sounds:
    explosion_sound.set_volume(0.4)
pygame.mixer.music.load(path.join(snd_dir, 'DST-RailJet-LongSeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.3) #reducing the volume by half

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    new_mob()

score = 0
pygame.mixer.music.play(loops = -1) #loop it everytime it reaches the end
#Game loop
running = True
while running:
    #keep loop running at the right speed
    clock.tick(FPS) #makes sure the loop pauses if it finishes before 1/30 second
    #if the loop takes more than 1/30 seconds, it leads to lag
    #Process input
    for event in pygame.event.get():
        #check for closing the window
        if event.type == pygame.QUIT:
            running = False
        """elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()"""   #this is to shoot bullets when hit space. it has been modified in the shoot func so that holding space will shoot continuously

    #update
    all_sprites.update()

    #check to see if bullet hit mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True) #first true:mobs ar deleted if they get hit, second true: bullets also get deleted
    for hit in hits:
        score += 50 - hit.radius
        random.choice(explosion_sounds).play()
        expl = Explosion(hit.rect.center, 'large')
        all_sprites.add(expl)
        new_mob()

    #check to see if a mob hit the Player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle) #true-meteors disappear when they hit us but we don't, false-game ends
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'small')
        all_sprites.add(expl)
        new_mob()
        if player.shield <= 0:
            running = False


    #render(draw)
    screen.fill(BLACK)
    screen.blit(background, background_rect) #copy pixels of first thing onto the second
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    pygame.display.flip() #after drawing everything flip the display after drawing everything

pygame.quit()
