import os
import sys
import pygame as pg
from random import randint
from math import ceil

SONG_END = pg.USEREVENT + 1
pg.mixer.music.set_endevent(SONG_END)


def calculate_size_for_background(screen_size):
    if screen_size[0] / screen_size[1] > 16 / 9:
        return screen_size[0], ceil(screen_size[0] / 16 * 9)
    elif screen_size[0] / screen_size[1] < 16 / 9:
        return ceil(screen_size[1] / 9 * 16), screen_size[1]
    else:
        return screen_size


def load_im(name, colorkey=None):
    fullname = os.path.join('data', 'imgs', name)
    try:
        img = pg.image.load(fullname)
    except FileNotFoundError:
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    if colorkey:
        img = img.convert()
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey)
    else:
        img = img.convert_alpha()
    return img


class MusicPlayer:
    song_count = 5

    def __init__(self):
        pg.mixer.music.set_volume(0.1)
        self.song_count = MusicPlayer.song_count
        self.current_song = None
        self.next_song()

    def next_song(self):
        while True:
            next_song = randint(0, self.song_count - 1)
            if next_song != self.current_song:
                self.current_song = next_song
                break
        pg.mixer.music.load(f'data/sfx/bgm_action_{self.current_song}.mp3')
        pg.mixer.music.play(fade_ms=100)


class MySpriteGroup(pg.sprite.Group):
    def draw(self, surf):
        for el in self.sprites():
            el.draw(surf)
