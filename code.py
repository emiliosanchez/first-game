#!/usr/bin/env python

import pygame
import tmx


animate = 0.10

class Player(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)
        self.sheet = pygame.image.load('player.png')
        self.direction = 'right'
        self.walking = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.stand = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.jump = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.climb = {
            'images': [],
            'frame': 0,
        }
        for i in range(4):
            image = self.sheet.subsurface(46*i, 0, 46, 71)
            self.walking['left'].append(image)
            self.walking['right'].append(pygame.transform.flip(image, True, False))
        for i in range(3):
            image = self.sheet.subsurface(46*i, 71, 46, 71)
            self.stand['left'].append(image)
            self.stand['right'].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(46*3, 71, 46, 71)
        self.jump['left'].append(image)
        self.jump['right'].append(pygame.transform.flip(image, True, False))

        for i in range(2):
            image = self.sheet.subsurface(46*i, 142, 46, 71)
            self.climb['images'].append(image)

        size = (46, 71)

        self.rect = pygame.rect.Rect((location[0], location[1]- 10), size)
        self.image = self.walking[self.direction][self.walking['frame']]
        self.image.blit(self.sheet, (0,0), self.rect)
        self.resting = False
        self.dy = 0
        self.walking_frame = 0
        self.cycletime = 0
        self.onladder = False

    def update_on_ladder(self, dt, game, key, last):
        climbing = False
        new = self.rect
        if key[pygame.K_UP] and key[pygame.K_DOWN]:
            pass
        elif key[pygame.K_UP]:
            self.rect.y -= 100 * dt
            self.climb_direction = 'up'
            climbing = True
        elif key[pygame.K_DOWN]:
            self.rect.y += 100 * dt
            self.climb_direction = 'down'
            climbing = True

        can_down = False
        self.onladder = False
        for cell in game.tilemap.layers['ladders'].collide(new, 'ladders'):
            new.left = cell.left
            if new.bottom <= cell.bottom:
                can_down = True
            self.onladder = True

        if self.onladder:
            for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
                blockers = cell['blockers']
                if not can_down and 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                    self.resting = True
                    new.bottom = cell.top
                    self.dy = 0
                    self.onladder = False
            if climbing and self.cycletime > animate:
                self.cycletime = 0
                self.climb['frame'] = (self.climb['frame'] + 1) % 2
                self.image = self.climb['images'][self.climb['frame']]
        game.tilemap.set_focus(new.x, new.y)

    def update(self, dt, game):
        last = self.rect.copy()
        key = pygame.key.get_pressed()
        self.cycletime += dt
        if self.onladder:
            return self.update_on_ladder(dt, game, key, last)

        new = self.rect
        if key[pygame.K_UP]:
            for cell in game.tilemap.layers['ladders'].collide(new, 'ladders'):
                if new.top >= cell.top:
                    self.onladder = True
                    return self.update_on_ladder(dt, game, key, last)
        elif key[pygame.K_DOWN]:
            if game.tilemap.layers['ladders'].collide(new, 'ladders'):
                self.onladder = True
                return self.update_on_ladder(dt, game, key, last)
        return self.update_on_floor(dt, game, key, last)

    def update_on_floor(self, dt, game, key, last):
        walking = False

        if key[pygame.K_LEFT] and key[pygame.K_RIGHT]:
            pass
        elif key[pygame.K_LEFT]:
            self.rect.x -= 300 * dt
            self.direction = 'left'
            walking = True
        elif key[pygame.K_RIGHT]:
            self.rect.x += 300 * dt
            self.direction = 'right'
            walking = True

        if self.resting and key[pygame.K_SPACE]:
            self.dy = -400
        self.dy = min(400, self.dy + 40)

        self.rect.y += self.dy * dt
        new = self.rect
        self.resting = False
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
                self.dy = 0
        game.tilemap.set_focus(new.x, new.y)

        if self.resting and walking:
            if self.cycletime > animate:
                self.cycletime = 0
                self.walking['frame'] = (self.walking['frame'] + 1) % 4
            self.image = self.walking[self.direction][self.walking['frame']]
        elif self.resting:
            #if self.cycletime > animate * 3:
                #self.cycletime = 0
                #self.stand['frame'] = (self.stand['frame'] + 1) % 3
            #self.image = self.stand[self.direction][self.stand['frame']]
            self.image = self.stand[self.direction][0]
        else:
            if self.cycletime > animate:
                self.cycletime = 0
                self.image = self.jump[self.direction][0]


class ScrolledGroup(pygame.sprite.Group):
    def draw(self, surface):
        for sprite in self.sprites():
            surface.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))


class Game(object):
    def main(self, screen):
        clock = pygame.time.Clock()

        background = pygame.image.load('background.png')
        self.tilemap = tmx.load('map.tmx', screen.get_size())
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)

        while 1:
            dt = clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_ESCAPE:
                    return

            self.tilemap.update(dt / 1000., self)
            background_y = min(0, (-self.tilemap.viewport.y / 2) - 350)
            background_x = -self.tilemap.viewport.x / 2
            screen.blit(background, (background_x, background_y))
            self.tilemap.draw(screen)
            pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    Game().main(screen)
