import pygame as pg
from services import SONG_END
from cycles import Game


# TODO: Сделать частицы для персонажа
# TODO: Сделать ограничение для слайда


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('раннер')
    display_size = pg.display.Info().current_w, pg.display.Info().current_h
    screen = pg.display.set_mode(display_size, pg.FULLSCREEN)
    pg.mixer.music.set_endevent(SONG_END)
    Game(screen).main_loop()
