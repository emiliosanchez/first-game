import pygame
from libs import tmx
from triggers import Box, Weapon, Goal

from config import LEFT, RIGHT, BASE_ANIMATION_LAG, TILE_SIZE
from character import Enemy, FlyEnemy


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
        self.direction = RIGHT
        self.walking_pick = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.walking = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.stand = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.attack_pick = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
            'animation': 0,
        }
        self.stand_pick = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.jump = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.jump_pick = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.dead = {
            LEFT: [],
            RIGHT: [],
            'frame': 0,
        }
        self.climb = {
            'images': [],
            'frame': 0,
        }
        for i in range(4):
            image = self.sheet.subsurface(46 * i, 0, 46, 71)
            self.walking[LEFT].append(image)
            self.walking[RIGHT].append(pygame.transform.flip(image, True, False))
        for i in range(3):
            image = self.sheet.subsurface(46 * i, 71, 46, 71)
            self.stand[LEFT].append(image)
            self.stand[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(46 * 3, 71, 46, 71)
        self.jump[LEFT].append(image)
        self.jump[RIGHT].append(pygame.transform.flip(image, True, False))

        for i in range(2):
            image = self.sheet.subsurface(46 * i, 142, 46, 71)
            self.climb['images'].append(image)

        image = self.sheet.subsurface(92, 142, 46, 71)
        self.dead[LEFT].append(image)
        self.dead[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.sheet.subsurface(138, 170, 63, 43)
        self.dead[LEFT].append(image)
        self.dead[RIGHT].append(pygame.transform.flip(image, True, False))

        for i in range(4):
            image = self.weapon_sheet.subsurface(46 * i, 0, 46, 71)
            self.walking_pick[LEFT].append(image)
            self.walking_pick[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.weapon_sheet.subsurface(0, 71, 46, 71)
        self.stand_pick[LEFT].append(image)
        self.stand_pick[RIGHT].append(pygame.transform.flip(image, True, False))

        image = self.weapon_sheet.subsurface(0, 159, 46, 71)
        self.jump_pick[LEFT].append(image)
        self.jump_pick[RIGHT].append(pygame.transform.flip(image, True, False))

        image = self.weapon_sheet.subsurface(46, 71, 67, 71)
        self.attack_pick[LEFT].append(image)
        self.attack_pick[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.weapon_sheet.subsurface(113, 71, 46, 71)
        self.attack_pick[LEFT].append(image)
        self.attack_pick[RIGHT].append(pygame.transform.flip(image, True, False))
        image = self.weapon_sheet.subsurface(159, 71, 73, 88)
        self.attack_pick[LEFT].append(image)
        self.attack_pick[RIGHT].append(pygame.transform.flip(image, True, False))

        size = (46, 71)

        self.rect = pygame.rect.Rect((location[0], location[1] + TILE_SIZE - size[1]), size)
        self.image = self.walking[self.direction][self.walking['frame']]
        self.image.blit(self.sheet, (0, 0), self.rect)
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

    def update_on_ladder(self, dt, level, key, last):
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
        for cell in level.tilemap.layers['ladders'].collide(new, 'ladders'):
            new.left = cell.left
            if new.bottom <= cell.bottom:
                can_down = True
            self.onladder = True

        if self.onladder:
            for cell in level.tilemap.layers['triggers'].collide(new, 'blockers'):
                blockers = cell['blockers']
                if not can_down and 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                    self.resting = True
                    new.bottom = cell.top
                    self.dy = 0
                    self.onladder = False
            if climbing and self.cycletime > BASE_ANIMATION_LAG + 0.1:
                self.cycletime = 0
                self.climb['frame'] = (self.climb['frame'] + 1) % 2
                self.image = self.climb['images'][self.climb['frame']]
        level.tilemap.set_focus(new.x, new.y)

    def check_block(self, last, collider, blockers):
        new = self.rect
        if 't' in blockers and last.bottom <= collider.top and new.bottom > collider.top and last.right != collider.left and last.left != collider.right:
            self.resting = True
            new.bottom = collider.top
            self.dy = 0
        if 'b' in blockers and last.top >= collider.bottom and new.top < collider.bottom and last.right != collider.left and last.left != collider.right:
            new.top = collider.bottom
            self.dy = 0
        if 'l' in blockers and last.right <= collider.left and new.right > collider.left and new.bottom != collider.top:
            new.right = collider.left
        if 'r' in blockers and last.left >= collider.right and new.left < collider.right and new.bottom != collider.top:
            new.left = collider.right

    def update_dead(self, dt, level):
        last = self.rect.copy()
        if not self.begin_animation:
            self.die_sound.play()
            self.dy = -400
            self.begin_animation = True
            self.resting = False
            self.wait_restart = 0
        self.wait_restart += dt
        if self.wait_restart > 2:
            level.sprites.remove(self)
            level.start()
        if self.resting:
            return
        self.dy = min(400, self.dy + 40)
        self.rect.y += self.dy * dt
        dx = 100
        if self.direction == RIGHT:
            dx = dx * - 1
        if not self.resting:
            self.rect.x += dx * dt

        self.cycletime += dt
        new = self.rect

        self.resting = False
        for cell in level.tilemap.layers['triggers'].collide(new, 'blockers'):
            self.check_block(last, cell, cell['blockers'])
        level.tilemap.set_focus(new.x, new.y)

        if self.resting:
            self.image = self.dead[self.direction][1]
            self.rect = pygame.rect.Rect((new.x, new.y + 28), self.image.get_size())
        else:
            self.image = self.dead[self.direction][0]

    def update(self, dt, level):
        if self.is_dead:
            return self.update_dead(dt, level)
        last = self.rect.copy()
        key = pygame.key.get_pressed()
        self.cycletime += dt
        if self.onladder:
            return self.update_on_ladder(dt, level, key, last)

        if self.stabbing:
            return self.update_on_floor(dt, level, key, last)
        new = self.rect
        if key[pygame.K_UP]:
            for cell in level.tilemap.layers['ladders'].collide(new, 'ladders'):
                if new.top >= cell.top and new.bottom <= cell.bottom:
                    self.onladder = True
                    return self.update_on_ladder(dt, level, key, last)
        elif key[pygame.K_DOWN]:
            if level.tilemap.layers['ladders'].collide(new, 'ladders'):
                self.onladder = True
                return self.update_on_ladder(dt, level, key, last)
        return self.update_on_floor(dt, level, key, last)

    def update_on_floor(self, dt, level, key, last):
        is_walking = False

        if self.stabbing_wait > 0.8:
            self.stabbing_wait = 0
        elif self.stabbing_wait:
            self.stabbing_wait += dt

        if self.stabbing and self.attack_pick['frame'] == 2 and self.attack_pick['animation'] > BASE_ANIMATION_LAG:
            self.stabbing = False
            size = self.stand[RIGHT][0].get_size()
            self.rect = pygame.rect.Rect((self.rect.x, self.rect.y), size)
            if self.direction == RIGHT:
                self.rect.left -= 13
            else:
                self.rect.left += 41
            last = pygame.rect.Rect((self.rect.x, self.rect.y), size)

        if self.resting and key[pygame.K_SPACE] and self.weapon:
            if not self.stabbing_wait:
                self.stabbing = True
                self.stabbing_wait += dt
                if self.direction == RIGHT:
                    self.rect.left -= 21

        if not self.stabbing:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT] and key[pygame.K_RIGHT]:
                pass
            elif key[pygame.K_LEFT]:
                self.rect.x -= 300 * dt
                self.direction = LEFT
                is_walking = True
            elif key[pygame.K_RIGHT]:
                self.rect.x += 300 * dt
                self.direction = RIGHT
                is_walking = True

            if self.resting and key[pygame.K_SPACE] and not self.weapon:
                self.dy = -500
                self.jump_sound.play()
            self.dy = min(400, self.dy + 40)

            self.rect.y += self.dy * dt
            new = self.rect
            self.resting = False
            for cell in level.tilemap.layers['triggers'].collide(new, 'blockers'):
                self.check_block(last, cell, cell['blockers'])
            for cell in pygame.sprite.spritecollide(self, level.blockers, False):
                self.check_block(last, cell.rect, cell.blockers)
            level.tilemap.set_focus(new.x, new.y)
        else:
            new = self.rect
            for cell in level.tilemap.layers['triggers'].collide(new, 'breakable'):
                cell['blockers'] = ''

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
            if self.attack_pick['animation'] > BASE_ANIMATION_LAG:
                self.attack_pick['animation'] = 0
                self.attack_pick['frame'] = (self.attack_pick['frame'] + 1) % 3
                if self.direction == LEFT:
                    if self.attack_pick['frame'] == 1:
                        dx = -14
                    elif self.attack_pick['frame'] == 2:
                        dx = -27
                elif self.attack_pick['frame'] == 1:
                    dx = 34
            else:
                self.attack_pick['animation'] += dt
            self.image = self.attack_pick[self.direction][self.attack_pick['frame']]
            size = self.image.get_size()
            self.rect = pygame.rect.Rect((self.rect.x, self.rect.y), self.image.get_size())
            self.rect.left += dx
        elif self.resting and is_walking:
            if self.cycletime > BASE_ANIMATION_LAG:
                self.cycletime = 0
                self.walking['frame'] = (self.walking['frame'] + 1) % 4
            self.image = walking[self.direction][self.walking['frame']]
        elif self.resting:
            #if self.cycletime > BASE_ANIMATION_LAG * 3:
                #self.cycletime = 0
                #self.stand['frame'] = (self.stand['frame'] + 1) % 3
            #self.image = self.stand[self.direction][self.stand['frame']]
            self.image = stand[self.direction][0]
        else:
            if self.cycletime > BASE_ANIMATION_LAG:
                self.cycletime = 0
                self.image = jump[self.direction][0]


class Level(object):

    def __init__(self, level_num, game):
        self.level_num = level_num
        self.game = game
        self.tilemap = tmx.load('resources/maps/map_%03d.tmx' % self.level_num, self.game.screen.get_size())
        self.enemycollide = pygame.sprite.collide_rect_ratio(0.8)
        self.sprites = None
        self.enemies = None
        self.blockers = None

    def start(self):
        self.background = pygame.image.load('resources/backgrounds/background.png')
        if self.sprites:
            self.tilemap.layers.remove(self.sprites)
        if self.enemies:
            self.tilemap.layers.remove(self.enemies)
        if self.blockers:
            self.tilemap.layers.remove(self.blockers)

        self.sprites = tmx.SpriteLayer()
        self.enemies = tmx.SpriteLayer()
        self.blockers = tmx.SpriteLayer()

        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        goal_cell = self.tilemap.layers['triggers'].find('exit')[0]
        self.goal = Goal((goal_cell.px, goal_cell.py), self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            if enemy.properties['type'] == 'f':
                FlyEnemy((enemy.px, enemy.py), int(enemy.properties.get('direction', '1')), self.enemies)
            else:
                Enemy((enemy.px, enemy.py), int(enemy.properties.get('direction', '1')), self.enemies)
        for weapon in self.tilemap.layers['triggers'].find('weapon'):
            Weapon((weapon.px, weapon.py), self.enemies)
        for box in self.tilemap.layers['triggers'].find('box'):
            Box((box.px, box.py), self.blockers)

        self.tilemap.layers.add_named(self.enemies, 'enemies')
        self.tilemap.layers.add_named(self.sprites, 'sprites')
        self.tilemap.layers.add_named(self.blockers, 'blockers')

    def update(self, dt):
        self.tilemap.update(dt, self)
        if self.player.rect.bottom > self.tilemap.px_height:
            self.player.is_dead = True
        background_y = min(0, (-self.tilemap.viewport.y / 2) + self.tilemap.px_height - self.background.get_size()[1] - 3100)
        background_x = -self.tilemap.viewport.x / 2
        self.game.screen.blit(self.background, (background_x, background_y))
        self.tilemap.draw(self.game.screen)
        pygame.display.flip()
