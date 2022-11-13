import math
import os
import sys
from configparser import RawConfigParser

DEFAULT_SIZE = 400
BOARD_SIZE = 8
CHECKER_SIZE = 30
MAX_VALID_SQ = 32

HEADER = 1
DESC = 2
BODY = 4

MOVE = 0
JUMP = 1

OCCUPIED = 0
BLACK = 1
WHITE = 2
MAN = 4
KING = 8
FREE = 16
COLORS = BLACK | WHITE
TYPES = OCCUPIED | BLACK | WHITE | MAN | KING | FREE

HUMAN = 0
COMPUTER = 1

MIN = 0
MAX = 1

IMAGE_DIR = 'images' + os.sep
RAVEN_ICON = IMAGE_DIR + '_raven.gif'
BULLET_IMAGE = IMAGE_DIR + 'bullet_green.gif'
CROWN_IMAGE = IMAGE_DIR + 'crown.gif'
BOLD_IMAGE = IMAGE_DIR + 'text_bold.gif'
ITALIC_IMAGE = IMAGE_DIR + 'text_italic.gif'
BULLETS_IMAGE = IMAGE_DIR + 'text_list_bullets.gif'
NUMBERS_IMAGE = IMAGE_DIR + 'text_list_numbers.gif'
ADDLINK_IMAGE = IMAGE_DIR + 'link.gif'
REMLINK_IMAGE = IMAGE_DIR + 'link_break.gif'
UNDO_IMAGE = IMAGE_DIR + 'resultset_previous.gif'
UNDO_ALL_IMAGE = IMAGE_DIR + 'resultset_first.gif'
REDO_IMAGE = IMAGE_DIR + 'resultset_next.gif'
REDO_ALL_IMAGE = IMAGE_DIR + 'resultset_last.gif'
LIGHT_SQUARES = 'tan'
DARK_SQUARES = 'dark green'
OUTLINE_COLOR = 'white'
LIGHT_CHECKERS = 'white'
DARK_CHECKERS = 'red'
WHITE_CHAR = 'w'
WHITE_KING = 'W'
BLACK_CHAR = 'b'
BLACK_KING = 'B'
FREE_CHAR = '.'
OCCUPIED_CHAR = '-'

INFINITY = 9999999
MAX_DEPTH = 10
VERSION = '0.6'
TITLE = 'Raven ' + VERSION
PROGRAM_TITLE = 'Raven Checkers'
CUR_DIR = sys.path[0]
TRAINING_DIR = 'training'

# search values for transposition table
hashfALPHA, hashfBETA, hashfEXACT = range(3)

# constants for evaluation function
TURN = 2      # color to move gets + turn
BRV = 3       # multiplier for back rank
KCV = 5       # multiplier for kings in center
MCV = 1       # multiplier for men in center

MEV = 1       # multiplier for men on edge
KEV = 5       # multiplier for kings on edge
CRAMP = 5     # multiplier for cramp

OPENING = 2   # multipliers for tempo
MIDGAME = -1
ENDGAME = 2
INTACT_DOUBLE_CORNER = 3

BLACK_IDX = [5, 6]
WHITE_IDX = [-5, -6]
KING_IDX = [-6, -5, 5, 6]

FIRST = 0
MID = 1
LAST = -1

#   (white)
#            45  46  47  48
#          39  40  41  42
#            34  35  36  37
#          28  29  30  31
#            23  24  25  26
#          17  18  19  20
#            12  13  14  15
#          6   7   8   9
#   (black)

# other squares reachable from a particular square with a white man
WHITE_MAP = {45: {39, 40, 34, 35, 28, 29, 30, 23, 24, 25, 17, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             46: {40, 41, 34, 35, 36, 28, 29, 30, 31, 23, 24, 25, 26, 17, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             47: {41, 42, 35, 36, 37, 29, 30, 31, 23, 24, 25, 26, 17, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             48: {42, 36, 37, 30, 31, 24, 25, 26, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             39: {34, 28, 29, 23, 24, 17, 18, 19, 12, 13, 14, 6, 7, 8, 9},
             40: {34, 35, 28, 29, 30, 23, 24, 25, 17, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             41: {35, 36, 29, 30, 31, 23, 24, 25, 26, 17, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             42: {36, 37, 30, 31, 24, 25, 26, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             34: {28, 29, 23, 24, 17, 18, 19, 12, 13, 14, 6, 7, 8, 9},
             35: {29, 30, 23, 24, 25, 17, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             36: {30, 31, 24, 25, 26, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             37: {31, 25, 26, 19, 20, 13, 14, 15, 7, 8, 9},
             28: {23, 17, 18, 12, 13, 6, 7, 8},
             29: {23, 24, 17, 18, 19, 12, 13, 14, 6, 7, 8, 9},
             30: {24, 25, 18, 19, 20, 12, 13, 14, 15, 6, 7, 8, 9},
             31: {25, 26, 19, 20, 13, 14, 15, 7, 8, 9},
             23: {17, 18, 12, 13, 6, 7, 8},
             24: {18, 19, 12, 13, 14, 6, 7, 8, 9},
             25: {19, 20, 13, 14, 15, 7, 8, 9},
             26: {20, 14, 15, 8, 9},
             17: {12, 6, 7},
             18: {12, 13, 6, 7, 8},
             19: {13, 14, 7, 8, 9},
             20: {14, 15, 8, 9},
             12: {6, 7},
             13: {7, 8},
             14: {8, 9},
             15: {9},
             6: set(),
             7: set(),
             8: set(),
             9: set()}

# other squares reachable from a particular square with a black man
BLACK_MAP = {6: {12, 17, 18, 23, 24, 28, 29, 30, 34, 35, 36, 39, 40, 41, 42, 45, 46, 47, 48},
             7: {12, 13, 17, 18, 19, 23, 24, 25, 28, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46, 47, 48},
             8: {13, 14, 18, 19, 20, 23, 24, 25, 26, 28, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46, 47, 48},
             9: {14, 15, 19, 20, 24, 25, 26, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46, 47, 48},
             12: {17, 18, 23, 24, 28, 29, 30, 34, 35, 36, 39, 40, 41, 42, 45, 46, 47, 48},
             13: {18, 19, 23, 24, 25, 28, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46, 47, 48},
             14: {19, 20, 24, 25, 26, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46, 47, 48},
             15: {20, 25, 26, 30, 31, 35, 36, 37, 40, 41, 42, 45, 46, 47, 48},
             17: {23, 28, 29, 34, 35, 39, 40, 41, 45, 46, 47},
             18: {23, 24, 28, 29, 30, 34, 35, 36, 39, 40, 41, 42, 45, 46, 47, 48},
             19: {24, 25, 29, 30, 31, 34, 35, 36, 37, 39, 40, 41, 42, 45, 46, 47, 48},
             20: {25, 26, 30, 31, 35, 36, 37, 40, 41, 42, 45, 46, 47, 48},
             23: {28, 29, 34, 35, 39, 40, 41, 45, 46, 47},
             24: {29, 30, 34, 35, 36, 39, 40, 41, 42, 45, 46, 47, 48},
             25: {30, 31, 35, 36, 37, 40, 41, 42, 45, 46, 47, 48},
             26: {31, 36, 37, 41, 42, 46, 47, 48},
             28: {34, 39, 40, 45, 46},
             29: {34, 35, 39, 40, 41, 45, 46, 47},
             30: {35, 36, 40, 41, 42, 45, 46, 47, 48},
             31: {36, 37, 41, 42, 46, 47, 48},
             34: {39, 40, 45, 46},
             35: {40, 41, 45, 46, 47},
             36: {41, 42, 46, 47, 48},
             37: {42, 47, 48},
             39: {45},
             40: {45, 46},
             41: {46, 47},
             42: {47, 48},
             45: set(),
             46: set(),
             47: set(),
             48: set()}

# translate from simple input notation to real checkerboard notation
IMAP = {'a1': 5,  'c1': 6,  'e1': 7,  'g1': 8,
        'b2': 10, 'd2': 11, 'f2': 12, 'h2': 13,
        'a3': 14, 'c3': 15, 'e3': 16, 'g3': 17,
        'b4': 19, 'd4': 20, 'f4': 21, 'h4': 22,
        'a5': 23, 'c5': 24, 'e5': 25, 'g5': 26,
        'b6': 28, 'd6': 29, 'f6': 30, 'h6': 31,
        'a7': 32, 'c7': 33, 'e7': 34, 'g7': 35,
        'b8': 37, 'd8': 38, 'f8': 39, 'h8': 40}

CB_MAP = {5: 4, 6: 3, 7: 2, 8: 1,
          10: 8, 11: 7, 12: 6, 13: 5,
          14: 12, 15: 11, 16: 10, 17: 9,
          19: 16, 20: 15, 21: 14, 22: 13,
          23: 20, 24: 19, 25: 18, 26: 17,
          28: 24, 29: 23, 30: 22, 31: 21,
          32: 28, 33: 27, 34: 26, 35: 25,
          37: 32, 38: 31, 39: 30, 40: 29}


def create_position_map():
    """ Maps compressed grid indices xi + yi * 8 to internal
        board indices """
    pos = {1: 45, 3: 46, 5: 47, 7: 48, 8: 39, 10: 40, 12: 41, 14: 42, 17: 34, 19: 35, 21: 36, 23: 37, 24: 28, 26: 29,
           28: 30, 30: 31, 33: 23, 35: 24, 37: 25, 39: 26, 40: 17, 42: 18, 44: 19, 46: 20, 49: 12, 51: 13, 53: 14,
           55: 15, 56: 6, 58: 7, 60: 8, 62: 9}
    return pos


def create_key_map():
    """ Maps internal board indices to checkerboard label numbers """
    key = {6: 4, 7: 3, 8: 2, 9: 1, 12: 8, 13: 7, 14: 6, 15: 5, 17: 12, 18: 11, 19: 10, 20: 9, 23: 16, 24: 15, 25: 14,
           26: 13, 28: 20, 29: 19, 30: 18, 31: 17, 34: 24, 35: 23, 36: 22, 37: 21, 39: 28, 40: 27, 41: 26, 42: 25,
           45: 32, 46: 31, 47: 30, 48: 29}
    return key


def create_grid_map():
    """ Maps internal board indices to grid (row, col) coordinates """
    grd = {6: (7, 0), 7: (7, 2), 8: (7, 4), 9: (7, 6), 12: (6, 1), 13: (6, 3), 14: (6, 5), 15: (6, 7), 17: (5, 0),
           18: (5, 2), 19: (5, 4), 20: (5, 6), 23: (4, 1), 24: (4, 3), 25: (4, 5), 26: (4, 7), 28: (3, 0), 29: (3, 2),
           30: (3, 4), 31: (3, 6), 34: (2, 1), 35: (2, 3), 36: (2, 5), 37: (2, 7), 39: (1, 0), 40: (1, 2), 41: (1, 4),
           42: (1, 6), 45: (0, 1), 46: (0, 3), 47: (0, 5), 48: (0, 7)}
    return grd


def flip_dict(m):
    d = {}
    keys = [k for k, _ in m.items()]
    values = [v for _, v in m.items()]
    for k, v in zip(values, keys):
        d[k] = v
    return d


def reverse_dict(m):
    d = {}
    keys = [k for k, _ in m.items()]
    values = [v for _, v in m.items()]
    for k, v in zip(keys, reversed(values)):
        d[k] = v
    return d


def similarity(pattern, pieces):
    global grid
    p1 = [grid[i] for i in pattern]
    p2 = [grid[j] for j in pieces]
    return sum(min(math.hypot(x1-x2, y1-y2) for x1, y1 in p1) for x2, y2 in p2)


def get_preferences_from_file():
    config = RawConfigParser()
    if not os.access('raven.ini', os.F_OK):
        # no .ini file yet, so make one
        config.add_section('AnnotationWindow')
        config.set('AnnotationWindow', 'font', 'Arial')
        config.set('AnnotationWindow', 'size', '12')
        # Writing our configuration file to 'raven.ini'
        with open('raven.ini', 'w') as configfile:
            config.write(configfile)
    config.read('raven.ini')
    font = config.get('AnnotationWindow', 'font')
    size = config.get('AnnotationWindow', 'size')
    return font, size


def write_preferences_to_file(font, size):
    config = RawConfigParser()
    config.add_section('AnnotationWindow')
    config.set('AnnotationWindow', 'font', font)
    config.set('AnnotationWindow', 'size', size)
    # Writing our configuration file to 'raven.ini'
    with open('raven.ini', 'w') as configfile:
        config.write(configfile)


def parse_index(idx):
    line, _, char = idx.partition('.')
    return int(line), int(char)


def to_string(line, char):
    return "%d.%d" % (line, char)


grid = create_grid_map()
keymap = create_key_map()
square_map = flip_dict(keymap)
