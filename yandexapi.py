import pygame as pg
import requests
import pyperclip
import os

pg.init()
COLOR_INACTIVE = (45, 52, 54)
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.SysFont('cmmi10', 15)
screen = pg.display.set_mode((823, 450))

delta = 1
z = "16"
map_file = "map1.jpg"
deltaLL = 0.02
running = True
Flag = False
typez = "map"


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.key != pg.K_v and event.key != pg.KMOD_CTRL and event.key != pg.K_RETURN:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, (53, 59, 72))

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)


class RadioButtun:
    def __init__(self, type, pos, checked=False, ):
        self.checked = checked
        self.type = type
        self.pos = pos
        self.raduis = 13
        self.rect = pg.Rect(pos[0] - self.raduis, pos[1] - self.raduis, self.raduis * 2, self.raduis * 2)

    def draw(self):
        if self.checked:
            self.color = (116, 185, 255)
        else:
            self.color = (255, 118, 117)

        pg.draw.circle(screen, self.color, self.pos, self.raduis, 3)

    def update(self, event):
        global typez, radiobuttons
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.checked = not self.checked
                typez = self.type
                get_map(areas[0].text, areas[1].text)


def get_delta(x):
    if float(x) < 16:
        return -0.0017948 * float(x) + 0.0282087
    else:
        return -(-0.0017948 * float(x) + 0.0282087)


def get_map(toponym_longitude, toponym_lattitude):
    global map_file, Flag, typez
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "z": z,
        "l": typez
    }

    if toponym_longitude and toponym_lattitude:
        response = requests.get(map_api_server, params=map_params)
        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
        else:
            with open(map_file, "wb") as file:
                file.write(response.content)
                Flag = True


def draw_text(line, pos, fz):
    f2 = pg.font.SysFont('serif', fz)
    text1 = f2.render(line, 1, (30, 144, 255))
    screen.blit(text1, pos)


radiobuttons = [RadioButtun("map", (620, 270), True), RadioButtun("sat", (620, 300)),
                RadioButtun("sat,skl", (620, 330))]

areas = [InputBox(610, 370, 30, 20), InputBox(610, 420, 30, 20)]
while running:
    for event in pg.event.get():

        if event.type == pg.QUIT:
            running = False
            if Flag:
                os.remove(map_file)

        for button in radiobuttons:
            button.update(event)

        radiobuttons.sort(key=lambda x: x.checked, reverse=True)

        if radiobuttons[1].checked:
            radiobuttons[0].checked = False

        radiobuttons.sort(key=lambda x: x.checked, reverse=True)

        for area in areas:
            area.handle_event(event)
            area.update()

        all_keys = pg.key.get_pressed()
        if all_keys[pg.K_LCTRL] or all_keys[pg.K_v]:
            for area in areas:
                if area.active:
                    spam = pyperclip.paste()
                    area.text = spam

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if areas[0].text and areas[1].text:
                    get_map(areas[0].text, areas[1].text)


            elif event.key == pg.K_PAGEUP:
                if int(z) + delta > 18:
                    z = "18"
                else:
                    z = str(int(z) + delta)
                get_map(areas[0].text, areas[1].text)

            elif event.key == pg.K_PAGEDOWN:
                if int(z) - delta <= 0:
                    z = "1"
                else:
                    z = str(int(z) - delta)
                get_map(areas[0].text, areas[1].text)

            if event.key in [pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN]:
                if event.key == pg.K_DOWN:
                    areas[1].text = str(float(areas[1].text) - get_delta(z))

                elif event.key == pg.K_UP:
                    areas[1].text = str(float(areas[1].text) + get_delta(z))

                elif event.key == pg.K_LEFT:
                    areas[0].text = str(float(areas[0].text) - get_delta(z))

                elif event.key == pg.K_RIGHT:
                    areas[0].text = str(float(areas[0].text) + get_delta(z))

                get_map(areas[0].text, areas[1].text)

    screen.fill((255, 255, 255))
    if Flag:
        screen.blit(pg.image.load(map_file), (0, 0))
    else:
        screen.blit(pg.image.load("map.jpg"), (0, 0))

    draw_text("Долгота", (614, 350), 15)
    draw_text("Широта", (614, 400), 15)
    draw_text("Схема", (640, 262), 15)
    draw_text("Спутник", (640, 292), 15)
    draw_text("Гибрид", (640, 322), 15)

    areas[0].draw(screen)
    areas[1].draw(screen)
    for button in radiobuttons:
        button.draw()
    pg.display.flip()
