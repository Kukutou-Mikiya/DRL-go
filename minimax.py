import random
import sys
#from read import readInput
from write import writeOutput
from go import Board
from point import Point
MAX_SCORE = 999999
MIN_SCORE = -999999

COLS = 'ABCDEFGHJKLMNOPQRST'
STONE_TO_CHAR = {
    None: ' . ',
    1: ' x ',
    2: ' o ',
}


def print_board(board):
    for row in range(0, board.size):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(0, board.size):
            stone = board.get_color(Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.size]))

def readInput(n, path="input.txt"):

    with open(path, 'r') as f:
        lines = f.readlines()

        player = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]
        #print('board')
        #print(board)
        return player, previous_board, board


class MiniMaxAgent():
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def select_move(self, board):
        best_moves = []
        best_score = None
        # Loop over all legal moves.
        for possible_move in board.legal_moves():
            # Calculate the game state if we select this move.
            next_state = board.apply_move(possible_move)
            # Since our opponent plays next, figure out their best
            # possible outcome from there.
            opponent_best_outcome = best_result(next_state, self.max_depth)
            # Our outcome is the opposite of our opponent's outcome.
            our_best_outcome = -1 * opponent_best_outcome
            if (not best_moves) or our_best_outcome > best_score:
                # This is the best move so far.
                best_moves = [possible_move]
                best_score = our_best_outcome
            elif our_best_outcome == best_score:
                # This is as good as our previous best move.
                best_moves.append(possible_move)
        # For variety, randomly select among all equally good moves.
        return random.choice(best_moves)
# end::depth-prune-agent[]

# tag::depth-prune[]
def best_result(board, max_depth):
    if max_depth == 0:                                     # <2>
        return capture_diff(board)                         # <2>

    best_so_far = MIN_SCORE
    for candidate_move in board.legal_moves():        # <3>
        next_state = board.apply_move(candidate_move) # <4>
        opponent_best_result = best_result(                # <5>
            next_state, max_depth - 1)            # <5>
        our_result = -1 * opponent_best_result             # <6>
        if our_result > best_so_far:                       # <7>
            best_so_far = our_result                       # <7>

    return best_so_far


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

def init_step( path="step.txt"):
    with open(path, 'w') as f:
        f.write(str(1))
    return 1    


def readStep( path="step.txt"):
    #try:
    with open(path, 'r') as f:
        lines = f.readlines()
        step = int(lines[0])
    with open(path, 'w') as f:
        f.write(str(step+1))            
    return step+1


if __name__ == "__main__":
    N = 5
    player, previous_board, current_board = readInput(N)
    board = Board(N)
    board.set_board(player, previous_board, current_board)
    if len(board.stone_island_dict) <= 1:
        step = init_step()
    else:
        step = readStep()
    depth = min(12-step, 2)
    player = MiniMaxAgent(depth)
    action = player.select_move(board)
    writeOutput(action)





