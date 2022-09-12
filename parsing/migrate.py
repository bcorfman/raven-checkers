import os.path
from datetime import datetime
from io import StringIO
from parsing.PDN import PDNWriter


def _make_fen_sublist(tag, men, kings):
    output = ''
    if men or kings:
        output += tag
        if men:
            output += _write_list(men)
        if kings:
            output += _write_list(kings)
    return output


def _write_list(items):
    with StringIO() as s:
        print(items, file=s, end='', sep=',')
        return s.getvalue()


class RCF2PDN:
    def __init__(self):
        self.description = []
        self.num_players = None
        self.first_to_move = None
        self.flip_board = None
        self.black_men = set()
        self.black_kings = set()
        self.white_men = set()
        self.white_kings = set()
        self.moves = []
        self.annotations = []
        self.lineno = 0
        self.event_name = None

    @classmethod
    def with_string(cls, rcf):
        with StringIO() as pdn:
            RCF2PDN().translate(rcf, pdn)
            return pdn.getvalue()

    @classmethod
    def with_file(cls, rcf_filepath, pdn_filepath):
        event = os.path.splitext(os.path.basename(rcf_filepath))[0]
        with open(rcf_filepath) as rcf:
            with open(pdn_filepath, 'w') as pdn:
                RCF2PDN().translate(rcf, pdn, event)

    def translate(self, rcf_stream, pdn_stream, event_name=None):
        rcf_tags = {'<description>': self._read_description,
                    '<setup>': self._read_setup,
                    '<moves>': self._read_moves}

        self.event_name = event_name

        while True:
            line = rcf_stream.readline()
            self.lineno += 1
            if not line:
                break
            line = line.rstrip('\n')
            for tag in rcf_tags:
                if line.lstrip().startswith(tag):
                    rcf_tags[tag](rcf_stream)
                    break

        if self._validate_rcf():
            event = self.event_name
            site = "*"
            date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            rnd = "*"
            black = "Player1"
            white = "Player2"
            result = self._get_game_result()
            fen = self._get_game_fen()
            movetext = self._get_game_moves()
            PDNWriter.to_stream(pdn_stream, event, site, date, rnd, black, white, result, fen, movetext)

    def _get_game_fen(self):
        if (self.black_kings or self.white_kings or self.black_men != set(range(12)) or
                self.white_men != set(range(20, 33))):
            turn = 'B' if self.first_to_move == 'black_first' else 'W'
            fen = f'{turn}:'
            fen += _make_fen_sublist('W', self.white_men, self.white_kings)
            fen += _make_fen_sublist('B', self.black_men, self.black_kings)
        else:
            fen = ""
        return fen

    def _get_game_result(self):
        final_annotation = self.annotations[-1].lower()
        if "white wins" in final_annotation:
            result = "1-0"
        elif "black wins" in final_annotation:
            result = "0-1"
        elif "draw" in final_annotation:
            result = "1/2-1/2"
        else:
            result = "*"  # ongoing game
        return result

    def _get_game_moves(self):
        movetext = ""
        return movetext

    def _read_description(self, stream):
        line = stream.readline()
        self.lineno += 1
        if not line:
            raise IOError(f"Unexpected end of file at line {self.lineno}")
        line = line.strip()
        if line.beginswith('**') and line.endswith('**'):
            self.event_name = line.split('**')[1].strip()
        self.description.append(line)
        while True:
            prior_loc = stream.tell()
            line = stream.readline()
            self.lineno += 1
            if not line:
                raise IOError(f"Unexpected end of file at line {self.lineno}")
            line = line.strip()
            if line == "<setup>":
                stream.seek(prior_loc)
                self.lineno -= 1
                break
            self.description.append(line)

    def _read_setup(self, stream):
        setup_tags = {"white_first": self._read_turn,
                      "black_first": self._read_turn,
                      "0_player_game": self._read_num_players,
                      "1_player_game": self._read_num_players,
                      "2_player_game": self._read_num_players,
                      "flip_board": self._read_board_direction,
                      "black_men": self._read_black_men,
                      "black_kings": self._read_black_kings,
                      "white_men": self._read_white_men,
                      "white_kings": self._read_white_kings,
                      }
        while True:
            line = stream.readline()
            self.lineno += 1
            if not line:
                raise IOError(f"Unexpected end of file at line {self.lineno}")
            line = line.strip()
            for tag in setup_tags:
                if line.startswith(tag):
                    setup_tags[tag](line)
                    break
            if line.startswith("white_kings"):
                break

    def _read_moves(self, stream):
        while True:
            line = stream.readline()
            self.lineno += 1
            if not line:
                break
            move, annotation = line.strip().split(';')
            self.moves.append(move)
            if annotation[0:2] == '. ':
                annotation = annotation[2:]
            self.annotations.append(annotation)

    def _read_turn(self, line):
        self.first_to_move = line[0].capitalize()

    def _read_num_players(self, line):
        self.num_players = int(line[0])

    def _read_board_direction(self, line):
        direction = int(line.split()[1])
        self.flip_board = direction == 1

    def _read_black_men(self, line):
        self.black_men = [int(i) for i in line.split()[1:]]

    def _read_black_kings(self, line):
        self.black_kings = [int(i) for i in line.split()[1:]]

    def _read_white_men(self, line):
        self.white_men = [int(i) for i in line.split()[1:]]

    def _read_white_kings(self, line):
        self.white_kings = [int(i) for i in line.split()[1:]]

    def _validate_rcf(self):
        return False
