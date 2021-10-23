import unittest

import six
import enum
from go import Board, Point
from my_player import AlphaBetaAgent
from write import writeOutput
class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white


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

class BoardTest(unittest.TestCase):
    def test_capture(self):
        board = Board(19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.white, Point(1, 2))
        self.assertEqual(Player.black, board.get_color(Point(2, 2)))
        board.place_stone(Player.white, Point(2, 1))
        self.assertEqual(Player.black, board.get_color(Point(2, 2)))
        board.place_stone(Player.white, Point(2, 3))
        self.assertEqual(Player.black, board.get_color(Point(2, 2)))
        board.place_stone(Player.white, Point(3, 2))
        self.assertIsNone(board.get_color(Point(2, 2)))

    def test_capture_two_stones(self):
        board = Board(19)
        board.place_stone(Player.black, Point(2, 2))
        board.place_stone(Player.black, Point(2, 3))
        board.place_stone(Player.white, Point(1, 2))
        board.place_stone(Player.white, Point(1, 3))
        self.assertEqual(Player.black, board.get_color(Point(2, 2)))
        self.assertEqual(Player.black, board.get_color(Point(2, 3)))
        board.place_stone(Player.white, Point(3, 2))
        board.place_stone(Player.white, Point(3, 3))
        self.assertEqual(Player.black, board.get_color(Point(2, 2)))
        self.assertEqual(Player.black, board.get_color(Point(2, 3)))
        board.place_stone(Player.white, Point(2, 1))
        board.place_stone(Player.white, Point(2, 4))
        self.assertIsNone(board.get_color(Point(2, 2)))
        self.assertIsNone(board.get_color(Point(2, 3)))

    def test_capture_is_not_suicide(self):
        board = Board(19)
        board.place_stone(Player.black, Point(0, 0))
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.black, Point(0, 2))
        board.place_stone(Player.white, Point(1, 0))
        board.place_stone(Player.white, Point(0, 1))
        self.assertIsNone(board.get_color(Point(0, 0)))
        self.assertEqual(Player.white, board.get_color(Point(1, 0)))
        self.assertEqual(Player.white, board.get_color(Point(0, 1)))

    def test_remove_liberties(self):
        board = Board(5)
        board.place_stone(Player.black, Point(3, 3))
        board.place_stone(Player.white, Point(2, 2))
        white_string = board.get_island(Point(2, 2))
        six.assertCountEqual(
            self,
            [Point(2, 3), Point(2, 1), Point(1, 2), Point(3, 2)],
            white_string.liberties)
        board.place_stone(Player.black, Point(3, 2))
        white_string = board.get_island(Point(2, 2))
        six.assertCountEqual(
            self,
            [Point(2, 3), Point(2, 1), Point(1, 2)],
            white_string.liberties)

    def test_empty_triangle(self):
        board = Board(5)
        board.place_stone(Player.black, Point(0, 0))
        board.place_stone(Player.black, Point(0, 1))
        board.place_stone(Player.black, Point(1, 1))
        board.place_stone(Player.white, Point(1, 0))

        black_string = board.get_island(Point(0, 0))
        six.assertCountEqual(
            self,
            [Point(2, 1), Point(1, 2), Point(0, 2)],
            black_string.liberties)

    def test_self_capture(self):
        # ooo..
        # x.xo.
        board = Board(5)
        board.place_stone(Player.black, Point(0, 0))
        board.place_stone(Player.black, Point(0, 2))
        board.place_stone(Player.white, Point(1, 0))
        board.place_stone(Player.white, Point(1, 1))
        board.place_stone(Player.white, Point(1, 2))
        board.place_stone(Player.white, Point(0, 3))

        self.assertTrue(board.is_place_self_capture(Player.black, Point(0, 1)))

    def test_not_self_capture(self):
        # o.o..
        # x.xo.
        board = Board(5)
        board.place_stone(Player.black, Point(0, 0))
        board.place_stone(Player.black, Point(0, 2))
        board.place_stone(Player.white, Point(1, 0))
        board.place_stone(Player.white, Point(1, 2))
        board.place_stone(Player.white, Point(0, 3))

        self.assertFalse(board.is_place_self_capture(Player.black, Point(0, 1)))

    def test_not_self_capture2(self):
        # ooo..
        # x.x..
        board = Board(5)
        board.place_stone(Player.black, Point(0, 0))
        board.place_stone(Player.black, Point(0, 2))
        board.place_stone(Player.white, Point(1, 0))
        board.place_stone(Player.white, Point(1, 2))
        board.place_stone(Player.white, Point(1, 1))

        self.assertFalse(board.is_place_self_capture(Player.black, Point(0, 1)))

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
        player = AlphaBetaAgent(2)
        move = player.select_move(board)
        writeOutput(move)

'''
class GameTest(unittest.TestCase):
    def test_new_game(self):
        start = GameState.new_game(19)
        next_state = start.apply_move(Move.play(Point(16, 16)))

        self.assertEqual(start, next_state.previous_state)
        self.assertEqual(Player.white, next_state.next_player)
        self.assertEqual(Player.black, next_state.board.get(Point(16, 16)))
'''

if __name__ == '__main__':
    unittest.main()

