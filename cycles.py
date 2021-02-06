from objects import *
import sys

FPS = 30


class Menu:
    """Главное меню меню"""

    buttons_count = 3

    def __init__(self, surf):
        self.screen_size = self.width, self.height = surf.get_width(), surf.get_height()
        self.surf = surf
        self.running = True
        self.settings = dict()
        self.buttons = MySpriteGroup()
        self.background = MySpriteGroup()
        self.clock = pg.time.Clock()
        self.read_settings()
        self.load_background()
        self.create_buttons()

    def create_buttons(self):
        """Создаёт кнопки"""
        for i in range(Menu.buttons_count):
            ClickButton(f'button{i}.png', i, self.height // 3, (self.width // 2, self.height // 2), self.buttons)

    def read_settings(self):
        """Чтение настроек из файла"""
        with open('data/settings.txt', encoding='UTF-8') as f:
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings[key] = value

    def load_background(self):
        """Загрузка фона"""
        if len(self.background) != self.settings['background_layers_count'] + 1:
            self.background.empty()
            size = calculate_size_for_background(self.screen_size)
            for i in range(0, self.settings['background_layers_count'] + 1):
                LoopedImage(f'bg/lay_{i}.png', 3 * i, size, self.background)

    def main_loop(self):
        """Основной цикл"""
        while self.running:
            self.clock.tick(FPS)
            self.check_events()
            self.update()
            self.render()

    def check_events(self):
        """Проверка событий"""
        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE or event.type == pg.QUIT:
                self.running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(self.buttons):
                    if button.rect.collidepoint(event.pos):
                        if i == 0:
                            Game(self.surf).main_loop()
                        elif i == 1:
                            Settings(self.surf).main_loop()
                            self.read_settings()
                            self.load_background()
                        if i == 2:
                            sys.exit(0)

    def update(self):
        """Обновление спрайтов"""
        self.background.update()

    def render(self):
        """Отрисовка спрайтов"""
        self.surf.fill((0, 0, 0))
        self.background.draw(self.surf)
        self.buttons.draw(self.surf)
        pg.display.update()


class Game:
    font = 'PressStart2P-vaV7.ttf'
    score_text_template = 'Score:{}'
    coins_text_template = 'Coins:{}'
    fps_text_template = 'FPS:{}'
    game_over_text_template = 'Press any key to start'

    def __init__(self, surf):
        self.screen_size = self.width, self.height = surf.get_width(), surf.get_height()
        self.background = MySpriteGroup()
        self.clock = pg.time.Clock()
        self.surf = surf
        self.settings = dict()
        self.running = True
        self.in_game = False
        self.max_score = 0
        self.score = 0
        self.coins_sum = 0
        self.coins = 0
        self.read_settings()
        self.load_objects()
        if self.settings['play_music']:
            self.music_player = MusicPlayer()

    def read_settings(self):
        """Чтение настроек из файла"""
        with open('data/settings.txt', encoding='UTF-8') as f:
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings[key] = value

    def load_objects(self):
        """Загрузка элеметов"""
        self.fps_font = pg.font.Font('data/' + Game.font, self.width // 80)
        self.score_and_coins_font = pg.font.Font('data/' + Game.font, self.width // 60)

        self.game_over_surf = pg.Surface(self.screen_size, pg.SRCALPHA)
        self.game_over_surf.fill((0, 0, 0))
        self.game_over_surf.set_alpha(150)
        game_over_text = pg.font.Font('data/' + Game.font, self.width // 40).render(
            Game.game_over_text_template.format(int(self.clock.get_fps())), True, (255, 255, 255)
        )
        self.game_over_surf.blit(game_over_text, (self.width // 2 - game_over_text.get_rect().w // 2,
                                                  self.height // 2 - game_over_text.get_rect().h // 2))

        size = calculate_size_for_background(self.screen_size)

        self.player = Player(
            (self.width // 10, self.height - self.height // 5), (self.height // 5, self.height // 5)
        )
        self.game_map = Map(self.screen_size, size)

        for i in range(0, self.settings['background_layers_count'] + 1):
            LoopedImage(f'bg/lay_{i}.png', 3 * i, size, self.background)

        if self.settings['play_sfx']:
            self.coin_pick_up_sfx = pg.mixer.Sound('data/sfx/coin_pick_up.mp3')
            self.death_sfx = pg.mixer.Sound('data/sfx/death.wav')
            self.death_sfx.set_volume(0.2)

    def main_loop(self):
        """Основной цикл"""
        while self.running:
            self.clock.tick(FPS)
            self.check_events()
            self.update()
            self.render()
        return self.coins_sum, self.max_score

    def check_events(self):
        """Проверка событий"""
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.settings['play_music']:
                        pg.mixer.music.stop()
                    self.running = False
                if self.in_game:
                    if event.key == pg.K_SPACE or event.key == pg.K_UP:
                        self.player.start_jump()
                    elif event.key == pg.K_LCTRL or event.key == pg.K_DOWN:
                        self.player.start_slide()
                else:
                    self.restart()
            elif event.type == pg.KEYUP:
                if self.in_game:
                    if event.key == pg.K_LCTRL or event.key == pg.K_DOWN:
                        self.player.stop_slide()
            elif event.type == pg.QUIT:
                pg.quit()
            elif event.type == SONG_END:
                self.music_player.next_song()

    def update(self):
        """Обновление спрайтов и других элеметов игры"""
        if self.in_game:
            self.score += 1
            if self.score % 500 == 0:
                self.game_map.up_speed()
            self.player.update()
            self.game_map.update()
            self.background.update()
            for el in pg.sprite.spritecollide(self.player, self.game_map.all_sprites, False, pg.sprite.collide_mask):
                if isinstance(el, Coin):
                    self.coins += 1
                    if self.settings['play_sfx']:
                        self.coin_pick_up_sfx.play()
                    self.game_map.free_coins.append(el)
                    el.kill()
                elif isinstance(el, (Ghost, Rock)):
                    self.in_game = False
                    self.coins_sum += self.coins
                    self.max_score = max(self.score, self.max_score)
                    if self.settings['play_sfx']:
                        self.death_sfx.play()

    def render(self):
        """Отрисовка спрайтов и текста"""
        self.surf.fill((0, 0, 0))
        self.background.draw(self.surf)
        self.player.draw(self.surf)
        self.game_map.draw(self.surf)
        score_text = self.score_and_coins_font.render(
                Game.score_text_template.format(self.score), True, (255, 255, 255)
            )
        coins_text = self.score_and_coins_font.render(
                Game.coins_text_template.format(self.coins), True, (255, 255, 255)
            )
        self.surf.blit(score_text, (10, 10))
        self.surf.blit(coins_text, (10, 20 + coins_text.get_rect().h))
        if self.settings['show_fps']:
            fps_text = self.fps_font.render(
                    Game.fps_text_template.format(int(self.clock.get_fps())), True, (255, 255, 255)
            )
            self.surf.blit(fps_text, (self.width - fps_text.get_rect().w - 10, 10))
        if not self.in_game:
            self.surf.blit(self.game_over_surf, (0, 0))
        pg.display.update()

    def restart(self):
        """Начать игру заново"""
        self.in_game = True
        self.score = 0
        self.coins = 0
        self.background.empty()
        self.load_objects()


class Settings:
    """Окно настроек"""
    options = 4
    number_of_options = [5, 2, 2, 2]

    def __init__(self, surf):
        self.screen_size = self.width, self.height = surf.get_width(), surf.get_height()
        self.surf = surf
        self.running = True
        self.settings = []
        self.settings_group = []
        self.clock = pg.time.Clock()
        self.background = MySpriteGroup()
        self.read_settings()
        self.load_background()
        self.create_settings()

    def create_settings(self):
        for i in range(len(self.settings)):
            self.settings_group.append(
                Setting(self.screen_size, i, Settings.number_of_options[i], self.settings[i][1])
            )

    def read_settings(self):
        """Чтение настроек из файла"""
        with open('data/settings.txt', encoding='UTF-8') as f:
            self.settings.clear()
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings.append((key, value))

    def load_background(self):
        """Загрузка фона"""
        if len(self.background) != self.settings[0][1] + 1:
            self.background.empty()
            size = calculate_size_for_background(self.screen_size)
            for i in range(0, self.settings[0][1] + 1):
                LoopedImage(f'bg/lay_{i}.png', 3 * i, size, self.background)

    def update_setting(self):
        """Перезаписывние настроек"""
        with open('data/settings.txt', 'w', encoding='utf8') as f:
            for i, el in enumerate(self.settings):
                f.write('=='.join([el[0], str(self.settings_group[i].get_checked_box_index())]) + '\n')

    def main_loop(self):
        """Основной цикл"""
        while self.running:
            self.clock.tick(FPS)
            self.check_events()
            self.update()
            self.render()

    def check_events(self):
        """Проверка событий"""
        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE or event.type == pg.QUIT:
                self.running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if any((el.update(event.pos) for el in self.settings_group)):
                    self.update_setting()
                    self.read_settings()
                    self.load_background()

    def update(self):
        """Обновление спрайтов"""
        self.background.update()

    def render(self):
        """Отрисовка спрайтов"""
        self.surf.fill((0, 0, 0))
        self.background.draw(self.surf)
        for el in self.settings_group:
            el.draw(self.surf)
        pg.display.update()
