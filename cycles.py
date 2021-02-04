from objects import *

FPS = 30


class Game:
    score_text_template = 'Coins:{}'
    fps_text_template = 'FPS:{}'
    game_over_text_template = 'Press any key to start'

    def __init__(self, surf):
        self.screen_size = self.width, self.height = surf.get_width(), surf.get_height()
        self.fps_font = pg.font.Font('data/PressStart2P-vaV7.ttf', self.width // 80)
        self.score_font = pg.font.Font('data/PressStart2P-vaV7.ttf', self.width // 60)
        self.background = MySpriteGroup()
        self.clock = pg.time.Clock()
        self.surf = surf
        self.settings = dict()
        self.running = True
        self.in_game = False
        self.score_sum = 0
        self.score = 0
        self.read_settings()
        self.load_objects()
        if self.settings['play_music']:
            self.music_player = MusicPlayer()

    def read_settings(self):
        with open('data/settings.txt', encoding='UTF-8') as f:
            for el in f.readlines():
                key, value = el.strip().split('==')
                value = int(value)
                self.settings[key] = value

    def load_objects(self):
        self.game_over_surf = pg.Surface(self.screen_size, pg.SRCALPHA)
        self.game_over_surf.fill((0, 0, 0))
        self.game_over_surf.set_alpha(150)
        game_over_text = pg.font.Font('data/PressStart2P-vaV7.ttf', self.width // 40).render(
            Game.game_over_text_template.format(int(self.clock.get_fps())), True, (255, 255, 255)
        )
        self.game_over_surf.blit(game_over_text, (self.width // 2 - game_over_text.get_rect().w // 2,
                                                  self.height // 2 - game_over_text.get_rect().h // 2))

        if self.width / self.height > 16 / 9:
            size = (self.width, ceil(self.width / 16 * 9))
        elif self.width / self.height < 16 / 9:
            size = (ceil(self.height / 9 * 16), self.height)
        else:
            size = self.screen_size

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
        while self.running:
            self.clock.tick(FPS)
            self.check_events()
            self.update()
            self.render()
        return self.score_sum + self.score

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
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
        if self.in_game:
            self.player.update()
            self.game_map.update()
            self.background.update()
            for el in pg.sprite.spritecollide(self.player, self.game_map.all_sprites, dokill=False):
                if pg.sprite.collide_mask(self.player, el):
                    if isinstance(el, Coin):
                        self.score += 1
                        if self.score % 10 == 0:
                            self.game_map.up_speed()
                        if self.settings['play_sfx']:
                            self.coin_pick_up_sfx.play()
                        self.game_map.free_coins.append(el)
                        el.kill()
                    elif isinstance(el, (Ghost, Rock)):
                        self.in_game = False
                        if self.settings['play_sfx']:
                            self.death_sfx.play()

    def render(self):
        self.surf.fill((0, 0, 0))
        self.background.draw(self.surf)
        self.player.draw(self.surf)
        self.game_map.draw(self.surf)
        self.surf.blit(
            self.score_font.render(
                Game.score_text_template.format(self.score), True, (255, 255, 255)
            ), (10, 10)
        )
        if self.settings['show_fps']:
            fps_text = self.fps_font.render(
                    Game.fps_text_template.format(int(self.clock.get_fps())), True, (255, 255, 255)
            )
            self.surf.blit(fps_text, (self.width - fps_text.get_rect().w - 10, 10))
        if not self.in_game:
            self.surf.blit(self.game_over_surf, (0, 0))
        pg.display.update()

    def restart(self):
        self.in_game = True
        self.score_sum += self.score
        self.score = 0
        self.background.empty()
        self.load_objects()
