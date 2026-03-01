import pygame as pg
import copy as cp
import random as rnd

import base64
import tempfile

# КОНФЛІКТНА СПРОБА НОМЕРР 2

""" -----------------------Шрифт------------------------------"""
font_base64 = """

"""

font_bytes = base64.b64decode(font_base64)
temp_font = tempfile.NamedTemporaryFile(delete=False, suffix=".ttf")
temp_font.write(font_bytes)
temp_font.close()

""" ------------------Додаткові функції--------------------------"""
def isOnGrid(pos):
    """
	Перевіряє, чи знаходиться позиція курсора на сітці чи ні
    """
    if 65 < pos[0] < 385 and 65 < pos[1] < 385:
        return True
    else:
        return False


def quitGame():
    pg.display.quit()
    quit()


def maxWeight(list):
    """
	Шукає найкращий хід для AI серед різних ходів.
    """
    max = list[0]
    maxIndex = (0, 0)
    for i in range(len(list)):
        for j in range(1, len(list[i])):
            if list[i][j][0] > max[0][0]:
                max = list[i]
                maxIndex = (i, j)
    return (maxIndex)


""" ---------------------------Гравець/IA--------------------------"""
class Player:
    """
    Об'єкт гравця
    """
    def __init__(self, id=0):
        self.id = id
        self.points = 0
        self.draw = []

    def update(self, pieces):
        """
        Перевіряє, чи панель з фігурами є пуста
        """
        if len(self.draw) == 0:
            for i in range(3):
                self.draw.append(pieces.histories[self.id][0])
                pieces.histories[self.id].remove(pieces.histories[self.id][0])


class IA(Player):
    """
	Об'єкт IA
    """

    def __init__(self):
        Player.__init__(self)
        self.id = 1

    def determineWhatToPlay(self, grid):
        """
		Симулює всі можливі ходи з поточними фігурами IA на копії сітки, оцінює кожен хід і повертає найкращий варіант
		"""
        drawLength = len(self.draw)
        weight = [[[0, 0, 0, 0] for j in range(100)] for i in range(drawLength)]
        for piece in range(drawLength):
            cpt = 0
            for i in range(grid.size - 2):
                for j in range(grid.size - 2):
                    ghostGrid = cp.deepcopy(grid)

                    weight[piece][cpt][1] = i
                    weight[piece][cpt][2] = j
                    weight[piece][cpt][3] = self.draw[piece]

                    if ghostGrid.isPiecePlaceable(i, j, self.draw[piece].figureNumber):
                        weight[piece][cpt][0] += 1
                        ghostGrid.putPiece(i + 1, j + 1, self.draw[piece])
                        ghostGrid.isThereAlignment()
                        weight[piece][cpt][0] += len(ghostGrid.linesCompleted)
                    cpt += 1
        choice = maxWeight(weight)
        return weight[choice[0]][choice[1]]


""" ---------------------------Сітка--------------------------"""
class Grid:
    def __init__(self, size, Pieces):
        self.size = size + 2
        self.grid = []

        self.Pieces = Pieces

        self.linesCompleted = []

    def init(self):
        """
        Cтворює сітку
        """
        for i in range(self.size):
            self.grid.append([])
            for j in range(self.size):
                self.grid[i].append(0)

    def print(self):
        """
        Виводить сітку в консоль
        """
        for row in reversed(self.grid):
            print(' '.join(str(cell) if cell != 0 else '.' for cell in row))

    def definePhysicalLimits(self):
        """
        Створює рамку з одиниць по краях сітки (щоб обмежити зону для фігур)
        """
        for i in range(self.size):
            self.grid[i][0] = 1
            self.grid[0][i] = 1
            self.grid[self.size - 1][i] = 1
            self.grid[i][self.size - 1] = 1

    def isPiecePlaceable(self, x, y, figure):
        """
        Перевіряє, чи можна розмістити фігуру
        """
        x -= 2
        y -= 2
        err = 0
        for i in range(5):
            for j in range(5):
                try:
                    if self.grid[x + i][y + j] and int(self.Pieces.pieces[figure][i][j]):
                        err += 1
                except:
                    pass
        if err:
            return False
        else:
            return True

    def putPiece(self, x, y, Piece):
        """
        Розміщує фігуру
        """
        x -= 2
        y -= 2
        for i in range(5):
            for j in range(5):
                try:
                    self.grid[x + i][y + j] += int(Piece.figure[i][j])
                except:
                    pass

    def isThereAlignment(self):
        """
        Перевіряє повністю заповнені рядки або стовпці
        """
        for i in range(self.size - 2):
            line = 0
            column = 0
            for j in range(self.size - 2):
                if self.grid[1 + i][1 + j]:
                    line += 1
                if self.grid[1 + j][1 + i]:
                    column += 1
            if line == self.size - 2:
                self.linesCompleted.append(['r', 1 + i])
            if column == self.size - 2:
                self.linesCompleted.append(['c', 1 + i])

    def eraseAlignment(self):
        """
        Стирає всі виявлені повністю заповнені рядки або стовпці
        """
        for i in self.linesCompleted:
            if i[0] == 'c':
                for j in range(self.size - 2):
                    self.grid[1 + j][i[1]] = 0
            if i[0] == 'r':
                for j in range(self.size - 2):
                    self.grid[i[1]][1 + j] = 0
            self.linesCompleted.remove(i)

    def isDrawPlaceable(self, Player):
        """
        Перевіряє, чи гравець може розмістити хоч одну з фігур з своєї панелі
        """
        err = 0
        for piece in Player.draw:
            for x in range(self.size - 2):
                for y in range(self.size - 2):
                    if not self.isPiecePlaceable(1 + x, 1 + y, piece.figureNumber):
                        err += 1
        if err == ((self.size - 2) ** 2) * len(Player.draw):
            return False
        else:
            return True


""" --------------------------Фігури---------------------------"""
class Pieces:
    """
    Набір фігур
    """
    def __init__(self):
        self.pieces = (
            ['00000', '00000', '00100', '00000', '00000'],  # 0  : Одиночний блок
            ['00000', '00000', '00110', '00000', '00000'],  # 1  : Лінія з 2 горизонтальних блоків
            ['00000', '00000', '00100', '00100', '00000'],  # 2  : Лінія з 2 вертикальних блоків
            ['00000', '00000', '01110', '00000', '00000'],  # 3  : Лінія з 3 горизонтальних блоків
            ['00000', '00100', '00100', '00100', '00000'],  # 4  : Лінія з 3 вертикальних блоків
            ['00000', '00000', '01100', '00100', '00000'],  # 5  : Гачок звичайний (ліворуч униз)
            ['00000', '00000', '00110', '00100', '00000'],  # 6  : Гачок вправо
            ['00000', '00000', '00100', '00110', '00000'],  # 7  : Гачок вгору вправо
            ['00000', '00000', '00100', '01100', '00000'],  # 8  : Гачок вгору вліво
            ['00000', '00000', '00110', '00110', '00000'],  # 9  : Блок 2x2
            ['00000', '01110', '01110', '01110', '00000'],  # 10 : Блок 3x3
            ['00000', '00000', '01111', '00000', '00000'],  # 11 : Лінія з 4 горизонтальних блоків
            ['00000', '00100', '00100', '00100', '00100'],  # 12 : Лінія з 4 вертикальних блоків
            ['00000', '00000', '11111', '00000', '00000'],  # 13 : Лінія з 5 горизонтальних блоків
            ['00100', '00100', '00100', '00100', '00100'],  # 14 : Лінія з 5 вертикальних блоків
            ['00000', '01110', '00100', '00000', '00000'],  # 15 : Маленька T-фігура (вгору)
            ['00000', '00000', '00100', '01110', '00000'],  # 16 : Маленька T-фігура (вниз)
            ['00000', '00100', '00110', '00100', '00000'],  # 17 : Маленька T-фігура (ліворуч)
            ['00000', '00100', '01100', '00100', '00000'],  # 18 : Маленька T-фігура (вправо)
            ['00000', '11100', '00100', '00100', '00000'],  # 19 : Великий гачок (знизу вліво)
            ['00000', '00100', '00100', '11100', '00000'],  # 20 : Великий гачок вгору вліво
            ['00000', '00111', '00100', '00100', '00000'],  # 21 : Великий гачок вправо
            ['00000', '00100', '00100', '00111', '00000'],  # 22 : Великий гачок вгору вправо
            ['00000', '01100', '00100', '00100', '00000'],  # 23 : Г-фігура (ліворуч)
            ['00000', '00110', '00100', '00100', '00000'],  # 24 : Г-фігура (варіант)
            ['00000', '00100', '00100', '01100', '00000'],  # 25 : Г-фігура (інша форма)
            ['00000', '00100', '00100', '00110', '00000'],  # 26 : Г-фігура (вгору)
            ['00000', '00000', '01100', '00110', '00000'],  # 27 : Змія (ліва)
            ['00000', '00000', '01100', '01100', '00000'],  # 28 : Змія (паралельна)
            ['00000', '00100', '00110', '00010', '00000'],  # 29 : Змія (вигнута вліво)
            ['00000', '00010', '00110', '00100', '00000'],  # 30 : Змія (вигнута вправо)
            ['00000', '01110', '00100', '00100', '00000'],  # 31 : T-фігура (вгору)
            ['00000', '00100', '00100', '01110', '00000'],  # 32 : T-фігура (вниз)
            ['00000', '00100', '00111', '00100', '00000'],  # 33 : T-фігура (вертикальна)
            ['00000', '00100', '11100', '00100', '00000']   # 34 : T-фігура (горизонтальна)
        )

        self.probs = [[8.5, 15.5, 22.5, 30.75, 39, 43.125, 47.25, 51.375, 55.5, 72, 84.5, 92.25, 100, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200],
                      [8.5, 14.5, 20.5, 27, 33.5, 37.125, 40.75, 44.375, 48, 63, 73, 78, 83, 87.5, 92, 94, 96, 98, 100, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200],
                      [6.5, 11.75, 17, 22.75, 28.5, 31.75, 35, 38.25, 41.5, 54, 63.5, 68.25, 73, 76.75, 80.5, 82.125, 83.75, 85.375, 87, 88.625, 90.25, 91.875, 93.5, 95.125, 96.75, 98.375, 100, 200, 200, 200, 200, 200, 200, 200, 200],
                      [5.5, 9.25, 13, 18.75, 24.5, 57.375, 30.25, 33.125, 36, 46.5, 55, 59.25, 63.5, 67.25, 71, 72.625, 74.25, 75.875, 77.5, 79.125, 80.75, 82.375, 84, 85.375, 86.75, 88.125, 89.5, 90.875, 92.25, 93.625, 95, 96.25, 97.5, 98.75, 100]]

        self.stage = 500
        self.level = 0

        self.history = []
        self.history2 = []
        self.histories = [self.history, self.history2]

    def alea(self):
        """
        Визначає випадкову фігуру
        """
        nb = rnd.randint(0, 100)
        figure = 0
        for i in range(0, 34):
            if nb <= self.probs[self.level][0]:
                figure = 0
            elif nb > self.probs[self.level][i] and nb <= self.probs[self.level][i + 1]:
                figure = i + 1
        return figure

    def update(self, Players):
        """
        Перевіряє, чи історія порожня, щоб заповнити її, та перевіряє, чи потрібно збільшити рівень
        """
        if len(self.history) == 0 or len(self.history2) == 0:
            for i in range(3):
                randFigure = self.alea()
                randColor = rnd.randint(1, 7)
                self.history.append(Piece(randFigure, randColor))
                self.history2.append(Piece(randFigure, randColor))
        for j in Players:
            if j.points // self.stage > 4 and self.level < 3:
                self.level += 1
                self.stage *= 1.25


class Piece(Pieces):
    """
    Об'єкт фігури
    """
    def __init__(self, figure, color):
        Pieces.__init__(self)
        self.color = piecescolors[color]
        self.figureNumber = figure
        self.color = color
        self.figure = self.applyColor(figure)
        self.x = -500
        self.y = 500
        self.dragged = False
        self.rect = pg.Rect(self.x, self.y, 160, 160)

    def repair(self, string):
        """
        Виправляє строкове значення числа так, щоб воно мало довжину 5 символів (3 - 00003)
        """
        stringLength = len(string)
        backup = string
        if stringLength != 5:
            string = '0'
            for i in range(4 - stringLength):
                string += '0'
            string += backup
        return string

    def applyColor(self, figure):
        """
        Змінює значення фігури, щоб зафарбувати її
        """
        piece = self.pieces[figure]
        for i in range(5):
            piece[i] = int(piece[i])
            piece[i] *= self.color
            piece[i] = str(piece[i])
            piece[i] = self.repair(piece[i])
        return piece

    def drawPiece(self, win):
        """
        Малює фігуру на екрані
        """
        for i in range(5):
            for j in range(5):
                if int(self.figure[i][j]) != 0:
                    pg.draw.rect(win, piecescolors[self.color], (self.x + 32 * i + 2, self.y + 32 * j + 2, 30, 30))

    def update(self, win):
        """
        Якщо фігуру тягнуть мишкою, її координати оновлюються відповідно до положення курсору
        """
        mousePos = pg.mouse.get_pos()
        if self.dragged:
            self.x = mousePos[0] - 80
            self.y = mousePos[1] - 80
        self.rect.x = self.x
        self.rect.y = self.y


""" ---------------------------Виведення на екран--------------------------"""
piecescolors = (
    (0, 0, 0),  # Щоб не було помилки
    (255, 241, 171),  # Жовтий
    (255, 196, 196),  # Червоний
    (161, 255, 170),  # Зелений
    (186, 238, 255),  # Синій
    (166, 255, 236),  # М’ятний зелений
    (240, 247, 244),  # Кремовий
    (255, 214, 239)  # Рожевий
)

BACKGROUNDCOLOR = (125, 201, 255)
BOARDCOLOR = (77, 164, 227)
CREAM = (240, 247, 244)
REDPINK = (255, 143, 137)
GREEN = (141, 232, 150)
NAVY = (7, 51, 92)
YELLOW = (255, 207, 74)
GRAY = (41, 41, 41)
RED = (219, 109, 103)
PINK = (255, 214, 239)
BLUE = (85, 169, 237)
LIGHTBLUE = (186, 233, 255)

margin = 2

pg.font.init()
font = pg.font.Font(temp_font.name, 25)
bigFont = pg.font.Font(temp_font.name, 100)
bigMediumFont = pg.font.Font(temp_font.name, 60)
mediumFont = pg.font.Font(temp_font.name, 40)
smallFont = pg.font.Font(temp_font.name, 25)

gameover = bigFont.render("Результат", True, GRAY)
gameoverShadow = bigFont.render("Результат", True, RED)
gameoverM = gameover
gameoverShadowM = gameoverShadow
J1 = font.render("Гравець 1 : ", True, GRAY)
J2 = font.render("Гравець 2 : ", True, GRAY)
JIA = font.render("IA : ", True, GRAY)
JYou = font.render("Гравець : ", True, GRAY)
Winner = mediumFont.render("Переможець : ", True, GRAY)

VJ1 = mediumFont.render("Гравець 1 ", True, GRAY)
VJ2 = mediumFont.render("Гравець 2 ", True, GRAY)
VIA = mediumFont.render("IA ", True, GRAY)
VYou = mediumFont.render("Гравець ", True, GRAY)
Vnope = mediumFont.render("Ніч'я! ", True, GRAY)

quitText1 = mediumFont.render("Вийти", True, GRAY)

puzzle = bigFont.render("Блок-пазл", True, NAVY)
puzzleShadow = bigFont.render("Блок-пазл", True, BOARDCOLOR)

multiplayerText = bigMediumFont.render("Мультиплеєр", True, NAVY)
multiplayerTextShadow = bigMediumFont.render("Мультиплеєр", True, BOARDCOLOR)
localText = mediumFont.render("Гравець 1 х Гравець 2 (Локал)", True, NAVY)
localTextHover = mediumFont.render("Гравець 1 х Гравець 2 (Локал)", True, RED)
iaText = mediumFont.render("Гравець х IA", True, NAVY)
iaTextHover = mediumFont.render("Гравець х IA", True, RED)

soloText = mediumFont.render("СОЛО", True, NAVY)
multiText = mediumFont.render("МУЛЬТИ", True, NAVY)
quitText = mediumFont.render("ВИХІД", True, NAVY)
restart = mediumFont.render("Рестарт", True, GRAY)

returnText = mediumFont.render("НАЗАД", True, NAVY)
returnMenuText = smallFont.render("НАЗАД", True, NAVY)
returnMenuText1 = smallFont.render("НАЗАД", True, CREAM)


def displayMenu(win):
    """
    Відображає головне меню
    """
    win.fill(BACKGROUNDCOLOR)
    pg.draw.rect(win, BOARDCOLOR, (155, 323, 150, 45))
    pg.draw.rect(win, BOARDCOLOR, (155, 388, 150, 45))
    pg.draw.rect(win, BOARDCOLOR, (155, 453, 150, 45))

    win.blit(puzzleShadow, (57, 170))
    win.blit(puzzle, (53, 165))

    pg.draw.rect(win, NAVY, (0, 670, 450, 30))


def displayMulti(win):
    """
    Відображає меню для вибору мультиплеєру
    """
    win.fill(BACKGROUNDCOLOR)
    win.blit(multiplayerTextShadow, (103, 73))
    win.blit(multiplayerText, (100, 70))
    pg.draw.rect(win, BOARDCOLOR, (155, 453, 150, 45))

    pg.draw.rect(win, NAVY, (0, 670, 450, 30))


def displayBoard(win, blitCoord, grid):
    """
    Виводить ігрове поле
    """
    boxWidth = 30
    win.fill(BACKGROUNDCOLOR)
    for i in range(0, grid.size - 2):
        for j in range(0, grid.size - 2):
            cell = grid.grid[1 + i][1 + j]
            if cell != 0:
                pg.draw.rect(win, piecescolors[cell % 8], (
                    blitCoord[0] + (margin + boxWidth) * i + margin, blitCoord[1] + (margin + boxWidth) * j + margin,
                    boxWidth, boxWidth))

            else:
                pg.draw.rect(win, BOARDCOLOR, (
                    blitCoord[0] + (margin + boxWidth) * i + margin, blitCoord[1] + (margin + boxWidth) * j + margin,
                    boxWidth, boxWidth))

    pg.draw.rect(win, NAVY, (0, 670, 450, 30))
    pg.draw.rect(win, BOARDCOLOR, (345, 620, 85, 30))


def displayDrawPieces(Player):
    """
    Визначає координати фігур, що розігруються
    """
    j = 0
    for i in Player.draw:
        if not i.dragged:
            i.x = j
            i.y = 400
            j += 140

def displayTextsSolo(win: object, Player: object) -> object:
    """
    Виводить інформацію про очки та номер гравця в соло
    """
    score = font.render("Очки: " + str(Player.points), True, NAVY)
    win.blit(score, (200, 20))

def displayTextsLocal(win, Player, currentBrick):
    """
    Виводить інформацію про гравця, очки та скільки фігур залишилось до зміни гравця
    """
    score = font.render("Очки: " + str(Player.points), True, NAVY)
    win.blit(score, (20, 20))

    currentPlayer = font.render("Гравець №: " + str(Player.id + 1), True, NAVY)
    win.blit(currentPlayer, (280, 20))

    leftBrick = font.render("Залишилось: " + str(currentBrickSetting - currentBrick), True, NAVY)
    win.blit(leftBrick, (120, 20))

def displayTextsIA(win, Players):
    """
    Виводить очки гравця і штучного інтелекту
    """
    score = font.render("Очки: " + str(Players[0].points), True, NAVY)
    score1 = font.render("Очки IA: " + str(Players[1].points), True, NAVY)
    win.blit(score, (20, 20))
    win.blit(score1, (320, 20))


def displayGameOverSolo(win, Player):
    """
    Малювання екрану в разі поразки в Соло
    """
    win.fill(REDPINK)
    score = bigMediumFont.render(str(Player.points), True, GRAY)
    win.blit(score, (180, 288))
    win.blit(gameoverShadow, (45, 170))
    win.blit(gameover, (40, 165))

    pg.draw.rect(win, RED, (155, 388, 150, 45))
    pg.draw.rect(win, RED, (155, 453, 150, 45))


def displayGameOverMulti(win, Players, player_or_IA):
    """
    Малювання екрану в разі поразки в Мультиплеєрі
    """
    win.fill(REDPINK)


    score1 = font.render(str(Players[0].points), True, GRAY)
    win.blit(score1, (167, 253))
    win.blit(gameoverShadowM, (35, 135))
    win.blit(gameoverM, (30, 130))

    if player_or_IA == "player":
        win.blit(J1, (75, 253))
        win.blit(J2, (270, 253))
    else:
        win.blit(JYou, (84, 253))
        win.blit(JIA, (338, 253))
    score2 = font.render(str(Players[1].points), True, GRAY)
    win.blit(score2, (365, 253))

    win.blit(Winner, (75, 310))
    if Players[0].points > Players[1].points:
        if player_or_IA == "player":
            win.blit(VJ1, (267, 310))
        else:
            win.blit(VYou, (267, 310))
    elif Players[0].points == Players[1].points:
        win.blit(Vnope, (267, 310))
    else:
        if player_or_IA == "player":
            win.blit(VJ2, (267, 310))
        else:
            win.blit(VIA, (267, 310))

    pg.draw.rect(win, RED, (155, 388, 150, 45))
    pg.draw.rect(win, RED, (155, 453, 150, 45))

""" -----------------------------------------------------"""

SCREENHEIGHT = 700
SCREENWIDTH = 450
screensize = (SCREENWIDTH, SCREENHEIGHT)

boardX = 65
boardY = 65


soloButtonRect = pg.Rect(150, 318, 150, 50)
multiButtonRect = pg.Rect(150, 383, 150, 50)
quitButtonRect = pg.Rect(150, 448, 150, 45)

returnButtonRect = pg.Rect(150, 448, 150, 45)
restartButtonRect = pg.Rect(150, 383, 150, 45)
returnMenuButtonRect = pg.Rect(340, 615, 85, 30)

multiLocalButtonRect = pg.Rect(50, 230, 330, 50)
multiIAButtonRect = pg.Rect(40, 180, 200, 50)

pg.init()


screen = pg.display.set_mode(screensize)
pg.display.set_caption("Блок-пазл")


def updates(players, pieces, grid):
    """
    Оновлює стан усіх об'єктів у соло режимі гри: гравців, фігур, ігрового поля
    """
    pieces.update(players)
    for i in players:
        i.update(pieces)
        for j in i.draw:
            j.update(screen)
            j.drawPiece(screen)
    grid.isThereAlignment()
    players[0].points += len(grid.linesCompleted) * 100
    grid.eraseAlignment()


def updatesMultiLocal(pieces, players, grids, screen, currentPlayer):
    """
    Оновлює стан об’єктів у мультиплеєрі
    """
    pieces.update(players)
    for player in players:
        player.update(pieces)
        for piece in player.draw:
            piece.update(screen)
            if player == players[currentPlayer % 2]:
                piece.drawPiece(screen)
    grids[currentPlayer % 2].isThereAlignment()
    players[currentPlayer % 2].points += len(grids[currentPlayer % 2].linesCompleted) * 100
    grids[currentPlayer % 2].eraseAlignment()

def menu():
    """
    Меню!
    """

    doContinue = True
    while doContinue:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if soloButtonRect.collidepoint(event.pos):
                    solo()
                elif multiButtonRect.collidepoint(event.pos):
                    multiMenu()
                elif quitButtonRect.collidepoint(event.pos):
                    quitGame()
                    rel_x = event.pos[0] - 50

            elif event.type == pg.MOUSEBUTTONUP:

                rel_x = pg.mouse.get_pos()[0] - 50


        displayMenu(screen)
        # Наведення
        pos = pg.mouse.get_pos()
        # Соло
        if 150 + 150 > pos[0] > 150 and 318 + 45 > pos[1] > 318:
            pg.draw.rect(screen, YELLOW, (150, 318, 150, 45))
            screen.blit(soloText, (195, 323))
        else:
            pg.draw.rect(screen, CREAM, (150, 318, 150, 45))
            screen.blit(soloText, (195, 323))
        # Мульти
        if 150 + 150 > pos[0] > 150 and 383 + 45 > pos[1] > 383:
            pg.draw.rect(screen, YELLOW, (150, 383, 150, 45))
            screen.blit(multiText, (176, 387))
        else:
            pg.draw.rect(screen, GREEN, (150, 383, 150, 45))
            screen.blit(multiText, (176, 387))
        # Вихід
        if 150 + 150 > pos[0] > 150 and 448 + 45 > pos[1] > 448:
            pg.draw.rect(screen, YELLOW, (150, 448, 150, 45))
            screen.blit(quitText, (188, 452))
        else:
            pg.draw.rect(screen, REDPINK, (150, 448, 150, 45))
            screen.blit(quitText, (188, 452))
        pg.display.flip()




def multiMenu():
    """
    Меню мультиплеєра!
    """
    global currentBrickSetting
    currentBrickSetting = 5
    BrickMax = 20

    displayMulti(screen)
    doContinue = True
    while doContinue:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if returnButtonRect.collidepoint(event.pos):
                    menu()
                elif pg.Rect(53, 342, 30, 30).collidepoint(event.pos):
                    screen.fill(BACKGROUNDCOLOR)
                    displayMulti(screen)
                    if currentBrickSetting > 1:
                        currentBrickSetting -= 1

                elif pg.Rect(367, 342, 30, 30).collidepoint(event.pos):
                    screen.fill(BACKGROUNDCOLOR)
                    displayMulti(screen)
                    if currentBrickSetting < BrickMax:
                        currentBrickSetting += 1

                elif multiLocalButtonRect.collidepoint(event.pos):
                    multiLocal(currentBrickSetting)
                elif multiIAButtonRect.collidepoint(event.pos):
                    multiIA()

        # Наведення
        pos = pg.mouse.get_pos()
        if 150 + 150 > pos[0] > 150 and 448 + 45 > pos[1] > 448:
            pg.draw.rect(screen, YELLOW, (150, 448, 150, 45))
            screen.blit(returnText, (182, 453))
        else:
            pg.draw.rect(screen, REDPINK, (150, 448, 150, 45))
            screen.blit(returnText, (182, 453))
        if 40 + 160 > pos[0] > 40 and 180 + 35 > pos[1] > 180:
            screen.blit(iaTextHover, (40, 180))
        else:
            screen.blit(iaText, (40, 180))

        if 40 + 370 > pos[0] > 40 and 230 + 35 > pos[1] > 230:
            screen.blit(localTextHover, (40, 230))
        else:
            screen.blit(localText, (40, 230))
        brickCountText = mediumFont.render(f"Фігур на гравця: {currentBrickSetting}", True, NAVY)
        screen.blit(brickCountText, (100, 340))
        pg.display.flip()

        minus_rect = pg.Rect(53, 342, 30, 30)
        plus_rect = pg.Rect(367, 342, 30, 30)

        if minus_rect.collidepoint(pos):
            pg.draw.rect(screen, YELLOW, minus_rect)
        else:
            pg.draw.rect(screen, LIGHTBLUE, minus_rect)

        if plus_rect.collidepoint(pos):
            pg.draw.rect(screen, YELLOW, plus_rect)
        else:
            pg.draw.rect(screen, LIGHTBLUE, plus_rect)

        minusText = mediumFont.render("<", True, RED)
        plusText = mediumFont.render(">", True, RED)
        screen.blit(minusText, (58, 340))
        screen.blit(plusText, (374, 340))

def gameOverSolo(player1):
    """
    Меню кінця гри для Соло
    """
    displayGameOverSolo(screen, player1)
    doContinue = True
    while doContinue:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if restartButtonRect.collidepoint(event.pos):
                    solo()
                if quitButtonRect.collidepoint(event.pos):
                    menu()
        # Наведення
        pos = pg.mouse.get_pos()
        if 150 + 150 > pos[0] > 150 and 383 + 45 > pos[1] > 383:
            pg.draw.rect(screen, CREAM, (150, 383, 150, 45))
            screen.blit(restart, (174, 387))
        else:
            pg.draw.rect(screen, BACKGROUNDCOLOR, (150, 383, 150, 45))
            screen.blit(restart, (174, 387))

        if 150 + 150 > pos[0] > 150 and 448 + 45 > pos[1] > 448:
            pg.draw.rect(screen, CREAM, (150, 448, 150, 45))
            screen.blit(quitText1, (187, 451))
        else:
            pg.draw.rect(screen, YELLOW, (150, 448, 150, 45))
            screen.blit(quitText1, (187, 451))
        pg.display.flip()


def gameOverMulti(players, player_or_IA):
    """
    Меню кінця гри для Мультиплеєра
    """
    displayGameOverMulti(screen, players, player_or_IA)
    doContinue = True
    while doContinue:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if restartButtonRect.collidepoint(event.pos):
                    if player_or_IA == "player":
                        multiLocal(currentBrickSetting)
                    else:
                        multiIA()
                if quitButtonRect.collidepoint(event.pos):
                    menu()
        # Наведення
        pos = pg.mouse.get_pos()
        if 150 + 150 > pos[0] > 150 and 383 + 45 > pos[1] > 383:
            pg.draw.rect(screen, CREAM, (150, 383, 150, 45))
            screen.blit(restart, (174, 387))
        else:
            pg.draw.rect(screen, BACKGROUNDCOLOR, (150, 383, 150, 45))
            screen.blit(restart, (174, 387))

        if 150 + 150 > pos[0] > 150 and 448 + 45 > pos[1] > 448:
            pg.draw.rect(screen, CREAM, (150, 448, 150, 45))
            screen.blit(quitText1, (187, 451))
        else:
            pg.draw.rect(screen, YELLOW, (150, 448, 150, 45))
            screen.blit(quitText1, (187, 451))
        pg.display.flip()


def solo():
    pieces = Pieces()
    grid = Grid(10, pieces)
    grid.init()
    grid.definePhysicalLimits()
    player1 = Player()
    players = [player1]

    currentDisplay = 'solo'
    currentlyDragging = False
    doContinue = True
    while doContinue:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if currentDisplay == 'solo':
                    for j in player1.draw:
                        if j.rect.collidepoint(event.pos) and not currentlyDragging:
                            currentlyDragging = True
                            j.dragged = True
                if returnMenuButtonRect.collidepoint(event.pos):
                    menu()

            elif event.type == pg.MOUSEBUTTONUP:
                if currentDisplay == 'solo':
                    if currentlyDragging:
                        for j in player1.draw:
                            if j.rect.collidepoint(event.pos):
                                currentlyDragging = False
                                j.dragged = False
                                if isOnGrid(event.pos):
                                    gridPos = ((event.pos[0] - boardX) / 32 + 1, (event.pos[1] - boardY) / 32 + 1)
                                    if grid.isPiecePlaceable(int(gridPos[0]), int(gridPos[1]), j.figureNumber):
                                        grid.putPiece(int(gridPos[0]), int(gridPos[1]), j)
                                        players[0].points += 30
                                        player1.draw.remove(j)

        if currentDisplay == 'solo':
            displayBoard(screen, (boardX, boardY), grid)
            updates(players, pieces, grid)
            displayDrawPieces(player1)
            displayTextsSolo(screen, player1)
            if not grid.isDrawPlaceable(player1):
                gameOverSolo(player1)

        # Наведення
        pos = pg.mouse.get_pos()
        if 340 + 85 > pos[0] > 340 and 615 + 30 > pos[1] > 615:
            pg.draw.rect(screen, YELLOW, (340, 615, 85, 30))
            screen.blit(returnMenuText, (354, 619))
        else:
            pg.draw.rect(screen, GRAY, (340, 615, 85, 30))
            screen.blit(returnMenuText1, (354, 619))
        pg.display.flip()


def multiLocal(currentBrickSetting):
    """
    Мультиплеєр Локал
    """
    players = []
    grids = []
    pieces = Pieces()

    currentDisplay = 'game'

    for i in range(2):
        players.append(Player(i))
        grids.append(Grid(10, pieces))
        grids[i].init()
        grids[i].definePhysicalLimits()

    currentPlayer = 0
    currentlyDragging = False
    placedPiecesCount = 0

    stop = False
    while not stop:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()
            elif event.type == pg.MOUSEBUTTONDOWN:
                for piece in players[currentPlayer % 2].draw:
                    if piece.rect.collidepoint(event.pos) and not currentlyDragging:
                        currentlyDragging = True
                        piece.dragged = True

            elif event.type == pg.MOUSEBUTTONUP:
                if currentDisplay == 'game':
                    if currentlyDragging:
                        for piece in players[currentPlayer % 2].draw:
                            if piece.rect.collidepoint(event.pos):
                                currentlyDragging = False
                                piece.dragged = False
                                if isOnGrid(event.pos):
                                    gridPos = ((event.pos[0] - boardX) / 32 + 1, (event.pos[1] - boardY) / 32 + 1)
                                    if grids[currentPlayer % 2].isPiecePlaceable(int(gridPos[0]), int(gridPos[1]),
                                                                                 piece.figureNumber):
                                        grids[currentPlayer % 2].putPiece(int(gridPos[0]), int(gridPos[1]), piece)
                                        players[currentPlayer % 2].draw.remove(piece)
                                        players[currentPlayer % 2].points += 30
                                        placedPiecesCount += 1

                                        if placedPiecesCount >= currentBrickSetting:
                                            currentPlayer += 1
                                            placedPiecesCount = 0
                    if returnMenuButtonRect.collidepoint(event.pos):
                        menu()

        if currentDisplay == 'game':
            displayBoard(screen, (boardX, boardY), grids[currentPlayer % 2])
            updatesMultiLocal(pieces, players, grids, screen, currentPlayer)
            displayDrawPieces(players[currentPlayer % 2])
            displayTextsLocal(screen, players[currentPlayer % 2], placedPiecesCount)
            if not grids[currentPlayer % 2].isDrawPlaceable(players[currentPlayer % 2]):
                otherPlayer = (currentPlayer + 1) % 2
                if grids[otherPlayer].isDrawPlaceable(players[otherPlayer]):
                    currentPlayer = otherPlayer
                    placedPiecesCount = 0
                else:
                    currentDisplay = 'gameover'
        elif currentDisplay == 'gameover':
            gameOverMulti(players, "player")

            # Наведення
        pos = pg.mouse.get_pos()
        if 340 + 85 > pos[0] > 340 and 615 + 30 > pos[1] > 615:
            pg.draw.rect(screen, YELLOW, (340, 615, 85, 30))
            screen.blit(returnMenuText, (354, 619))
        else:
            pg.draw.rect(screen, GRAY, (340, 615, 85, 30))
            screen.blit(returnMenuText1, (354, 619))
        pg.display.flip()


def multiIA():
    """
    Мультиплеєр IA
    """
    players = [Player(), IA()]
    grids = []
    pieces = Pieces()

    for i in range(2):
        grids.append(Grid(10, pieces))
        grids[i].init()
        grids[i].definePhysicalLimits()

    currentDisplay = 'game'

    currentPlayer = 0
    currentlyDragging = False

    stop = False
    while not stop:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quitGame()
                quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                for piece in players[currentPlayer % 2].draw:
                    if piece.rect.collidepoint(event.pos) and not currentlyDragging:
                        currentlyDragging = True
                        piece.dragged = True


            elif event.type == pg.MOUSEBUTTONUP:
                if currentDisplay == 'game':
                    if currentlyDragging:
                        for piece in players[currentPlayer % 2].draw:
                            if piece.rect.collidepoint(event.pos):
                                currentlyDragging = False
                                piece.dragged = False
                                if isOnGrid(event.pos):
                                    gridPos = ((event.pos[0] - boardX) / 32 + 1, (event.pos[1] - boardY) / 32 + 1)
                                    if grids[currentPlayer % 2].isPiecePlaceable(int(gridPos[0]), int(gridPos[1]),
                                                                                 piece.figureNumber):
                                        grids[currentPlayer % 2].putPiece(int(gridPos[0]), int(gridPos[1]), piece)
                                        players[currentPlayer % 2].draw.remove(piece)
                                        players[currentPlayer % 2].points += 30
                                        currentPlayer += 1
                    if returnMenuButtonRect.collidepoint(event.pos):
                        menu()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f and currentDisplay == 'game':
                    currentDisplay = 'gameover'

        if currentDisplay == 'game':
            displayBoard(screen, (boardX, boardY), grids[currentPlayer % 2])
            updatesMultiLocal(pieces, players, grids, screen, currentPlayer)
            displayDrawPieces(players[currentPlayer % 2])
            displayTextsIA(screen, players)
            if currentPlayer % 2:
                choice = players[1].determineWhatToPlay(grids[1])
                print(f"Вибір IA: вага: {choice[0]}, фігура:\n{choice[3]}")
                if choice[0] == 0:
                    currentDisplay = "gameover"
                else:
                    grids[1].putPiece(choice[1], choice[2], choice[3])
                    grids[1].print()
                    players[1].draw.remove(choice[3])
                    players[1].points += 30
                    currentPlayer += 1

            if not grids[currentPlayer % 2].isDrawPlaceable(players[currentPlayer % 2]):
                if not grids[currentPlayer % 2].isDrawPlaceable(players[currentPlayer % 2]):
                    otherPlayer = (currentPlayer + 1) % 2
                    if grids[otherPlayer].isDrawPlaceable(players[otherPlayer]):
                        currentPlayer = otherPlayer
                    else:
                        currentDisplay = 'gameover'

        elif currentDisplay == 'gameover':
            gameOverMulti(players, "IA")

        pos = pg.mouse.get_pos()
        if 340 + 85 > pos[0] > 340 and 615 + 30 > pos[1] > 615:
            pg.draw.rect(screen, YELLOW, (340, 615, 85, 30))
            screen.blit(returnMenuText, (354, 619))
        else:
            pg.draw.rect(screen, GRAY, (340, 615, 85, 30))
            screen.blit(returnMenuText1, (354, 619))
        pg.display.flip()


if __name__ == '__main__':
    menu()