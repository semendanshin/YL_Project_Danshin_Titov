import pygame
import os
import sys
from random import randint
from math import floor


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
    def __init__(self, img_name, speed, screen_size, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.screen_size = screen_size
        self.image = load_im(img_name).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.w = self.rect.w * 2
        self.rect.x = 0
        self.rect.y = screen_size[1] - self.rect.size[1]
        self.shift = 0

    def update(self):
        self.shift = (self.shift + self.speed) % (self.rect.size[0] / 2)

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
    def __init__(self, pos, screen_size, *groups):
        super().__init__(*groups)
        self.vy = 0
        self.t = 0
        self.g = 4
        self.run_anim_count = 6
        self.run_anim_ind = 0
        self.run_anim_speed = 0.6
        self.run_images = [
            pygame.transform.scale(
                load_im(f'player/run_{i}.png').convert_alpha(), (screen_size[1] // 5, screen_size[1] // 5)
            )
            for i in range(self.run_anim_count)
        ]
        self.jump_anim_count = 9
        self.jump_anim_index = 0
        self.jump_anim_speed = 0.2
        self.jump_images = [
            pygame.transform.scale(
                load_im(f'player/jump_{i}.png').convert_alpha(), (screen_size[1] // 5, screen_size[1] // 5)
            )
            for i in range(self.jump_anim_count)
        ]
        self.slide_anim_count = 4
        self.slide_anim_index = 0
        self.slide_anim_speed = 0.5
        self.slide_images = [
            pygame.transform.scale(
                load_im(f'player/slide_{i}.png').convert_alpha(), (screen_size[1] // 5, screen_size[1] // 5)
            )
            for i in range(self.slide_anim_count)
        ]
        self.in_jump = False
        self.in_slide = False
        self.rect = self.run_images[0].get_rect()
        self.mask = pygame.mask.from_surface(self.run_images[0])
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]
        self.ground_y_coord = self.rect.y

    def start_jump(self):
        if self.rect.y == self.ground_y_coord:
            self.in_jump = True
            self.in_slide = False
            self.jump_anim_index = 0
            self.vy = randint(35, 40)
            self.t = 0

    def start_slide(self):
        if not self.in_slide:
            self.in_jump = False
            self.in_slide = True
            self.slide_anim_index = 0

    def stop_slide(self):
        if self.in_slide:
            self.in_slide = False
            self.rect.y = self.ground_y_coord

    def update(self, coins, rocks, ghosts):
        if self.in_jump:
            if self.rect.y + (-self.vy + self.g * self.t) >= self.ground_y_coord:
                self.rect.y = self.ground_y_coord
                self.in_jump = False
            else:
                self.rect.y += (-self.vy + self.g * self.t)
            self.t += 1
            self.jump_anim_index = (self.jump_anim_index + self.jump_anim_speed) % (self.jump_anim_count - 1)
            self.mask = pygame.mask.from_surface(self.jump_images[floor(self.jump_anim_index)])
        elif self.in_slide:
            self.slide_anim_index += self.slide_anim_speed if self.slide_anim_index < 4 - self.slide_anim_speed else 0
            if self.rect.y + 40 < self.ground_y_coord:
                self.rect.y += 40
            else:
                self.rect.y = self.ground_y_coord
            self.mask = pygame.mask.from_surface(self.slide_images[floor(self.slide_anim_index)])
        else:
            self.run_anim_ind = (self.run_anim_ind + self.run_anim_speed) % (self.run_anim_count - 1)
            self.mask = pygame.mask.from_surface(self.run_images[floor(self.run_anim_ind)])

    def draw(self, screen):
        if self.in_jump:
            screen.blit(self.jump_images[floor(self.jump_anim_index)], self.rect)
        elif self.in_slide:
            screen.blit(self.slide_images[floor(self.slide_anim_index)], self.rect)
        else:
            screen.blit(self.run_images[floor(self.run_anim_ind)], self.rect)


class Ghost(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_size, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.anim_count = 11
        self.anim_ind = 0
        self.anim_speed = 0.4
        self.images = [
            pygame.transform.scale(
                load_im(f'ghost/fly_{i}.png').convert_alpha(), (screen_size[1] // 10, screen_size[1] // 10)
            )
            for i in range(self.anim_count)
        ]
        self.mask = pygame.mask.from_surface(self.images[0])
        self.rect = self.images[0].get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def update(self):
        self.anim_ind = (self.anim_ind + self.anim_speed) % (self.anim_count - 1)
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.images[round(self.anim_ind)], self.rect)


class Rock(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_size, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.image = pygame.transform.scale(load_im('rock.png'), (screen_size[1] // 10, screen_size[1] // 10))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_size, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.image = pygame.transform.scale(load_im('coin.png'), (screen_size[1] // 15, screen_size[1] // 15))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Map:
    def __init__(self, screen_size, filename):
        self.screen_size = screen_size
        self.all_sprites = MySpriteGroup()
        self.ghosts = MySpriteGroup()
        self.rocks = MySpriteGroup()
        self.coins = MySpriteGroup()
        self.frame = 0
        self.cell_size = 120
        self.speed = 40
        self.load_freq = self.cell_size // self.speed
        self.game_map = []
        self.col_ind = 0
        self.stop_game = False
        self.read_map(filename)
        self.ground = LoopedImage('ground.png', self.speed, self.screen_size, self.all_sprites)

    def get_coins(self):
        return self.coins

    def get_rocks(self):
        return self.rocks

    def get_ghosts(self):
        return self.ghosts

    def read_map(self, filename):
        with open(f'maps/{filename}', encoding='UTF-8') as f:
            self.game_map = [list(map(int, el.strip())) for el in f.readlines()]

    def load_next(self, col_count=1):
        if self.col_ind + col_count < len(self.game_map[0]):
            for i in range(col_count):
                for j in (self.game_map[0][(self.col_ind + i)],
                          self.game_map[1][(self.col_ind + i)]):
                    if j == 1:
                        Coin((self.screen_size[0] + self.cell_size * i,
                              self.screen_size[1] - self.ground.get_size()[1]),
                             self.speed,
                             self.screen_size, self.all_sprites, self.coins)
                    elif j == 2:
                        Rock((self.screen_size[0] + self.cell_size * i,
                              self.screen_size[1] - self.ground.get_size()[1] + 5),
                             self.speed,
                             self.screen_size, self.all_sprites, self.rocks)
                    elif j == 3:
                        Ghost((self.screen_size[0] + self.cell_size * i,
                               self.screen_size[1] - self.ground.get_size()[1] - 150),
                              self.speed,
                              self.screen_size, self.all_sprites, self.rocks)
            self.col_ind += col_count

    def update(self):
        if self.frame % self.load_freq == 0:
            self.load_next()
        self.frame = (self.frame + 1) % self.load_freq
        self.all_sprites.update()
        for el in self.all_sprites:
            if el.rect.x < -100:
                self.all_sprites.remove(el)

    def draw(self, screen):
        self.all_sprites.draw(screen)


class Game:
    def __init__(self, screen):
        self.screen_size = self.width, self.height = screen.get_width(), screen.get_height()
        self.background = MySpriteGroup()
        self.clock = pygame.time.Clock()
        self.settings = dict()
        self.screen = screen
        self.running = True

    def read_settings(self):
        with open('settings.txt', encoding='UTF-8') as f:
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings[key] = value

    def load_objects(self):
        self.game_map = Map(self.screen_size, '1.txt')
        self.player = Player((200, self.height - 200), self.screen_size)
        Sky('bg/sky.png', self.screen_size, self.background)
        if self.settings['background_layers_count'] > 1:
            LoopedImage('bg/lay_1.png', 5, self.screen_size, self.background)
        if self.settings['background_layers_count'] > 2:
            LoopedImage('bg/lay_2.png', 10, self.screen_size, self.background)
        if self.settings['background_layers_count'] > 3:
            LoopedImage('bg/lay_3.png', 20, self.screen_size, self.background)
        if self.settings['background_layers_count'] > 4:
            LoopedImage('bg/lay_4.png', 25, self.screen_size, self.background)

    def main_loop(self):
        while self.running:
            print(int(self.clock.get_fps()))
            self.clock.tick(24)
            self.check_events()
            self.update()
            self.render()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                self.player.start_jump()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_LCTRL or event.key == pygame.K_DOWN):
                self.player.start_slide()
            if event.type == pygame.KEYUP and (event.key == pygame.K_LCTRL or event.key == pygame.K_DOWN):
                self.player.stop_slide()

    def update(self):
        self.player.update(self.game_map.get_coins(), self.game_map.get_rocks(), self.game_map.get_ghosts())
        self.game_map.update()
        self.background.update()
        if self.game_map.stop_game:
            self.running = False

    def render(self):
        self.screen.fill((0, 0, 0))
        self.background.draw(self.screen)
        self.player.draw(self.screen)
        self.game_map.draw(self.screen)
        pygame.display.update()


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
