from go import Point

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