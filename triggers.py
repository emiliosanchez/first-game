import pygame


class Trigger(pygame.sprite.Sprite):

    def player_trigger(self, dt, level):
        pass

    def animate(self, dt, level):
        pass

    def update(self, dt, level):
        if level.enemycollide(self, level.player):
            self.player_trigger(dt, level)
        self.animate(dt, level)


class Box(Trigger):

    image = pygame.image.load('resources/sprites/box.png')

    def __init__(self, location, *groups):
        super(Box, self).__init__(*groups)
        size = self.image.get_size()
        y = location[1] + 70 - size[1]
        self.rect = pygame.rect.Rect((location[0], y), self.image.get_size())

    def player_trigger(self, dt, level):
        level.player.weapon = 1
        level.enemies.remove(self)


class Weapon(Trigger):

    sheet = pygame.image.load('resources/sprites/player_weapon.png')

    def __init__(self, location, *groups):
        super(Weapon, self).__init__(*groups)
        self.image = self.sheet.subsurface(184, 0, 38, 38)
        size = self.image.get_size()
        y = location[1] + 70 - size[1]
        self.rect = pygame.rect.Rect((location[0], y), self.image.get_size())

    def player_trigger(self, dt, level):
        level.player.weapon = 1
        level.enemies.remove(self)


class Goal(Trigger):
    sheet = pygame.image.load('resources/sprites/tent.png')

    def __init__(self, location, *groups):
        super(Goal, self).__init__(*groups)
        self.without_player = self.sheet.subsurface(0, 0, 138, 90)
        self.with_player = self.sheet.subsurface(0, 90, 138, 90)
        self.image = self.without_player
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.end = False
        self.wait = 0

    def animate(self, dt, level):
        if self.end:
            self.wait += dt
            if self.wait > 2:
                self.wait = 0
                self.end = False
                level.enemies.remove(self)
                level.start()

    def player_trigger(self, dt, level):
        self.image = self.with_player
        self.end = True
        level.sprites.remove(level.player)
