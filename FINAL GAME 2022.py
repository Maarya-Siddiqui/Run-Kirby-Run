# This game was written by Maarya Siddiqui on Jan 19th 2022
# This game is called Run Kirby Run! :)

import pygame, os, random, time
from pygame.locals import *

# set up window size
WINDOWWIDTH = 900
WINDOWHEIGHT = 700

# set up the colours
PINK = (255, 105, 180)

# set up the frame rate
FRAMERATE = 60

# Ground where Kirby runs
GROUND = 565

# Max background parameter
MAXBG = 8000

# the number of time before a new creature/powerup is added
NEWITEMS = 5

# the number of creatures when the game begins
INITIALITEMS = 2

def scrollLeft(anobject, speed):
    """This function allows an object to move left"""
    anobject.x_change = -speed

def scrollRight(anobject, speed):
    """This function allows an object to move right"""
    anobject.x_change = speed

def stop_scrolling(anobject):
    """This function stops an object from moving"""
    anobject.x_change = 0

def gravity(anobject, platforms):
    """This function implements gravity in the game"""
    # if the player is not jumping
    if anobject.y_change == 0:
        anobject.y_change = 1
    # if the player is jumping, implement gravity
    else:
        anobject.y_change += 0.35

    block_hit_list = pygame.sprite.spritecollide(anobject, platforms, False)
    for block in block_hit_list:
        # See if we are on the ground.
        if anobject.rect.y >= block.rect.top - anobject.rect.height and anobject.y_change >= 0:
            anobject.y_change = 0
            anobject.rect.y = block.rect.top - anobject.rect.height

def vertical_collisions(anobject, platforms):
    """This function checks for vertical collisions between an object
        and platforms"""
    # See if we hit anything in the vertical plane
    block_hit_list = pygame.sprite.spritecollide(anobject, platforms, False)
    for block in block_hit_list:
        # Reset our position based on the top/bottom of the object.
        if anobject.y_change > 0:
            anobject.rect.bottom = block.rect.top
        elif anobject.y_change < 0:
            anobject.rect.top = block.rect.bottom

        # Stop our vertical movement
        anobject.y_change = 0

def horizontal_collision(anobject, platforms):
    """This function checks for horizontal collision between an object
        and platforms"""
    # See if we hit anything in the horizontal plane
    block_hit_list = pygame.sprite.spritecollide(anobject, platforms, False)
    for block in block_hit_list:
        # If we are moving right,
        # set our right side to the left side of the item we hit
        if anobject.x_change > 0:
            anobject.rect.right = block.rect.left
        elif anobject.x_change < 0:
            # Otherwise if we are moving left, do the opposite.
            anobject.rect.left = block.rect.right
    
def terminate():
    """ This function is called when the user closes the window or presses ESC """
    pygame.quit()
    os._exit(1)

class Player(pygame.sprite.Sprite):
    """The player controlled by the user"""
    def __init__(self, image, lives, points):
        pygame.sprite.Sprite.__init__(self)

        # setting up the players image, lives and points
        self.original = image
        self.image = pygame.transform.scale(image,(90,80))
        self.rect = self.image.get_rect()
        self.lives = lives
        self.points = points

        # setting up the location of the player
        self.rect.x = 50
        self.rect.y = GROUND - self.rect.height

        # set up speed vector of the player
        self.x_change = 0
        self.y_change = 0
               
    def update(self, platforms):
        """This function allows the player to run, jump and duck"""
        gravity(self, platforms)

        # moving the player left and right
        self.rect.left += self.x_change

        # see if we hit anything in the horizontal plane
        horizontal_collision(self, platforms)

        # Move up/down
        self.rect.y += self.y_change

        # see if we hit anything in the vertical plane
        vertical_collisions(self, platforms)
            
    def jump(self, platforms):
        """This function allows the player to jump"""
        # move down a bit and see if there is a platform beneath us
        # move down 2 pixels, bc 1 doesn't work well
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 2
        # if it is okay to jump, set our speed upwards
        if len(platforms) > 0 or self.rect.bottom >= GROUND:
            self.y_change = -13

    def flip_head(self):
        """This function flips the players head depending on what direction the player moves"""
        self.image = pygame.transform.flip(self.image, True, False)
            
class Background(pygame.sprite.Sprite):
    """The background for the game"""
    def __init__(self, background_image):
        pygame.sprite.Sprite.__init__(self)

        # setting up the background image
        self.original = background_image
        self.image = pygame.transform.scale(background_image, (MAXBG, WINDOWHEIGHT))
        self.rect = self.image.get_rect()
        
        # set up speed vector of the background
        self.x_change = 0

    def update(self):
        # moving the background left and right
        self.rect.left += self.x_change

class Coin(pygame.sprite.Sprite):
    """The coins for the player to collect"""
    def __init__(self, coin_image):
        pygame.sprite.Sprite.__init__(self)
        
        self.original = coin_image
        self.image = pygame.transform.scale(coin_image,(50,50))
        self.rect = self.image.get_rect()

        # set the position to a random location
        self.rect.top = GROUND - self.rect.height
        self.rect.left = random.randrange(0, 6500 - self.rect.width)

        # set up speed vector of the coins
        self.x_change = 0
        self.y_change = 0

    def update(self):
        """This function allows the pipes and platforms to move along with the background"""
        # moving the coins left and right
        self.rect.left += self.x_change

class Obstacles(pygame.sprite.Sprite):
    """The platforms for the player to jump onto
        and the plants for player to collide with
        and the wall the player collides with to win the game"""
    def __init__(self, width, height, transparent_image):
        pygame.sprite.Sprite.__init__(self)
        
        self.original = transparent_image
        self.image = pygame.transform.scale(transparent_image,([width, height]))
        self.rect = self.image.get_rect()

        # set up speed vector of the barriers
        self.x_change = 0

    def update(self):
        """This function allows the pipes and platforms to move along with the background"""
        # moving the barriers left and right
        self.rect.left += self.x_change

class Creature(pygame.sprite.Sprite):
    """This class is for the evil creatures that can kill the player"""
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)

        self.original = image
        self.image = pygame.transform.scale(image, (50,50))
        self.rect = self.image.get_rect()

        # set the position to a location
        self.rect.y = random.randrange(0, GROUND - self.rect.height)
        self.rect.x = WINDOWWIDTH

        self.y_change = 0

    def update(self, platforms):
        """This function allows the player to run, jump and duck"""
        gravity(self, platforms)

        # moving the creature left and right
        self.rect.x -= 3

        # See if we hit anything in the horizontal plane
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            # left side of creature is right side of block
            self.rect.left = block.rect.right

        # Move down
        self.rect.y += self.y_change

        # see if we hit anything in the vertical plane
        vertical_collisions(self, platforms)

class Star(pygame.sprite.Sprite):
    """This class is for the evil creatures that can kill the player"""
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)

        self.original = image
        self.image = pygame.transform.scale(image, (60,50))
        self.rect = self.image.get_rect()

        # set the position to a location
        self.rect.y = random.randrange(0, 200)
        self.rect.x = WINDOWWIDTH

    def update(self):
        """This function allows the player to run, jump and duck"""

        # moving the star left
        self.rect.left -= 8
        
class Game():
    """ This class represents the instance of the game. Create a new instance of this
        class to reset the game."""
    
    def __init__(self):
        # Set to True when the lives are 0 or when the player reaches the finish line
        self.game_over = False

        # Set to True when the user wants to restart the game
        self.restart = False

        # controls when evil creatures are added
        self.add_item_time = time.time()

        # load the winning and losing screens
        self.winning_screen = load_image('winning_screen.png')
        self.losing_screen = load_image('gameover_screen.png')
        
        # set up the all_sprites group
        self.all_sprites = pygame.sprite.Group()

        # set up the background group
        self.background_group = pygame.sprite.Group()
        
        # add the background to the group
        background_image = load_image('Background_updated.png')
        self.background = Background(background_image)
        self.all_sprites.add(self.background)
        self.background_group.add(self.background)

        # set up the player group
        self.kirby = pygame.sprite.Group()

        # set up player lives
        lives = 5
        
        # add the player to the group
        player_image = load_image('pink_kirby.png')
        self.player = Player(player_image,lives, 0)
        self.all_sprites.add(self.player)
        self.kirby.add(self.player)

        # set up and add the star to a group
        self.powerup = pygame.sprite.Group()
        self.star_image = load_image('star.png')
        self.star = Star(self.star_image)
        self.all_sprites.add(self.star)
        self.powerup.add(self.star)
        
        # set up the platform group
        self.platform_list = pygame.sprite.Group()
        transparent_image = load_image('transparentimage.png')
        
        # List with width, height, x, and y of platforms
        platform_details = [[95, 90, 515, 475],
                            [145, 75, 645, 261],
                            [145,65,950,184],
                            [95,140,1040,456],
                            [85,260,1550,332],
                            [290,75,1995,255],
                            [115,100,2550,467],
                            [145,75,2740,132],
                            [65,210,2980,380],
                            [550,69,3300,210],
                            [85,93,3759,476],
                            [80,93,4225,480],
                            [73,240,4490,342],
                            [80,97,4810,472],
                            [220,55,5230,285],
                            [80,250,5705,340],
                            [80,80,6445,485],
                            [80,80,6530,393],
                            [80,80,6610,310],
                            [2055,100,0,565],
                            [865,100,2255,565],
                            [1260,100,3305,565],
                            [1170,100,4757,565],
                            [1800,100,6170,565]]
 
        # Go through the list above and add platforms to group
        for platform in platform_details:
            self.block = Obstacles(platform[0], platform[1], transparent_image)
            self.block.rect.x = platform[2]
            self.block.rect.y = platform[3]
            self.platform_list.add(self.block)
            self.all_sprites.add(self.block)

        # set up the poisonous plant group
        self.plants = pygame.sprite.Group()
        
        # List with width, height, x, and y of poisonous plants
        plant_details = [[45,130,1070,330],
                         [40,125,4240,365],
                         [45,120,5328,330]]

        # Go through the list above an add plants to group
        for p in plant_details:
            self.plant = Obstacles(p[0], p[1], transparent_image)
            self.plant.rect.x = p[2]
            self.plant.rect.y = p[3]
            self.plants.add(self.plant)
            self.all_sprites.add(self.plant)

        # set up coin group, load image and add coins to the group
        self.coin_list = pygame.sprite.Group()
        self.coin_image = load_image('coin.png')
        for x in range (30):
            self.coin = Coin(self.coin_image)
            self.coin_list.add(self.coin)
            self.all_sprites.add(self.coin)

        # set up the creature group and add creatures
        self.creatures = pygame.sprite.Group()
        self.creature_image = load_image('creature.png')
        for i in range(INITIALITEMS):
            self.acreature = Creature(self.creature_image)
            self.creatures.add(self.acreature)
            self.all_sprites.add(self.acreature)

        # create the winning block that determines if the player wins
        self.winning_signal = pygame.sprite.Group()
        winning_block = [[100,700,7380,200]]
        for w in winning_block:
            self.win_signal = Obstacles(w[0], w[1], transparent_image)
            self.win_signal.rect.x = w[2]
            self.win_signal.rect.y = w[3]
            self.winning_signal.add(self.win_signal)
            self.all_sprites.add(self.win_signal)

        # set up music
        self.pickUpSound = pygame.mixer.Sound('pickup.wav')
        self.losingSound = pygame.mixer.Sound('game_over(losing).wav')
        self.winningSound = pygame.mixer.Sound('game_over(winning).wav')
        self.jumpSound = pygame.mixer.Sound('jump.wav')
        self.levelUpSound = pygame.mixer.Sound('level_up.wav')
        self.poisonSound = pygame.mixer.Sound('plant_collision_sound.wav')
        pygame.mixer.music.load('background_music.mp3')
        pygame.mixer.music.play(-1,0.0)
        self.musicPlaying = True
        
    def process_events(self, windowSurface):
        """Process all of the keyboard and mouse events"""
        # if the event type is to exit the program
        for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    # the player is moving left
                    if event.key == K_LEFT:
                        scrollLeft(self.player, 10)
                        self.player.flip_head()
                        
                    # the player is moving right
                    elif event.key == K_RIGHT:
                        scrollRight(self.player, 10)
                        
                    # the player is jumping
                    elif event.key == K_UP:
                        for ablock in self.platform_list:
                            if self.player.rect.bottom == GROUND or self.player.rect.bottom == ablock.rect.top:
                                self.player.jump(self.platform_list)
                                if self.musicPlaying:
                                    self.jumpSound.play()
                                    
                    # the user clicks the spacebar in order to return back to restart the game
                    elif event.key == ord(' '):
                        if self.game_over:
                            self.restart = True
                    
                elif event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminate()
                        
                    # the player has stopped moving
                    elif event.key == K_LEFT and self.player.x_change < 0:
                        stop_scrolling(self.player)
                        
                    elif event.key == K_RIGHT and self.player.x_change > 0:
                        stop_scrolling(self.player)
                        self.player.flip_head()

                    elif event.key == ord('m'):
                        if self.musicPlaying:
                            pygame.mixer.music.stop()
                        else:
                            pygame.mixer.music.play(-1,0.0)
                        self.musicPlaying = not self.musicPlaying
                        

    def run_logic(self, windowSurface):
        """This function runs the logic of the game"""
        if not self.game_over:

            # Make sure the player doesn't move past the right side of the screen
            if self.player.rect.right > WINDOWWIDTH/2:
                self.player.rect.right = WINDOWWIDTH/2
     
            # Make sure the player doesn't move past the left side of the screen
            elif self.player.rect.left < 100:
                self.player.rect.left = 100

            # Make sure the player remains on the ground, otherwise the game is over
            if self.player.rect.bottom >= WINDOWHEIGHT:
                self.player.lives = 0

            # Scroll the background, platforms, enemies and coins
            for ablock in self.platform_list:
                for w in self.winning_signal:
                    for acoin in self.coin_list:
                        for aplant in self.plants:
                            # scroll everything right if the player moves left
                            if self.player.x_change < 0:
                                if self.player.rect.x >= WINDOWWIDTH/4:
                                    scrollRight(self.background, 5)
                                    scrollRight(ablock, 5)
                                    scrollRight(w, 5)
                                    scrollRight(acoin, 5)
                                    scrollRight(aplant, 5)

                            # scroll everything left if the player moves right
                            elif self.player.x_change > 0:
                                scrollLeft(self.background, 5)
                                scrollLeft(ablock, 5)
                                scrollLeft(w, 5)
                                scrollLeft(acoin, 5)
                                scrollLeft(aplant, 5)

                            # stop scrolling everything if the player stops moving
                            # also don't scroll if the player is in a certain screen range
                            elif self.player.rect.right < WINDOWWIDTH and self.player.rect.left > 0:
                                if self.player.x_change == 0:
                                    stop_scrolling(self.background)
                                    stop_scrolling(ablock)
                                    stop_scrolling(w)
                                    stop_scrolling(acoin)
                                    stop_scrolling(aplant)


            # check for collisions between coins and player and add points
            coin_hit_list = pygame.sprite.spritecollide(self.player, self.coin_list, True)
            for c in coin_hit_list:
                self.player.points += 1
                if self.musicPlaying:
                    self.pickUpSound.play()

            # Check for collisions between Kirby and powerups, add a life
            power_up_collected = pygame.sprite.spritecollide(self.player, self.powerup, True)
            if len(power_up_collected) > 0:
                self.player.lives += 1
                if self.musicPlaying:
                    self.levelUpSound.play()
                   
            # check for collisions between plants and player, instantly die
            plant_hit_list = pygame.sprite.spritecollide(self.player, self.plants, False)
            for p in plant_hit_list:
                self.player.lives = 0
                    
            # Add new creatures and powerups when the time is right
            end_item_time = time.time()
            if end_item_time - self.add_item_time >= NEWITEMS:
                self.add_item_time = time.time()
                acreature = Creature(self.creature_image)
                astar = Star(self.star_image)
                self.creatures.add(acreature)
                self.powerup.add(astar)
                self.all_sprites.add(acreature, astar)

            # Check for collisions between Kirby and creatures
            creature_hit_list = pygame.sprite.spritecollide(self.player, self.creatures, True)
            if len(creature_hit_list) > 0:
                self.player.lives -= 1
                if self.musicPlaying:
                    self.poisonSound.play()

            # check if the player collides with the winning block (player wins)
            did_player_win = pygame.sprite.spritecollide(self.player, self.winning_signal, True)
            if len(did_player_win) > 0:
                pygame.mixer.music.stop()
                if self.musicPlaying:
                    self.winningSound.play()
                    time.sleep(5)
                    self.musicPlaying = False
                self.game_over = True

            # check if the player loses (game over)
            if self.player.lives == 0 or self.player.rect.bottom == WINDOWHEIGHT:
                pygame.mixer.music.stop()
                self.game_over = True
                if self.musicPlaying:
                    self.losingSound.play()
                    self.musicPlaying = False
    
    def display_frame(self, windowSurface):
        """This function displays the images onto the screen and creates a scrolling background"""
        if self.game_over:
            # display the losing screen if the player loses
            if self.player.lives == 0:
                windowSurface.blit(self.losing_screen, (0,0))
            # display the winning screen if the player wins
            elif self.player.lives > 0:
                windowSurface.blit(self.winning_screen, (0,0))

        else:
            self.all_sprites.draw(windowSurface)
            basicFont = pygame.font.SysFont("Arial Black",40)
            displaylives = ["Lives: " + str(self.player.lives)]
            for i in range(len(displaylives)):
                drawText(displaylives[i], basicFont, windowSurface, 10,0, PINK)
            displaypoints = ["Points: " + str(self.player.points)]
            for x in range(len(displaypoints)):
                drawText(displaypoints[x], basicFont, windowSurface, 675,0, PINK)                

        # update the screen
        pygame.display.update()

    def update_sprites(self):
        """This function updates all the sprites in the game loop"""
        if not self.game_over:
            # update the player
            self.player.update(self.platform_list)

            # update the evil creaures
            self.creatures.update(self.platform_list)

            # update the power up (star)
            self.powerup.update()
            
            # update the background
            self.background.update()

            # update the pipes, platforms and winning block
            self.platform_list.update()
            self.winning_signal.update()

            # update the poisonous plants
            self.plants.update()

            # update the coins
            self.coin_list.update()
            
                    
def load_image(filename):
    """This function loads an image"""
    image = pygame.image.load(filename)
    image = image.convert_alpha()
    return image

def drawText(text, font, surface, x, y, textcolour):
    """ Draws the text on the surface at the location specified """
    textobj = font.render(text, 1, textcolour)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def display_menu(windowSurface):
    """This function blits the opening screen image onto the windowSurface"""
    opening_image = load_image('opening_screen.png')
    windowSurface.blit(opening_image, (0,0))
    pygame.display.update()

def user_input(image, windowSurface):
    """Checking for user input for the control/credit screen"""
    windowSurface.blit(image, (0,0))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == ord('X'):
                    terminate()
                elif event.key == ord(' '):
                    return False
    
def menu_input(windowSurface):
    """Checking for user input, mousebuttondown"""
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONUP:
                if event.pos[0] >= 675 and event.pos[1] >= 475 and event.pos[0] <= 885 and event.pos[1] <= 535:
                    response = True
                    return response
                elif event.pos[0] >= 500 and event.pos[1] >= 550 and event.pos[0] <= 900 and event.pos[1] <= 610:
                    controls_image = load_image('controls_image.png')
                    response = user_input(controls_image, windowSurface)
                    return response
                elif event.pos[0] >= 650 and event.pos[1] >= 617 and event.pos[0] <= 885 and event.pos[1] <= 674:
                    credits_image = load_image('credits-game.png')
                    response = user_input(credits_image, windowSurface)
                    return response
            elif event.type == KEYDOWN:
                if event.key == ord('X'):
                    terminate()
def main():
    """The mainline for the game"""
    # set up pygame
    pygame.init()
    mainClock = pygame.time.Clock()

    # set up the windowSurface
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),0,32)
    pygame.display.set_caption('Run Kirby Run!')

    while True:
        start_game = False
        while not start_game:
            # display the menu screen and get user input
            display_menu(windowSurface)
            start_game = menu_input(windowSurface)
        
        # instantiate a game
        game = Game()

        # run the game loop until the user quits
        while not game.restart:
           # check for the QUIT event
           game.process_events(windowSurface)

           # update the sprites in the game
           game.update_sprites()

           # run logic
           game.run_logic(windowSurface)

           # draw the current frame
           game.display_frame(windowSurface)

           # keep the clock going
           mainClock.tick(FRAMERATE)

main()


