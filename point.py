from collections import namedtuple
class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row + 1, self.col),
            Point(self.row - 1, self.col),                        
            Point(self.row, self.col + 1),
            Point(self.row, self.col - 1),
        ]