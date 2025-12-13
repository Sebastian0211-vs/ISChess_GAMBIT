import time

def alpha_beta(board, color, depth, alpha, beta, is_maximizing, stop_time, transposition_table):

    if time.time() >= stop_time:
        raise TimeoutError("Search time exceeded")

    board_hash = get_board_hash(board, color)
    original_alpha = alpha

    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        # If the stored depth is greater or equal, we can use the stored value
        if entry['depth'] >= depth:
            if entry['flag'] == 'EXACT':
                return entry['value']
            elif entry['flag'] == 'LOWERBOUND': # Alpha value
                alpha = max(alpha, entry['value'])
            elif entry['flag'] == 'UPPERBOUND': # Beta value
                beta = min(beta, entry['value'])

            # If alpha and beta cross (lowerbound > upperbound), we can return the stored value
            if alpha >= beta:
                return entry['value']

    if depth == 0 or is_terminal(board, color):
        return evaluate(board)

    possible_moves = generate_moves(board, color)

    best_eval = float('-inf') if is_maximizing else float('inf')

    if is_maximizing:
        #max_eval = float('-inf')
        for move in possible_moves:
            new_board = do_move(board, move)
            move_eval = alpha_beta(new_board, opposite(color), depth-1, alpha, beta, False, stop_time, transposition_table)
            best_eval = max(best_eval, move_eval)
            alpha = max(alpha, move_eval)
            if beta <= alpha:
                break
        #return max_eval
    else:
        #min_eval = float('inf')
        for move in possible_moves:
            new_board = do_move(board, move)
            move_eval = alpha_beta(new_board, opposite(color), depth-1, alpha, beta, True, stop_time, transposition_table)
            best_eval = min(best_eval, move_eval)
            beta = min(beta, move_eval)
            if beta <= alpha:
                break
        #return min_eval

    # Determine the flag for the transposition table
    entry_flag = 'EXACT'
    if best_eval <= original_alpha:
        entry_flag = 'UPPERBOUND' # We did not find a better move
    elif best_eval >= beta:
        entry_flag = 'LOWERBOUND' # We found a better move

    # Store the result in the transposition table
    transposition_table[board_hash] = {
        'value': best_eval,
        'depth': depth,
        'flag': entry_flag
    }

    return best_eval


def is_terminal(board, color):
    # TODO
    # One king is missing
    if is_king_missing(board, 'w') or is_king_missing(board, 'b'):
        return True

    # No more possible moves
    if len(generate_moves(board, color)) == 0:
        return True

    # Other final conditions

    # Default
    return False


def evaluate(board):
    # TODO
    return 0


def generate_moves(board, color):
    # TODO
    possible_moves = []
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x, y]
            if piece != '' and piece[1] == color:
                if piece[0] == 'p':
                    if x + 1 < board.shape[0]:
                        # Move forward
                        if board[x + 1, y] == '':
                            possible_moves.append(((x, y), (x + 1, y)))
                        # Capture diagonally
                        if y - 1 >= 0 and board[x + 1, y - 1] != '' and board[x + 1, y - 1][1] != color:
                            possible_moves.append(((x, y), (x + 1, y - 1)))
                        if y + 1 < board.shape[1] and board[x + 1, y + 1] != '' and board[x + 1, y + 1][1] != color:
                            possible_moves.append(((x, y), (x + 1, y + 1)))
                elif piece[0] == 'r':
                    possible_moves.extend(rook_moves(board, x, y, color))
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
                    possible_moves.extend(bishop_moves(board, x, y, color))
                elif piece[0] == 'q':
                    # Move straight
                    possible_moves.extend(rook_moves(board, x, y, color))
                    # Move diagonally
                    possible_moves.extend(bishop_moves(board, x, y, color))
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


def rook_moves(board, x, y, color):
    possible_moves = []
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

    return possible_moves


def bishop_moves(board, x, y, color):
    possible_moves = []
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

    return possible_moves


def opposite(color):
    return 'w' if color == 'b' else 'b'


def get_board_hash(board, color):
    return hash((board.tobytes(), color))