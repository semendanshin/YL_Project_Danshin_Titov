import pygame
import os
import sys
from random import randint


def load_im(name):
    fullname = os.path.join('imgs', name)
    try:
        return pygame.image.load(fullname)
    except FileNotFoundError:
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit(0)


class MySpriteGroup(pygame.sprite.Group):
    def draw(self, screen):
        for el in self.sprites():
            el.draw(screen)


class LoopedImage(pygame.sprite.Sprite):
    def __init__(self, img_name, speed, screen_size, *gropus):
        super().__init__(*gropus)
        self.speed = speed
        self.screen_size = screen_size
        self.image = load_im(img_name).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.w = self.rect.w * 2
        self.rect.x = 0
        self.rect.y = screen_size[1] - self.rect.size[1]
        self.shift = 0

    def update(self):
        self.shift = (self.shift + self.speed) % self.screen_size[0]

    def draw(self, screen):
        screen.blit(self.image, (-self.shift, self.rect.y))
        screen.blit(self.image, (self.rect.size[0] / 2 - self.shift, self.rect.y))

    def get_size(self):
        return self.rect.size

    def set_pos(self, pos):
        self.rect.x, self.rect.y = pos


class Sky(pygame.sprite.Sprite):
    def __init__(self, img_name, screen_size, *groups):
        super().__init__(*groups)
        self.screen_size = screen_size
        self.image = load_im(img_name).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, anim_count, *groups):
        super().__init__(*groups)
        self.images = [pygame.transform.scale(load_im(f'player/run_{i + 1}.png').convert_alpha(), (120, 142)) for i in range(anim_count)]
        self.anim_count = anim_count
        self.anim_ind = 0
        self.rect = self.images[0].get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]
        self.ground_y_coord = self.rect.y
        self.in_jump = False
        self.anim_speed = 1
        self.vy = 0
        self.t = 0
        self.g = 1

    def start_jump(self):
        if not self.in_jump:
            self.vy = randint(20, 25)
            self.in_jump = True
            self.t = 0

    def update(self):
        if self.in_jump:
            if self.rect.y - (self.g * self.vy - self.t) >= self.ground_y_coord:
                self.rect.y = self.ground_y_coord
                self.in_jump = False
            else:
                self.rect.y -= self.g * self.vy - self.t
            self.t += 1
        else:
            self.anim_ind = (self.anim_ind + self.anim_speed) % (self.anim_count - 1)

    def draw(self, screen):
        screen.blit(self.images[round(self.anim_ind)], self.rect)


class Game:
    def __init__(self, screen):
        self.screen_size = self.width, self.height = screen.get_width(), screen.get_height()
        self.background = MySpriteGroup()
        self.all_sprites = MySpriteGroup()
        self.clock = pygame.time.Clock()
        self.screen = screen
        self.running = True

    def read_settings(self):
        pass

    def load_objects(self):
        Sky('bg/sky.png', self.screen_size, self.background, self.all_sprites)
        LoopedImage('bg/clouds_1.png', 3, self.screen_size, self.background, self.all_sprites)
        LoopedImage('bg/rocks.png', 8, self.screen_size, self.background, self.all_sprites)
        LoopedImage('bg/ground1.png', 15, self.screen_size, self.background, self.all_sprites)
        self.ground = LoopedImage('ground.png', 60, self.screen_size, self.all_sprites)
        self.player = Player((200, self.height - self.ground.get_size()[1]), 6, self.all_sprites)

    def main_loop(self):
        while self.running:
            print(self.clock.get_fps())
            self.clock.tick(24)
            self.check_events()
            self.update()
            self.render()
            pygame.display.update()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                self.player.start_jump()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.all_sprites.draw(screen)

    def update(self):
        self.all_sprites.update()


class Map:  # пока не работает
    def __init__(self, filename):
        with open(f'maps/{filename}', encoding='UTF-8') as f:
            file = [el.strip() for el in f.readlines()]
        self.col_ind = 0

    def load_next(self, col_num=1):
        pass

    def update(self):
        pass

    def draw(self):
        pass


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('раннер')
    display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
    SIZE = WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode(SIZE)
    game = Game(screen)
    game.read_settings()
    game.load_objects()
    game.main_loop()
