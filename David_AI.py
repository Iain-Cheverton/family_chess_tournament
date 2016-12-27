"""This was written by David for fun on 24th - 27th December 2016
Micheal and Robert not allowed to read this file until the competition is over.
This program implements a tree search of possible future moves.
The main data structures are:
    - board: this is a [str] representing a 2D board
    - state: a list representing a node in a the search tree. It contains a board and some metadata.

A board can be scored with the score function.

The score of a state can be simply calculated by passing its associated board to the score function. To get a more
accurate score of a position it is necessary to explore the children of the state.


Not implemented yet:
    - castling
    - en passant

I use the time to calculate and score the first 3 moves as a benchmark for my algorithm.

search strategy             scoring                         time taken
----------------------------------------------------------------------
recursive explore calls     sum pieces & pawn position      0.340
recursive explore calls     sum pieces                      0.207

"""
import time

PIECE_VALUE = {
    '.': 0,
    'K': 20, 'Q': 9, 'R': 5, 'B': 3.2, 'N': 3, 'P': 0.9,
    'k': -20, 'q': -9, 'r': -5, 'b': -3.2, 'n': -3, 'p': -0.9}
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


def pretty_print(_board):
    print('\n'.join(_board.__reversed__()) + '\n')


def move(board: [str], y1, x1, y2, x2)-> [str]:
    """returns a board with a move made"""
    board = board.copy()
    # add piece to destination
    line = board[y2]
    board[y2] = line[:x2] + board[y1][x1] + line[x2 + 1:]
    # remove piece from source
    line = board[y1]
    board[y1] = line[:x1] + '.' + line[x1 + 1:]
    return board


def moves(board: [str], _player_is_white: bool)->[[str]]:
    """This generates a list of all possible game states after one move"""
    _moves = []
    for x in range(8):
        for y in range(8):
            piece = board[y][x]
            if piece in 'KQRBN' if _player_is_white else piece in 'kqrbn':
                for xd, yd in PIECE_MOVE_DIRECTION[piece]:
                    for i in range(1, 100):
                        x2 = x+i*xd
                        y2 = y+i*yd
                        if not (0 <= x2 <= 7 and 0 <= y2 <= 7):
                            # then it is a move off the board
                            break
                        target_piece = board[y2][x2]
                        if target_piece.isupper() if _player_is_white else target_piece.islower():
                            # then it is taking it's own piece
                            break
                        if target_piece.islower() if _player_is_white else target_piece.isupper():
                            # then it is taking an opponent's piece
                            _moves.append(move(board, y, x, y2, x2))
                            break
                        _moves.append(move(board, y, x, y2, x2))
                        if piece in 'KkNn':
                            break

            # pawns are weird
            if piece == 'P' if _player_is_white else piece == 'p':
                pawn_moves = []
                y2 = y+1 if _player_is_white else y-1
                for x2 in (x - 1, x + 1):
                    if 0 <= x2 <= 7:
                        if board[y2][x2].islower() if _player_is_white else board[y2][x2].isupper():
                            # then a take is possible
                            pawn_moves.append((y2, x2))
                # move forward by 1
                if board[y2][x] == '.':
                    # then the move is into an empty square
                    pawn_moves.append((y2, x))
                    # move forward by 2
                    if y == 1 if _player_is_white else y == 6:
                        y2 = y + 2 if _player_is_white else y - 2
                        if board[y2][x] == '.':
                            _moves.append(move(board, y, x, y2, x))
                for y2, x2 in pawn_moves:
                    after_pawn_move = move(board, y, x, y2, x2)
                    if y2 == 7 if _player_is_white else y2 == 0:
                        # then the end of the board has been reached and promotion is needed
                        for replacement_piece in ('QRBN' if _player_is_white else 'qrbn'):
                            after_pawn_replacement = board.copy()
                            line = after_pawn_replacement[y2]
                            after_pawn_replacement[y2] = line[:x2] + replacement_piece + line[x2 + 1:]
                            _moves.append(after_pawn_replacement)
                    else:
                        _moves.append(after_pawn_move)
    return _moves


def score(_board: [str])->float:
    """This takes a gameState object and returns the current score of white"""
    _score = 0.0
    for row in _board:
        for piece in row:
            _score += PIECE_VALUE[piece]
    return _score


def smart_score(board: [str], _player_is_white: bool, depth: int)->float:
    _moves = moves(board, _player_is_white)
    if not _moves:
        # if there are no possible moves then it is a draw
        return 0
    if depth == 1:
        if _player_is_white:
            return max(score(_move) for _move in _moves)
        else:
            return min(score(_move) for _move in _moves)
    else:
        if _player_is_white:
            return max(smart_score(_move, not _player_is_white, depth - 1) for _move in _moves)
        else:
            return max(smart_score(_move, not _player_is_white, depth - 1) for _move in _moves)


def main():
    # --------- read in game state ----------
    game_history = open('game state.txt').read().split('\n')
    initial_board = game_history[-14:-6]
    initial_board.reverse()
    turn = int(game_history[-16].split(' ')[2])
    player_is_white = game_history[-5][9] == 'w'
    white_time = float(game_history[-4][12:])
    black_time = float(game_history[-3][12:])
    if player_is_white:
        my_time = white_time + 2
        their_time = black_time
    else:
        my_time = black_time + 2
        their_time = white_time
    # Vector = List[float]
    # initial_state = [initial_board]

    # ---------- modify game state ----------
    '''
    original_game_state = {
        'board': initial_state, 'white': player_is_white, 'move_no': 0,
        'score': score(initial_state), 'priority': 100,
        'parent': None, 'children': None}
    childless_states = [original_game_state]
    for i in range(10):
        childless_states.sort(key=lambda x: x['priority'])
        for state in childless_states[-1000:]:
            children = []
            for move in moves(state['board']):
                children.append(State(move, state))
            state['children'] = children
            childless_states.append(children)
    '''
    # ----------- proven method
    possible_moves = moves(initial_board, player_is_white)
    if not possible_moves:
        print('The game is a draw')
        exit(1)
    # if my_time < 10:
    depth = 2
    # else:
    #    depth = 3
    moves_with_scores =[]
    for _move in possible_moves:
        _score = smart_score(_move, not player_is_white, depth)
        moves_with_scores.append((_move, _score))
    game_state, predicted_score = (max if player_is_white else min)(moves_with_scores, key=lambda x: x[1])
    print('predicted score: {:.3f}'.format(predicted_score))

    # ---------- write game state -----------
    to_write = '\n-------- turn: {} --------\n\n'.format(turn+1)
    to_write += '\n'.join(game_state.__reversed__())
    open('game state.txt', 'a').write(to_write)

main()
