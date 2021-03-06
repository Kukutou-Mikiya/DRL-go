from collections import namedtuple
import enum
import copy


COLS = 'ABCDEFGHJKLMNOPQRST'
STONE_TO_CHAR = {
    None: ' . ',
    1: ' x ',
    2: ' o ',
}

#this is test
def print_board(board):
    for row in range(board.size-1, -1, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(0, board.size):
            stone = board.get_color(Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))
    print('    ' + '  '.join(COLS[:board.size]))

#checked
class Island():                                        
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def get_liberty(self, point):
        self.liberties.add(point)

    def del_liberty(self, point):
        self.liberties.remove(point)

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


class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row + 1, self.col),
            Point(self.row - 1, self.col),                        
            Point(self.row, self.col + 1),
            Point(self.row, self.col - 1),
        ]


class Board():                                
    def __init__(self, size):
        self.size = size        
        self.stone_island_dict = {}
        self.eat_flag = False
        
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
            neighbor_string = self.stone_island_dict.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_island = Island(player, [point], liberties)
        for same_color_island in adjacent_same_color:               
            new_island = new_island.merge(same_color_island)
        for new_island_point in new_island.stones:
            self.stone_island_dict[new_island_point] = new_island
        for other_color_string in adjacent_opposite_color:       
            other_color_string.del_liberty(point)
        # for other_color_string in adjacent_opposite_color:          
            if other_color_string.num_liberties == 0:
                self.eat_flag = True
                self._remove_string(other_color_string)

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

    def is_place_self_capture(self, player, point):
        next_board = copy.deepcopy(self)
        next_board.place_stone(player, point)
        new_string = next_board.get_island(point)
        return new_string.num_liberties == 0

    # not test
    def does_move_violate_ko(self, player, point):
        next_board = copy.deepcopy(self)
        next_board.eat_flag = False
        next_board.place_stone(player, point)
        if next_board.eat_flag and self.previous_board == next_board:
            return True
        return False

    def is_valid_place(self, player, point):
        return (
            self.get_color(point) is None and
            not self.is_place_self_capture(player, point) and
            not self.does_move_violate_ko(player, point))

    def legal_moves(self):
        moves = []
        for row in range(0, self.size):
            for col in range(0, self.size):
                if self.is_valid_place(self.player, Point(row, col)):
                    moves.append(Point(row, col))
        moves = self.order_moves(self.average_center(), moves)
        moves.append('PASS')
        return moves

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
                cnt+=1
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
        if count!=0:
            return (x_average/count, y_average/count)
        else:
            return (2, 2)

    def order_moves(self, average_point, legal_moves):
        order_moves = []
        for i in legal_moves:
            order_moves.append((self.cal_dis(average_point,i),i))
        order_moves.sort(key = lambda x:x[0])
        order_moves = [i[1] for i in order_moves]
        return order_moves[:12]

    def cal_dis(self, point1, point2):
        return (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2

    def _remove_string(self, island):
        for point in island.stones:
            for neighbor in point.neighbors():                
                neighbor_island = self.stone_island_dict.get(neighbor)
                # if neighbor_island is None:
                #    continue
                if neighbor_island is not island and neighbor_island is not None:
                    neighbor_island.get_liberty(point)
            self.stone_island_dict[point] = None

    def equal_board(self, other):
        for key in (self.stone_island_dict.keys() | other.stone_island_dict.keys()):
            if self.get_color(key) != other.get_color(key):
                return False
        return True

    def __eq__(self, other):
        return self.size == other.size and \
            self.equal_board(other)
