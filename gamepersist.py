from globalconst import BLACK, WHITE

class SavedGame(object):
    def __init__(self):
        self.intro = ""
        self.to_move = None
        self.black_men = []
        self.black_kings = []
        self.white_men = []
        self.white_kings = []
        self.moves = []

    def read(self, filename):
        f = open(filename, 'r')
        lines = f.readlines()
        linelen = len(lines)
        f.close()

        i = -1
        while True:
            i += 1
            if i >= linelen:
                break

            if '<intro>' in lines[i]:
                i += 1
                while i < linelen and '<setup>' not in lines[i]:
                    self.intro += lines[i].strip() + " "
                    i += 1
            if '<setup>' in lines[i]:
                self._parse_setup(lines, i, linelen)
            if '<moves>' in lines[i]:
                self._parse_moves(lines, i, linelen)
                self._translate_moves()
                return self
        return None

    def _parse_items(self, line, lst):
        men = line.split()[1:]
        lst.extend(map(int, men))

    def _parse_setup(self, lines, idx, linelen):
        idx += 1
        while idx < linelen and '<moves>' not in lines[idx]:
            line = lines[idx].strip()
            if line == 'WHITE_FIRST':
                self.to_move = WHITE
            elif line == 'BLACK_FIRST':
                self.to_move = BLACK
            elif line.startswith('BLACK_MEN'):
                self._parse_items(line, self.black_men)
            elif line.startswith('WHITE_MEN'):
                self._parse_items(line, self.white_men)
            elif line.startswith('BLACK_KINGS'):
                self._parse_items(line, self.black_kings)
            elif line.startswith('WHITE_KINGS'):
                self._parse_items(line, self.white_kings)
            idx += 1

    def _parse_moves(self, lines, idx, linelen):
        # get rid of any semicolons in the lines to aid in parsing
        mlines = [lines[x].strip().replace(';',' ')
                  for x in range(idx+1, linelen)]
        # join all lines together
        m = ' '.join(mlines)
        # tokenize all items on the lines
        lst = m.split()
        lstlen = len(lst)
        j = -1
        while True:
            j += 1
            if j >= lstlen:
                break

            # any sidenotes about the various moves are indicated
            # in parentheses. These are searched for specifically and
            # joined back together into a single string
            if lst[j].startswith('('):
                for k in range(j+1, lstlen):
                    if lst[k].endswith(')'):
                        self.moves.append(' '.join(lst[j:k+1]))
                        j = k
                        break
                else:
                    raise IndexError("Matching close paren not found")
            else:
                # append regular moves w/o change
                self.moves.append(lst[j])

    def _translate_moves(self, moves):
        pass
