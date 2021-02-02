import pygame as pg
from random import choice

SONG_END = pg.USEREVENT + 1


def load_im(name):
    fullname = f'data/imgs/{name}'
    try:
        return pg.image.load(fullname)
    except FileNotFoundError:
        print(f"Файл с изображением '{fullname}' не найден")
        exit(0)


class MusicPlayer:
    song_count = 6

    def __init__(self):
        pg.mixer.music.set_volume(0.1)
        self.song_count = MusicPlayer.song_count
        self.current_song = None
        self.songs = [open(f'data/sfx/bgm_action_{i}.mp3', 'rb') for i in range(self.song_count)]
        self.next_song()

    def next_song(self):
        while True:
            next_song = choice(self.songs)
            if next_song != self.current_song:
                break
        pg.mixer.music.load(next_song)
        pg.mixer.music.play()


class MySpriteGroup(pg.sprite.Group):
    def draw(self, surf):
        for el in self.sprites():
            el.draw(surf)
