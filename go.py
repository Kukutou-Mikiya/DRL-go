from collections import namedtuple
import enum
import copy
import zobrist_hash
import random
from point import Point


class Island():                                        
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def get_liberty(self, point):
        new_liberties = self.liberties | set([point])
        return Island(self.color, self.stones, new_liberties)

    def del_liberty(self, point):
        new_liberties = self.liberties - set([point])
        return Island(self.color, self.stones, new_liberties)

    def merge(self, island):                    
        if island.color != self.color:
            return False
        merged_stones = self.stones | island.stones
        return Island(
            self.color,
            merged_stones,
            (self.liberties | island.liberties) - merged_stones)

    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.color == other.color and self.stones == other.stones\
            and self.liberties == other.liberties

    def __deepcopy__(self, memodict={}):
        return Island(self.color, self.stones, copy.deepcopy(self.liberties))


class Board():                                
    def __init__(self, size):
        self.size = size        
        self.stone_island_dict = {}
        self.eat_flag = False
        self._hash = zobrist_hash.EMPTY_BOARD
        
    def set_board(self, player, previous, board):
        self.player = player
        self.previous_board = Board(len(board))
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == 1:
                    self.place_stone(1, Point(i, j))
                if board[i][j] == 2:
                    self.place_stone(2, Point(i, j))    
                if previous[i][j] == 1:
                    self.previous_board.place_stone(1, Point(i, j))
                if previous[i][j] == 2:
                    self.previous_board.place_stone(2, Point(i, j))

    def place_stone(self, player, point):
        if not self.boundary_check(point):
            return False
        if self.stone_island_dict.get(point) is not None:
            return False
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in point.neighbors():           
            if not self.boundary_check(neighbor):
                continue
            neighbor_island = self.stone_island_dict.get(neighbor)
            if neighbor_island is None:
                liberties.append(neighbor)
            elif neighbor_island.color == player:
                if neighbor_island not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_island)
            else:
                if neighbor_island not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_island)
        new_island = Island(player, [point], liberties)

        for same_color_island in adjacent_same_color:               
            new_island = new_island.merge(same_color_island)
        for new_island_point in new_island.stones:
            self.stone_island_dict[new_island_point] = new_island

        self._hash ^= zobrist_hash.HASH_CODE[point, player]

        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.del_liberty(point)  
            if replacement.num_liberties:
                self._replace_island(other_color_string.del_liberty(point))
            else:
                self.eat_flag = True
                self.remove_island(other_color_string)  

    def apply_move(self, point):
        if point == 'PASS':
            next_board = copy.deepcopy(self)
            next_board.eat_flag = False
        else:
            next_board = copy.deepcopy(self)
            next_board.eat_flag = False
            next_board.place_stone(self.player, point)
        next_board.player = 3 - next_board.player
        next_board.previous_board = self
        return next_board

    '''
    def is_place_self_capture(self, player, point):
        next_board = copy.deepcopy(self)
        next_board.place_stone(player, point)
        new_string = next_board.get_island(point)
        return new_string.num_liberties == 0

    def does_move_violate_ko(self, player, point):
        next_board = copy.deepcopy(self)
        next_board.eat_flag = False
        next_board.place_stone(player, point)
        if next_board.eat_flag and self.previous_board == next_board:
            return True
        return False
    '''

    def ko_and_self_capture_check(self, player, point):
        next_board = copy.deepcopy(self)
        next_board.eat_flag = False
        next_board.place_stone(player, point)
        new_string = next_board.get_island(point)
        if next_board.eat_flag and self.previous_board == next_board:
            return True
        elif new_string.num_liberties == 0:
            return True
        return False

    def is_valid_place(self, player, point):
        return (
            self.get_color(point) is None and
            not self.ko_and_self_capture_check(player, point))

    def prority_move(self, point):
        for neighbor in point.neighbors():           
            if not self.boundary_check(neighbor):
                continue
            neighbor_island = self.stone_island_dict.get(neighbor)
            if neighbor_island is not None and neighbor_island.color == 3 - self.player:
                return True
        return False

    def order_moves(self, legal_moves):
        order_moves = []
        for i in legal_moves:
            if self.prority_move(i):
                order_moves.append((i, 1))
            else:
                order_moves.append((i, 0))
        order_moves.sort(key=lambda x: x[1])
        order_moves.reverse()
        order_moves = [x[0] for x in order_moves]
        return order_moves

    def legal_moves(self):
        moves = []
        for row in range(0, self.size):
            for col in range(0, self.size):
                if self.is_valid_place(self.player, Point(row, col)):
                    moves.append(Point(row, col))
        #random.shuffle(moves)
        moves = self.order_moves(moves)
        moves.append('PASS')
        return moves[:18]


    def boundary_check(self, point):
        return 0 <= point.row < self.size and 0 <= point.col < self.size

    def get_color(self, point):                 
        island = self.stone_island_dict.get(point)
        if island is None:
            return None
        return island.color

    def get_island(self, point):       
        island = self.stone_island_dict.get(point)
        if island is None:
            return None
        return island

    def score(self, player):
        cnt = 0
        for i in self.stone_island_dict.keys():
            if self.get_color(i) == player:
                cnt += 1
        return cnt 

    def average_center(self):
        x_average = 0
        y_average = 0
        count = 0
        for i in self.stone_island_dict.keys():
            if self.stone_island_dict[i] is not None:
                count += 1
                x_average += i.col
                y_average += i.row
        if count != 0:
            return (x_average/count, y_average/count)
        else:
            return (2, 2)

    def cal_dis(self, point1, point2):
        return (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2

    def _replace_island(self, new_island):  
        for point in new_island.stones:
            self.stone_island_dict[point] = new_island

    def remove_island(self, island):
        for point in island.stones:
            for neighbor in point.neighbors():                
                neighbor_island = self.stone_island_dict.get(neighbor)
                # if neighbor_island is None:
                #    continue
                if neighbor_island is not None and neighbor_island is not island:
                    self._replace_island(neighbor_island.get_liberty(point))
            self.stone_island_dict[point] = None

            self._hash ^= zobrist_hash.HASH_CODE[point, island.color]
             
    def equal_board(self, other):
        for key in (self.stone_island_dict.keys() | other.stone_island_dict.keys()):
            if self.get_color(key) != other.get_color(key):
                return False
        return True

    def __eq__(self, other):
        return self.size == other.size and \
        self._hash == other._hash

        
    def __deepcopy__(self, memodict={}):
        copied = Board(self.size)
        copied.stone_island_dict = copy.copy(self.stone_island_dict)
        copied.player = self.player
        copied._hash = self._hash
        return copied

    def zobrist_hash(self):
        return self._hash