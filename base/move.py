class Move(object):
    def __init__(self, squares, annotation=''):
        self.affected_squares = squares
        self.annotation = annotation

    def __repr__(self):
        return str(self.affected_squares)
