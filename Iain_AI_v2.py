"""
r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
P P P P P P P P
R N B Q K B N R

things todo in order of importance:
    Pawn Promotion
    implement increasing depth search
    implement time management
    implement pawn double move 
    
"""
import copy
import time
PIECE_MOVE_DIRECTION = {
    'K': ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)),
    'k': ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)),
    'Q': ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)),
    'q': ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)),
    'R': ((1, 0), (0, 1), (-1, 0), (0, -1)),
    'r': ((1, 0), (0, 1), (-1, 0), (0, -1)),
    'B': ((1, 1), (1, -1), (-1, 1), (-1, -1)),
    'b': ((1, 1), (1, -1), (-1, 1), (-1, -1)),
    'N': ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)),
    'n': ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)),
}
PIECE_VALUE = {
    '.': 0,
    'K': 20_000_000, 'Q': 900, 'R': 500, 'B': 300, 'N': 300, 'P': 100,
    'k': -20_000_000, 'q': -900, 'r': -500, 'b': -300, 'n': -300, 'p': -100
}

Position_Scores = {
    'P': [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]],
    'N': [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]],
    'B': [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]],
    'R': [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]],
    'Q': [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]],
    'K': [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]],
    '.': [[0 for _ in range(8)] for _ in range(8)]
}

for piece in list(Position_Scores):
    Position_Scores[piece.lower()] = [[-value for value in row] for row in Position_Scores[piece]]
    Position_Scores[piece] = list(Position_Scores[piece].__reversed__())

# This adds piece value to positional value to increase speed
for piece in Position_Scores:
    Position_Scores[piece] = [[value + PIECE_VALUE[piece] for value in row] for row in Position_Scores[piece]]


def score(board):
    points = 0
    for y in range(8):
        for x in range(8):
            points += Position_Scores[board[y][x]][y][x]
    return points


def moves(board, white_turn):
    legal_moves = []
    for y in range(8):
        for x in range(8):
            piece = board[y][x]
            if white_turn:
                if piece in 'KQRBN':
                    for y_move_direction, x_move_direction in PIECE_MOVE_DIRECTION[piece]:
                        for distance in range(1, 8):
                            new_y = y + y_move_direction * distance
                            new_x = x + x_move_direction * distance
                            if 0 <= new_y <= 7 and 0 <= new_x <= 7:
                                if board[new_y][new_x] == '.':
                                    new_board = copy.deepcopy(board)
                                    new_board[y][x] = '.'
                                    new_board[new_y][new_x] = piece
                                    legal_moves.append(new_board)
                                elif board[new_y][new_x].islower():
                                    new_board = copy.deepcopy(board)
                                    new_board[y][x] = '.'
                                    new_board[new_y][new_x] = piece
                                    legal_moves.append(new_board)
                                    break
                                else:
                                    break
                                    # breaks if one of own pieces
                            else:
                                break
                            if piece in 'KN':
                                break
                if piece == 'P' and y <= 6:
                    if board[y+1][x] == '.':
                        new_board = copy.deepcopy(board)
                        new_board[y][x] = '.'
                        new_board[y+1][x] = 'P'
                        legal_moves.append(new_board)
                        if board[y+2][x] == '.' and y == 1:
                            new_board = copy.deepcopy(board)
                            new_board[y][x] = '.'
                            new_board[y+2][x] = 'P'
                            legal_moves.append(new_board)
                    if x < 7 and board[y+1][x+1].islower():
                        new_board = copy.deepcopy(board)
                        new_board[y][x] = '.'
                        new_board[y+1][x+1] = 'P'
                        legal_moves.append(new_board)
                    if x > 0 and board[y+1][x-1].islower():
                        new_board = copy.deepcopy(board)
                        new_board[y][x] = '.'
                        new_board[y+1][x-1] = 'P'
                        legal_moves.append(new_board)
            else:
                if piece in 'kqrbn':
                    for y_move_direction, x_move_direction in PIECE_MOVE_DIRECTION[piece]:
                        for distance in range(1, 8):
                            new_y = y + y_move_direction * distance
                            new_x = x + x_move_direction * distance
                            if 0 <= new_y <= 7 and 0 <= new_x <= 7:
                                if board[new_y][new_x] == '.':
                                    new_board = copy.deepcopy(board)
                                    new_board[y][x] = '.'
                                    new_board[new_y][new_x] = piece
                                    legal_moves.append(new_board)
                                elif board[new_y][new_x].isupper():
                                    new_board = copy.deepcopy(board)
                                    new_board[y][x] = '.'
                                    new_board[new_y][new_x] = piece
                                    legal_moves.append(new_board)
                                    break
                                else:
                                    break
                                    # breaks if one of own pieces
                            else:
                                break
                            if piece in 'kn':
                                break
                if piece == 'p' and y >= 1:
                    if board[y-1][x] == '.':
                        new_board = copy.deepcopy(board)
                        new_board[y][x] = '.'
                        new_board[y-1][x] = 'p'
                        legal_moves.append(new_board)
                        if board[y-2][x] == '.' and y == 6:
                            new_board = copy.deepcopy(board)
                            new_board[y][x] = '.'
                            new_board[y-2][x] = 'p'
                            legal_moves.append(new_board)
                    if x < 7 and board[y-1][x+1].isupper():
                        new_board = copy.deepcopy(board)
                        new_board[y][x] = '.'
                        new_board[y-1][x+1] = 'p'
                        legal_moves.append(new_board)
                    if x > 0 and board[y-1][x-1].isupper():
                        new_board = copy.deepcopy(board)
                        new_board[y][x] = '.'
                        new_board[y-1][x-1] = 'p'
                        legal_moves.append(new_board)
    return legal_moves


def search(board, white_turn, depth):
    best_score = -99_900_000  # this will only matter if there are no moves and avoids crashing runner
    best_move = board
    for move in moves(board, white_turn):
        current_score = score(move) if white_turn else -score(move)
        if depth > 1 and abs(current_score) < 1_000_000:
            current_score = -search(move, not white_turn, depth - 1)[1]
        if current_score > best_score:
            best_move = move
            best_score = current_score
        # print(current_score, best_score, best_move)
    return best_move, best_score


def main(history, white_time, black_time):
    start_time = time.perf_counter()
    if len(history) % 2 == 1:
        white_turn = True
        my_time = white_time
    else:
        white_turn = False
        my_time = black_time
    current_board = history[-1]
    for depth in range(1, 999):
        best_move, best_score = search(current_board, white_turn, depth)
        current_time = time.perf_counter()
        time_spent = current_time - start_time
        time_remaining = my_time - time_spent
        print(depth, best_score)
        if time_remaining < 50 * time_spent:
            return best_move
        if abs(best_score) > 1_000_000:  # detect king take
            return best_move

initialPosition = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
initialPosition.reverse()
