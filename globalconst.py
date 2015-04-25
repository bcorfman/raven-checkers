import math, os, sys
from ConfigParser import RawConfigParser

DEFAULT_SIZE = 400
BOARD_SIZE = 8
CHECKER_SIZE = 30
MAX_VALID_SQ = 32

# goal status
INACTIVE = 0
ACTIVE = 1
COMPLETED = 2
FAILED = 3

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
RAVEN_ICON = IMAGE_DIR + '_raven.ico'
BULLET_IMAGE = IMAGE_DIR + 'bullet_green.gif'
CROWN_IMAGE = IMAGE_DIR + 'crown.gif'
BOLD_IMAGE = IMAGE_DIR + 'text_bold.gif'
ITALIC_IMAGE = IMAGE_DIR + 'text_italic.gif'
BULLETS_IMAGE = IMAGE_DIR + 'text_list_bullets.gif'
NUMBERS_IMAGE = IMAGE_DIR + 'text_list_numbers.gif'
ADDLINK_IMAGE = IMAGE_DIR + 'link.gif'
REMLINK_IMAGE = IMAGE_DIR + 'link_break.gif'
UNDO_IMAGE = IMAGE_DIR + 'resultset_previous.gif'
UNDOALL_IMAGE = IMAGE_DIR + 'resultset_first.gif'
REDO_IMAGE = IMAGE_DIR + 'resultset_next.gif'
REDOALL_IMAGE = IMAGE_DIR + 'resultset_last.gif'
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
MAXDEPTH = 10
VERSION = '0.4'
TITLE = 'Raven ' + VERSION
PROGRAM_TITLE = 'Raven Checkers'
CUR_DIR = sys.path[0]
TRAINING_DIR = 'training'

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
INTACTDOUBLECORNER = 3

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


# translate from black indices to white indices and vice versa
INDEX_MAP = {6: 48, 7: 47, 8: 46, 9: 45,
             12: 42, 13: 41, 14: 40, 15: 39,
             17: 37, 18: 36, 19: 35, 20: 34,
             23: 31, 24: 30, 25: 29, 26: 28,
             28: 26, 29: 25, 30: 24, 31: 23,
             34: 20, 35: 19, 36: 18, 37: 17,
             39: 15, 40: 14, 41: 13, 42: 12,
             45: 9, 46: 8, 47: 7, 48: 6}

# translate from simple input notation to real checkerboard notation
IMAP = {'a1': 5,  'c1': 6,  'e1': 7,  'g1': 8,
        'b2': 10, 'd2': 11, 'f2': 12, 'h2': 13,
        'a3': 14, 'c3': 15, 'e3': 16, 'g3': 17,
        'b4': 19, 'd4': 20, 'f4': 21, 'h4': 22,
        'a5': 23, 'c5': 24, 'e5': 25, 'g5': 26,
        'b6': 28, 'd6': 29, 'f6': 30, 'h6': 31,
        'a7': 32, 'c7': 33, 'e7': 34, 'g7': 35,
        'b8': 37, 'd8': 38, 'f8': 39, 'h8': 40}

CBMAP = {5: 4, 6: 3, 7: 2, 8: 1,
         10: 8, 11: 7, 12: 6, 13: 5,
         14: 12, 15: 11, 16: 10, 17: 9,
         19: 16, 20: 15, 21: 14, 22: 13,
         23: 20, 24: 19, 25: 18, 26: 17,
         28: 24, 29: 23, 30: 22, 31: 21,
         32: 28, 33: 27, 34: 26, 35: 25,
         37: 32, 38: 31, 39: 30, 40: 29}

# Maps compressed grid indices xi + yi * 8 to internal board indices
POS_MAP = {1: 45,  3: 46,  5: 47,  7: 48,
           8: 39, 10: 40, 12: 41, 14: 42,
           17: 34, 19: 35, 21: 36, 23: 37,
           24: 28, 26: 29, 28: 30, 30: 31,
           33: 23, 35: 24, 37: 25, 39: 26,
           40: 17, 42: 18, 44: 19, 46: 20,
           49: 12, 51: 13, 53: 14, 55: 15,
           56: 6,  58:  7, 60:  8, 62:  9}

# Maps internal board indices to checkerboard label numbers
KEY_MAP = {6: 4, 7: 3, 8: 2, 9: 1,
           12: 8, 13: 7, 14: 6, 15: 5,
           17: 12, 18: 11, 19: 10, 20: 9,
           23: 16, 24: 15, 25: 14, 26: 13,
           28: 20, 29: 19, 30: 18, 31: 17,
           34: 24, 35: 23, 36: 22, 37: 21,
           39: 28, 40: 27, 41: 26, 42: 25,
           45: 32, 46: 31, 47: 30, 48: 29}

# Maps internal board indices to grid (row, col) coordinates
GRID_MAP = {6:  (7, 0), 7:  (7, 2), 8:  (7, 4), 9:  (7, 6),
            12: (6, 1), 13: (6, 3), 14: (6, 5), 15: (6, 7),
            17: (5, 0), 18: (5, 2), 19: (5, 4), 20: (5, 6),
            23: (4, 1), 24: (4, 3), 25: (4, 5), 26: (4, 7),
            28: (3, 0), 29: (3, 2), 30: (3, 4), 31: (3, 6),
            34: (2, 1), 35: (2, 3), 36: (2, 5), 37: (2, 7),
            39: (1, 0), 40: (1, 2), 41: (1, 4), 42: (1, 6),
            45: (0, 1), 46: (0, 3), 47: (0, 5), 48: (0, 7)}


def flip_dict(m):
    d = {}
    keys = [k for k, _ in m.iteritems()]
    vals = [v for _, v in m.iteritems()]
    for k, v in zip(vals, keys):
        d[k] = v
    return d


def reverse_dict(m):
    d = {}
    keys = [k for k, _ in m.iteritems()]
    vals = [v for _, v in m.iteritems()]
    for k, v in zip(keys, reversed(vals)):
        d[k] = v
    return d


def get_preferences_from_file():
    config = RawConfigParser()
    if not os.access('raven.ini',os.F_OK):
        # no .ini file yet, so make one
        config.add_section('AnnotationWindow')
        config.set('AnnotationWindow', 'font', 'Arial')
        config.set('AnnotationWindow', 'size', '12')
        # Writing our configuration file to 'raven.ini'
        with open('raven.ini', 'wb') as configfile:
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
    with open('raven.ini', 'wb') as configfile:
        config.write(configfile)


def parse_index(idx):
    line, _, char = idx.partition('.')
    return int(line), int(char)


def to_string(line, char):
    return "%d.%d" % (line, char)

squaremap = flip_dict(KEY_MAP)
