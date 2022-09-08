import os


def _read_value(line):
    return line.split('"')[1]


class PDNReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.fileiter = None
        self.event = ""
        self.site = ""
        self.date = ""
        self.round = ""
        self.white_player = ""
        self.black_player = ""
        self.result = ""
        self.fen = ""
        self.read_pdn_file(filepath)

    def read_pdn_file(self, filepath):
        parse_pdn = {"[Event": self.read_event,
                     "[Site": self.read_site,
                     "[Date": self.read_date,
                     "[Round": self.read_round,
                     "[White": self.read_white_player,
                     "[Black": self.read_black_player,
                     "[Result": self.read_result,
                     "1.": self.read_fen}

        with open(filepath) as self.fileiter:
            while True:
                line = self.fileiter.readline()
                if not line:
                    raise IOError(f"Unexpected EOF in {os.path.basename(self.filepath)}")
                for tag in parse_pdn:
                    if line.stripleft().beginswith(tag):
                        parse_pdn[tag](line)

    def read_event(self, line):
        self.event = _read_value(line)

    def read_site(self, line):
        self.site = _read_value(line)

    def read_date(self, line):
        self.date = _read_value(line)

    def read_round(self, line):
        self.round = _read_value(line)

    def read_white_player(self, line):
        self.white_player = _read_value(line)

    def read_black_player(self, line):
        self.black_player = _read_value(line)

    def read_result(self, line):
        self.result = _read_value(line)

    def read_fen(self, line):
        if not self.result:
            raise IOError("Didn't get a result value")
        self.fen = line
        while True:
            line = self.fileiter.readline()
            if not line:
                raise IOError(f"Unexpected EOF in {os.path.basename(self.filepath)}")
            self.fen += line
            if self.result in line:
                break
