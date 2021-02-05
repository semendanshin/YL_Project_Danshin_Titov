import pygame as pg
from cycles import Menu


# TODO: Сделать частицы для персонажа
# TODO: Сделать ограничение для слайда
# TODO: Переписать прыжок


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('раннер')
    display_size = pg.display.Info().current_w, pg.display.Info().current_h
    screen = pg.display.set_mode(display_size)
    Menu(screen).main_loop()
