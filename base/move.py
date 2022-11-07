class Move(object):
    def __init__(self, squares, annotation=""):
        self.affected_squares = squares
        self.annotation = annotation

    def __eq__(self, other):
        return self.affected_squares == other.affected_squares

    def __repr__(self):
        return str(self.affected_squares)
