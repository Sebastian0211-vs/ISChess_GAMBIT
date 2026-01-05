import sys
#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
import time
from Bots.ChessBotList import register_chess_bot
from Bots.Gambit_utils import alpha_beta, generate_moves, do_move, opposite

# Gambit chess bot implementation
def Gambit_chess_bot(player_sequence, board, time_budget, **kwargs):

    start_time = time.time()
    stop_time = start_time + time_budget - 0.1

    color = player_sequence[1]
    root_color = color

    transposition_table = {}

    possible_moves = generate_moves(board, color, root_color)

    # No possible moves
    if not possible_moves:
        return (0,0), (0,0)

    best_move = possible_moves[0]

    search_depth = 1
    max_search_depth = 20

    killer_moves = [set() for _ in range(max_search_depth + 5)]

    try:
        while search_depth <= max_search_depth:

            if best_move in possible_moves:
                # We prioritize the previously best move
                possible_moves.sort(key=lambda m: m == best_move, reverse=True)

            current_best_move = None
            best_value = float('-inf')

            for move in possible_moves:
                if time.time() >= stop_time:
                    raise TimeoutError("Search time exceeded")

                new_board = do_move(board, move)
                move_value = alpha_beta(
                    new_board,
                    opposite(color),
                    search_depth - 1,
                    float('-inf'),
                    float('inf'),
                    False,
                    stop_time,
                    transposition_table,
                    killer_moves,
                    ply=1,
                    root_color=root_color
                )

                if move_value > best_value:
                    best_value = move_value
                    current_best_move = move

            if current_best_move is not None:
                best_move = current_best_move
            search_depth += 1

    except TimeoutError:
        print("Search time exceeded, returning best move found so far.", file=sys.stderr)

    return best_move


# Register the Gambit chess bot
register_chess_bot("Gambit", Gambit_chess_bot)
