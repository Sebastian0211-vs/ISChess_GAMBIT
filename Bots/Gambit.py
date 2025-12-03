
#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
from Bots.ChessBotList import register_chess_bot
from Bots.Gambit_utils import alpha_beta, generate_moves, do_move

# Gambit chess bot implementation
def Gambit_chess_bot(player_sequence, board, time_budget, **kwargs):

    color = player_sequence[1]

    possible_moves = generate_moves(board, color)

    # No possible moves
    if possible_moves is None or len(possible_moves) == 0:
        return (0,0), (0,0)

    best_move = None
    best_value = float('-inf')

    search_depth = 5

    for move in possible_moves:
        new_board = do_move(board, move)
        move_value = alpha_beta(new_board, color, search_depth-1, float('-inf'), float('inf'), False)

        if move_value > best_value:
            best_value = move_value
            best_move = move


    return best_move


# Register the Gambit chess bot
register_chess_bot("Gambit", Gambit_chess_bot)
