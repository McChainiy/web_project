import pygame as pg
import random
from math import sqrt

WHITE = pg.Color('white')
BLACK = pg.Color('black')
screen = pg.display.set_mode((501, 501))


class Board:
    def __init__(self, width, heigth):
        self.width = width
        self.height = heigth
        self.board = [[0] * width for _ in range(heigth)]
        self.left = 10
        self.top = 10
        self.cell_size = 10

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        for i in range(self.height):
            for j in range(self.width):
                color = 0 if self.board[i][j] else 1
                pg.draw.rect(screen, WHITE, [self.left + self.cell_size * j,
                            self.top + self.cell_size * i, self.cell_size, self.cell_size], color)

    def get_cell(self, mouse_pos):
        y_cell = (mouse_pos[1] - self.top) // self.cell_size
        x_cell = (mouse_pos[0] - self.left) // self.cell_size
        if 0 <= x_cell < self.width and 0 <= y_cell < self.height:
            return [y_cell, x_cell]
        return None

    def on_click(self, cell_coords):
        self.board[cell_coords[0]][cell_coords[1]] =\
            0 if self.board[cell_coords[0]][cell_coords[1]] else 1
        self.render()

    def get_click(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            self.on_click(cell_pos)


def main():
    running = True

    pg.init()

    MYEVENTTYPE = 19

    screen.fill((0, 0, 0))

    pg.time.set_timer(MYEVENTTYPE, 15)

    board = Board(25, 25)
    board.set_view(0, 0, 20)
    board.render()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
                screen.fill((0, 0, 0))
                board.render()
            if event.type == pg.MOUSEBUTTONUP:
                pass
            if event.type == MYEVENTTYPE:
                pass
        pg.display.flip()


if __name__ == '__main__':
    main()
