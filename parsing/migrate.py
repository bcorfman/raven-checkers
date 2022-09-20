import os.path
from pathlib import Path
from datetime import datetime, timezone
from io import StringIO
from parsing.PDN import PDN, PDNWriter


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
        self.file_mod_time = None
        self._pdn = None

    @classmethod
    def with_string(cls, rcf):
        with StringIO() as pdn:
            RCF2PDN().translate(rcf, pdn)
            return pdn.getvalue()

    @classmethod
    def with_file(cls, rcf_filepath, pdn_filepath):
        event = os.path.splitext(os.path.basename(rcf_filepath))[0]
        file_mtime = Path(rcf_filepath).stat().st_mtime
        file_mod_time = datetime.fromtimestamp(file_mtime, tz=timezone.utc).strftime(r'%m/%d/%Y')
        with open(rcf_filepath) as rcf:
            with open(pdn_filepath, 'w') as pdn:
                RCF2PDN().translate(rcf, pdn, event, file_mod_time)

    def translate(self, rcf_stream, pdn_stream, event_name=None, file_mod_time=None):
        self.event_name = event_name
        self.file_mod_time = file_mod_time
        self._read_input(rcf_stream)
        if self._validate_input():
            self._transform_input()
            self._write_output(pdn_stream)

    def _read_input(self, rcf_stream):
        rcf_tags = {'<description>': self._read_description,
                    '<setup>': self._read_setup,
                    '<moves>': self._read_moves}

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

    def _transform_input(self):
        event = self.event_name
        site = "*"
        date = self.file_mod_time or datetime.now().strftime("%d/%m/%Y")
        rnd = "*"
        black = "Player1"
        white = "Player2"
        result = self._get_game_result()
        fen = self._get_game_fen()
        movetext = self._get_game_moves()
        description = ""
        for line in self.description:
            description += line
        self._pdn = PDN(event, site, date, rnd, black, white, result, fen, description, movetext)

    def _write_output(self, pdn_stream):
        pdn = self._pdn
        PDNWriter.to_stream(pdn_stream, pdn.event, pdn.site, pdn.date, pdn.round, pdn.black, pdn.white, pdn.result,
                            pdn.fen, pdn.description, pdn.movetext)

    def _get_game_fen(self):
        if (self.black_kings or self.white_kings or frozenset(self.black_men) != frozenset(range(1, 13)) or
                frozenset(self.white_men) != frozenset(range(21, 33))):
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
        if self.moves:
            for i, move in enumerate(self.moves):
                start, dest = move.split("-")
                strength = self._get_move_strength(i)
                if i == 0:
                    movetext += f"{i+1}."
                elif i % 2 == 0:
                    movetext += f"  {i+1}."
                if abs(int(start)-int(dest)) <= 5:
                    movetext += f" {start}-{dest}{strength}"  # regular move
                else:
                    movetext += f" {start}x{dest}{strength}"  # jump
            movetext += " *"  # end of moves marked with asterisk
        return movetext

    def _get_move_strength(self, idx):
        if self.annotations[idx] and self.annotations[idx][0] in ['?', '!']:
            move_strength = self.annotations[idx][0]
        else:
            move_strength = ""
        return move_strength

    def _read_event_name(self, line):
        tokens = line.split('**')
        if len(tokens) == 3:
            self.event_name = tokens[1].strip()

    def _read_description(self, stream):
        line = stream.readline()
        self.lineno += 1
        if not line:
            raise IOError(f"Unexpected end of file at line {self.lineno}")
        self._read_event_name(line)
        self.description.append(line)
        while True:
            prior_loc = stream.tell()
            line = stream.readline()
            self.lineno += 1
            if not line:
                raise IOError(f"Unexpected end of file at line {self.lineno}")
            elif line.startswith("<setup>"):
                stream.seek(prior_loc)
                self.lineno -= 1
                break
            elif line == '\n':
                continue
            else:
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
            try:
                move, annotation = line.strip().split(';', 1)
            except ValueError:
                raise IOError(f"Missing newline on line {self.lineno}")
            if annotation[0:2] == '. ':
                annotation = annotation[2:]
            self.moves.append(move)
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

    def _validate_input(self):
        return (self.num_players in range(3) and self.first_to_move in ['B', 'W'] and
                self.flip_board in range(2) and self.moves and
                (self.black_men or self.black_kings or self.white_men or self.white_kings))
