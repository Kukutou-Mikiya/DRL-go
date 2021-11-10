import unittest

import six
import enum
from go import Board
from point import Point
from my_player3 import AlphaBetaAgent
from write import writeOutput
import copy
from util import print_board
class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return 1 if self == 2 else 2




class BoardTest(unittest.TestCase):
    def test_capture(self):
        board = Board(19)
        board.place_stone(1, Point(2, 2))
        board.place_stone(2, Point(1, 2))
        self.assertEqual(1, board.get_color(Point(2, 2)))
        board.place_stone(2, Point(2, 1))
        self.assertEqual(1, board.get_color(Point(2, 2)))
        board.place_stone(2, Point(2, 3))
        self.assertEqual(1, board.get_color(Point(2, 2)))
        board.place_stone(2, Point(3, 2))
        self.assertIsNone(board.get_color(Point(2, 2)))

    def test_capture_two_stones(self):
        board = Board(19)
        board.place_stone(1, Point(2, 2))
        board.place_stone(1, Point(2, 3))
        board.place_stone(2, Point(1, 2))
        board.place_stone(2, Point(1, 3))
        self.assertEqual(1, board.get_color(Point(2, 2)))
        self.assertEqual(1, board.get_color(Point(2, 3)))
        board.place_stone(2, Point(3, 2))
        board.place_stone(2, Point(3, 3))
        self.assertEqual(1, board.get_color(Point(2, 2)))
        self.assertEqual(1, board.get_color(Point(2, 3)))
        board.place_stone(2, Point(2, 1))
        board.place_stone(2, Point(2, 4))
        self.assertIsNone(board.get_color(Point(2, 2)))
        self.assertIsNone(board.get_color(Point(2, 3)))
    
    def test_capture_is_not_suicide(self):
        board = Board(19)
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(1, 1))
        board.place_stone(1, Point(0, 2))
        board.place_stone(2, Point(1, 0))
        board.place_stone(2, Point(0, 1))
        self.assertIsNone(board.get_color(Point(0, 0)))
        self.assertEqual(2, board.get_color(Point(1, 0)))
        self.assertEqual(2, board.get_color(Point(0, 1)))

    def test_remove_liberties(self):
        board = Board(5)
        board.place_stone(1, Point(3, 3))
        board.place_stone(2, Point(2, 2))
        white_string = board.get_island(Point(2, 2))
        six.assertCountEqual(
            self,
            [Point(2, 3), Point(2, 1), Point(1, 2), Point(3, 2)],
            white_string.liberties)
        board.place_stone(1, Point(3, 2))
        white_string = board.get_island(Point(2, 2))
        six.assertCountEqual(
            self,
            [Point(2, 3), Point(2, 1), Point(1, 2)],
            white_string.liberties)

    def test_empty_triangle(self):
        board = Board(5)
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(0, 1))
        board.place_stone(1, Point(1, 1))
        board.place_stone(2, Point(1, 0))

        black_string = board.get_island(Point(0, 0))
        six.assertCountEqual(
            self,
            [Point(2, 1), Point(1, 2), Point(0, 2)],
            black_string.liberties)

    def test_self_capture(self):
        # ooo..
        # x.xo.
        board = Board(5)
        board.player = 1
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(0, 2))
        board.place_stone(2, Point(1, 0))
        board.place_stone(2, Point(1, 1))
        board.place_stone(2, Point(1, 2))
        board.place_stone(2, Point(0, 3))

        self.assertTrue(board.ko_and_self_capture_check(1, Point(0, 1)))

    def test_not_self_capture(self):
        # o.o..
        # x.xo.
        board = Board(5)
        board.player = 1
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(0, 2))
        board.place_stone(2, Point(1, 0))
        board.place_stone(2, Point(1, 2))
        board.place_stone(2, Point(0, 3))

        self.assertFalse(board.ko_and_self_capture_check(1, Point(0, 1)))

    def test_not_self_capture2(self):
        # ooo..
        # x.x..
        board = Board(5)
        board.player = 1
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(0, 2))
        board.place_stone(2, Point(1, 0))
        board.place_stone(2, Point(1, 2))
        board.place_stone(2, Point(1, 1))

        self.assertFalse(board.ko_and_self_capture_check(1, Point(0, 1)))

    def test_not_ko(self):
        # .xo..
        # xoxo.
        board = Board(5)
        board.player = 1
        board = board.apply_move(Point(0, 0))
        board = board.apply_move(Point(0, 3))
        board = board.apply_move(Point(1, 1))
        board = board.apply_move(Point(1, 2))
        board = board.apply_move(Point(0, 2))
        self.assertFalse(board.ko_and_self_capture_check(2, Point(0, 1)))
        #print_board(board)        
        board = board.apply_move(Point(0, 1))        
        #print_board(board)
        self.assertTrue(board.ko_and_self_capture_check(1, Point(0, 2)))


    '''
    def test_score(self):
        # ooo..
        # x.x..
        board = Board(5)
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(0, 2))
        board.place_stone(2, Point(1, 0))
        board.place_stone(2, Point(1, 2))
        board.place_stone(2, Point(1, 1))

        self.assertEqual(board.score(1),2)
        self.assertEqual(board.score(2),3)
    '''
    def test_apply_move(self):
        board = Board(5)
        board.player = 1
        previous = board
        board = board.apply_move( Point(0, 0))
        #print(previous.stone_island_dict)
        #print(board.stone_island_dict)
        self.assertEqual(1, len(board.stone_island_dict))
        self.assertEqual(0, len(previous.stone_island_dict))
        self.assertEqual(2, board.player)
        board = board.apply_move( 'PASS')
        self.assertEqual(1, board.player)
        board = board.apply_move( Point(1, 0))
        self.assertEqual(2, board.player)
        #print(board.stone_island_dict)
        board = board.apply_move( Point(1, 2))
        self.assertEqual(1, board.player)
        #print(board.stone_island_dict)
        board = board.apply_move( Point(1, 1))
        self.assertEqual(4, len(board.stone_island_dict))

    def test_legal_move(self):
        board = Board(5)
        board.player = 1
        previous = board
        #board = board.apply_move( Point(0, 0))
        #print(previous.stone_island_dict)
        #print(board.stone_island_dict)
        moves = board.legal_moves()
        #print(moves)


class AgentTest(unittest.TestCase):
    def test_moves(self):
        # ooo..
        # x.x..
        board = Board(5)
        board.player = 1
        board.place_stone(1, Point(0, 0))
        board.place_stone(1, Point(0, 2))
        board.place_stone(2, Point(1, 0))
        board.place_stone(2, Point(1, 2))
        board.place_stone(2, Point(1, 1))
        player = AlphaBetaAgent(0)
        move = player.select_move(board)
        print(move)
        writeOutput(move)

'''
class GameTest(unittest.TestCase):
    def test_new_game(self):
        start = GameState.new_game(19)
        next_state = start.apply_move(Move.play(Point(16, 16)))

        self.assertEqual(start, next_state.previous_state)
        self.assertEqual(2, next_state.next_player)
        self.assertEqual(1, next_state.board.get(Point(16, 16)))
'''

if __name__ == '__main__':
    unittest.main()

