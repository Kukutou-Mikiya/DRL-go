import random
import sys
#from read import readInput
from write import writeOutput
from go import Board, Point

MAX_SCORE = 999999
MIN_SCORE = -999999

def readInput(n, path="input.txt"):

    with open(path, 'r') as f:
        lines = f.readlines()

        player = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]
        print('board')
        print(board)
        return player, previous_board, board


class AlphaBetaAgent():
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def select_move(self, board):
        best_moves = []
        best_score = None
        best_black = MIN_SCORE
        best_white = MIN_SCORE
        # Loop over all legal moves.
        for possible_move in board.legal_moves():
            # Calculate the game state if we select this move.
            next_state = board.apply_move(possible_move)
            # Since our opponent plays next, figure out their best
            # possible outcome from there.
            opponent_best_outcome = alpha_beta_result(
                next_state, self.max_depth,
                best_black, best_white,)
            print(possible_move,-1 * opponent_best_outcome)
            # Our outcome is the opposite of our opponent's outcome.
            our_best_outcome = -1 * opponent_best_outcome
            if (not best_moves) or our_best_outcome > best_score:
                # This is the best move so far.
                best_moves = [possible_move]
                best_score = our_best_outcome
                if board.player == 1:
                    best_black = best_score
                elif board.player == 2:
                    best_white = best_score
            elif our_best_outcome == best_score:
                # This is as good as our previous best move.
                best_moves.append(possible_move)
        #print(best_moves)
        # For variety, randomly select among all equally good moves.
        return random.choice(best_moves)

#checked
# tag::alpha-beta-prune-1[]
def alpha_beta_result(board, max_depth, best_black, best_white):
    if max_depth == 0:
        #print_board(board)
        #print('score for player',board.player)
        #print(capture_diff(board))                                     # <2>
        return capture_diff(board)                             # <2>

    best_so_far = MIN_SCORE
    for candidate_move in board.legal_moves():            # <3>
        next_board = board.apply_move(candidate_move)     # <4>
        opponent_best_result = alpha_beta_result(              # <5>
            next_board, max_depth - 1,                         # <5>
            best_black, best_white,                            # <5>
            )                                           # <5>
        our_result = -1 * opponent_best_result                 # <6>

        if our_result > best_so_far:                           # <7>
            best_so_far = our_result                           # <7>
# end::alpha-beta-prune-1[]

# tag::alpha-beta-prune-2[]
        if board.player == 2:
            if best_so_far > best_white:                       # <8>
                best_white = best_so_far                       # <8>
            outcome_for_black = -1 * best_so_far               # <9>
            if outcome_for_black < best_black:                 # <9>
                return best_so_far                             # <9>
# end::alpha-beta-prune-2[]
# tag::alpha-beta-prune-3[]
        elif board.player == 1:
            if best_so_far > best_black:                       # <10>
                best_black = best_so_far                       # <10>
            outcome_for_white = -1 * best_so_far               # <11>
            if outcome_for_white < best_white:                 # <11>
                return best_so_far                             # <11>
# end::alpha-beta-prune-3[]
# tag::alpha-beta-prune-4[]

    return best_so_far
# end::alpha-beta-prune-4[]

def capture_diff(board):
    black_stones = 0
    white_stones = 0
    for r in range(0, board.size):
        for c in range(0, board.size):
            p = Point(r, c)
            color = board.get_color(p)
            if color == 1:
                black_stones += 1
            elif color == 2:
                white_stones += 1
    diff = black_stones - white_stones                    # <1>
    if board.player == 1:    # <2>
        return diff                                       # <2>
    return -1 * diff                                      # <3>


if __name__ == "__main__":
    N = 5
    player, previous_board, current_board = readInput(N)
    board = Board(N)
    board.set_board(player, previous_board, current_board)
    player = AlphaBetaAgent(2)
    action = player.select_move(board)
    writeOutput(action)

COLS = 'ABCDEFGHJKLMNOPQRST'
STONE_TO_CHAR = {
    None: ' . ',
    1: ' x ',
    2: ' o ',
}




def print_board(board):
    for row in range(board.size-1, -1, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(0, board.size):
            stone = board.get_color(Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.size]))
