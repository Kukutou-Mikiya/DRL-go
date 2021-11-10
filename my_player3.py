import random
import sys
#from write import writeOutput
from go import Board
from point import Point
MAX_SCORE = 9999
MIN_SCORE = -9999

# reference the sample code provided by 561
def readInput(n, path="input.txt"):

    with open(path, 'r') as f:
        lines = f.readlines()

        player = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]

        return player, previous_board, board

# reference the sample code provided by 561
def writeOutput(result, path="output.txt"):
    res = ""
    if result == "PASS":
        res = "PASS"
    else:
        res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)

def remove_edge(moves):
    for i in range(len(moves)):
        if moves[i][0] != 0 and moves[i][0] != 4 and moves[i][1] != 0 and moves[i][1] != 4:
            return moves[i]
    return moves[0]

'''
def second_heuristic(moves,board):
    if len(moves) == 0:
        return []
    liberty_lost = []
    for i in range(len(moves)):
        adjacent_opposite_color = []
        if moves[i] == 'PASS':
            liberty_lost.append((moves[i], 0))
        else:
            for neighbor in moves[i].neighbors():           
                if not board.boundary_check(neighbor):
                    continue
                neighbor_island = board.stone_island_dict.get(neighbor)
                if neighbor_island is not None and neighbor_island.color == 3 - board.player:
                    if neighbor_island not in adjacent_opposite_color:
                        adjacent_opposite_color.append(neighbor_island)
            liberty_lost.append((moves[i],len(adjacent_opposite_color)))
    liberty_lost.sort(key=lambda x: x[1])
    liberty_lost.reverse()
    max_lost = liberty_lost[0][1]
    for i in range(len(liberty_lost)):
        if liberty_lost[i][1] < max_lost:
            return [x[0] for x in liberty_lost[:i]]
    return [x[0] for x in liberty_lost]
'''
def second_heuristic(moves,board):
    if len(moves) == 0:
        return []
    liberty_lost = []
    for i in range(len(moves)):
        adjacent_opposite_color = []
        if moves[i] == 'PASS':
            liberty_lost.append(0)
        else:
            for neighbor in moves[i].neighbors():           
                if not board.boundary_check(neighbor):
                    continue
                neighbor_island = board.stone_island_dict.get(neighbor)
                if neighbor_island is not None and neighbor_island.color == 3 - board.player:
                    if neighbor_island not in adjacent_opposite_color:
                        adjacent_opposite_color.append(neighbor_island)
            liberty_lost.append(len(adjacent_opposite_color))
    max_index = liberty_lost.index(max(liberty_lost))
    return moves[max_index]

class AlphaBetaAgent():
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def select_move(self, board):
        best_moves = []
        best_score = None
        alpha_black = MIN_SCORE
        alpha_white = MIN_SCORE

        for possible_move in board.legal_moves():

            next_board = board.apply_move(possible_move)

            oppo_score = alpha_beta_result(
                next_board, self.max_depth,
                alpha_black, alpha_white,)

            current_best = -1 * oppo_score

            if (not best_moves) or current_best > best_score:

                best_moves = [possible_move]
                best_score = current_best
                if board.player == 1:
                    alpha_black = best_score
                elif board.player == 2:
                    alpha_white = best_score
            elif current_best == best_score:

                best_moves.append(possible_move)
        
        #best_move = remove_edge(best_moves)        
        best_move = second_heuristic(best_moves,board)
        
        return best_move


def alpha_beta_result(board, max_depth, alpha_black, alpha_white):
    if max_depth == 0:
        return cal_score(board)                             

    current_score = MIN_SCORE
    for candidate_move in board.legal_moves():            
        next_board = board.apply_move(candidate_move)     
        opponent_best_result = alpha_beta_result(              
            next_board, max_depth - 1,                         
            alpha_black, alpha_white,                            
            )                                          
        our_result = -1 * opponent_best_result                 

        if our_result > current_score:                           
            current_score = our_result                           

        if board.player == 2:
            if current_score > alpha_white:                       
                alpha_white = current_score                       
            outcome_for_black = -1 * current_score               
            if outcome_for_black < alpha_black:                 
                return current_score                             

        elif board.player == 1:
            if current_score > alpha_black:                       
                alpha_black = current_score                       
            outcome_for_white = -1 * current_score               
            if outcome_for_white < alpha_white:                 
                return current_score                             

    return current_score


def cal_score(board):
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
    diff = black_stones - white_stones                    
    if board.player == 1:    
        return diff                                       
    return -1 * diff                                      


def init_step(player, path="step.txt"):
    if player == 1:
        with open(path, 'w') as f:
            f.write(str(1))
        return 1    
    else:
        with open(path, 'w') as f:
            f.write(str(2))
        return 2 


def readStep(path="step.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()
        step = int(lines[0])
    with open(path, 'w') as f:
        f.write(str(step+2))            
    return step+2


if __name__ == "__main__":
    N = 5
    player, previous_board, current_board = readInput(N)
    board = Board(N)
    board.set_board(player, previous_board, current_board)
    if len(board.stone_island_dict) <= 1:
        step = init_step(player)
    else:
        step = readStep()
    depth = min(24-step, 3)
    if step != 1:
        player = AlphaBetaAgent(depth)
        action = player.select_move(board)
    else:
        action = Point(2, 2)
    writeOutput(action)


