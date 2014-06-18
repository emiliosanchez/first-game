import pygame
from base import StaticItem


class Box(StaticItem):

    image = pygame.image.load('resources/sprites/box.png')
    blockers = 'tlrb'

    def player_trigger(self, dt, level):
        if level.player.weapon and level.player.stabbing:
            level.player.weapon = 0
            for group in self.groups():
                group.remove(self)


class Weapon(StaticItem):

    sheet = pygame.image.load('resources/sprites/player_weapon.png')

    def get_image(self):
        return self.sheet.subsurface(184, 0, 38, 38)

    def player_trigger(self, dt, level):
        level.player.weapon = 1
        for group in self.groups():
            group.remove(self)


class Goal(StaticItem):
    sheet = pygame.image.load('resources/sprites/tent.png')

    def get_image(self):
        return self.without_player

    def __init__(self, location, *groups):
        self.without_player = self.sheet.subsurface(0, 0, 138, 90)
        self.with_player = self.sheet.subsurface(0, 90, 138, 90)
        super(Goal, self).__init__((location[0], location[1] + 4), *groups)
        self.end = False
        self.wait = 0

    def post_update(self, dt, level):
        if self.end:
            self.wait += dt
            if self.wait > 2:
                level.game.next_level()

    def player_trigger(self, dt, level):
        self.image = self.with_player
        self.end = True
        for group in self.groups():
            group.remove(self)
