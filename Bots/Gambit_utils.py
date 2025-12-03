
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
                    # Move forward
                    if board[x + 1, y] == '':
                        possible_moves.append(((x, y), (x + 1, y)))
                    # Capture diagonally
                    if y - 1 >= 0 and board[x + 1, y - 1] != '' and board[x + 1, y - 1][1] != color:
                        possible_moves.append(((x, y), (x + 1, y - 1)))
                    if y + 1 < board.shape[1] and board[x + 1, y + 1] != '' and board[x + 1, y + 1][1] != color:
                        possible_moves.append(((x, y), (x + 1, y + 1)))
                elif piece[0] == 'r':
                    # Move forward
                    for i in range(x + 1, board.shape[0]):
                        if board[i, y] == '':
                            possible_moves.append(((x, y), (i, y)))
                        elif board[i, y][1] != color:
                            possible_moves.append(((x, y), (i, y)))
                            break
                        else:
                            break
                    # Move backward
                    for i in range(x - 1, -1, -1):
                        if board[i, y] == '':
                            possible_moves.append(((x, y), (i, y)))
                        elif board[i, y][1] != color:
                            possible_moves.append(((x, y), (i, y)))
                            break
                        else:
                            break
                    # Move right
                    for j in range(y + 1, board.shape[1]):
                        if board[x, j] == '':
                            possible_moves.append(((x, y), (x, j)))
                        elif board[x, j][1] != color:
                            possible_moves.append(((x, y), (x, j)))
                            break
                        else:
                            break
                    # Move left
                    for j in range(y - 1, -1, -1):
                        if board[x, j] == '':
                            possible_moves.append(((x, y), (x, j)))
                        elif board[x, j][1] != color:
                            possible_moves.append(((x, y), (x, j)))
                            break
                        else:
                            break
                elif piece[0] == 'n':
                    knight_moves = [
                        (x + 2, y + 1), (x + 2, y - 1),
                        (x - 2, y + 1), (x - 2, y - 1),
                        (x + 1, y + 2), (x + 1, y - 2),
                        (x - 1, y + 2), (x - 1, y - 2)
                    ]
                    for i, j in knight_moves:
                        if 0 <= i < board.shape[0] and 0 <= j < board.shape[1]:
                            if board[i, j] == '' or board[i, j][1] != color:
                                possible_moves.append(((x, y), (i, j)))
                elif piece[0] == 'b':
                    # Diagonal up-right
                    i, j = x + 1, y + 1
                    while i < board.shape[0] and j < board.shape[1]:
                        if board[i, j] == '':
                            possible_moves.append(((x, y), (i, j)))
                        elif board[i, j][1] != color:
                            possible_moves.append(((x, y), (i, j)))
                            break
                        else:
                            break
                        i += 1
                        j += 1
                    # Diagonal up-left
                    i, j = x + 1, y - 1
                    while i < board.shape[0] and j >= 0:
                        if board[i, j] == '':
                            possible_moves.append(((x, y), (i, j)))
                        elif board[i, j][1] != color:
                            possible_moves.append(((x, y), (i, j)))
                            break
                        else:
                            break
                        i += 1
                        j -= 1
                    # Diagonal down-right
                    i, j = x - 1, y + 1
                    while i >= 0 and j < board.shape[1]:
                        if board[i, j] == '':
                            possible_moves.append(((x, y), (i, j)))
                        elif board[i, j][1] != color:
                            possible_moves.append(((x, y), (i, j)))
                            break
                        else:
                            break
                        i -= 1
                        j += 1
                    # Diagonal down-left
                    i, j = x - 1, y - 1
                    while i >= 0 and j >= 0:
                        if board[i, j] == '':
                            possible_moves.append(((x, y), (i, j)))
                        elif board[i, j][1] != color:
                            possible_moves.append(((x, y), (i, j)))
                            break
                        else:
                            break
                        i -= 1
                        j -= 1
                elif piece[0] == 'q':
                    pass
                elif piece[0] == 'k':
                    king_moves = [
                        (x + 1, y), (x - 1, y),
                        (x, y + 1), (x, y - 1),
                        (x + 1, y + 1), (x + 1, y - 1),
                        (x - 1, y + 1), (x - 1, y - 1)
                    ]
                    for i, j in king_moves:
                        if 0 <= i < board.shape[0] and 0 <= j < board.shape[1]:
                            if board[i, j] == '' or board[i, j][1] != color:
                                possible_moves.append(((x, y), (i, j)))

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