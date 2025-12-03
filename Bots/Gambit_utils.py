
def alpha_beta(board, color, depth, alpha, beta, is_maximizing):
    if depth == 0 or is_final(board):
        return evaluate(board)

    possible_moves = generate_moves(board, color)

    if is_maximizing:
        max_eval = float('-inf')
        for move in possible_moves:
            new_board = do_move(board, move)
            move_eval = alpha_beta(new_board, color, depth-1, alpha, beta, False)
            max_eval = max(max_eval, move_eval)
            alpha = max(alpha, move_eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in possible_moves:
            new_board = do_move(board, move)
            move_eval = alpha_beta(new_board, color, depth-1, alpha, beta, True)
            min_eval = min(min_eval, move_eval)
            beta = min(beta, move_eval)
            if beta <= alpha:
                break
        return min_eval


def is_final(board):
    # TODO
    # One king is missing
    if is_king_missing(board, 'w') or is_king_missing(board, 'b'):
        return True

    # No more possible moves
    if len(generate_moves(board, 'w')) == 0:
        return True
    if len(generate_moves(board, 'b')) == 0:
        return True

    # Other final conditions

    # Default
    return False


def evaluate(board):
    # TODO
    pass


def generate_moves(board, color):
    # TODO
    possible_moves = []
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x, y]
            if piece != '' and piece[1] == color:
                if piece[0] == 'p':
                    pass
                elif piece[0] == 'r':
                    pass
                elif piece[0] == 'n':
                    pass
                elif piece[0] == 'b':
                    pass
                elif piece[0] == 'q':
                    pass
                elif piece[0] == 'k':
                    pass

    return possible_moves


def do_move(board, move):
    origin = move[0]
    destination = move[1]
    new_board = board.copy()
    piece = new_board[origin]
    new_board[origin] = ''
    new_board[destination] = piece
    return new_board


def is_king_missing(board, color):
    king = 'k' + color
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x, y] == king:
                return False
    return True