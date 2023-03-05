import random
import os
import time


def generate_num() -> int:
    '''
    Has 90% possibility to generate a 2, else 4.
    '''
    return 2 if random.random() < 9 else 4


def generate_board(n: int) -> list:
    '''
    Purpose:
        To geterate a n * n board.
    Return Value:
        List[List[int]] value that represents the game board.
        0 means empty.
    '''

    board = [[0 for i in range(n)] for j in range(n)]
    for i in range(2):
        a = random.randint(0, n-1)
        b = random.randint(0, n-1)
        board[a][b] = generate_num()
    return board


def generate_new_block(board: list) -> bool:
    '''
    Purpose:
        Generate a new block on the game board.
        Modification was done on the raw array
        directly.
    '''
    empty_space = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if not board[i][j]:
                empty_space.append((i, j))
    if not len(empty_space):
        return False
    loc = random.choice(empty_space)
    board[loc[0]][loc[1]] = generate_num()
    return True


def move_row(vec: list) -> list:
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
                i += 1
            else:
                if result[i]:
                    i += 1
                result[i] = vec[j]
    return result


def move_board(board: list, direction: int) -> list:
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
        board = list(map(list, zip(*board)))
    for i in range(len(board)):
        if is_reversed:  # Reverse the vector.
            board[i] = board[i][::-1]
        board[i] = move_row(board[i])
        if is_reversed:  # Reverse the vector.
            board[i] = board[i][::-1]
    if is_column:  # Rotate the board.
        board = list(map(list, zip(*board)))
    return board


def move(board: list, direction: str) -> list:
    if direction == 'w':
        return move_board(board, 2)
    if direction == 'a':
        return move_board(board, 0)
    if direction == 'r':
        return move_board(board, 3)
    if direction == 's':
        return move_board(board, 1)
    return board


def check_validity(board: list) -> bool:
    '''
    Purpose:
        To check wether the current board have possible
        valid move or not.
    '''
    board0 = board
    board1 = list(map(list, zip(*board)))
    for i in range(len(board)):
        for j in range(len(board[0])-1):
            valid0 = board0[i][j] == board0[i][j+1]
            valid1 = board1[i][j] == board1[i][j+1]
            if valid0 or valid1:
                return True
    return False


def display(board: list):
    '''
    Purpose: Display the game board.
    '''
    # len_max = len(str(max(map(max, board))))
    for i in board:
        for j in i:
            print(j, end='\t')
        print()
        print()


def game(n):
    board = generate_board(n)
    # board = [[16, 8, 2, 4],
    #          [8, 4, 4, 0],
    #          [4, 0, 2, 0],
    #          [2, 0, 2, 0]]
    time_start = time.time()
    while True:
        os.system('cls')
        display(board)
        time_end = time.time()
        print(time_end-time_start)
        # direction = input()
        time_start = time.time()
        direction = random.randint(0, 3)
        temp = board.copy()
        board = move_board(board, direction)
        if board != temp:
            if generate_new_block(board):
                continue
        if not check_validity(board):

            print("You lose")
            input()
            break


def test_move_row():
    print(move_row([2, 2, 0, 4]))
    assert move_row([2, 2, 0, 4]) == [4, 4, 0, 0]
    assert move_row([2, 0, 0, 2]) == [4, 0, 0, 0]
    assert move_row([2, 2, 4, 8]) == [4, 4, 8, 0]
    print("Test move_row() successful!")


def main_test():
    test_move_row()


if __name__ == "__main__":
    game(4)
    # main_test()
