### Space Shooter - Game Objects ###

### Importing Packets
import pygame
import os
import random

### Defining Classes
class Player(pygame.sprite.Sprite):

    MAXVEL = 4
    SHOOTCOOLDOWN = 30
    AFTERDEATHINVINCIBILITY = 600
    MAXLIVES = 5

    def __init__(self, x, y):
        ### Pygame Sprite
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites","player.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])
        self.images.append(img)
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites","blank.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])
        self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        ### Defining Variables
        self.__pos = pygame.math.Vector2(x, y)
        self.__vel = pygame.math.Vector2(0, 0)
        self.__shooting = False
        self.__shootCooldown = 0
        self.__afterDeathInvincibility = 0
        self.score = 0
        self.lives = 5
    
    def update(self, spritesList):
        ### Updating the players info
        self.__pos += self.__vel
        if self.__pos.x > Game.WIDTH:
            self.__pos.x += -Game.WIDTH
        if self.__pos.x < 0:
            self.__pos.x += Game.WIDTH
        if self.__pos.y <= 16:
            self.__pos.y = 16
        if self.__pos.y >= Game.HEIGHT - 16:
            self.__pos.y = Game.HEIGHT - 16
        if self.__shootCooldown > 0:
            self.__shootCooldown += -1
        if self.__afterDeathInvincibility > 0:
            self.__afterDeathInvincibility += -1
        if self.__shootCooldown == 0 and self.__shooting:
            self.__shootCooldown = Player.SHOOTCOOLDOWN
            spritesList.add(PlayerBullet(self.__pos.x - 6, self.__pos.y + 6))
            spritesList.add(PlayerBullet(self.__pos.x + 6, self.__pos.y + 6))
        
        ### Checking if the Player should lose a life
        if self.__afterDeathInvincibility == 0:
            self.image = self.images[0]
            for sprite in spritesList:
                if isinstance(sprite, EnemyBullet):
                    if self.rect.colliderect(sprite.rect):
                        spritesList.remove(sprite)
                        self.lives += -1
                        self.__afterDeathInvincibility = Player.SHOOTCOOLDOWN
                        break
        elif self.__afterDeathInvincibility % 50 == 0:
            if self.image == self.images[0]:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
        
        ### If the player gains score for getting more lives than they should
        if self.lives > Player.MAXLIVES:
            self.lives = Player.MAXLIVES
            self.score += 200

        ### Updating the players image
        self.rect.center = self.__pos

    def handleInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == ord("a"):
                self.__vel.x = -Player.MAXVEL
            if event.key == ord("d"):
                self.__vel.x = Player.MAXVEL
            if event.key == ord("w"):
                self.__vel.y = -Player.MAXVEL
            if event.key == ord("s"):
                self.__vel.y = Player.MAXVEL
            if event.key == ord(" "):
                self.__shooting = True

        if event.type == pygame.KEYUP:
            if event.key == ord("a") and self.__vel.x == -Player.MAXVEL:
                self.__vel.x = 0
            if event.key == ord("d") and self.__vel.x == Player.MAXVEL:
                self.__vel.x = 0
            if event.key == ord("w") and self.__vel.y == -Player.MAXVEL:
                self.__vel.y = 0
            if event.key == ord("s") and self.__vel.y == Player.MAXVEL:
                self.__vel.y = 0
            if event.key == ord(" "):
                self.__shooting = False

    @property
    def getPos(self):
        return pos[0], pos[1]

class Enemy(pygame.sprite.Sprite):

    MAXVEL = 1
    SHOOTCOOLDOWN = 90

    def __init__(self, x, y, direction):
        ### Pygame Sprite
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites","enemy.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])
        self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        ### Defining Variables
        self.__pos = pygame.math.Vector2(x, y)
        self.__vel = pygame.math.Vector2(Enemy.MAXVEL*direction, 0.25)
        self.__shooting = True
        self.__shootCooldown = Enemy.SHOOTCOOLDOWN
        self.__destroyed = False
    
    def update(self, spritesList):
        ### Updating the players info
        self.__pos += self.__vel
        if self.__pos.x > Game.WIDTH - 100:
            self.__vel.x = -Enemy.MAXVEL
        if self.__pos.x < 100:
            self.__vel.x = Enemy.MAXVEL
        self.__pos += self.__vel
        if self.__shootCooldown > 0:
            self.__shootCooldown += -1
        if self.__shootCooldown == 0 and self.__shooting:
            self.__shootCooldown = Enemy.SHOOTCOOLDOWN
            spritesList.add(EnemyBullet(self.__pos.x - 6, self.__pos.y + 6))
            spritesList.add(EnemyBullet(self.__pos.x + 6, self.__pos.y + 6))

        ### Updating the players image
        self.rect.center = self.__pos

        ### Checking if the Enemy should be destroyed
        for sprite in spritesList:
            if isinstance(sprite, PlayerBullet):
                if self.rect.colliderect(sprite.rect):
                    spritesList.remove(sprite)
                    spritesList.remove(self)
                    self.__destroyed = True
                    if random.randint(0, 5) == 0:
                        spritesList.add(HealPickup(self.__pos.x, self.__pos.y))
                    break
        
        if self.__destroyed:
            for sprite in spritesList:
                if isinstance(sprite, Player):
                    sprite.score += 50

        if self.__pos.y > Game.HEIGHT + 32:
            for sprite in spritesList:
                if isinstance(sprite, Player):
                    sprite.score += -50
            spritesList.remove(self)

class Game():

    ### Defining Constants
    FPS = 60
    SIZE = WIDTH, HEIGHT = 800, 640

    def __init__(self):
        ### Initialising the pygame
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Space Shooter")
        self.__screen = pygame.display.set_mode(Game.SIZE)
        self.__FPSClock = pygame.time.Clock()
        self.__spritesList = pygame.sprite.Group()
        self.__font = pygame.font.SysFont('Arial', 20)
        
        ### Initialising Game Data
        self.__ended = False
        self.__player = Player(Game.WIDTH // 2, Game.HEIGHT - 80)
        self.__spritesList.add(self.__player)
    
    def run(self):
        while not self.__ended:
            ### Wipe the screen
            self.__screen.fill([0, 0, 0])
            
            ### Go though events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                else:
                    self.__player.handleInput(event)
            
            ### Creating stars
            if random.randint(0,20) == 0:
                self.__spritesList.add(Star(random.randint(0, Game.WIDTH)))
            if self.__countEnemies() == 0:
                self.__spawnEnemies()
            
            ### Drawing Sprites
            for sprite in self.__spritesList:
                sprite.update(self.__spritesList)
            self.__spritesList.draw(self.__screen)

            self.__screen.blit(self.__font.render("Lives: ", False, [255, 255, 255]), [5, 5])
            for lifeNum in range(self.__player.lives):
                lifeImage = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites","player.png")).convert()
                lifeImage.convert_alpha()
                lifeImage.set_colorkey([0, 255, 0])
                self.__screen.blit(lifeImage, [60 + 32*lifeNum, 5])
            self.__screen.blit(self.__font.render(f"Score: {self.__player.score}", False, [255, 255, 255]), [5, 32])

            pygame.display.flip()

            if self.__player.lives == 0:
                self.__ended = True

            ### Moving the FPS clock on
            self.__FPSClock.tick(Game.FPS)
        
        ### Game over screen
        while True:
            ### Go though events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()

            ### Wipe the screen
            self.__screen.fill([0, 0, 0])

            ### Writing Text
            textSprite = pygame.font.SysFont('Arial', 70).render("Game Over!", False, [255, 255, 255])
            textRect = textSprite.get_rect()
            textRect.center = [Game.WIDTH//2, Game.HEIGHT//2]
            self.__screen.blit(textSprite, textRect)
            textSprite = self.__font.render(f"Score: {self.__player.score}", False, [255, 255, 255])
            textRect = textSprite.get_rect()
            textRect.center = [Game.WIDTH//2, Game.HEIGHT//2 + 100]
            self.__screen.blit(textSprite, textRect)

            pygame.display.flip()

            ### Moving the FPS clock on
            self.__FPSClock.tick(Game.FPS)
        
        pygame.quit()
    
    def __countEnemies(self):
        numEnemies = 0
        for sprite in self.__spritesList:
            if isinstance(sprite, Enemy):
                numEnemies += 1
        return numEnemies
    
    def __spawnEnemies(self):
        wave = random.randint(0, 5)
        if wave == 0:
            self.__spritesList.add(Enemy(100, -32, 1))
            self.__spritesList.add(Enemy(150, -32, 1))
            self.__spritesList.add(Enemy(200, -32, 1))
            self.__spritesList.add(Enemy(Game.WIDTH - 100, -32, -1))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -32, -1))
            self.__spritesList.add(Enemy(Game.WIDTH - 200, -32, -1))
        elif wave == 1:
            self.__spritesList.add(Enemy(150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 - 50, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 + 50, -32, 0))
        elif wave == 2:
            self.__spritesList.add(Enemy(150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 - 50, -32, 1))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 + 50, -32, -1))
        elif wave == 3:
            self.__spritesList.add(Enemy(100, -32, 1))
            self.__spritesList.add(Enemy(150, -32, 1))
            self.__spritesList.add(Enemy(200, -32, 1))
            self.__spritesList.add(Enemy(Game.WIDTH - 100, -32, -1))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -32, -1))
            self.__spritesList.add(Enemy(Game.WIDTH - 200, -32, -1))
            self.__spritesList.add(Enemy(100, -64, 1))
            self.__spritesList.add(Enemy(150, -64, 1))
            self.__spritesList.add(Enemy(200, -64, 1))
            self.__spritesList.add(Enemy(Game.WIDTH - 100, -64, -1))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -64, -1))
            self.__spritesList.add(Enemy(Game.WIDTH - 200, -64, -1))
        elif wave == 4:
            self.__spritesList.add(Enemy(150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 - 50, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 + 50, -32, 0))
            self.__spritesList.add(Enemy(150, -64, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 - 50, -64, 0))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -64, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 + 50, -64, 0))
        elif wave == 5:
            self.__spritesList.add(Enemy(150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 - 50, -32, 1))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -32, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 + 50, -32, -1))
            self.__spritesList.add(Enemy(150, -64, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 - 50, -64, 1))
            self.__spritesList.add(Enemy(Game.WIDTH - 150, -64, 0))
            self.__spritesList.add(Enemy(Game.WIDTH//2 + 50, -64, -1))

class Star(pygame.sprite.Sprite):
    def __init__(self, x):
        ### Pygame Sprite
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites",f"star{random.randint(0,8)}.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])
        self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        ### Defining Variables
        self.__pos = pygame.math.Vector2(x, -32)
        self.__vel = pygame.math.Vector2(0, 6)
    
    def update(self, spritesList):
        ### Updating the players info
        self.__pos += self.__vel

        ### Updating the players image
        self.rect.center = self.__pos

        if self.__pos.y >= Game.HEIGHT + 32:
            spritesList.remove(self)

class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        ### Pygame Sprite
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        ### Defining Variables
        self.__pos = pygame.math.Vector2(x, y)
        self.__vel = pygame.math.Vector2(0, 2)
    
    def update(self, spritesList):
        ### Updating the players info
        self.__pos += self.__vel

        ### Updating the players image
        self.rect.center = self.__pos

        for sprite in spritesList:
            if isinstance(sprite, Player):
                if self.rect.colliderect(sprite.rect):
                    self.activate(sprite)
                    spritesList.remove(self)
                    break

        if self.__pos.y >= Game.HEIGHT + 32:
            spritesList.remove(self)
    
    def activate(self, player):
        pass

class HealPickup(Pickup):
    def __init__(self, x, y):
        ### Getting the sprites image
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites",f"healPickup.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])

        ### Running the parent classes constructor method
        super().__init__(x, y, img)
    
    def activate(self, player):
        player.lives += 1

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        ### Pygame Sprite
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites",f"playerBullet.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])
        self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        ### Defining Variables
        self.__pos = pygame.math.Vector2(x, y)
        self.__vel = pygame.math.Vector2(0, -12)
    
    def update(self, spritesList):
        ### Updating the players info
        self.__pos += self.__vel

        ### Updating the players image
        self.rect.center = self.__pos

        if self.__pos.y < -32:
            spritesList.remove(self)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        ### Pygame Sprite
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        img = pygame.image.load(os.path.join(os.path.dirname(__file__),"Sprites",f"enemyBullet.png")).convert()
        img.convert_alpha()
        img.set_colorkey([0, 255, 0])
        self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        ### Defining Variables
        self.__pos = pygame.math.Vector2(x, y)
        self.__vel = pygame.math.Vector2(0, 12)
    
    def update(self, spritesList):
        ### Updating the players info
        self.__pos += self.__vel

        ### Updating the players image
        self.rect.center = self.__pos

        if self.__pos.y > Game.HEIGHT + 32:
            spritesList.remove(self)

### Name Guard
if __name__ == "__main__":
    pass
