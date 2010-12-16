class Move(object):
    def __init__(self, squares):
        self.affected_squares = squares
        self.annotation = ''

    def __repr__(self):
        return str(self.affected_squares)
