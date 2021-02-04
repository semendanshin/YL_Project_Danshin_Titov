import pygame, os


'''
TODO: сделать нормальный текст
TODO: сделать или убрать магазин
'''

def load_im(name):
    fullname = f'data/imgs/{name}'
    try:
        return pygame.image.load(fullname)
    except FileNotFoundError:
        print(f"Файл с изображением '{fullname}' не найден")
        exit(0)


def pp1():
    print(1)
def pp2():
    print(2)
def pp3():
    print(3)


class MySpriteGroup(pygame.sprite.Group):
    def draw(self, screen):
        for el in self.sprites():
            el.draw(screen)

    def update(self, ind):
        for el in self.sprites():
            el.update(ind)


class ClickButton(pygame.sprite.Sprite):
    '''Класс создает кнопку на которую можно нажимать'''
    def __init__(self, name, func, i, X, Y, *groups):
        '''Кнопка хранит своё изображение, размеры, позицию, а также функцию, которая запускается при нажатии на нее'''
        super().__init__(*groups)
        self.name = name
        self.func = func
        im = load_im(name).convert_alpha()
        k = im.get_height() / im.get_width()
        self.image = pygame.transform.scale(load_im(name).convert_alpha(), (X // 7, int(X // 7 * k)))
        self.rect = self.image.get_rect()
        x, y = X // 2, Y // 2
        y += (self.rect.height + 50) * i
        self.rect.x, self.rect.y = x - self.rect.width // 2, y - self.rect.height // 2

    def collide(self, pos):
        '''проверка что точка лежит на кнопке'''
        return self.rect.collidepoint(pos)

    def draw(self, screen):
        '''отрисовка'''
        screen.blit(self.image, self.rect)

    def update(self, *args):
        pass


class CheckBox(pygame.sprite.Sprite):
    '''Класс создает check box'''
    def __init__(self, i, X, Y, x, y, check, *groups):
        '''хранит текущее состояние (картинка + число), размеры, позицию, картинки для всех возможных состояний'''
        super().__init__(*groups)
        image0 = load_im('check0.png').convert_alpha()
        image1 = load_im('check1.png').convert_alpha()
        k = image1.get_height() / image1.get_width()
        self.image0 = pygame.transform.scale(image0, (X // 10, int(X // 10 * k)))
        self.image1 = pygame.transform.scale(image1, (X // 10, int(X // 10 * k)))
        self.i = i
        self.image = self.image0
        self.rect = self.image.get_rect()
        x += (self.rect.width + 20) * i
        self.rect.x, self.rect.y = x - self.rect.width // 2, y - self.rect.height // 2
        self.type = 0
        self.update(check)

    def update(self, ind):
        '''если индекс кнопки, на которую нажали совпадает с индексом кнопки, но отображается картинка 1-ого состояния
        если передан индекс равный кол-во кнопок, значит нажатие было не по кнопкам'''
        if ind == len(self.groups()[0].sprites()):
            return None
        if self.i == ind:
            self.type = 1
            self.image = self.image1
        else:
            self.type = 0
            self.image = self.image0

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Setting:
    '''класс объеднидяет в себе полнцоенную настройку.
    Отображает параметр настройки, значения кнопок и сами кнопки, реализует все методы'''
    def __init__(self, i, n, check):
        self.group = MySpriteGroup()
        self.boxs = MySpriteGroup()
        x, y = 300, 100 + i * 250
        # создание и отрисовка описания настройки

        # создание и отрисовка пояснений к кнопка

        # создание и отрисовка кнопок
        for i in range(n):
            CheckBox(i, screen.get_width(), screen.get_height(), x, y, check, self.boxs)


    def update(self, pos):
        i = 0
        for sprite in self.boxs.sprites():
            if sprite.rect.collidepoint(pos):
                sprite.type = 1
                break
            i += 1
        self.boxs.update(i)

    def draw(self, screen):
        self.group.draw(screen)
        self.boxs.draw(screen)

    def get_clicked(self):
        '''возвращает индекс кнопки, которую нажали'''
        i = 0
        for sprite in self.boxs.sprites():
            if sprite.type == 1:
                return i
            i += 1


class Menu:
    '''главное меню'''
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.buttons = MySpriteGroup()
        ClickButton('button1.png', pp1, 0, screen.get_width(), screen.get_height(), self.buttons)
        ClickButton('button2.png', settings.main_loop, 1, screen.get_width(), screen.get_height(), self.buttons)
        ClickButton('button3.png', pp3, 2, screen.get_width(), screen.get_height(), self.buttons)

    def main_loop(self):
        self.update_background()
        self.render()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.run_next_condition(event.pos)
                    self.update_background()
                    self.render()
            pygame.display.update()

    def update_background(self):
        '''обновление фона'''
        with open('data/settings.txt', 'r', encoding='utf8') as f:
            n = int(f.readline().split('==')[1][0])
        self.background = []
        for i in range(n + 1):
            self.background.append(load_im(f'bg/lay_{i}.png'))

    def draw_background(self, screen):
        '''отрисовка фона'''
        for i in self.background:
            screen.blit(i, (0, 0))

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_background(self.screen)
        self.buttons.draw(self.screen)

    def run_next_condition(self, pos):
        '''запускается при нажатии кнопки и запускает состояние игры, которое соответствует кнопке'''
        for bt in self.buttons.sprites():
            if bt.collide(pos):
                bt.func()


class Settings:
    '''окно настроек'''
    options = 4
    number_of_options = [5, 2, 2, 2]

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.settings = []
        with open('data/settings.txt', 'r', encoding='utf8') as f:
            openes = list(map(lambda s: int(s.split('==')[1][0]), f.readlines()))
        for i in range(Settings.options):
            self.settings.append(Setting(i, Settings.number_of_options[i], openes[i]))

    def update_background(self):
        with open('data/settings.txt', 'r', encoding='utf8') as f:
            n = int(f.readline().split('==')[1][0])
        self.background = []
        for i in range(n + 1):
            self.background.append(load_im(f'bg/lay_{i}.png'))

    def draw_background(self, screen):
        for i in self.background:
            screen.blit(i, (0, 0))

    def main_loop(self):
        self.update_background()
        self.render()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.update(event.pos)
                    self.render()
            pygame.display.update()
        self.running = True

    def update(self, pos):
        for i in self.settings:
            i.update(pos)
            self.update_setting()
            self.update_background()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_background(self.screen)
        for i in self.settings:
            i.draw(self.screen)

    def update_setting(self):
        '''Функция обновляет настройки'''
        f = open('data/settings.txt', 'r', encoding='utf8')
        l = list(f.readlines())
        for i in range(len(l)):
            l[i] = l[i].split('==')[0] + '==' + str(self.settings[i].get_clicked()) + '\n'
        f.close()
        f = open('data/settings.txt', 'w', encoding='utf8')
        f.writelines(l)
        f.close()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('раннер')
    display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
    SIZE = WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode(SIZE)
    settings = Settings(screen)
    menu = Menu(screen)
    menu.main_loop()