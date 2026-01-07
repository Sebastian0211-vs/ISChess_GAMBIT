import time

from Bots.Gambit_evaluation import evaluate


def alpha_beta(board, color, depth, alpha, beta, is_maximizing, stop_time,transposition_table, killer_moves, ply, root_color, config, info):

    info['nodes'] += 1

    if time.time() >= stop_time:
        raise TimeoutError("Search time exceeded")

    board_hash = get_board_hash(board, color)
    original_alpha = alpha
    original_beta = beta

    if config["USE_TT"] and board_hash in transposition_table:
        entry = transposition_table[board_hash]
        # If the stored depth is greater or equal, we can use the stored value
        if entry['depth'] >= depth:
            if entry['flag'] == 'EXACT':
                info['tt_cuts'] += 1
                return entry['value']
            elif entry['flag'] == 'LOWERBOUND': # Alpha value
                alpha = max(alpha, entry['value'])
            elif entry['flag'] == 'UPPERBOUND': # Beta value
                beta = min(beta, entry['value'])

            # If alpha and beta cross (lowerbound > upperbound), we can return the stored value
            if alpha >= beta:
                info['tt_cuts'] += 1
                return entry['value']

    # if is_terminal(board, color, root_color):
    #     value = evaluate(board, color)
    #     if not is_maximizing:
    #         return -value
    #     return value

    if is_king_missing(board, 'w') or is_king_missing(board, 'b'):
        return evaluate(board, root_color)

    if depth == 0:
        return quiescence(board, color, alpha, beta, stop_time, transposition_table, root_color=root_color, info=info)

    possible_moves = generate_moves(board, color, root_color)

    if not possible_moves or len(possible_moves) == 0:
        return evaluate(board, color)

    is_maximizing = (color == root_color)

    def is_capture(board, move):
        (_, _), (dx, dy) = move
        return board[dx, dy] != ""

    if config["USE_MOVE_ORDERING"]:
        possible_moves.sort(
            key=lambda m: (
                config["USE_KILLER_MOVES"] and m in killer_moves[ply],  # killers first
                score_move(board, m)  # then your existing capture heuristic
            ),
            reverse=True
        )

    best_eval = float('-inf') if is_maximizing else float('inf')

    if is_maximizing:
        #max_eval = float('-inf')
        for move in possible_moves:
            new_board = do_move(board, move)
            move_eval = alpha_beta(new_board, opposite(color), depth-1, alpha, beta, False, stop_time, transposition_table, killer_moves, ply+1, root_color, config, info)
            best_eval = max(best_eval, move_eval)
            alpha = max(alpha, move_eval)
            if beta <= alpha:
                # Store killer ONLY if it's a quiet move (captures are already ordered by score_move)
                if config["USE_KILLER_MOVES"] and not is_capture(board, move):
                    killer_moves[ply].add(move)
                break

        #return max_eval
    else:
        #min_eval = float('inf')
        for move in possible_moves:
            new_board = do_move(board, move)
            move_eval = alpha_beta(new_board, opposite(color), depth-1, alpha, beta, True, stop_time, transposition_table, killer_moves, ply +1, root_color, config, info)
            best_eval = min(best_eval, move_eval)
            beta = min(beta, move_eval)
            if beta <= alpha:
                if config["USE_KILLER_MOVES"] and not is_capture(board, move):
                    killer_moves[ply].add(move)
                break

        #return min_eval

    # Determine the flag for the transposition table
    if config["USE_TT"]:
        entry_flag = 'EXACT'
        if best_eval <= original_alpha:
            entry_flag = 'UPPERBOUND' # We did not find a better move
        elif best_eval >= original_beta:
            entry_flag = 'LOWERBOUND' # We found a better move

        # Store the result in the transposition table
        transposition_table[board_hash] = {
            'value': best_eval,
            'depth': depth,
            'flag': entry_flag
        }

    return best_eval




def is_terminal(board, color, root_color):
    # One king is missing
    if is_king_missing(board, 'w') or is_king_missing(board, 'b'):
        return True

    # No more possible moves
    if len(generate_moves(board, color, root_color)) == 0:
        return True

    # Other final conditions

    # Default
    return False

def generate_captures(board, color, root_color):
    """Return capture moves only: moves where destination contains enemy piece."""
    caps = []
    for move in generate_moves(board, color, root_color):
        (_, _), (dx, dy) = move
        dst = board[dx, dy]
        if dst != '' and dst[1] != color:
            caps.append(move)
    return caps

def quiescence(board, color, alpha, beta, stop_time, transposition_table, q_depth=16, root_color=None, info=None):
    """
    Quiescence search (captures-only) to reduce horizon effect.
    Semantics match your current code style: evaluate(board, color) is 'good for color'.
    """
    info['nodes'] += 1

    if time.time() >= stop_time:
        raise TimeoutError("Search time exceeded")

    # Score always from root_color perspective
    stand_pat = evaluate(board, root_color)

    # Decide whether this node is maximizing or minimizing
    maximizing = (color == root_color)

    if maximizing:
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat

    if q_depth <= 0:
        return alpha if maximizing else beta

    captures = generate_captures(board, color, root_color)

    # Order captures by victim value (same as you did)
    piece_value = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000}

    def capture_order(m):
        (_, _), (dx, dy) = m
        victim = board[dx, dy]
        return piece_value.get(victim[0], 0) if victim != '' else 0

    captures.sort(key=capture_order, reverse=True)

    if maximizing:
        for move in captures:
            if time.time() >= stop_time:
                raise TimeoutError("Search time exceeded")
            new_board = do_move(board, move)
            score = quiescence(new_board, opposite(color), alpha, beta,
                               stop_time, transposition_table,
                               q_depth=q_depth - 1, root_color=root_color, info=info)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        for move in captures:
            if time.time() >= stop_time:
                raise TimeoutError("Search time exceeded")
            new_board = do_move(board, move)
            score = quiescence(new_board, opposite(color), alpha, beta,
                               stop_time, transposition_table,
                               q_depth=q_depth - 1, root_color=root_color, info=info)
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta

def generate_moves(board, color, root_color):
    possible_moves = []
    direction  = 1 if color == root_color else -1

    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x, y]
            if piece != '' and piece[1] == color:
                # if piece[0] == 'p':
                #     if x + 1 < board.shape[0]:
                #         # Move forward
                #         if board[x + 1, y] == '':
                #             possible_moves.append(((x, y), (x + 1, y)))
                #         # Capture diagonally
                #         if y - 1 >= 0 and board[x + 1, y - 1] != '' and board[x + 1, y - 1][1] != color:
                #             possible_moves.append(((x, y), (x + 1, y - 1)))
                #         if y + 1 < board.shape[1] and board[x + 1, y + 1] != '' and board[x + 1, y + 1][1] != color:
                #             possible_moves.append(((x, y), (x + 1, y + 1)))
                if piece[0] == 'p':
                    next_x = x + direction
                    if 0 <= next_x < board.shape[0]:
                        # Move forward
                        if board[next_x, y] == '':
                            possible_moves.append(((x, y), (next_x, y)))
                        # Capture diagonally left
                        if y - 1 >= 0:
                            target = board[next_x, y - 1]
                            if target != '' and target[1] != color:
                                possible_moves.append(((x, y), (next_x, y - 1)))
                        # Capture diagonally right
                        if y + 1 < board.shape[1]:
                            target = board[next_x, y + 1]
                            if target != '' and target[1] != color:
                                possible_moves.append(((x, y), (next_x, y + 1)))
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
    (ox, oy), (dx, dy) = move
    new_board = board.copy()

    piece = new_board[ox, oy]
    new_board[ox, oy] = ''

    # if piece != '' and piece[0] == 'p' and dx == new_board.shape[0] - 1:
    #     piece = 'q' + piece[1]

    if piece != '' and piece[0] == 'p':
        if dx == 0 or dx == new_board.shape[0] - 1:
            piece = 'q' + piece[1]

    new_board[dx, dy] = piece
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
    #return hash((color, tuple(board.ravel().tolist())))
    return hash((color, board.tobytes()))



PIECE_VALUE = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000}

def score_move(board, move, tt_move=None, killer_moves=None):
    (ox, oy), (dx, dy) = move

    if tt_move is not None and move == tt_move:
        return 10_000_000  # always search TT-best first

    piece = board[ox, oy]
    captured = board[dx, dy]

    attacker = piece[0] if piece else ''
    victim = captured[0] if captured else ''

    score = 0

    # Killer moves (non-captures that caused a beta cutoff at same depth)
    if killer_moves is not None and move in killer_moves:
        score += 50_000

    # Promotions (your rules: auto queen promotion when pawn reaches last rank)
    # if attacker == 'p' and dx == board.shape[0] - 1:
    #     score += 80_000

    if attacker == 'p' and (dx == 0 or dx == board.shape[0] - 1):
        score += 80_000

    # MVV-LVA capture ordering
    if victim:
        score += 100_000  # ensure captures > quiet moves
        score += 10 * PIECE_VALUE[victim] - PIECE_VALUE[attacker]

    return score

