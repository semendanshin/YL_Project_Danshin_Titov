import pygame
from random import randint, choice
from math import floor, ceil


# TODO: Сделать музыку
# TODO: Сделать звуковые эффекты
# TODO: Сделать генрацию карты на ходу
# TODO: Сделать частицы для персонажа


def load_im(name):
    fullname = f'data/imgs/{name}'
    try:
        return pygame.image.load(fullname)
    except FileNotFoundError:
        print(f"Файл с изображением '{fullname}' не найден")
        exit(0)


class MySpriteGroup(pygame.sprite.Group):
    def draw(self, screen):
        for el in self.sprites():
            el.draw(screen)


class Map:
    cell_size = 300
    speed = 50

    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.all_sprites = MySpriteGroup()
        self.ghosts = MySpriteGroup()
        self.rocks = MySpriteGroup()
        self.coins = MySpriteGroup()
        self.free_ghosts = []
        self.free_rocks = []
        self.free_coins = []
        self.frame = 0
        self.cell_size = Map.cell_size
        self.speed = Map.speed
        self.load_freq = ceil(self.cell_size / self.speed)
        self.game_map = [[0, 0], [0, 0], [0, 0]]
        self.ground = LoopedImage('ground.png', self.speed, self.screen_size, self.all_sprites)

    def generate_next(self):
        new_items = []
        while True:
            item = choice([0] * 2 + [1] * 4 + [2] * 4)
            if self.game_map[-2][0] != 2 and self.game_map[-1][0] != 2 and self.game_map[-1][1] != 3 or item != 2:
                new_items.append(item)
                break
        while True:
            item = choice([0] * 7 + [3] * 3)
            if new_items[0] != 2 and self.game_map[-1][0] != 2 and self.game_map[-1][1] != 3 or item != 3:
                new_items.append(item)
                break
        self.game_map.append(new_items)

    def load_next(self):
        for i, el in enumerate(self.game_map[-1]):
            if el == 1:
                if self.free_coins:
                    coin = self.free_coins.pop(0)
                    coin.set_pos((self.screen_size[0] + self.cell_size,
                                  self.screen_size[1] - self.screen_size[1] // 5 - 150 * i))
                    self.coins.add(coin)
                    self.all_sprites.add(coin)
                else:
                    Coin(self.speed, self.screen_size,
                         (self.screen_size[0] + self.cell_size,
                          self.screen_size[1] - self.screen_size[1] // 5),
                         self.all_sprites, self.coins)
            elif el == 2:
                if self.free_rocks:
                    rock = self.free_rocks.pop(0)
                    rock.set_pos((self.screen_size[0] + self.cell_size,
                                  self.screen_size[1] - self.screen_size[1] // 5 + 5))
                    self.rocks.add(rock)
                    self.all_sprites.add(rock)
                else:
                    Rock(self.speed, self.screen_size,
                         (self.screen_size[0] + self.cell_size,
                          self.screen_size[1] - self.screen_size[1] // 5 + 5),
                         self.all_sprites, self.rocks)
            elif el == 3:
                if self.free_ghosts:
                    ghost = self.free_ghosts.pop(0)
                    ghost.set_pos((self.screen_size[0] + self.cell_size,
                                   self.screen_size[1] - self.screen_size[1] // 5 - 150))
                    self.ghosts.add(ghost)
                    self.all_sprites.add(ghost)
                else:
                    Ghost(self.speed, self.screen_size,
                          (self.screen_size[0] + self.cell_size,
                           self.screen_size[1] - self.screen_size[1] // 5 - 150),
                          self.all_sprites, self.ghosts)
        self.game_map = self.game_map[1:]

    def update(self):
        self.frame = (self.frame + 1) % self.load_freq
        if self.frame == 0:
            self.generate_next()
            self.load_next()
        self.all_sprites.update()
        for el in self.all_sprites:
            if el.rect.x < -100:
                el.kill()
                if isinstance(el, Coin):
                    self.free_coins.append(el)
                elif isinstance(el, Ghost):
                    self.free_ghosts.append(el)
                else:
                    self.free_rocks.append(el)

    def draw(self, screen):
        self.all_sprites.draw(screen)


class Ghost(pygame.sprite.Sprite):
    anim_count = 3
    anim_speed = 0.4

    def __init__(self, speed, screen_size, pos=(0, 0), *groups):
        super().__init__(*groups)
        self.speed = speed
        self.anim_count = Ghost.anim_count
        self.anim_speed = Ghost.anim_speed
        self.anim_ind = 0
        self.images = [
            pygame.transform.scale(
                load_im(f'ghost/fly_{i}.png').convert_alpha(), (screen_size[1] // 9, screen_size[1] // 9)
            )
            for i in range(self.anim_count)
        ]
        self.mask = pygame.mask.from_surface(self.images[0])
        self.rect = self.images[0].get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_pos(self, pos):
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_speed(self, speed):
        self.speed = speed

    def update(self):
        self.anim_ind = (self.anim_ind + self.anim_speed) % (self.anim_count - 1)
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.images[round(self.anim_ind)], self.rect)


class Rock(pygame.sprite.Sprite):
    def __init__(self, speed, screen_size, pos=(0, 0), *groups):
        super().__init__(*groups)
        self.speed = speed
        self.image = pygame.transform.scale(
            load_im('rock.png').convert_alpha(), (screen_size[1] // 9, screen_size[1] // 9))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_pos(self, pos):
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_speed(self, speed):
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self, speed, screen_size, pos=(0, 0), *groups):
        super().__init__(*groups)
        self.speed = speed
        self.image = pygame.transform.scale(
            load_im('coin.png').convert_alpha(), (screen_size[1] // 15, screen_size[1] // 15))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_pos(self, pos):
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_speed(self, speed):
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class ScoreBoard:
    text_template = 'Coins:{}'

    def __init__(self, pos, font_path='data/PressStart2P-vaV7.ttf', size=44):
        self.font = pygame.font.Font(font_path, size)
        self.pos = pos
        self.text_template = ScoreBoard.text_template
        self.score = 0

    def get_score(self):
        return self.score

    def draw(self, screen):
        screen.blit(self.font.render(self.text_template.format(self.score), True, (255, 255, 255)), self.pos)


class FPSBoard:
    text_template = 'FPS:{}'

    def __init__(self, pos, font_path='data/PressStart2P-vaV7.ttf', size=28):
        self.font = pygame.font.Font(font_path, size)
        self.text_template = FPSBoard.text_template
        self.pos = pos

    def draw(self, screen, fps):
        screen.blit(self.font.render(self.text_template.format(fps), True, (255, 255, 255)), self.pos)


class LoopedImage(pygame.sprite.Sprite):
    def __init__(self, img_name, speed, screen_size, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.screen_size = screen_size
        self.image = load_im(img_name).convert_alpha()
        if self.screen_size[0] / self.screen_size[1] > 16 / 9:
            self.image = pygame.transform.scale(self.image, (self.screen_size[0], ceil(self.screen_size[0] / 16 * 9)))
        elif self.screen_size[0] / self.screen_size[1] < 16 / 9:
            self.image = pygame.transform.scale(self.image, (ceil(self.screen_size[1] / 9 * 16), self.screen_size[1]))
        else:
            self.image = pygame.transform.scale(self.image, self.screen_size)
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
        if self.screen_size[0] / self.screen_size[1] > 16 / 9:
            self.image = pygame.transform.scale(self.image, (self.screen_size[0], ceil(self.screen_size[0] / 16 * 9)))
        elif self.screen_size[0] / self.screen_size[1] < 16 / 9:
            self.image = pygame.transform.scale(self.image, (ceil(self.screen_size[1] / 9 * 16), self.screen_size[1]))
        else:
            self.image = pygame.transform.scale(self.image, self.screen_size)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    run_anim_count = 6
    run_anim_speed = 0.6
    jump_anim_count = 9
    jump_anim_speed = 0.5
    slide_anim_count = 4
    slide_anim_speed = 0.5
    vy = 0
    t = 0
    g = 5

    def __init__(self, pos, screen_size, *groups):
        super().__init__(*groups)
        self.screen_size = screen_size
        self.vy = Player.vy
        self.t = Player.t
        self.g = Player.g
        self.run_images = []
        self.run_anim_count = Player.run_anim_count
        self.run_anim_speed = Player.run_anim_speed
        self.run_anim_ind = 0
        self.jump_images = []
        self.jump_anim_count = Player.jump_anim_count
        self.jump_anim_speed = Player.jump_anim_speed
        self.jump_anim_index = 0
        self.slide_images = []
        self.slide_anim_count = Player.slide_anim_count
        self.slide_anim_speed = Player.slide_anim_speed
        self.slide_anim_index = 0
        self.in_jump = False
        self.in_slide = False
        self.load_animations()
        self.rect = self.run_images[0].get_rect()
        self.mask = pygame.mask.from_surface(self.run_images[0])
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]
        self.ground_y_coord = self.rect.y

    def load_animations(self):
        self.run_images = [
            pygame.transform.scale(
                load_im(f'player/run_{i}.png').convert_alpha(), (self.screen_size[1] // 5, self.screen_size[1] // 5)
            )
            for i in range(self.run_anim_count)
        ]
        self.jump_images = [
            pygame.transform.scale(
                load_im(f'player/jump_{i}.png').convert_alpha(), (self.screen_size[1] // 5, self.screen_size[1] // 5)
            )
            for i in range(self.jump_anim_count)
        ]
        self.slide_images = [
            pygame.transform.scale(
                load_im(f'player/slide_{i}.png').convert_alpha(), (self.screen_size[1] // 5, self.screen_size[1] // 5)
            )
            for i in range(self.slide_anim_count)
        ]

    def start_jump(self):
        if not self.in_jump:
            self.in_jump = True
            self.in_slide = False
            self.jump_anim_index = 0
            self.vy = randint(33, 38)
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

    def update(self):
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


class Game:
    def __init__(self, screen):
        self.screen_size = self.width, self.height = screen.get_width(), screen.get_height()
        self.screen = screen
        self.screens = (screen, screen)
        self.background = MySpriteGroup()
        self.clock = pygame.time.Clock()
        self.settings = dict()
        self.read_settings()
        self.load_objects()
        self.running = True
        self.in_game = True

    def read_settings(self):
        with open('data/settings.txt', encoding='UTF-8') as f:
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings[key] = value

    def load_objects(self):
        self.score_board = ScoreBoard((self.height // 80, self.height // 80))
        self.game_map = Map(self.screen_size)
        self.player = Player((200, self.height - self.height // 5), self.screen_size)
        Sky('bg/sky.png', self.screen_size, self.background)
        for i in range(1, self.settings['background_layers_count']):
            LoopedImage(f'bg/lay_{i}.png', 5 * i, self.screen_size, self.background)
        if self.settings['play_sfx']:
            self.coin_pick_up_sfx = pygame.mixer.Sound('data/sfx/coin_pick_up.mp3')
        if self.settings['show_fps']:
            self.fps_board = FPSBoard((self.width - 180, self.height // 80))

    def main_loop(self):
        while self.running:
            self.clock.tick(24)
            self.check_events()
            self.update()
            self.render()

    def check_events(self):
        for event in pygame.event.get():
            if self.in_game:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.player.start_jump()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_LCTRL or event.key == pygame.K_DOWN):
                    self.player.start_slide()
                if event.type == pygame.KEYUP and (event.key == pygame.K_LCTRL or event.key == pygame.K_DOWN):
                    self.player.stop_slide()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.restart()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        if self.in_game:
            self.player.update()
            self.game_map.update()
            self.background.update()
            for el in self.game_map.all_sprites:
                if pygame.sprite.collide_mask(self.player, el):
                    if isinstance(el, Coin):
                        if self.settings['play_sfx']:
                            self.coin_pick_up_sfx.play()
                        self.score_board.score += 1
                        self.game_map.free_coins.append(el)
                        el.kill()
                    elif isinstance(el, (Ghost, Rock)):
                        self.in_game = False

    def render(self):
        if self.settings['motion_blur']:
            self.screens = (self.screens[1], self.screen)
        self.screen.fill((0, 0, 0))
        self.background.draw(self.screen)
        self.player.draw(self.screen)
        self.game_map.draw(self.screen)
        self.score_board.draw(self.screen)
        if self.settings['show_fps']:
            self.fps_board.draw(self.screen, int(self.clock.get_fps()))
        if self.settings['motion_blur']:
            for i, el in enumerate(self.screens, 1):
                el.set_alpha(25 * i)
                self.screen.blit(el, (0, 0))
        pygame.display.update()

    def restart(self):
        self.in_game = True
        self.background.empty()
        self.load_objects()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('раннер')
    display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
    # display_size = 1280, 1024
    screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
    Game(screen).main_loop()
