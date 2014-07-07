import pygame

from base import HorizontalMovable
from config import LEFT, RIGHT, BASE_ANIMATION_LAG


class Enemy(HorizontalMovable):
    sheet = pygame.image.load('resources/sprites/dino.png')
    speed = 350
    animation_lag = 0.08

    def init_horizontal_images(self):
        for i in range(5):
            image = self.sheet.subsurface(48 * i, 0, 48, 43)
            self.horizontal[LEFT].append(image)
            self.horizontal[RIGHT].append(
                pygame.transform.flip(image, True, False))

    def pre_update(self, dt, level):
        self.rect.x += self.direction * self.speed * dt
        self.cycletime += dt
        for cell in level.tilemap.layers['triggers'].collide(
                self.rect, 'reverse'):
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
    speed = 100

    def init_horizontal_images(self):
        image = self.sheet.subsurface(0, 0, 60, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(60, 0, 60, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(120, 0, 64, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(184, 0, 65, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(249, 0, 63, 60)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))


class ToucanEnemy(Enemy):
    sheet = pygame.image.load('resources/sprites/toucan.png')
    speed = 400

    def init_horizontal_images(self):
        image = self.sheet.subsurface(0, 0, 45, 31)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(45, 0, 45, 31)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(90, 0, 45, 31)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(135, 0, 45, 31)
        self.horizontal[LEFT].append(image)
        self.horizontal[RIGHT].append(
            pygame.transform.flip(image, True, False))

    def pre_update(self, dt, level):
        self.rect.y += self.direction * 100 * dt
        self.cycletime += dt
        for cell in level.tilemap.layers['triggers'].collide(
                self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.bottom = cell.top
            else:
                self.rect.top = cell.bottom
            self.direction *= -1
            return

    def post_update(self, dt, level):
        if self.cycletime > BASE_ANIMATION_LAG:
            self.cycletime = 0
            self.horizontal['current_frame'] = (
                (self.horizontal['current_frame'] + 1) %
                self.horizontal['frames'])
        if (level.player.rect.x - self.rect.x) > 0:
            self.image = self.horizontal[RIGHT][
                self.horizontal['current_frame']]
        else:
            self.image = self.horizontal[LEFT][
                self.horizontal['current_frame']]
