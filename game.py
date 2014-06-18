#!/usr/bin/env python

import pygame
from level import Level


class Game(object):

    def next_level(self):
        self.current_level = Level(self.current_level.level_num + 1, self)
        self.current_level.start()

    def main(self, screen):
        self.screen = screen
        clock = pygame.time.Clock()
        pygame.mixer.init()
        pygame.mixer.music.load("resources/music/music.mp3")
        pygame.mixer.music.set_volume(0.5)

        self.current_level = Level(1, self)
        self.current_level.start()
        pygame.mixer.music.play(-1)

        while 1:
            dt = clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_ESCAPE:
                    return

            self.current_level.update(dt / 1000.)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    Game().main(screen)
