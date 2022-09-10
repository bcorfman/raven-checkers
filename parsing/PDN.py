import os
import textwrap
from io import StringIO
from typing import NamedTuple


def _read_value(line):
    return line.split('"')[1]


PDN = NamedTuple("PDN", [("event", str), ("site", str), ("date", str),
                         ("round", str), ("white", str), ("black", str),
                         ("result", str), ("fen", str)])


class PDNReader:
    def __init__(self, stream, source=""):
        self._stream = stream
        self._source = f"in {source}" if source else ""
        self._lineno = 0
        self.PDNs = []
        self._reset_pdn_vars()
        self._read_stream()

    @classmethod
    def from_string(cls, pdn_string):
        stream = StringIO(pdn_string)
        return cls(stream, "PDN string")

    @classmethod
    def from_file(cls, filepath):
        filename = os.path.basename(filepath)
        with open(filepath) as stream:
            return cls(stream, filename)

    def _reset_pdn_vars(self):
        self._event = None
        self._site = None
        self._date = None
        self._round = None
        self._black = None
        self._white = None
        self._result = None
        self._fen = None

    def _read_stream(self):
        parse_pdn = {"[Event": self._read_event,
                     "[Site": self._read_site,
                     "[Date": self._read_date,
                     "[Round": self._read_round,
                     "[White": self._read_white_player,
                     "[Black": self._read_black_player,
                     "[Result": self._read_result,
                     "1.": self._read_fen}
        self._lineno = 0
        while True:
            line = self._stream.readline()
            if not line:
                break
            self._lineno += 1
            line = line.rstrip('\n')
            for tag in parse_pdn:
                if line.lstrip().startswith(tag):
                    parse_pdn[tag](line)
                    break

    def _read_event(self, line):
        self._event = _read_value(line)

    def _read_site(self, line):
        self._site = _read_value(line)

    def _read_date(self, line):
        self._date = _read_value(line)

    def _read_round(self, line):
        self._round = _read_value(line)

    def _read_white_player(self, line):
        self._white = _read_value(line)

    def _read_black_player(self, line):
        self._black = _read_value(line)

    def _read_result(self, line):
        self._result = _read_value(line)

    def _read_fen(self, line):
        if not self._result:
            raise IOError("Didn't get a result value")
        self._fen = line.rstrip('\n')
        if self._result not in line:
            while True:
                line = self._stream.readline()
                if not line:
                    error = f"Unexpected EOF {self._source} on " + \
                            f"line {self._lineno}"
                    raise IOError(error)
                self._lineno += 1
                self._fen += line.rstrip('\n')
                if self._result in line:
                    break
        self.PDNs.append(PDN(self._event, self._site, self._date, self._round,
                         self._white, self._black, self._result, self._fen))
        self._reset_pdn_vars()


class PDNWriter:
    def __init__(self, stream, event, site, date, rnd, black, white, result, 
                 fen):
        self.stream = stream
        self._wrapper = textwrap.TextWrapper(width=79)
        self._write(event, site, date, rnd, black, white, result, fen)

    def _write(self, event, site, date, rnd, black, white, result, fen):
        self.stream.write(f'[Event] "{event}]"\n')
        self.stream.write(f'[Site] "{site}]"\n')
        self.stream.write(f'[Date] "{date}]"\n')
        self.stream.write(f'[Round] "{rnd}]"\n')
        self.stream.write(f'[Black] "{black}]"\n')
        self.stream.write(f'[White] "{white}]"\n')
        self.stream.write(f'[Result] "{result}]"\n')
        for line in self._wrap_lines(fen):
            self.stream.write(line + '\n')

    def _wrap_lines(self, lines):
        output = []
        for line in lines:
            if not line:
                output.append('')
            else:
                output.append(self._wrapper.fill(line))
        return output

    @classmethod
    def to_string(cls, event, site, date, rnd, black, white, result, fen):
        output = ""
        with StringIO(output) as stream:
            writer = cls(stream, event, site, date, rnd, black, white, result,
                         fen)
        return writer.stream

    @classmethod
    def to_file(cls, filepath, event, site, date, rnd, black, white, result,
                fen):
        with open(filepath) as stream:
            writer = cls(stream, event, site, date, rnd, black, white, result,
                         fen)
        return writer.stream