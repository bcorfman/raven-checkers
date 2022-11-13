import os.path
from datetime import datetime, timezone
from io import StringIO
from parsing.PDN import Game, PDNWriter
from pathlib import Path


def _get_game_result(_anno):
    final_annotation = _anno.lower()
    if "white wins" in final_annotation:
        game_result = "1-0"
    elif "black wins" in final_annotation:
        game_result = "0-1"
    elif "draw" in final_annotation:
        game_result = "1/2-1/2"
    else:
        game_result = "*"  # ongoing game
    return game_result


def build_move_annotation_pairs(move_list, anno_list):
    # populate real moves list with move pairs
    move_collection = []
    anno_collection = []
    move_pair = []
    anno_pair = []
    i = 0
    moves = list(reversed(move_list))
    annotations = list(reversed(anno_list))
    result = None
    while moves:
        move = moves.pop()
        anno = annotations.pop()
        result = _get_game_result(anno)
        move_pair.append(move)
        anno_pair.append(anno)
        i += 1
        if i % 2 == 0:
            move_collection.append(move_pair[:])
            anno_collection.append(anno_pair[:])
            move_pair = []
            anno_pair = []
    if result:
        move_pair.append(result)
        anno_pair.append("")
    if move_pair:
        move_collection.append(move_pair[:])
        anno_collection.append(anno_pair[:])
    return move_collection, anno_collection


class RCF2PDN:
    def __init__(self):
        self.description = []
        self.num_players = None
        self.next_to_move = None
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
        self._game = None

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
        else:
            raise RuntimeError("RCF input not valid")

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
        black_player = "Player1"
        white_player = "Player2"
        result = _get_game_result(self.moves[-1][-1])
        orientation = "black_on_top" if self.flip_board == 1 else "white_on_top"
        description = ""
        for line in self.description:
            description += f"% {line}"
        self._game = Game(event, site, date, rnd, black_player, white_player, self.next_to_move, list(self.black_men),
                          list(self.white_men), list(self.black_kings), list(self.white_kings), result,
                          orientation, description, self.moves)

    def _write_output(self, pdn_stream):
        game = self._game
        PDNWriter.to_stream(pdn_stream, game.event, game.site, game.date, game.round, game.black_player,
                            game.white_player, game.next_to_move, game.black_men, game.white_men, game.black_kings,
                            game.white_kings, game.result, game.board_orientation, game.moves, self.annotations,
                            game.description)

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
        moves = []
        annotations = []
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
            move_list = [int(sq) for sq in move.split('-')]
            moves.append(move_list)
            annotations.append(annotation)
        self.moves, self.annotations = build_move_annotation_pairs(moves, annotations)

    def _read_turn(self, line):
        self.next_to_move = line.split("_")[0].lower()

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
        return (self.num_players in range(3) and self.next_to_move in ["black", "white"] and
                self.flip_board in range(2) and self.moves and
                (self.black_men or self.black_kings or self.white_men or self.white_kings))
