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
from Bots.Log_Gambit_utils import alpha_beta, generate_moves, do_move, opposite, score_move

# Configuration options
GAMBIT_CONFIG = {
    "USE_TT": True,            # Table de Transposition
    "USE_MOVE_ORDERING": True, # Tri des coups (MVV-LVA + Promotion)
    "USE_KILLER_MOVES": True,  # Killer Moves
    "USE_QUIESCENCE": True,    # Quiescence Search
    "DEBUG_STATS": True        # Afficher les stats dans la console
}

import os
import csv
from datetime import datetime
# Chemin du fichier de logs
LOG_FILE = os.path.join(os.path.dirname(__file__), 'gambit_logs.csv')


def log_stats(stats):
    """Écrit les stats dans un fichier CSV pour comparaison."""
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)

        # Création de l'en-tête si le fichier est nouveau
        if not file_exists:
            headers = ['Timestamp', 'Depth', 'Score', 'Time', 'Nodes', 'NPS', 'TT_Cuts']
            # Ajout dynamique des colonnes de config
            headers += [key for key in GAMBIT_CONFIG.keys()]
            writer.writerow(headers)

        # Préparation de la ligne de données
        row = [
            datetime.now().strftime("%H:%M:%S"),
            stats['depth'],
            stats['score'],
            f"{stats['time']:.3f}",
            stats['nodes'],
            stats['nps'],
            stats['tt_cuts']
        ]
        # Ajout des valeurs de config (True/False)
        row += [GAMBIT_CONFIG[key] for key in GAMBIT_CONFIG.keys()]

        writer.writerow(row)

# Gambit chess bot implementation
def Log_Gambit_chess_bot(player_sequence, board, time_budget, **kwargs):

    start_time = time.time()
    stop_time = start_time + time_budget - min(0.1, time_budget*0.1)

    color = player_sequence[1]
    root_color = color

    transposition_table = {}

    # Dictionnaire pour collecter des stats
    info = {'nodes': 0, 'tt_cuts': 0}
    stats = {}

    possible_moves = generate_moves(board, color, root_color)

    # No possible moves
    if not possible_moves:
        return (0,0), (0,0)

    best_move = possible_moves[0]

    search_depth = 1
    max_search_depth = 20

    killer_moves = [set() for _ in range(max_search_depth + 5)]
    root_scores = {m: 0 for m in possible_moves}


    try:
        while search_depth <= max_search_depth:

            if GAMBIT_CONFIG["USE_MOVE_ORDERING"] and best_move in possible_moves:
                # We prioritize the previously best move
                possible_moves.sort(
                    key=lambda m: (
                        root_scores.get(m, float('-inf')),  # best from last completed depth first
                        score_move(board, m)  # then tactical ordering
                    ),
                    reverse=True
                )
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
                    root_color=root_color,
                    config=GAMBIT_CONFIG,
                    info=info
                )

                root_scores[move] = move_value


                if move_value > best_value:
                    best_value = move_value
                    current_best_move = move

            if current_best_move is not None:
                best_move = current_best_move

            if GAMBIT_CONFIG["DEBUG_STATS"]:
                elapsed_time = time.time() - start_time
                nps = int(info['nodes'] / elapsed_time) if elapsed_time > 0 else 0
                #print(f"Depth: {search_depth} | Score: {best_value} | Nodes: {info['nodes']} | NPS: {nps} | TT Cuts: {info['tt_cuts']}")

                stats = {
                    'depth': search_depth,
                    'score': best_value,
                    'time': elapsed_time,
                    'nodes': info['nodes'],
                    'nps': nps,
                    'tt_cuts': info['tt_cuts']
                }

            search_depth += 1

    except TimeoutError:
        print("Search time exceeded, returning best move found so far.", file=sys.stderr)

    if stats:
        log_stats(stats)

    return best_move


# Register the Gambit chess bot
register_chess_bot("Log_Gambit", Log_Gambit_chess_bot)
