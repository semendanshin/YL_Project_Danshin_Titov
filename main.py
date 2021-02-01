import pygame
from random import randint
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


class Ghost(pygame.sprite.Sprite):
    def __init__(self, speed, screen_size, pos=(0, 0), *groups):
        super().__init__(*groups)
        self.speed = speed
        self.anim_count = 3
        self.anim_ind = 0
        self.anim_speed = 0.4
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

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, screen_size, *groups):
        super().__init__(*groups)
        self.screen_size = screen_size
        self.vy = 0
        self.t = 0
        self.g = 5
        self.run_images = []
        self.jump_images = []
        self.slide_images = []
        self.run_anim_count = 6
        self.run_anim_ind = 0
        self.run_anim_speed = 0.6
        self.jump_anim_count = 9
        self.jump_anim_index = 0
        self.jump_anim_speed = 0.5
        self.slide_anim_count = 4
        self.slide_anim_index = 0
        self.slide_anim_speed = 0.5
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
        if self.rect.y == self.ground_y_coord:
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


class ScoreBoard:
    def __init__(self, pos, font_path='data/PressStart2P-vaV7.ttf', size=44):
        self.font = pygame.font.Font(font_path, size)
        self.text_template = 'Coins:{}'
        self.pos = pos
        self.score = 0

    def get_score(self):
        return self.score

    def draw(self, screen):
        screen.blit(self.font.render(self.text_template.format(self.score), True, (255, 255, 255)), self.pos)


class FPSBoard:
    def __init__(self, pos, font_path='data/PressStart2P-vaV7.ttf', size=28):
        self.font = pygame.font.Font(font_path, size)
        self.text_template = 'FPS:{}'
        self.pos = pos

    def draw(self, screen, fps):
        screen.blit(self.font.render(self.text_template.format(fps), True, (255, 255, 255)), self.pos)


class Map:
    def __init__(self, screen_size, filename):
        self.screen_size = screen_size
        self.all_sprites = MySpriteGroup()
        self.ghosts = MySpriteGroup()
        self.rocks = MySpriteGroup()
        self.coins = MySpriteGroup()
        self.free_ghosts = []
        self.free_rocks = []
        self.free_coins = []
        self.frame = 0
        self.cell_size = 150
        self.speed = 50
        self.load_freq = self.cell_size // self.speed
        self.read_map(filename)
        self.col_ind = 0
        self.ground = LoopedImage('ground.png', self.speed, self.screen_size, self.all_sprites)
        self.run = True

    def read_map(self, filename):
        with open(f'data/maps/{filename}', encoding='UTF-8') as f:
            self.game_map = [list(map(int, el.strip())) for el in f.readlines()]

    def load_next(self, col_count=1):
        if self.col_ind + col_count < len(self.game_map[0]):
            for i in range(col_count):
                for j in (self.game_map[0][self.col_ind + i],
                          self.game_map[1][self.col_ind + i]):
                    if j == 1:
                        if self.free_coins:
                            coin = self.free_coins.pop(0)
                            coin.set_pos((self.screen_size[0] + self.cell_size * i,
                                          self.screen_size[1] - self.screen_size[1] // 5))
                            self.coins.add(coin)
                            self.all_sprites.add(coin)
                        else:
                            Coin(self.speed, self.screen_size,
                                 (self.screen_size[0] + self.cell_size * i,
                                  self.screen_size[1] - self.screen_size[1] // 5),
                                 self.all_sprites, self.coins)
                    elif j == 2:
                        if self.free_rocks:
                            rock = self.free_rocks.pop(0)
                            rock.set_pos((self.screen_size[0] + self.cell_size * i,
                                          self.screen_size[1] - self.screen_size[1] // 5 + 5))
                            self.rocks.add(rock)
                            self.all_sprites.add(rock)
                        else:
                            Rock(self.speed, self.screen_size,
                                 (self.screen_size[0] + self.cell_size * i,
                                  self.screen_size[1] - self.screen_size[1] // 5 + 5),
                                 self.all_sprites, self.rocks)
                    elif j == 3:
                        if self.free_ghosts:
                            ghost = self.free_ghosts.pop(0)
                            ghost.set_pos((self.screen_size[0] + self.cell_size * i,
                                           self.screen_size[1] - self.screen_size[1] // 5 - 150))
                            self.ghosts.add(ghost)
                            self.all_sprites.add(ghost)
                        else:
                            Ghost(self.speed, self.screen_size,
                                  (self.screen_size[0] + self.cell_size * i,
                                   self.screen_size[1] - self.screen_size[1] // 5 - 150),
                                  self.all_sprites, self.ghosts)
            self.col_ind += col_count
        else:
            pass
            # self.finish_flag = FinishFlag((self.screen_size[0] + self.cell_size,
            #                                self.screen_size[1] - self.screen_size[1] // 5))

    def update(self):
        self.frame = (self.frame + 1) % self.load_freq
        if self.frame == 0:
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


class Game:
    def __init__(self, screen):
        self.screen_size = self.width, self.height = screen.get_width(), screen.get_height()
        self.screen = screen
        self.background = MySpriteGroup()
        self.clock = pygame.time.Clock()
        self.settings = dict()
        self.read_settings()
        self.load_objects()
        self.running = True
        self.updating = True

    def read_settings(self):
        with open('data/settings.txt', encoding='UTF-8') as f:
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings[key] = value

    def load_objects(self):
        self.coin_pick_up_sfx = pygame.mixer.Sound('data/sfx/coin_pick_up.mp3')
        self.fps_board = FPSBoard((self.width - 180, self.height // 80))
        self.score_board = ScoreBoard((self.height // 80, self.height // 80))
        self.game_map = Map(self.screen_size, '1.txt')
        self.player = Player((200, self.height - self.height // 5), self.screen_size)
        Sky('bg/sky.png', self.screen_size, self.background)
        for i in range(1, self.settings['background_layers_count']):
            LoopedImage(f'bg/lay_{i}.png', 5 * i, self.screen_size, self.background)

    def main_loop(self):
        while self.running:
            self.clock.tick(24)
            self.check_events()
            self.update()
            self.render()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                self.running = False
            if self.updating:
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                    self.player.start_jump()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_LCTRL or event.key == pygame.K_DOWN):
                    self.player.start_slide()
                if event.type == pygame.KEYUP and (event.key == pygame.K_LCTRL or event.key == pygame.K_DOWN):
                    self.player.stop_slide()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.restart()

    def update(self):
        if self.updating:
            self.player.update()
            self.game_map.update()
            self.background.update()
            for el in self.game_map.all_sprites:
                if pygame.sprite.collide_mask(self.player, el):
                    if isinstance(el, Coin):
                        self.coin_pick_up_sfx.play()
                        self.score_board.score += 1
                        self.game_map.free_coins.append(el)
                        el.kill()
                    elif isinstance(el, (Ghost, Rock)):
                        self.updating = False

    def render(self):
        self.screen.fill((0, 0, 0))
        self.background.draw(self.screen)
        self.player.draw(self.screen)
        self.game_map.draw(self.screen)
        self.score_board.draw(self.screen)
        self.fps_board.draw(self.screen, int(self.clock.get_fps()))
        pygame.display.update()

    def restart(self):
        self.updating = True
        self.background.empty()
        self.load_objects()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('раннер')
    display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
    # display_size = 1280, 1024
    screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
    Game(screen).main_loop()
