"""Search (Chapters 3-4)

The way to use this code is to subclass Problem to create a class of problems,
then create problem instances and solve them with calls to the various search
functions."""
import sys
import math
import random
from util import abstract, update, FIFOQueue, Stack, memoize, PriorityQueue, \
    if_, infinity, argmax_random_tie, probability, distance, argmin
from utils import cmp


class Problem(object):
    """The abstract class for a formal problem.  You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal.  Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        abstract()

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        abstract()

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Override this
        method if checking against a single self.goal is not enough."""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        abstract()


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node %s>" % (self.state,)

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """Fig. 3.10"""
        next_state = problem.result(self.state, action)
        return Node(next_state, self, action,
                    problem.path_cost(self.path_cost, self.state, action, next_state))

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


class SimpleProblemSolvingAgentProgram:
    """Abstract framework for a problem-solving agent. [Fig. 3.1]"""
    def __init__(self, initial_state=None):
        update(self, state=initial_state, seq=[])

    def __call__(self, percept):
        self.state = self.update_state(self.state, percept)
        if not self.seq:
            goal = self.formulate_goal(self.state)
            problem = self.formulate_problem(self.state, goal)
            self.seq = self.search(problem)
            if not self.seq:
                return None
        return self.seq.pop(0)

    def update_state(self, percept):
        abstract()

    def formulate_goal(self, state):
        abstract()

    def formulate_problem(self, state, goal):
        abstract()

    def search(self, problem):
        abstract()


# Uninformed Search algorithms
def tree_search(problem, frontier):
    """Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Don't worry about repeated paths to a state. [Fig. 3.7]"""
    frontier.append(Node(problem.initial))
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        frontier.extend(node.expand(problem))
    return None


def graph_search(problem, frontier):
    """Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    If two paths reach a state, only use the first one. [Fig. 3.7]"""
    frontier.append(Node(problem.initial))
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored
                        and child not in frontier)
    return None


def breadth_first_tree_search(problem):
    """Search the shallowest nodes in the search tree first."""
    return tree_search(problem, FIFOQueue())


def depth_first_tree_search(problem):
    """Search the deepest nodes in the search tree first."""
    return tree_search(problem, Stack())


def depth_first_graph_search(problem):
    """Search the deepest nodes in the search tree first."""
    return graph_search(problem, Stack())


def breadth_first_search(problem):
    """[Fig. 3.11]"""
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = FIFOQueue()
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child
                frontier.append(child)
    return None


def best_first_graph_search(problem, f):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = PriorityQueue(min, f)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                incumbent = frontier[child]
                if f(child) < f(incumbent):
                    del frontier[incumbent]
                    frontier.append(child)
    return None


def uniform_cost_search(problem):
    """[Fig. 3.14]"""
    return best_first_graph_search(problem, lambda node: node.path_cost)


def depth_limited_search(problem, limit=50):
    """[Fig. 3.17]"""
    def recursive_dls(node, problem, limit):
        if problem.goal_test(node.state):
            return node
        elif node.depth == limit:
            return 'cutoff'
        else:
            cutoff_occurred = False
            for child in node.expand(problem):
                result = recursive_dls(child, problem, limit)
                if result == 'cutoff':
                    cutoff_occurred = True
                elif result is not None:
                    return result
            return if_(cutoff_occurred, 'cutoff', None)

    # Body of depth_limited_search:
    return recursive_dls(Node(problem.initial), problem, limit)


def iterative_deepening_search(problem):
    """[Fig. 3.18]"""
    for depth in range(sys.maxint):
        result = depth_limited_search(problem, depth)
        if result != 'cutoff':
            return result


# Informed (Heuristic) Search
greedy_best_first_graph_search = best_first_graph_search
# Greedy best-first search is accomplished by specifying f(n) = h(n).


def astar_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))


# Other search algorithms
def recursive_best_first_search(problem, h=None):
    """[Fig. 3.26]"""
    h = memoize(h or problem.h, 'h')

    def RBFS(problem, node, flimit):
        if problem.goal_test(node.state):
            return node, 0   # (The second value is immaterial)
        successors = node.expand(problem)
        if len(successors) == 0:
            return None, infinity
        for s in successors:
            s.f = max(s.path_cost + h(s), node.f)
        while True:
            successors.sort(lambda x, y: cmp(x.f, y.f))  # Order by lowest f value
            best = successors[0]
            if best.f > flimit:
                return None, best.f
            if len(successors) > 1:
                alternative = successors[1].f
            else:
                alternative = infinity
            result, best.f = RBFS(problem, best, min(flimit, alternative))
            if result is not None:
                return result, best.f

    node = Node(problem.initial)
    node.f = h(node)
    result, bestf = RBFS(problem, node, infinity)
    return result


def hill_climbing(problem):
    """From the initial node, keep choosing the neighbor with highest value,
    stopping when no neighbor is better. [Fig. 4.2]"""
    current = Node(problem.initial)
    while True:
        neighbors = current.expand(problem)
        if not neighbors:
            break
        neighbor = argmax_random_tie(neighbors,
                                     lambda node: problem.value(node.state))
        if problem.value(neighbor.state) <= problem.value(current.state):
            break
        current = neighbor
    return current.state


def exp_schedule(k=20, lam=0.005, limit=100):
    """One possible schedule function for simulated annealing"""
    return lambda t: if_(t < limit, k * math.exp(-lam * t), 0)


def simulated_annealing(problem, schedule=exp_schedule()):
    """[Fig. 4.5]"""
    current = Node(problem.initial)
    for t in range(sys.maxint):
        t_prime = schedule(t)
        if t_prime == 0:
            return current
        neighbors = current.expand(problem)
        if not neighbors:
            return current
        next_neighbor = random.choice(neighbors)
        delta_e = problem.value(next_neighbor.state) - \
            problem.value(current.state)
        if delta_e > 0 or probability(math.exp(delta_e / t_prime)):
            current = next_neighbor


# The remainder of this file implements examples for the search algorithms.
# Graphs and Graph Problems
class Graph:
    """A graph connects nodes (vertices) by edges (links).  Each edge can also
    have a length associated with it.  The constructor call is something like:
        g = Graph({'A': {'B': 1, 'C': 2})
    this makes a graph with 3 nodes, A, B, and C, with an edge of length 1 from
    A to B,  and an edge of length 2 from A to C.  You can also do:
        g = Graph({'A': {'B': 1, 'C': 2}, directed=False)
    This makes an undirected graph, so inverse links are also added. The graph
    stays undirected; if you add more links with g.connect('B', 'C', 3), then
    inverse link is also added.  You can use g.nodes() to get a list of nodes,
    g.get('A') to get a dct of links out of A, and g.get('A', 'B') to get the
    length of the link from A to B.  'Lengths' can actually be any obj at
    all, and nodes can be any hashable obj."""

    def __init__(self, dict=None, directed=True):
        self.dict = dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()

    def make_undirected(self):
        """Make a digraph into an undirected graph by adding symmetric edges."""
        for a in self.dict.keys():
            for b, dist in self.dict[a].items():
                self.connect1(b, a, dist)

    def connect(self, a, b, dist=1):
        """Add a link from A and B of given dist, and also add the inverse
        link if the graph is undirected."""
        self.connect1(a, b, dist)
        if not self.directed:
            self.connect1(b, a, dist)

    def connect1(self, a, b, dist):
        """Add a link from A to B of given dist, in one direction only."""
        self.dict.setdefault(a, {})[b] = dist

    def get(self, a, b=None):
        """Return a link dist or a dct of {node: dist} entries.
        .get(a,b) returns the dist or None;
        .get(a) returns a dct of {node: dist} entries, possibly {}."""
        links = self.dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)

    def nodes(self):
        """Return a list of nodes in the graph."""
        return self.dict.keys()


def UndirectedGraph(dct=None):
    """Build a Graph where every edge (including future ones) goes both ways."""
    return Graph(dict=dct, directed=False)


def RandomGraph(nodes=range(10), min_links=2, width=400, height=300,
                curvature=lambda: random.uniform(1.1, 1.5)):
    """Construct a random graph, with the specified nodes, and random links.
    The nodes are laid out randomly on a (width x height) rectangle.
    Then each node is connected to the min_links nearest neighbors.
    Because inverse links are added, some nodes will have more connections.
    The dist between nodes is the hypotenuse times curvature(),
    where curvature() defaults to a random number between 1.1 and 1.5."""
    g = UndirectedGraph()
    g.locations = {}
    # Build the cities
    for node in nodes:
        g.locations[node] = (random.randrange(width), random.randrange(height))
    # Build roads from each city to at least min_links nearest neighbors.
    for i in range(min_links):
        for node in nodes:
            if len(g.get(node)) < min_links:
                here = g.locations[node]

                def distance_to_node(n):
                    if n is node or g.get(node, n):
                        return infinity
                    return distance(g.locations[n], here)
                neighbor = argmin(nodes, distance_to_node)
                d = distance(g.locations[neighbor], here) * curvature()
                g.connect(node, neighbor, int(d))
    return g


class GraphProblem(Problem):
    """The problem of searching a graph from one node to another."""
    def __init__(self, initial, goal, graph):
        Problem.__init__(self, initial, goal)
        self.graph = graph

    def actions(self, a):
        """The actions at a graph node are just its neighbors."""
        return self.graph.get(a).keys()

    def result(self, state, action):
        """The result of going to a neighbor is just that neighbor."""
        return action

    def path_cost(self, cost_so_far, a, action, b):
        return cost_so_far + (self.graph.get(a, b) or infinity)

    def h(self, node):
        """h function is straight-line dist from a node's state to goal."""
        locs = getattr(self.graph, 'locations', None)
        if locs:
            return int(distance(locs[node.state], locs[self.goal]))
        else:
            return infinity


class NQueensProblem(Problem):
    """The problem of placing N queens on an NxN board with none attacking
    each other.  A state is represented as an N-element array, where
    a value of r in the c-th entry means there is a queen at column c,
    row r, and a value of None means that the c-th column has not been
    filled in yet.  We fill in columns left to right.
    >>> depth_first_tree_search(NQueensProblem(8))
    <Node [7, 3, 0, 2, 5, 1, 6, 4]>
    """
    def __init__(self, n, initial):
        super(NQueensProblem, self).__init__(initial)
        self.N = n
        self.initial = [None] * n

    def actions(self, state):
        """In the leftmost empty column, try all non-conflicting rows."""
        if state[-1] is not None:
            return []  # All columns filled; no successors
        else:
            col = state.index(None)
            return [row for row in range(self.N)
                    if not self.conflicted(state, row, col)]

    def result(self, state, row):
        """Place the next queen at the given row."""
        col = state.index(None)
        new = state[:]
        new[col] = row
        return new

    def conflicted(self, state, row, col):
        """Would placing a queen at (row, col) conflict with anything?"""
        return any(self.conflict(row, col, state[c], c)
                   for c in range(col))

    def conflict(self, row1, col1, row2, col2):
        """Would putting two queens in (row1, col1) and (row2, col2) conflict?"""
        return (row1 == row2  # same row
                or col1 == col2  # same column
                or row1-col1 == row2-col2  # same \ diagonal
                or row1+col1 == row2+col2)  # same / diagonal

    def goal_test(self, state):
        """Check if all columns filled, no conflicts."""
        if state[-1] is None:
            return False
        return not any(self.conflicted(state, state[col], col)
                       for col in range(len(state)))


__doc__ += """
>>> ab = GraphProblem('A', 'B', romania)
>>> breadth_first_tree_search(ab).solution()
['S', 'F', 'B']
>>> breadth_first_search(ab).solution()
['S', 'F', 'B']
>>> uniform_cost_search(ab).solution()
['S', 'R', 'P', 'B']
>>> depth_first_graph_search(ab).solution()
['T', 'L', 'M', 'D', 'C', 'P', 'B']
>>> iterative_deepening_search(ab).solution()
['S', 'F', 'B']
>>> len(depth_limited_search(ab).solution())
50
>>> astar_search(ab).solution()
['S', 'R', 'P', 'B']
>>> recursive_best_first_search(ab).solution()
['S', 'R', 'P', 'B']
"""
