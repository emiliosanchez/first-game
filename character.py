import pygame

from base import HorizontalMovable
from config import LEFT, RIGHT


class Enemy(HorizontalMovable):
    sheet = pygame.image.load('resources/sprites/dino.png')

    def init_horizontal_images(self):
        for i in range(5):
            image = self.sheet.subsurface(48 * i, 0, 48, 43)
            self.horizontal[LEFT].append(image)
            self.horizontal[RIGHT].append(pygame.transform.flip(image, True, False))

    def pre_update(self, dt, level):
        self.rect.x += self.direction * 100 * dt
        self.cycletime += dt
        for cell in level.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            return

    def player_trigger(self, dt, level):
        level.player.is_dead = True


class FlyEnemy(Enemy):
    sheet = pygame.image.load('resources/sprites/fly.png')

    def init_horizontal_images(self):
        image = self.sheet.subsurface(0, 0, 60, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(60, 0, 60, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(120, 0, 64, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(184, 0, 65, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(249, 0, 63, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(pygame.transform.flip(image, True, False))
