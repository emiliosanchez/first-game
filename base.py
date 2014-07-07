import pygame

from config import LEFT, RIGHT, BASE_ANIMATION_LAG, TILE_SIZE


class StaticItem(pygame.sprite.Sprite):

    image = None

    def get_image(self):
        raise NotImplementedError

    def __init__(self, location, *groups):
        super(StaticItem, self).__init__(*groups)
        if not self.image:
            self.image = self.get_image()
        size = self.image.get_size()
        y = location[1] + TILE_SIZE - size[1]
        self.rect = pygame.rect.Rect((location[0], y), self.image.get_size())

    def player_trigger(self, dt, level):
        pass

    def pre_update(self, dt, level):
        pass

    def post_update(self, dt, level):
        pass

    def update(self, dt, level):
        self.pre_update(dt, level)
        if level.enemycollide(self, level.player):
            self.player_trigger(dt, level)
        self.post_update(dt, level)


class HorizontalMovable(StaticItem):

    sheet = None
    animation_lag = BASE_ANIMATION_LAG

    def init_horizontal_images(self):
        raise NotImplementedError

    def get_image(self):
        return self.horizontal[self.direction][0]

    def __init__(self, location, direction, *groups):
        self.direction = direction
        self.horizontal = {
            LEFT: [],
            RIGHT: [],
            'current_frame': 0,
            'frames': 0,
        }
        self.init_horizontal_images()
        self.horizontal['frames'] = len(self.horizontal[LEFT])
        self.cycletime = 0
        super(HorizontalMovable, self).__init__(location, *groups)

    def player_trigger(self, dt, level):
        pass

    def post_update(self, dt, level):
        if self.cycletime > self.animation_lag:
            self.cycletime = 0
            self.horizontal['current_frame'] = (
                self.horizontal['current_frame'] + 1
            ) % self.horizontal['frames']
        self.image = self.horizontal[self.direction][
            self.horizontal['current_frame']]
