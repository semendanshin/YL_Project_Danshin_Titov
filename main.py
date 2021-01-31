import pygame, os


def load_im(name):
    fullname = f'imgs/{name}'
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
    def __init__(self, name, func, i, X, Y, *groups):
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
        return self.rect.collidepoint(pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, *args):
        pass


class CheckBox(pygame.sprite.Sprite):
    def __init__(self, i, X, Y, *groups):
        super().__init__(*groups)
        image0 = load_im('check0.png').convert_alpha()
        image1 = load_im('check1.png').convert_alpha()
        k = image1.get_height() / image1.get_width()
        self.image0 = pygame.transform.scale(image0, (X // 10, int(X // 10 * k)))
        self.image1 = pygame.transform.scale(image1, (X // 10, int(X // 10 * k)))
        self.i = i
        self.image = self.image0
        self.rect = self.image.get_rect()
        x, y = X // 2, Y // 2
        x += (self.rect.width + 20) * i
        self.rect.x, self.rect.y = x - self.rect.width // 2, y - self.rect.height // 2
        self.update(3)

    def update(self, ind):
        if ind == 4:
            return None
        if self.i == ind:
            self.image = self.image1
        else:
            self.image = self.image0

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.buttons = MySpriteGroup()
        ClickButton('button1.png', pp1, 0, screen.get_width(), screen.get_height(), self.buttons)
        ClickButton('button2.png', settings.main_loop, 1, screen.get_width(), screen.get_height(), self.buttons)
        ClickButton('button3.png', pp3, 2, screen.get_width(), screen.get_height(), self.buttons)

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.run_next_condition(event.pos)
            self.update()
            self.render()
            pygame.display.update()

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))
        self.buttons.draw(self.screen)

    def run_next_condition(self, pos):
        for bt in self.buttons.sprites():
            if bt.collide(pos):
                bt.func()


class Settings:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.checkboxs = MySpriteGroup()
        for _ in range(4):
            CheckBox(_, screen.get_width(), screen.get_height(), self.checkboxs)

    def main_loop(self):
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
        i = 0
        for sprite in self.checkboxs.sprites():
            if sprite.rect.collidepoint(pos):
                break
            i += 1
        self.checkboxs.update(i)

    def render(self):
        self.screen.fill((100, 0, 0))
        self.checkboxs.draw(self.screen)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('раннер')
    display_size = pygame.display.Info().current_w, pygame.display.Info().current_h
    SIZE = WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode(SIZE)
    settings = Settings(screen)
    menu = Menu(screen)
    menu.main_loop()