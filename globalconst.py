import math, os, sys
from ConfigParser import RawConfigParser

DEFAULT_SIZE = 400
BOARD_SIZE = 8
CHECKER_SIZE = 30
MAX_VALID_SQ = 32

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
INTACTDOUBLECORNER = 3

BLACK_IDX = [5,6]
WHITE_IDX = [-5,-6]
KING_IDX = [-6,-5,5,6]

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
WHITEMAP = {45: set([39,40,34,35,28,29,30,23,24,25,17,18,19,20,12,13,14,15,6,7,8,9]),
            46: set([40,41,34,35,36,28,29,30,31,23,24,25,26,17,18,19,20,12,13,14,15,6,7,8,9]),
            47: set([41,42,35,36,37,29,30,31,23,24,25,26,17,18,19,20,12,13,14,15,6,7,8,9]),
            48: set([42,36,37,30,31,24,25,26,18,19,20,12,13,14,15,6,7,8,9]),
            39: set([34,28,29,23,24,17,18,19,12,13,14,6,7,8,9]),
            40: set([34,35,28,29,30,23,24,25,17,18,19,20,12,13,14,15,6,7,8,9]),
            41: set([35,36,29,30,31,23,24,25,26,17,18,19,20,12,13,14,15,6,7,8,9]),
            42: set([36,37,30,31,24,25,26,18,19,20,12,13,14,15,6,7,8,9]),
            34: set([28,29,23,24,17,18,19,12,13,14,6,7,8,9]),
            35: set([29,30,23,24,25,17,18,19,20,12,13,14,15,6,7,8,9]),
            36: set([30,31,24,25,26,18,19,20,12,13,14,15,6,7,8,9]),
            37: set([31,25,26,19,20,13,14,15,7,8,9]),
            28: set([23,17,18,12,13,6,7,8]),
            29: set([23,24,17,18,19,12,13,14,6,7,8,9]),
            30: set([24,25,18,19,20,12,13,14,15,6,7,8,9]),
            31: set([25,26,19,20,13,14,15,7,8,9]),
            23: set([17,18,12,13,6,7,8]),
            24: set([18,19,12,13,14,6,7,8,9]),
            25: set([19,20,13,14,15,7,8,9]),
            26: set([20,14,15,8,9]),
            17: set([12,6,7]),
            18: set([12,13,6,7,8]),
            19: set([13,14,7,8,9]),
            20: set([14,15,8,9]),
            12: set([6,7]),
            13: set([7,8]),
            14: set([8,9]),
            15: set([9]),
            6: set(),
            7: set(),
            8: set(),
            9: set()}

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
# other squares reachable from a particular square with a black man
BLACKMAP = {6: set([12,17,18,23,24,28,29,30,34,35,36,39,40,41,42,45,46,47,48]),
            7: set([12,13,17,18,19,23,24,25,28,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48]),
            8: set([13,14,18,19,20,23,24,25,26,28,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48]),
            9: set([14,15,19,20,24,25,26,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48]),
            12: set([17,18,23,24,28,29,30,34,35,36,39,40,41,42,45,46,47,48]),
            13: set([18,19,23,24,25,28,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48]),
            14: set([19,20,24,25,26,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48]),
            15: set([20,25,26,30,31,35,36,37,40,41,42,45,46,47,48]),
            17: set([23,28,29,34,35,39,40,41,45,46,47]),
            18: set([23,24,28,29,30,34,35,36,39,40,41,42,45,46,47,48]),
            19: set([24,25,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48]),
            20: set([25,26,30,31,35,36,37,40,41,42,45,46,47,48]),
            23: set([28,29,34,35,39,40,41,45,46,47]),
            24: set([29,30,34,35,36,39,40,41,42,45,46,47,48]),
            25: set([30,31,35,36,37,40,41,42,45,46,47,48]),
            26: set([31,36,37,41,42,46,47,48]),
            28: set([34,39,40,45,46]),
            29: set([34,35,39,40,41,45,46,47]),
            30: set([35,36,40,41,42,45,46,47,48]),
            31: set([36,37,41,42,46,47,48]),
            34: set([39,40,45,46]),
            35: set([40,41,45,46,47]),
            36: set([41,42,46,47,48]),
            37: set([42,47,48]),
            39: set([45]),
            40: set([45,46]),
            41: set([46,47]),
            42: set([47,48]),
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

CBMAP = {5:4, 6:3, 7:2, 8:1,
         10:8, 11:7, 12:6, 13:5,
         14:12, 15:11, 16:10, 17:9,
         19:16, 20:15, 21:14, 22:13,
         23:20, 24:19, 25:18, 26:17,
         28:24, 29:23, 30:22, 31:21,
         32:28, 33:27, 34:26, 35:25,
         37:32, 38:31, 39:30, 40:29}

def create_position_map():
    """ Maps compressed grid indices xi + yi * 8 to internal
        board indices """
    pos = {}
    pos[1] = 45;   pos[3]  = 46; pos[5] =  47; pos[7]  = 48
    pos[8] = 39;   pos[10] = 40; pos[12] = 41; pos[14] = 42
    pos[17] = 34;  pos[19] = 35; pos[21] = 36; pos[23] = 37
    pos[24] = 28;  pos[26] = 29; pos[28] = 30; pos[30] = 31
    pos[33] = 23;  pos[35] = 24; pos[37] = 25; pos[39] = 26
    pos[40] = 17;  pos[42] = 18; pos[44] = 19; pos[46] = 20
    pos[49] = 12;  pos[51] = 13; pos[53] = 14; pos[55] = 15
    pos[56] = 6;   pos[58] = 7;  pos[60] =  8; pos[62] = 9
    return pos

def create_key_map():
    """ Maps internal board indices to checkerboard label numbers """
    key = {}
    key[6]  = 4;  key[7]  = 3;  key[8]  = 2;  key[9]  = 1
    key[12] = 8;  key[13] = 7;  key[14] = 6;  key[15] = 5
    key[17] = 12; key[18] = 11; key[19] = 10; key[20] = 9
    key[23] = 16; key[24] = 15; key[25] = 14; key[26] = 13
    key[28] = 20; key[29] = 19; key[30] = 18; key[31] = 17
    key[34] = 24; key[35] = 23; key[36] = 22; key[37] = 21
    key[39] = 28; key[40] = 27; key[41] = 26; key[42] = 25
    key[45] = 32; key[46] = 31; key[47] = 30; key[48] = 29
    return key

def create_grid_map():
    """ Maps internal board indices to grid (row, col) coordinates """
    grd = {}
    grd[6]  = (7,0); grd[7]  = (7,2); grd[8]  = (7,4); grd[9]  = (7,6)
    grd[12] = (6,1); grd[13] = (6,3); grd[14] = (6,5); grd[15] = (6,7)
    grd[17] = (5,0); grd[18] = (5,2); grd[19] = (5,4); grd[20] = (5,6)
    grd[23] = (4,1); grd[24] = (4,3); grd[25] = (4,5); grd[26] = (4,7)
    grd[28] = (3,0); grd[29] = (3,2); grd[30] = (3,4); grd[31] = (3,6)
    grd[34] = (2,1); grd[35] = (2,3); grd[36] = (2,5); grd[37] = (2,7)
    grd[39] = (1,0); grd[40] = (1,2); grd[41] = (1,4); grd[42] = (1,6)
    grd[45] = (0,1); grd[46] = (0,3); grd[47] = (0,5); grd[48] = (0,7)
    return grd

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


def similarity(pattern, pieces):
    global grid
    p1 = [grid[i] for i in pattern]
    p2 = [grid[j] for j in pieces]
    return sum(min(math.hypot(x1-x2, y1-y2) for x1, y1 in p1) for x2, y2 in p2)

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

grid = create_grid_map()
keymap = create_key_map()
squaremap = flip_dict(keymap)
