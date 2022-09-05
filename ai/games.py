"""Games, or Adversarial Search. (Chapters 6)

"""

from ai.utils import infinity, argmax, argmax_random_tie, num_or_str, Dict, update
from ai.utils import if_, Struct, abstract
import random

# Minimax Search


def minimax_decision(state, game):
    """Given a st in a game, calculate the best move by searching
    forward all the way to the terminal states. [Fig. 6.4]"""

    player = game.to_move(state)

    def max_value(st):
        if game.terminal_test(st):
            return game.utility(st, player)
        v = -infinity
        for (_, s) in game.successors(st):
            v = max(v, min_value(s))
        return v

    def min_value(st):
        if game.terminal_test(st):
            return game.utility(st, player)
        v = infinity
        for (_, s) in game.successors(st):
            v = min(v, max_value(s))
        return v

    # Body of minimax_decision starts here:
    action, state = argmax(game.successors(state),
                           lambda a_s: min_value(a_s[1]))
    return action


def alphabeta_full_search(state, game):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Fig. 6.7], this version searches all the way to the leaves."""

    player = game.to_move(state)

    def max_value(st, alpha, beta):
        if game.terminal_test(st):
            return game.utility(st, player)
        v = -infinity
        for (a, s) in game.successors(st):
            v = max(v, min_value(s, alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(st, alpha, beta):
        if game.terminal_test(st):
            return game.utility(st, player)
        v = infinity
        for (a, s) in game.successors(st):
            v = min(v, max_value(s, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_search starts here:
    action, state = argmax(game.successors(state),
                           lambda a_s: min_value(a_s[1], -infinity, infinity))
    return action


def alphabeta_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    player = game.to_move(state)

    def max_value(st, alpha, beta, depth):
        if cutoff_test(st, depth):
            return eval_fn(st)
        v = -infinity
        successor = game.successors(st)
        for (a, s) in successor:
            v = max(v, min_value(s, alpha, beta, depth+1))
            if v >= beta:
                successor.close()
                return v
            alpha = max(alpha, v)
        return v

    def min_value(st, alpha, beta, depth):
        if cutoff_test(st, depth):
            return eval_fn(st)
        v = infinity
        successor = game.successors(st)
        for (a, s) in successor:
            v = min(v, max_value(s, alpha, beta, depth+1))
            if v <= alpha:
                successor.close()
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_search starts here:
    # The default test cuts off at depth d or at a terminal st
    cutoff_test = (cutoff_test or
                   (lambda st, depth: depth > d or game.terminal_test(st)))
    eval_fn = eval_fn or (lambda st: game.utility(player, st))
    action, state = argmax_random_tie(game.successors(state),
                                      lambda a_s: min_value(a_s[1], -infinity, infinity, 0))
    return action


# Players for Games
def query_player(game, state):
    """Make a move by querying standard input."""
    game.display(state)
    return num_or_str(input('Your move? '))


def random_player(game, state):
    """A player that chooses a legal move at random."""
    return random.choice(game.legal_moves())


def alphabeta_player(game, state):
    return alphabeta_search(state, game)


def play_game(game, *players):
    """Play an n-person, move-alternating game."""
    print(game.curr_state)
    while True:
        for player in players:
            if game.curr_state.to_move == player.color:
                move = player.select_move(game)
                print(game.make_move(move))
                if game.terminal_test():
                    return game.utility(player.color)


# Some Sample Games
class Game:
    """A game is similar to a problem, but it has a utility for each
    st and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement
    legal_moves, make_move, utility, and terminal_test. You may
    override display and successors or you can inherit their default
    methods. You will also need to set the .initial attribute to the
    initial st; this can be done in the constructor."""

    def __init__(self):
        pass

    def legal_moves(self, state):
        """Return a list of the allowable moves at this point."""
        abstract()

    def make_move(self, move, state):
        """Return the st that results from making a move from a st."""
        abstract()

    def utility(self, state, player):
        """"Return the value of this final st to player."""
        abstract()

    def terminal_test(self, state):
        """Return True if this is a final st for the game."""
        return not self.legal_moves(state)

    def to_move(self, state):
        """Return the player whose move it is in this st."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the st."""
        print(state)

    def successors(self, state):
        """Return a list of legal (move, st) pairs."""
        return [(move, self.make_move(move, state))
                for move in self.legal_moves(state)]

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class Fig62Game(Game):
    """The game represented in [Fig. 6.2]. Serves as a simple test case.
    >>> g = Fig62Game()
    >>> minimax_decision('A', g)
    'a1'
    >>> alphabeta_full_search('A', g)
    'a1'
    >>> alphabeta_search('A', g)
    'a1'
    """

    succs = {'A': [('a1', 'B'), ('a2', 'C'), ('a3', 'D')],
             'B': [('b1', 'B1'), ('b2', 'B2'), ('b3', 'B3')],
             'C': [('c1', 'C1'), ('c2', 'C2'), ('c3', 'C3')],
             'D': [('d1', 'D1'), ('d2', 'D2'), ('d3', 'D3')]}
    utils = Dict(B1=3, B2=12, B3=8, C1=2, C2=4, C3=6, D1=14, D2=5, D3=2)
    initial = 'A'

    def __init__(self):
        Game.__init__(self)

    def successors(self, state):
        return self.succs.get(state, [])

    def utility(self, state, player):
        if player == 'MAX':
            return self.utils[state]
        else:
            return -self.utils[state]

    def terminal_test(self, state):
        return state not in ('A', 'B', 'C', 'D')

    def to_move(self, state):
        return if_(state in 'BCD', 'MIN', 'MAX')


class TicTacToe(Game):
    """Play TicTacToe on an h x v board, with Max (first player) playing 'X'.
    A st has the player to move, a cached utility, a list of moves in
    the form of a list of (x, y) positions, and a board, in the form of
    a dct of {(x, y): Player} entries, where Player is 'X' or 'O'."""
    def __init__(self, h=3, v=3, k=3):
        Game.__init__(self)
        update(self, h=h, v=v, k=k)
        moves = [(x, y) for x in range(1, h+1)
                 for y in range(1, v+1)]
        self.initial = Struct(to_move='X', utility=0, board={}, moves=moves)

    def legal_moves(self, state):
        """Legal moves are any square not yet taken."""
        return state.moves

    def make_move(self, move, state):
        if move not in state.moves:
            return state  # Illegal move has no effect
        board = state.board.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return Struct(to_move=if_(state.to_move == 'X', 'O', 'X'),
                      utility=self.compute_utility(board, move, state.to_move),
                      board=board, moves=moves)

    def utility(self, state, player):
        """Return the value to X; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility

    def terminal_test(self, state):
        """A st is terminal if it is won or there are no empty squares."""
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state):
        board = state.board
        for x in range(1, self.h+1):
            for y in range(1, self.v+1):
                print(board.get((x, y), '.'),)
            print

    def compute_utility(self, board, move, player):
        """If X wins with this move, return 1; if O return -1; else return 0."""
        if (self.k_in_row(board, move, player, (0, 1)) or
                self.k_in_row(board, move, player, (1, 0)) or
                self.k_in_row(board, move, player, (1, -1)) or
                self.k_in_row(board, move, player, (1, 1))):
            return if_(player == 'X', +1, -1)
        else:
            return 0

    def k_in_row(self, board, move, player, delta):
        """Return true if there is a line through move on board for player."""
        delta_x, delta_y = delta
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k


class ConnectFour(TicTacToe):
    """A TicTacToe-like game in which you can only make a move on the bottom
    row, or in a square directly above an occupied square.  Traditionally
    played on a 7x6 board and requiring 4 in a row."""

    def __init__(self, h=7, v=6, k=4):
        TicTacToe.__init__(self, h, v, k)

    def legal_moves(self, state):
        """Legal moves are any square not yet taken."""
        return [(x, y) for (x, y) in state.moves
                if y == 0 or (x, y-1) in state.board]
