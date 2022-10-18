import charset_normalizer
import os
import textwrap
from io import StringIO
from pyparsing import Combine, Forward, Group, LineStart, LineEnd, Literal, OneOrMore, Optional, \
    QuotedString, Suppress, Word, WordEnd, WordStart, nums, one_of, rest_of_line, srange
from typing import NamedTuple


def _removeLineFeed(s):
    return s[0].replace('\n', ' ')


def _join(result):
    return ''.join(result)


Game = NamedTuple("Game", [("event", str), ("site", str), ("date", str),
                           ("round", str), ("black_player", str), ("white_player", str),
                           ("next_to_move", str), ("black_men", list), ("white_men", list),
                           ("black_kings", list), ("white_kings", list),
                           ("result", str), ("board_orientation", int),
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
_PDNTag = LineStart() + Suppress('[') + Group(_Identifier('key') + QuotedString('"')('value')) + Suppress(']') + \
          Suppress(LineEnd())
_GameHeader = OneOrMore(_PDNTag)
_SingleGameMove = Group(_MoveNumber('number') + _Move('first') + Optional(_Comment('comment1')) + Group(_Result))
_DoubleGameMove = Group(_MoveNumber('number') + _Move('first') + Optional(_Comment('comment1')) +
                        _Move('second') + Optional(_Comment('comment2')))
_Variation = Forward()
_GameBody = OneOrMore(_SingleGameMove | _DoubleGameMove | _Variation | _LineComment)('body')
_Variation <<= Combine('(' + _GameBody + ')')
_Game = (_GameHeader('header') + Optional(_GameBody)) | _GameBody
# _PDNStream = _Game + Suppress(ZeroOrMore(_Result + _Game)) + Suppress(_Result[0, 1])


class PDNReader:
    def __init__(self, stream, source=""):
        self._stream = stream
        self._source = f"in {source}" if source else ""
        self._lineno = 0
        self._games = []
        self._namelist = []
        self._reset_pdn_vars()

    @classmethod
    def from_string(cls, pdn_string):
        stream = StringIO(pdn_string)
        return cls(stream, "PDN string")

    @classmethod
    def from_file(cls, filepath):
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as test:
            pdn_encoding = charset_normalizer.detect(test.read())['encoding']
            with open(filepath, encoding=pdn_encoding) as stream:
                return cls(stream, filename)

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
        self._game_idx = 0
        self._game_titles = []

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
        if value == "white_on_top":
            self._flip_board = 0
        elif value == "black_on_top":
            self._flip_board = 1
        else:
            raise SyntaxError(f"Unknown {value} used in board_orientation tag.")

    def _start_move_list(self, _):
        if self._black_player and self._white_player:
            title = f"{self._event}: {self._black_player} vs. {self._white_player}"
        else:
            title = f"{self._event}"  
        self._game_titles.append(GameTitle(index=self._game_idx, name=title))
        self._game_idx += 1

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

    def get_game_list(self):
        parse_header = {"[Event": self._read_event,
                        "[White": self._read_white_player,
                        "[Black": self._read_black_player,
                        "1.": self._start_move_list,
                        }

        self._game_titles = []
        while True:
            line = self._stream.readline()
            if line == "":
                break
            for key in parse_header:
                if line.lstrip().startswith(key):
                    parse_header[key](line)
                    break
        return self._game_titles

    def read_game(self, idx):
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
        pdn = _Game.search_string(self._stream.read())
        for game in pdn:
            if game.header:
                for tag in game.header:
                    if parse_header.get(tag.key):
                        parse_header[tag.key](tag.value)
            if game.comment:
                self._description += game.comment
            if game.body:
                for item in game.body:
                    if len(item) > 1:
                        idx = 1
                        moves = [list(item[idx])]
                        annotations = []
                        if item.comment1:
                            idx += 1
                            annotations.append(list(item[idx]))
                        else:
                            annotations.append("")
                        idx += 1
                        moves.append(list(item[idx]))
                        if item.comment2:
                            idx += 1
                            annotations.append(item[idx])
                        else:
                            annotations.append("")
                        self._moves.append(moves)

                self._games.append(Game(self._event, self._site, self._date, self._round, self._black_player,
                                        self._white_player, self._next_to_move, self._black_men, self._white_men,
                                        self._black_kings, self._white_kings, self._result, self._flip_board,
                                        self._description, self._moves))
                self._reset_pdn_vars()

    def _get_player_to_move(self, turn):
        turn = turn.upper()
        if turn == "B":
            result = "black"
        elif turn == "W":
            result = "white"
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


def _translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings):
    if next_to_move.lower() == "black":
        fen = "B:"
    elif next_to_move.lower() == "white":
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
            if white_men:
                fen += ','
            fen += ",".join([f"K{n}" for n in black_kings])
    return fen


def _translate_to_movetext(moves):
    def _translate_to_text(move):
        sq1, sq2 = move[0], move[1]
        sep = '-' if abs(sq1 - sq2) <= 5 else 'x'
        return sep.join([str(n) for n in move])

    moves.reverse()
    movetext = ""
    movenum = 0
    while True:
        if len(moves) == 0:
            break
        item = moves.pop()
        if len(item) == 1:
            movetext += item.pop()
        else:
            item.reverse()
            movenum += 1
            # use a pipe as a temporary delimiter so TextWrapper will treat each numbered move
            # as a single item for wrapping. After the wrapping is done, the pipe characters
            # will be replaced with spaces.  
            # TODO: handle annotations also. 
            movetext += f"{movenum}.|"
            black_move = item.pop()
            movetext += f"{_translate_to_text(black_move)}"
            if item:
                white_move = item.pop()
                movetext += f"|{_translate_to_text(white_move)}"
            if moves:
                movetext += " "
    return movetext


class PDNWriter:
    def __init__(self, stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                 black_kings, white_kings, result, board_orientation, description, moves):
        self.stream = stream
        self._wrapper = textwrap.TextWrapper(width=79)
        self._write(event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men, black_kings,
                    white_kings, result, board_orientation, description, moves)

    def _write(self, event: str, site: str, date: str, rnd: str, black_player: str, white_player: str,
               next_to_move: str, black_men: list, white_men: list, black_kings: list, white_kings: list, result: str,
               board_orientation: str, description: str, moves: list):
        self.stream.write(f'[Event "{event}"]\n')
        self.stream.write(f'[Date "{date}"]\n')
        if rnd:
            self.stream.write(f'[Round "{rnd}"]\n')
        self.stream.write(f'[Black "{black_player}"]\n')
        self.stream.write(f'[White "{white_player}"]\n')
        self.stream.write(f'[Site "{site}"]\n')
        self.stream.write(f'[Result "{result}"]\n')
        if (black_kings or white_kings or frozenset(black_men) != frozenset(range(1, 13)) or
                frozenset(white_men) != frozenset(range(21, 33))):
            self.stream.write('[SetUp "1"]')
            self.stream.write(f'[FEN "{result}"]\n')
            for line in self._wrapper.wrap(_translate_to_fen(next_to_move, black_men, white_men, black_kings,
                                                             white_kings)):
                self.stream.write(line + '\n')
        self.stream.write(f'[BoardOrientation "{board_orientation}"]\n')
        if description:
            for line in description:
                self.stream.write(line)
        for line in self._wrapper.wrap(_translate_to_movetext(moves)):
            line = line.replace("|", " ")  # NOTE: see _translate_to_movetext function
            self.stream.write(line + '\n')

    @classmethod
    def to_string(cls, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                  black_kings, white_kings, result, board_orientation, moves, description=""):
        with StringIO() as stream:
            cls(stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                black_kings, white_kings, result, board_orientation, description, moves)
            return stream.getvalue()

    @classmethod
    def to_file(cls, filepath, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                black_kings, white_kings, result, board_orientation, moves, description=""):
        with open(filepath, 'w') as stream:
            cls(stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                black_kings, white_kings, result, board_orientation, description, moves)

    @classmethod
    def to_stream(cls, stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men,
                  black_kings, white_kings, result, board_orientation, description, moves):
        cls(stream, event, site, date, rnd, black_player, white_player, next_to_move, black_men, white_men, black_kings,
            white_kings, result, board_orientation, description, moves)
