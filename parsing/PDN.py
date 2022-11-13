import charset_normalizer
import copy
import os
import textwrap
from io import StringIO
from pyparsing import Combine, Forward, Group, LineStart, LineEnd, Literal, OneOrMore, Optional, \
    QuotedString, Suppress, Word, WordEnd, WordStart, nums, one_of, rest_of_line, srange
from typing import NamedTuple
from base.move import Move
from game.checkers import Checkers
from util.globalconst import keymap, square_map, BLACK, WHITE, MAN, KING, HEADER, DESC, BODY


def is_game_terminator(item):
    return item in ["0-1", "1-0", "1/2-1/2", "*"]


def _is_move(delta):
    return delta in [3, 4, 5, -3, -4, -5]


def _removeLineFeed(s):
    return s[0].replace('\n', ' ')


Game = NamedTuple("Game", [("event", str), ("site", str), ("date", str),
                           ("round", str), ("black_player", str), ("white_player", str),
                           ("next_to_move", int), ("black_men", list), ("white_men", list),
                           ("black_kings", list), ("white_kings", list),
                           ("result", str), ("board_orientation", str),
                           ("description", str), ("moves", list)])

GameTitle = NamedTuple("GameTitle", [("index", int), ("name", str)])

_MoveStrength = one_of('! ?') | '(' + one_of('! ?') + ')'
_Identifier = Word(srange('[A-Z]'), srange('[A-Za-z0-9_]'))
_lbrace, _rbrace = map(Literal, "{}")
_Comment = Suppress('{') + ... + Suppress('}')
_Comment = _Comment.setParseAction(_removeLineFeed)

_Win = WordStart() + '1-0' + WordEnd()
_Draw = WordStart() + '1/2-1/2' + WordEnd()
_Loss = WordStart() + '0-1' + WordEnd()
_Asterisk = WordStart() + '*' + WordEnd()
_Result = _Asterisk | _Win | _Draw | _Loss
_Ellipses = '...'
_MoveNumber = WordStart() + Combine(Word(nums) + '.')("move_number")
_Square = Word(nums).set_parse_action(lambda n: [int(n[0])])
_MoveSeparator = '-'
_CaptureSeparator = 'x'
_NormalMove = Group(_Square + Suppress(_MoveSeparator) + _Square)
_CaptureMove = Group(_Square + OneOrMore(Suppress(_CaptureSeparator) + _Square))
_Move = _NormalMove | _CaptureMove
_LineComment = LineStart() + Group('% ' + rest_of_line()('comment'))
_Description = Combine((OneOrMore(Combine(LineStart() + Suppress('% ') + ... + LineEnd()))))('description')
_PDNTag = LineStart() + Suppress('[') + Group(_Identifier('key') + QuotedString('"')('value')) + Suppress(']') + \
          Suppress(LineEnd())
_GameHeader = OneOrMore(_PDNTag)
_SingleGameMove = Group(_MoveNumber('number') + _Move('first') + Suppress(Optional(_MoveStrength)) +
                        Optional(_Comment('comment1')) + Group(_Result))
_DoubleGameMove = Group(_MoveNumber('number') + _Move('first') + Suppress(Optional(_MoveStrength)) +
                        Optional(_Comment('comment1')) + _Move('second') + Suppress(Optional(_MoveStrength)) +
                        Optional(_Comment('comment2')))
_Variation = Forward()
_GameBody = OneOrMore(_SingleGameMove | _DoubleGameMove | _Variation | _LineComment)('body')
_Variation <<= Combine('(' + _GameBody + ')')
_Game = (_GameHeader('header') + Optional(_Description) + Optional(_GameBody)) | _GameBody


class PDNReader:
    def __init__(self, stream, source=""):
        self._stream = stream
        self._model = Checkers()
        self._source = f"in {source}" if source else ""
        self._stream_pos = 0
        self._lineno = 0
        self._games = []
        self._game_titles = []
        self._game_indexes = []
        self._game_ctr = 0
        self._description = ""
        self._reset_pdn_vars()

    @classmethod
    def from_string(cls, pdn_string):
        stream = StringIO(pdn_string)
        return cls(stream, "PDN string")

    @classmethod
    def from_file(cls, filepath):
        filename = os.path.basename(filepath)
        # sample a small chunk of the file to determine encoding
        chunk_size = min(os.path.getsize(filepath), 10000)
        with open(filepath, 'rb') as test:
            pdn_encoding = charset_normalizer.detect(test.read(chunk_size))['encoding']
            stream = open(filepath, encoding=pdn_encoding)
            return cls(stream, filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_t, exc_v, trace):
        self.close()

    def close(self):
        self._stream.close()

    def _reset_pdn_vars(self):
        self._event = None
        self._site = None
        self._date = None
        self._round = None
        self._event_name = None
        self._black_name = None
        self._white_name = None
        self._black_player = None
        self._white_player = None
        self._next_to_move = None
        self._black_men = None
        self._white_men = None
        self._black_kings = None
        self._white_kings = None
        self._result = None
        self._flip_board = None
        self._description = ""
        self._moves = []
        self._annotations = []

    def _read_event(self, value):
        self._event = value

    def _read_site(self, value):
        self._site = value

    def _read_date(self, value):
        self._date = value

    def _read_round(self, value):
        self._round = value

    def _read_white_player(self, value):
        self._white_player = value

    def _read_black_player(self, value):
        self._black_player = value

    def _read_black_type(self, value):
        self._black_type = value

    def _read_white_type(self, value):
        self._white_type = value

    def _read_game_type(self, value):
        self._game_type = value

    def _read_result(self, value):
        self._result = value

    def _read_board_orientation(self, value):
        if value == "white_on_top" or value == "black_on_top":
            self._flip_board = value == "white_on_top"
        else:
            raise SyntaxError(f"Unknown {value} used in board_orientation tag.")

    def _start_move_list(self, _):
        if self._black_player and self._white_player:
            title = f"{self._event}: {self._black_player} vs. {self._white_player}"
        else:
            title = f"{self._event}"
        self._game_titles.append(GameTitle(index=self._game_ctr, name=title))
        self._game_ctr += 1

    def _read_fen(self, value):
        turn, first_squares, second_squares = value.split(":")
        self._next_to_move = self._get_player_to_move(turn)
        player = first_squares[0].upper()
        if player == "W":
            self._white_men, self._white_kings = self._get_player_pieces(first_squares)
        elif player == "B":
            self._black_men, self._black_kings = self._get_player_pieces(first_squares)
        else:
            raise SyntaxError("Unknown player type {player} in first set of FEN squares")
        player = second_squares[0].upper()
        if player == "W":
            self._white_men, self._white_kings = self._get_player_pieces(second_squares)
        elif player == "B":
            self._black_men, self._black_kings = self._get_player_pieces(second_squares)
        else:
            raise SyntaxError("Unknown player type {player} in second set of FEN squares")

    def _add_game_index(self, value):
        self._event = value
        self._game_indexes.append(self._stream_pos)

    def _set_board_defaults_if_needed(self):
        if self._flip_board is None:
            self._flip_board = "white_on_top"
        if self._next_to_move is None:
            self._next_to_move = BLACK
        if self._black_men is None:
            self._black_men = list(range(1, 13))
            self._black_kings = []
        if self._white_men is None:
            self._white_men = list(range(21, 33))
            self._white_kings = []

    def get_game_list(self):
        self._game_ctr = 0
        self._stream.seek(0)
        parse_header = {"[Event": self._add_game_index,
                        "[White": self._read_white_player,
                        "[Black": self._read_black_player,
                        "1.": self._start_move_list,
                        }

        self._game_titles = []
        self._game_indexes = []
        while True:
            self._stream_pos = self._stream.tell()
            line = self._stream.readline()
            if line == "":
                self._game_indexes.append(self._stream.tell())
                break
            for key in parse_header:
                if line.startswith(key):
                    line = line.lstrip()
                    value = line.split('"')[1] if line.startswith("[") else line
                    parse_header[key](value)
                    break
        return self._game_titles

    def read_game(self, idx):
        # parse the game at the requested index
        parse_header = {"Event": self._read_event,
                        "Site": self._read_site,
                        "Date": self._read_date,
                        "White": self._read_white_player,
                        "Black": self._read_black_player,
                        "BlackType": self._read_black_type,
                        "WhiteType": self._read_white_type,
                        "GameType": self._read_game_type,
                        "Result": self._read_result,
                        "FEN": self._read_fen,
                        "BoardOrientation": self._read_board_orientation}

        self._reset_pdn_vars()
        if not self._game_indexes:
            self.get_game_list()
        self._stream.seek(self._game_indexes[idx])
        game_chunk = self._game_indexes[idx+1] - self._game_indexes[idx]
        pdn = _Game.search_string(self._stream.read(game_chunk))
        processed = 0
        for game in pdn:
            if game.header and not (processed & HEADER):
                for tag in game.header:
                    if parse_header.get(tag.key):
                        parse_header[tag.key](tag.value)
                processed += HEADER
            if game.description and not (processed & DESC):
                self._description = game.description.as_list().pop()
                processed += DESC
            if game.body and not (processed & BODY):
                self._set_board_defaults_if_needed()
                for item in game.body:
                    if len(item) > 1:
                        idx = 1
                        move_list = list(item[idx])
                        if item.comment1:
                            idx += 1
                            annotation = item[idx]
                        else:
                            annotation = ""
                        self._moves.append([move_list, annotation])
                        idx += 1
                        move_list = list(item[idx])
                        if item.comment2:
                            idx += 1
                            annotation = item[idx]
                        else:
                            annotation = ""
                        self._moves.append([move_list, annotation])
                    else:
                        raise RuntimeError(f"Cannot interpret item {item} in game.body")
            # if no game description was in the file, add a basic one so the user has something to guide them.
        if not self._description:
            if self._black_player and self._white_player:
                self._description += f"{self._event}: {self._black_player} vs. {self._white_player}"
            else:
                self._description += f"{self._event}"
            self._description += "\n\nUse the arrow keys in the toolbar above to progress through the game moves."
        board_moves = self._PDN_to_board_ready(self._next_to_move, self._black_men, self._black_kings,
                                               self._white_men, self._white_kings, self._moves)
        return Game(self._event, self._site, self._date, self._round, self._black_player,
                    self._white_player, self._next_to_move, self._black_men, self._white_men,
                    self._black_kings, self._white_kings, self._result, self._flip_board,
                    self._description, board_moves)

    def _get_player_to_move(self, turn):
        turn = turn.upper()
        if turn == "B":
            result = BLACK
        elif turn == "W":
            result = WHITE
        else:
            raise SyntaxError("Unknown turn type {turn} in FEN")
        return result

    def _get_player_pieces(self, fen_line: str):
        fen_line = fen_line[1:]
        sq_text = fen_line.split(",")
        men = []
        kings = []
        for sq in sq_text:
            if sq.startswith('K'):
                kings.append(int(sq[1:]))
            else:
                men.append(int(sq))
        return men, kings

    def _try_move(self, squares: list, annotation: str, state_copy: Checkers):
        board_squares = [square_map[sq] for sq in squares]
        legal_moves = self._model.legal_moves(state_copy)
        # try to match squares with available moves on checkerboard
        sq_len = len(squares)
        for move in legal_moves:
            if sq_len == len(move.affected_squares) and \
                    all(sq == move.affected_squares[i][0] for i, sq in enumerate(board_squares)):
                move.annotation = annotation
                self._model.make_move(move, state_copy, False, False)
                return move

    def _try_jump(self, squares: list, annotation: str, state_copy: Checkers):
        board_squares = [square_map[sq] for sq in squares]
        if self._model.captures_available(state_copy):
            legal_moves = self._model.legal_moves(state_copy)
            for move in legal_moves:
                if all(sq == move.affected_squares[i*2][0] for i, sq in enumerate(board_squares)):
                    move.annotation = annotation
                    self._model.make_move(move, state_copy, False, False)
                    return move

    def _PDN_to_board_ready(self, next_to_move: int, black_men: list[int], black_kings: list[int],
                            white_men: list[int], white_kings: list[int], pdn_moves: list):
        """ Each move in the file lists the beginning and ending square, along
        with an optional annotation string (in Creole fmt) that describes it.
        I make sure that each move works on a copy of the model before I commit
        to using it inside the code. """
        state_copy = copy.deepcopy(self._model.curr_state)
        state_copy.clear()
        state_copy.to_move = next_to_move
        for i in black_men:
            state_copy.squares[square_map[i]] = BLACK | MAN
        for i in black_kings:
            state_copy.squares[square_map[i]] = BLACK | KING
        for i in white_men:
            state_copy.squares[square_map[i]] = WHITE | MAN
        for i in white_kings:
            state_copy.squares[square_map[i]] = WHITE | KING

        # analyze squares to perform a move or jump.
        idx = 0
        moves_len = len(pdn_moves)
        translated_moves = []
        while idx < moves_len:
            squares, annotation = pdn_moves[idx]
            if is_game_terminator(squares[0]):
                break
            delta = squares[0] - squares[1]
            if _is_move(delta):
                move = self._try_move(squares, annotation, state_copy)
                if move:
                    translated_moves.append(move)
                else:
                    raise RuntimeError(f"Illegal move {squares} found")
            else:
                jump = self._try_jump(squares, annotation, state_copy)
                if jump:
                    translated_moves.append(jump)
                else:
                    raise RuntimeError(f"Illegal jump {squares} found")
            idx += 1
        translated_moves.reverse()
        return translated_moves


def translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings):
    if next_to_move == 'black':
        fen = "B:"
    elif next_to_move == 'white':
        fen = "W:"
    else:
        raise RuntimeError(f"Unknown player {next_to_move} in next_to_move variable")
    if white_men or white_kings:
        fen += "W"
        if white_men:
            fen += ",".join([str(n) for n in white_men])
        if white_kings:
            if white_men:
                fen += ','
            fen += ",".join([f"K{n}" for n in white_kings])
        fen += ":"
    if black_men or black_kings:
        fen += "B"
        if black_men:
            fen += ",".join([str(n) for n in black_men])
        if black_kings:
            if black_men:
                fen += ','
            fen += ",".join([f"K{n}" for n in black_kings])
    return fen


def _translate_to_movetext(moves: list, annotations: list):
    def _translate_to_text(move):
        sq1, sq2 = move[0], move[1]
        sep = '-' if abs(sq1 - sq2) <= 5 else 'x'
        return sep.join([str(n) for n in move])

    moves.reverse()
    annotations.reverse()
    movetext = ""
    movenum = 0
    while True:
        if len(moves) == 0:
            break
        item = moves.pop()
        anno = annotations.pop()

        item.reverse()
        anno.reverse()
        movenum += 1
        # use a backquote as a temporary delimiter so TextWrapper will treat each numbered move
        # as a single item for wrapping. After the wrapping is done, the pipe characters
        # will be replaced with spaces.
        move1 = item.pop()
        if is_game_terminator(move1):
            movetext += move1
            break
        movetext += f"{movenum}.`"
        comment1 = anno.pop()
        if comment1 and comment1[0] in ['!', '?']:
            tokens = comment1.split(maxsplit=1)
            strength1 = tokens[0]
            comment1 = tokens[1] if len(tokens) > 1 else ""
        else:
            strength1 = ""
        movetext += f"{_translate_to_text(move1)}{strength1}"
        if comment1:
            movetext += " {" + f"{comment1}" + "} "
        else:
            movetext += "`"
        if item:
            move2 = item.pop()
            if is_game_terminator(move2):
                movetext += move2
                break
            comment2 = anno.pop()
            if comment2 and comment2[0] in ['!', '?']:
                tokens = comment2.split(maxsplit=1)
                strength2 = tokens[0]
                comment2 = tokens[1] if len(tokens) > 1 else ""
            else:
                strength2 = ""
            movetext += f"{_translate_to_text(move2)}{strength2}"
            if comment2:
                movetext += " {" + f"{comment2}" + "}"
        movetext += " "
    return movetext


class PDNWriter:
    def __init__(self, stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                 black_kings, white_kings, result, board_orientation, description, moves, annotations):
        self.stream = stream
        self._wrapper = textwrap.TextWrapper(width=119)  # minus one character for line feed
        self._write(event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men, black_kings,
                    white_kings, result, board_orientation, description, moves, annotations)

    def _write(self, event: str, site: str, date: str, rnd: str, black_player: str, white_player: str,
               next_to_move: str, black_men: list, white_men: list, black_kings: list, white_kings: list, result: str,
               board_orientation: str, description: str, moves: list, annotations: list):
        self.stream.write(f'[Event "{event}"]\n')
        self.stream.write(f'[Date "{date}"]\n')
        if rnd:
            self.stream.write(f'[Round "{rnd}"]\n')
        self.stream.write(f'[Black "{black_player}"]\n')
        self.stream.write(f'[White "{white_player}"]\n')
        self.stream.write(f'[Site "{site}"]\n')
        self.stream.write(f'[Result "{result}"]\n')
        if (next_to_move == "white" or black_kings or white_kings or frozenset(black_men) != frozenset(range(1, 13)) or
                frozenset(white_men) != frozenset(range(21, 33))):
            self.stream.write('[SetUp "1"]\n')
            fen = translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings)
            self.stream.write(f'[FEN "{fen}"]\n')
        self.stream.write(f'[BoardOrientation "{board_orientation}"]\n')
        if description:
            self.stream.write(description + "\n")
        if annotations is None:
            annotations = [["", ""] for _ in moves]
        for line in self._wrapper.wrap(_translate_to_movetext(moves, annotations)):
            line = line.replace("`", " ")  # NOTE: see _translate_to_movetext function
            self.stream.write(line + '\n')

    @classmethod
    def to_string(cls, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                  black_kings, white_kings, result, board_orientation, moves, annotations=None, description=""):
        with StringIO() as stream:
            cls(stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                black_kings, white_kings, result, board_orientation, description, moves, annotations)
            return stream.getvalue()

    @classmethod
    def to_file(cls, filepath, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                black_kings, white_kings, result, board_orientation, moves, annotations=None, description=""):
        with open(filepath, 'w') as stream:
            cls(stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                black_kings, white_kings, result, board_orientation, description, moves, annotations)

    @classmethod
    def to_stream(cls, stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                  black_kings, white_kings, result, board_orientation, moves, annotations=None, description=""):
        cls(stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men, black_kings,
            white_kings, result, board_orientation, description, moves, annotations)


def board_to_PDN_ready(board_moves: list[Move]):
    pdn_moves = []
    annotations = []
    for idx, move in enumerate(board_moves):
        num_squares = len(move.affected_squares)
        if num_squares == 2:  # move
            sq1 = keymap[move.affected_squares[0][0]]
            sq2 = keymap[move.affected_squares[1][0]]
            pdn_moves.append([sq1, sq2])
        elif num_squares >= 3:  # jump
            jump = []
            for i in range(0, num_squares-2, 2):
                sq = keymap[move.affected_squares[i][0]]
                jump.append(sq)
            sq = keymap[move.affected_squares[-1][0]]
            jump.append(sq)
            pdn_moves.append(jump)
        else:
            raise RuntimeError("unknown number of affected_squares")
        if move.annotation:
            annotations.append(move.annotation)
        else:
            annotations.append("")
    pdn_moves.reverse()
    annotations.reverse()
    return pdn_moves, annotations
