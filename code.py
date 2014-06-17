#!/usr/bin/env python

import pygame
from libs import tmx


animate = 0.10

class Trigger(pygame.sprite.Sprite):

    def move(self, dt, game):
        pass

    def player_trigger(self, dt, game):
        pass

    def animate(self, dt, game):
        pass

    def update(self, dt, game):
        self.move(dt, game)
        if game.enemycollide(self, game.player):
            self.player_trigger(dt, game)
        self.animate(dt, game)


class Box(Trigger):

    image = pygame.image.load('resources/sprites/box.png')

    def __init__(self, location, *groups):
        super(Box, self).__init__(*groups)
        size = self.image.get_size()
        y = location[1] + 70 - size[1]
        self.rect = pygame.rect.Rect((location[0], y), self.image.get_size())

    def player_trigger(self, dt, game):
        game.player.weapon = 1
        game.enemies.remove(self)


class Weapon(Trigger):

    sheet = pygame.image.load('resources/sprites/player_weapon.png')

    def __init__(self, location, *groups):
        super(Weapon, self).__init__(*groups)
        self.image = self.sheet.subsurface(184, 0, 38, 38)
        size = self.image.get_size()
        y = location[1] + 70 - size[1]
        self.rect = pygame.rect.Rect((location[0], y), self.image.get_size())

    def player_trigger(self, dt, game):
        game.player.weapon = 1
        game.enemies.remove(self)


class Enemy(Trigger):
    sheet = pygame.image.load('resources/sprites/dino.png')

    def init_images(self):
        for i in range(5):
            image = self.sheet.subsurface(48*i, 0, 48, 43)
            self.walking['left'].append(image)
            self.walking['right'].append(pygame.transform.flip(image, True, False))

    def __init__(self, location, direction, *groups):
        super(Enemy, self).__init__(*groups)
        self.walking = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.init_images()
        self.image = self.walking['left'][0]
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = direction
        self.cycletime = 0

    def move(self, dt, game):
        self.rect.x += self.direction * 100 * dt
        self.cycletime += dt
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            return

    def player_trigger(self, dt, game):
            game.player.is_dead = True

    def animate(self, dt, game):
        if self.cycletime > animate:
            self.cycletime = 0
            self.walking['frame'] = (self.walking['frame'] + 1) % 5
        direction = 'left'
        if self.direction == 1:
            direction = 'right'
        self.image = self.walking[direction][self.walking['frame']]


class FlyEnemy(Enemy):
    sheet = pygame.image.load('resources/sprites/fly.png')

    def init_images(self):
        image = self.sheet.subsurface(0, 0, 60, 60)
        self.walking['left'].append(image)
        self.walking['right'].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(60, 0, 60, 60)
        self.walking['left'].append(image)
        self.walking['right'].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(120, 0, 64, 60)
        self.walking['left'].append(image)
        self.walking['right'].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(184, 0, 65, 60)
        self.walking['left'].append(image)
        self.walking['right'].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(249, 0, 63, 60)
        self.walking['left'].append(image)
        self.walking['right'].append(pygame.transform.flip(image, True, False))


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

    def move(self, dt, game):
        if self.end:
            self.wait += dt
            if self.wait > 2:
                self.wait = 0
                self.end = False
                game.enemies.remove(self)
                game.start()

    def player_trigger(self, dt, game):
        self.image = self.with_player
        self.end = True
        game.sprites.remove(game.player)


class Player(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)
        self.weapon = 0
        self.jump_sound = pygame.mixer.Sound("resources/sounds/jump.wav")
        self.jump_sound.set_volume(0.1)
        self.die_sound = pygame.mixer.Sound("resources/sounds/die.wav")
        self.die_sound.set_volume(0.2)
        self.sheet = pygame.image.load('resources/sprites/player.png')
        self.weapon_sheet = pygame.image.load('resources/sprites/player_weapon.png')
        self.direction = 'right'
        self.walking_pick = {
            'left': [],
            'right': [],
            'frame': 0,
        }
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
        self.attack_pick = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.stand_pick = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.jump = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.jump_pick = {
            'left': [],
            'right': [],
            'frame': 0,
        }
        self.dead = {
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

        image = self.sheet.subsurface(92, 142, 46, 71)
        self.dead['left'].append(image)
        self.dead['right'].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(138, 170, 63, 43)
        self.dead['left'].append(image)
        self.dead['right'].append(pygame.transform.flip(image, True, False))

        for i in range(4):
            image = self.weapon_sheet.subsurface(46*i, 0, 46, 71)
            self.walking_pick['left'].append(image)
            self.walking_pick['right'].append(pygame.transform.flip(image, True, False))
        image = self.weapon_sheet.subsurface(0, 71, 46, 71)
        self.stand_pick['left'].append(image)
        self.stand_pick['right'].append(pygame.transform.flip(image, True, False))

        image = self.weapon_sheet.subsurface(0, 159, 46, 71)
        self.jump_pick['left'].append(image)
        self.jump_pick['right'].append(pygame.transform.flip(image, True, False))

        image = self.weapon_sheet.subsurface(46, 71, 67, 71)
        self.attack_pick['left'].append(image)
        self.attack_pick['right'].append(pygame.transform.flip(image, True, False))
        image = self.weapon_sheet.subsurface(113, 71, 46, 71)
        self.attack_pick['left'].append(image)
        self.attack_pick['right'].append(pygame.transform.flip(image, True, False))
        image = self.weapon_sheet.subsurface(159, 71, 73, 88)
        self.attack_pick['left'].append(image)
        self.attack_pick['right'].append(pygame.transform.flip(image, True, False))

        size = (46, 71)

        self.rect = pygame.rect.Rect((location[0], location[1]- 10), size)
        self.image = self.walking[self.direction][self.walking['frame']]
        self.image.blit(self.sheet, (0,0), self.rect)
        self.resting = False
        self.dy = 0
        self.walking_frame = 0
        self.cycletime = 0
        self.onladder = False
        self.is_dead = 0
        self.begin_animation = False
        self.wait_restart = 0
        self.stabbing = False
        self.stabbing_wait = 0

    def update_on_ladder(self, dt, game, key, last):
        climbing = False
        new = self.rect
        self.dy = 0
        if key[pygame.K_UP] and key[pygame.K_DOWN]:
            pass
        elif key[pygame.K_UP]:
            self.rect.y -= 200 * dt
            self.climb_direction = 'up'
            climbing = True
        elif key[pygame.K_DOWN]:
            self.rect.y += 200 * dt
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
            if climbing and self.cycletime > animate + 0.1:
                self.cycletime = 0
                self.climb['frame'] = (self.climb['frame'] + 1) % 2
                self.image = self.climb['images'][self.climb['frame']]
        game.tilemap.set_focus(new.x, new.y)

    def update_dead(self, dt, game):
        last = self.rect.copy()
        if not self.begin_animation:
            self.die_sound.play()
            self.dy = -400
            self.begin_animation = True
            self.resting = False
            self.wait_restart = 0
        if self.resting:
            self.wait_restart += dt
            if self.wait_restart > 2:
                game.sprites.remove(self)
                game.start()
            return
        self.dy = min(400, self.dy + 40)
        self.rect.y += self.dy * dt
        dx = 100
        if self.direction == 'right':
            dx = dx * - 1
        if not self.resting:
            self.rect.x += dx * dt

        self.cycletime += dt
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

        if self.resting:
            self.image = self.dead[self.direction][1]
            self.rect = pygame.rect.Rect((new.x, new.y + 28), self.image.get_size())
        else:
            self.image = self.dead[self.direction][0]

    def update(self, dt, game):
        if self.is_dead:
            return self.update_dead(dt, game)
        last = self.rect.copy()
        key = pygame.key.get_pressed()
        self.cycletime += dt
        if self.onladder:
            return self.update_on_ladder(dt, game, key, last)

        if self.stabbing:
            return self.update_on_floor(dt, game, key, last)
        new = self.rect
        if key[pygame.K_UP]:
            for cell in game.tilemap.layers['ladders'].collide(new, 'ladders'):
                if new.top >= cell.top and new.bottom <= cell.bottom:
                    self.onladder = True
                    return self.update_on_ladder(dt, game, key, last)
        elif key[pygame.K_DOWN]:
            if game.tilemap.layers['ladders'].collide(new, 'ladders'):
                self.onladder = True
                return self.update_on_ladder(dt, game, key, last)
        return self.update_on_floor(dt, game, key, last)

    def update_on_floor(self, dt, game, key, last):
        is_walking = False

        if self.stabbing_wait > 0.8:
            self.stabbing_wait = 0
        elif self.stabbing_wait:
            self.stabbing_wait += dt

        if self.stabbing and self.attack_pick['frame'] == 2 and self.cycletime > animate:
            self.stabbing = False
            size = self.stand['right'][0].get_size()
            self.rect = pygame.rect.Rect((self.rect.x, self.rect.y), size)
            if self.direction == 'right':
                self.rect.left -= 13
            else:
                self.rect.left += 13
            last = pygame.rect.Rect((self.rect.x, self.rect.y), size)

        if not self.stabbing:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT] and key[pygame.K_RIGHT]:
                pass
            elif key[pygame.K_LEFT]:
                self.rect.x -= 300 * dt
                self.direction = 'left'
                is_walking = True
            elif key[pygame.K_RIGHT]:
                self.rect.x += 300 * dt
                self.direction = 'right'
                is_walking = True

            if self.resting and key[pygame.K_SPACE]:
                if self.weapon:
                    if not self.stabbing_wait:
                        self.stabbing = True
                        self.stabbing_wait += dt
                        if self.direction == 'right':
                            self.rect.left -= 21
                        else:
                            self.rect.left += 21
                else:
                    self.dy = -500
                    self.jump_sound.play()
            self.dy = min(400, self.dy + 40)

            self.rect.y += self.dy * dt
            new = self.rect
            self.resting = False
            for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
                blockers = cell['blockers']
                if 'l' in blockers and last.right <= cell.left and new.right > cell.left and new.bottom != cell.top:
                    new.right = cell.left
                if 'r' in blockers and last.left >= cell.right and new.left < cell.right and new.bottom != cell.top:
                    new.left = cell.right
                if 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top and new.right != cell.left and new.left != cell.right:
                    self.resting = True
                    new.bottom = cell.top
                    self.dy = 0
                if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom and new.right != cell.left and new.left != cell.right:
                    new.top = cell.bottom
                    self.dy = 0
            game.tilemap.set_focus(new.x, new.y)

        if self.weapon:
            walking = self.walking_pick
            stand = self.stand_pick
            jump = self.jump_pick
        else:
            walking = self.walking
            stand = self.stand
            jump = self.jump

        if self.resting and self.stabbing:
            dx = 0
            if self.cycletime > animate:
                self.cycletime = 0
                self.attack_pick['frame'] = (self.attack_pick['frame'] + 1) % 3
                if self.attack_pick['frame'] == 1:
                    dx = -34
            self.image = self.attack_pick[self.direction][self.attack_pick['frame']]
            if self.direction == 'right':
                size = self.image.get_size()
                self.rect = pygame.rect.Rect((self.rect.x, self.rect.y), self.image.get_size())
                self.rect.left -= dx
            else:
                self.rect = pygame.rect.Rect((self.rect.x, self.rect.y), self.image.get_size())
                self.rect.left += dx
        elif self.resting and is_walking:
            if self.cycletime > animate:
                self.cycletime = 0
                self.walking['frame'] = (self.walking['frame'] + 1) % 4
            self.image = walking[self.direction][self.walking['frame']]
        elif self.resting:
            #if self.cycletime > animate * 3:
                #self.cycletime = 0
                #self.stand['frame'] = (self.stand['frame'] + 1) % 3
            #self.image = self.stand[self.direction][self.stand['frame']]
            self.image = stand[self.direction][0]
        else:
            if self.cycletime > animate:
                self.cycletime = 0
                self.image = jump[self.direction][0]


class ScrolledGroup(pygame.sprite.Group):
    def draw(self, surface):
        for sprite in self.sprites():
            surface.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))


class Game(object):

    def start(self):
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        goal_cell = self.tilemap.layers['triggers'].find('exit')[0]
        self.goal = Goal((goal_cell.px, goal_cell.py + 70 - 88), self.enemies)


    def main(self, screen):
        clock = pygame.time.Clock()
        pygame.mixer.init()
        pygame.mixer.music.load("resources/music/music.mp3")
        pygame.mixer.music.set_volume(0.5)
        self.enemycollide = pygame.sprite.collide_rect_ratio(0.8)
        self.tilemap = tmx.load('resources/maps/map.tmx', screen.get_size())
        self.sprites = tmx.SpriteLayer()
        self.enemies = tmx.SpriteLayer()

        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            if enemy.properties['type'] == 'f':
                FlyEnemy((enemy.px, enemy.py + 70 - 60), int(enemy.properties.get('direction', 1)), self.enemies)
            else:
                Enemy((enemy.px, enemy.py + 70 - 43), int(enemy.properties.get('direction', 1)), self.enemies)
        for weapon in self.tilemap.layers['triggers'].find('weapon'):
            Weapon((weapon.px, weapon.py), self.enemies)
        for box in self.tilemap.layers['triggers'].find('box'):
            Box((box.px, box.py), self.enemies)
        self.start()
        self.tilemap.layers.append(self.enemies)
        background = pygame.image.load('resources/backgrounds/background.png')
        self.tilemap.layers.append(self.sprites)
        pygame.mixer.music.play(-1);

        while 1:
            dt = clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_ESCAPE:
                    return

            self.tilemap.update(dt / 1000., self)
            background_y = min(0, (-self.tilemap.viewport.y / 2) + 2250)
            background_x = -self.tilemap.viewport.x / 2
            screen.blit(background, (background_x, background_y))
            self.tilemap.draw(screen)
            pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    Game().main(screen)