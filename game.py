import random
import pygame
import json
import pickle
from copy import deepcopy


class Archive():
    '''
    Purpose:
        To storage certaim amount of items in a list.
        Items entered earlier will be poped if the storage
        is full.
    Instances:
        lth(int): The maximum amount of storage.
        storage(list[item]): The list to storage items.
        cur(int): The pointer of current item extracting.
    '''

    def __init__(self, length):
        self.lth = length  # Max num of storage.
        self.storage = []
        self.cur = 0

    def add(self, item):
        '''
        Add the item to the archive. Pop earliest item
        if the storage is full. Backtrace the storage if
        later items are extracted.
        '''
        if self.cur:
            self.storage = self.storage[0:-(self.cur-1)]
            self.cur = 0
        if len(self.storage) >= self.lth:
            self.storage.pop(0)
        self.storage.append(deepcopy(item))

    def extract(self):
        '''
        Return an earlier item to which current item pointed.
        Every call on extract() will move the pointer to an
        earlier item.
        '''
        if self.cur < len(self.storage)-1:
            self.cur += 1
        return self.storage[-(self.cur+1)]

    def redo(self):
        '''
        Return a later item to which current item pointed.
        Every call on redo() will move the pointer to a later item.
        '''
        if self.cur > 1:
            self.cur -= 1
        return self.storage[-(self.cur+1)]


class Game:
    def __init__(self, n: int):
        self.n = n
        self._init_constants('config.json')

        if not self.load_archive(True):
            self.score = 0
            self.generate_board(self.n)
        self.archive = Archive(self.n_withdraw)
        self.archive.add((self.board, self.score))
        self._init_pygame()
        self.play()

    def _init_constants(self, filepath: str):
        with open(filepath) as input_file:
            constants = json.load(input_file)
        self.size = constants['screen_size']
        self.box_style = constants['box_style']
        self.bg_color = constants['bg_color']
        self.font = constants['font']
        self.keys = constants['keys']
        self.n_withdraw = constants['n_withdraw']
        self.archive_filepath = constants["archive_filepath"]

    def _init_pygame(self):
        pygame.init()
        self._init_box_style()
        self.box = self.size[0] // self.n
        self.pad = self.size[0] // 100
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('2048')
        self.display_pygame()

    def _init_box_style(self):
        self.style = dict()
        width_factor = {1: 0.75, 2: 0.65, 3: 0.55, 4: 0.5, 5: 0.5, 6: 0.5}
        for i in self.box_style:
            bg_color, text_color, text_size = self.box_style[i]
            text_size = int(text_size*35/45)
            font = pygame.font.SysFont(self.font, text_size, bold=True)
            text = font.render("{:>4}".format(i), 1, text_color)
            text_w = width_factor[len(i)] * text.get_rect().width
            text_h = 0.6*text.get_rect().height
            self.style[int(i)] = (bg_color, text_color,
                                  text_size, text_w, text_h)

    def generate_num(self) -> int:
        '''
        Has 90% possibility to generate a 2, else 4.
        '''
        # return 2 if random.random() < 0.9 else 4
        return 2

    def generate_board(self, n: int):
        '''
        To geterate a n * n board with 2 inital block.
        '''
        self.board = [[0 for i in range(n)] for j in range(n)]
        for i in range(2):
            self.generate_new_block()
        # self.board = [[4, 8, 16, 32], [64, 128, 256, 512], [
        #     1024, 2048, 4096, 8192], [16384, 32768, 65536, 131072]]

    def generate_new_block(self) -> bool:
        '''
        Purpose:
            Generate a new block on the game board.
            Modification was done on the raw array
            directly.
        '''
        empty_space = []
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if not self.board[i][j]:
                    empty_space.append((i, j))
        loc = random.choice(empty_space)
        self.board[loc[0]][loc[1]] = self.generate_num()
        return len(empty_space) > 1

    def load_archive(self, load) -> bool:
        try:
            mode = 'rb' if load else 'wb'
            with open(self.archive_filepath, mode) as file:
                if load:
                    self.board, self.score = pickle.load(file)
                else:
                    pickle.dump((self.board, self.score), file)
            return True
        except Exception as e:
            print(e)
            return False

    def move_row(self, vec: list) -> list:
        '''
        Purpose:
            Given an integer array, move every item
            to left and integrate them if they have
            same value.
        Paras:
            vec(list[int]): The row of a 2048 board.
        Return Value:
            A list[int] value that is the integrated row.
        '''
        result = [0]*len(vec)
        i = 0
        for j in range(len(vec)):
            if vec[j]:
                if vec[j] == result[i]:
                    result[i] *= 2
                    self.score += result[i]
                    i += 1
                else:
                    if result[i]:
                        i += 1
                    result[i] = vec[j]
        return result

    def move_board(self, direction: int):
        '''
        Purpose:
            Shift all the items on the board to given
            direction. Modification applies on the
            raw array directly.
        Paras:
            board(list[list[int]]): The board of the game.
            direction(int):
                The direction of the move. 0, 1, 2, 3
                for left, right, up, down.
        '''
        is_reversed = direction % 2 == 1
        is_column = direction > 1

        if is_column:  # Rotate the board.
            self.board = list(map(list, zip(*self.board)))
        for i in range(len(self.board)):
            if is_reversed:  # Reverse the vector.
                self.board[i] = self.board[i][::-1]
            self.board[i] = self.move_row(self.board[i])
            if is_reversed:  # Reverse the vector.
                self.board[i] = self.board[i][::-1]
        if is_column:  # Rotate the board.
            self.board = list(map(list, zip(*self.board)))

    def move(self, direction: int):
        board_temp = self.board.copy()
        self.move_board(direction)
        if self.board != board_temp:  # Check if board is updated.
            if not self.generate_new_block():
                if not self.check_validity():
                    print("You lose")
                    exit()

    def check_validity(self) -> bool:
        '''
        Purpose:
            To check wether the current board have possible
            valid move or not.
        '''
        if 0 in sum(self.board, []):
            return True
        board0 = self.board
        board1 = list(map(list, zip(*self.board)))
        for i in range(len(board0)):
            for j in range(len(board0[0])-1):
                valid0 = board0[i][j] == board0[i][j+1]
                valid1 = board1[i][j] == board1[i][j+1]
                if valid0 or valid1:
                    return True
        return False

    def display(self):
        '''
        Purpose: Display the game board.
        '''
        # len_max = len(str(max(map(max, board))))
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                print(self.board[i][j], end='\t')
            print()
            print()

    def display_pygame(self):
        """
        Display the board 'matrix' on the game window.

        Parameters:
            board (list): game board
            theme (str): game interface theme
        """
        self.screen.fill(self.bg_color)

        for i in range(self.n):
            for j in range(self.n):
                color, text_color, text_size, text_w, text_h = self.style[self.board[i][j]]
                loc = (j * self.box + self.pad, i * self.box + self.pad,
                       self.box - 2 * self.pad, self.box - 2 * self.pad)
                pygame.draw.rect(self.screen, color, loc, 0)
                if self.board[i][j] != 0:
                    font = pygame.font.SysFont(self.font, text_size, bold=True)
                    text = font.render("{:>4}".format(
                        self.board[i][j]), 1, text_color)
                    loc = ((j+0.5)*self.box-text_w,
                           (i+0.5)*self.box-text_h)
                    self.screen.blit(text, loc)
        print(self.score)
        pygame.display.update()

    def keyboard_event(self, key):
        if key == 4:
            self.board, self.score = self.archive.extract()
        elif key == 5:
            self.board, self.score = self.archive.redo()
        elif key == 6:
            print('Saving')
            self.load_archive(False)
        else:
            board_temp = deepcopy(self.board)
            self.move_board(key)
            if self.board != board_temp:
                if not self.generate_new_block():
                    if not self.check_validity():
                        print("You lose")
                self.archive.add((self.board, self.score))

    def play(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if str(event.key) in self.keys:
                        self.keyboard_event(self.keys[str(event.key)])
                        self.display_pygame()


if __name__ == '__main__':
    a = Game(4)
