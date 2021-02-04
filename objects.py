from math import floor, ceil
from random import choice
from services import *


class Player(pg.sprite.Sprite):
    run_anim_count = 6
    run_anim_speed = 0.5
    jump_anim_count = 9
    jump_anim_speed = 0.5
    slide_anim_count = 4
    slide_anim_speed = 0.5

    def __init__(self, pos, im_size, *groups):
        super().__init__(*groups)
        self.vy = im_size[0] // 6
        self.g = self.vy // 6
        self.t = 0
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
        self.load_animations(im_size)
        self.rect = self.run_images[0].get_rect()
        self.mask = pg.mask.from_surface(self.run_images[0])
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]
        self.ground_y_coord = self.rect.y

    def load_animations(self, im_size):
        self.run_images = [
            pg.transform.scale(
                load_im(f'player/run_{i}.png').convert_alpha(), im_size
            )
            for i in range(self.run_anim_count)
        ]
        self.jump_images = [
            pg.transform.scale(
                load_im(f'player/jump_{i}.png').convert_alpha(), im_size
            )
            for i in range(self.jump_anim_count)
        ]
        self.slide_images = [
            pg.transform.scale(
                load_im(f'player/slide_{i}.png').convert_alpha(), im_size
            )
            for i in range(self.slide_anim_count)
        ]

    def start_jump(self):
        if not self.in_jump and self.rect.y == self.ground_y_coord:
            self.jump_anim_index = 0
            self.in_slide = False
            self.in_jump = True
            self.t = 0

    def start_slide(self):
        if not self.in_slide:
            self.slide_anim_index = 0
            self.in_slide = True
            self.in_jump = False

    def stop_slide(self):
        if self.in_slide:
            self.rect.y = self.ground_y_coord
            self.in_slide = False

    def update(self):
        if self.in_jump:
            if self.rect.y + (-self.vy + self.g * self.t) >= self.ground_y_coord:
                self.rect.y = self.ground_y_coord
                self.in_jump = False
            else:
                self.rect.y += (-self.vy + self.g * self.t)
            if self.jump_anim_count - 1 - self.jump_anim_index > 0:
                self.jump_anim_index += self.jump_anim_speed
                self.mask = pg.mask.from_surface(self.jump_images[floor(self.jump_anim_index)])
            self.t += 1
        elif self.in_slide:
            if self.rect.y + 40 < self.ground_y_coord:
                self.rect.y += 40
            else:
                self.rect.y = self.ground_y_coord
            if self.slide_anim_count - 1 - self.slide_anim_index > 0:
                self.slide_anim_index += self.slide_anim_speed
                self.mask = pg.mask.from_surface(self.slide_images[floor(self.slide_anim_index)])
        else:
            self.run_anim_ind = (self.run_anim_ind + self.run_anim_speed) % (self.run_anim_count - 1)
            self.mask = pg.mask.from_surface(self.run_images[floor(self.run_anim_ind)])

    def draw(self, surf):
        if self.in_jump:
            surf.blit(self.jump_images[floor(self.jump_anim_index)], self.rect)
        elif self.in_slide:
            surf.blit(self.slide_images[floor(self.slide_anim_index)], self.rect)
        else:
            surf.blit(self.run_images[floor(self.run_anim_ind)], self.rect)


class Map:
    cell_size = 300
    speed = 30
    first_floor = [0] * 2 + [1] * 4 + [2] * 4
    second_floor = [0] * 7 + [3] * 3

    def __init__(self, screen_size, ground_size):
        self.screen_size = screen_size
        self.all_sprites = MySpriteGroup()
        self.ghosts = MySpriteGroup()
        self.rocks = MySpriteGroup()
        self.coins = MySpriteGroup()
        self.free_ghosts = []
        self.free_rocks = []
        self.free_coins = []
        self.first_floor = Map.first_floor
        self.second_floor = Map.second_floor
        self.frame = 0
        self.cell_size = Map.cell_size
        self.speed = Map.speed
        self.load_freq = ceil(self.cell_size / self.speed)
        self.game_map = [[0, 0], [0, 0]]
        self.ground = LoopedImage('ground.png', self.speed, ground_size, self.all_sprites)

    def up_speed(self):
        self.speed += 1
        self.ground.set_speed(self.speed)
        self.load_freq = ceil(self.cell_size / self.speed)

    def generate_next(self):
        new_items = []
        while True:
            item = choice(self.first_floor)
            if self.game_map[-2][0] != 2 and self.game_map[-1][0] != 2 and self.game_map[-1][1] != 3 or item != 2:
                new_items.append(item)
                break
        while True:
            item = choice(self.second_floor)
            if new_items[0] != 2 and self.game_map[-1][0] != 2 and self.game_map[-1][1] != 3 or item != 3:
                new_items.append(item)
                break
        self.game_map.append(new_items)

    def load_next(self):
        for el in self.game_map[-1]:
            if el == 1:
                if self.free_coins:
                    coin = self.free_coins.pop(0)
                    coin.set_pos((self.screen_size[0] + self.cell_size,
                                  self.screen_size[1] - self.screen_size[1] // 5 - 10))
                    coin.set_speed(self.speed)
                    self.coins.add(coin)
                    self.all_sprites.add(coin)
                else:
                    Coin('coin.png', self.speed, (self.screen_size[1] // 15, self.screen_size[1] // 15),
                         (self.screen_size[0] + self.cell_size,
                          self.screen_size[1] - self.screen_size[1] // 5 - 10),
                         self.all_sprites, self.coins)
            elif el == 2:
                if self.free_rocks:
                    rock = self.free_rocks.pop(0)
                    rock.set_pos((self.screen_size[0] + self.cell_size,
                                  self.screen_size[1] - self.screen_size[1] // 5 + 5))
                    rock.set_speed(self.speed)
                    self.rocks.add(rock)
                    self.all_sprites.add(rock)
                else:
                    Rock('rock.png', self.speed, (self.screen_size[1] // 9, self.screen_size[1] // 9),
                         (self.screen_size[0] + self.cell_size,
                          self.screen_size[1] - self.screen_size[1] // 5 + 5),
                         self.all_sprites, self.rocks)
            elif el == 3:
                if self.free_ghosts:
                    ghost = self.free_ghosts.pop(0)
                    ghost.set_pos((self.screen_size[0] + self.cell_size,
                                   self.screen_size[1] - self.screen_size[1] // 5 - self.screen_size[1] // 8))
                    ghost.set_speed(self.speed)
                    self.ghosts.add(ghost)
                    self.all_sprites.add(ghost)
                else:
                    Ghost('ghost.png', self.speed, (self.screen_size[1] // 9, self.screen_size[1] // 9),
                          (self.screen_size[0] + self.cell_size,
                           self.screen_size[1] - self.screen_size[1] // 5 - self.screen_size[1] // 8),
                          self.all_sprites, self.ghosts)
        self.game_map = self.game_map[1:]

    def update(self):
        for el in self.all_sprites:
            if el.rect.x < -100:
                el.kill()
                if isinstance(el, Coin):
                    self.free_coins.append(el)
                elif isinstance(el, Ghost):
                    self.free_ghosts.append(el)
                else:
                    self.free_rocks.append(el)
        if self.frame == 0:
            self.generate_next()
            self.load_next()
        self.frame = (self.frame + 1) % self.load_freq
        self.all_sprites.update()

    def draw(self, surf):
        self.all_sprites.draw(surf)


class StaticObject(pg.sprite.Sprite):
    def __init__(self, filename, speed, size, pos=(0, 0), *groups):
        super().__init__(*groups)
        self.speed = speed
        self.image = pg.transform.scale(load_im(filename).convert_alpha(), size)
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_pos(self, pos):
        self.rect.x, self.rect.y = pos[0], pos[1] - self.rect.size[1]

    def set_speed(self, speed):
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Coin(StaticObject):
    pass


class Ghost(StaticObject):
    pass


class Rock(StaticObject):
    pass


class LoopedImage(pg.sprite.Sprite):
    def __init__(self, img_name, speed, size, *groups):
        super().__init__(*groups)
        self.speed = speed
        self.image = pg.transform.scale(load_im(img_name).convert_alpha(), size)
        self.rect = self.image.get_rect()
        self.shift = 0

    def set_speed(self, speed):
        self.speed = speed

    def update(self):
        self.shift = (self.shift + self.speed) % self.rect.w

    def draw(self, surf):
        surf.blit(self.image, (-self.shift, self.rect.y))
        surf.blit(self.image, (self.rect.w - self.shift, self.rect.y))
