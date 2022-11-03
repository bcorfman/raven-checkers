import copy
from util.globalconst import square_map
from game.checkers import Checkers, Checkerboard


class SavedGame(object):
    def __init__(self):
        self._model = Checkers()
        self.to_move = None
        self.moves = []
        self.description = ''
        self.black_men = []
        self.white_men = []
        self.black_kings = []
        self.white_kings = []
        self.flip_board = False
        self.num_players = 1
        self._bm_check = False
        self._bk_check = False
        self._wm_check = False
        self._wk_check = False

