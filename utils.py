"""Provide some widely useful utilities. Safe for "from utils import *"."""

from __future__ import generators
import operator, math, random, copy, sys, os.path, bisect

#______________________________________________________________________________
# Simple Data Structures: booleans, infinity, Dict, Struct

infinity = 1.0e400

def Dict(**entries):
    """Create a dict out of the argument=value arguments.
    Ex: Dict(a=1, b=2, c=3) ==> {'a':1, 'b':2, 'c':3}"""
    return entries

class DefaultDict(dict):
    """Dictionary with a default value for unknown keys.
    Ex: d = DefaultDict(0); d['x'] += 1; d['x'] ==> 1
    d =  DefaultDict([]); d['x'] += [1]; d['y'] += [2]; d['x'] ==> [1]"""
    def __init__(self, default):
        self.default = default

    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, copy.deepcopy(self.default))


class Struct:
    """Create an instance with argument=value slots.
    This is for making a lightweight object whose class doesn't matter.
    Ex: s = Struct(a=1, b=2); s.a ==> 1; s.a = 3; s ==> Struct(a=3, b=2)"""
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __cmp__(self, other):
        if isinstance(other, Struct):
            return cmp(self.__dict__, other.__dict__)
        else:
            return cmp(self.__dict__, other)

    def __repr__(self):
        args = ['%s=%s' % (k, repr(v)) for (k, v) in vars(self).items()]
        return 'Struct(%s)' % ', '.join(args)

def update(x, **entries):
    """Update a dict, or an object with slots, according to entries.
    Ex: update({'a': 1}, a=10, b=20) ==> {'a': 10, 'b': 20}
    update(Struct(a=1), a=10, b=20) ==> Struct(a=10, b=20)"""
    if isinstance(x, dict):
        x.update(entries)
    else:
        x.__dict__.update(entries)
    return x

#______________________________________________________________________________
# Functions on Sequences (mostly inspired by Common Lisp)
# NOTE: Sequence functions (count_if, find_if, every, some) take function
# argument first (like reduce, filter, and map).

def sort(seq, compare=cmp):
    """Sort seq (mutating it) and return it.  compare is the 2nd arg to .sort.
    Ex: sort([3, 1, 2]) ==> [1, 2, 3]; reverse(sort([3, 1, 2])) ==> [3, 2, 1]
    sort([-3, 1, 2], comparer(abs)) ==> [1, 2, -3]"""
    if isinstance(seq, str):
        seq = ''.join(sort(list(seq), compare))
    elif compare == cmp:
        seq.sort()
    else:
        seq.sort(compare)
    return seq


def comparer(key=None, cmp=cmp):
    """Build a compare function suitable for sort. The most common use is
    to specify key, meaning compare the values of key(x), key(y)."""
    if key == None:
        return cmp
    else:
        return lambda x,y: cmp(key(x), key(y))

def removeall(item, seq):
    """Return a copy of seq (or string) with all occurences of item removed.
    Ex: removeall(3, [1, 2, 3, 3, 2, 1, 3]) ==> [1, 2, 2, 1]
    removeall(4, [1, 2, 3]) ==> [1, 2, 3]"""
    if isinstance(seq, str):
        return seq.replace(item, '')
    else:
        return [x for x in seq if x != item]

def reverse(seq):
    """Return the reverse of a string or list or tuple.  Mutates the seq.
    Ex: reverse([1, 2, 3]) ==> [3, 2, 1]; reverse('abc') ==> 'cba'"""
    if isinstance(seq, str):
        return ''.join(reverse(list(seq)))
    elif isinstance(seq, tuple):
        return tuple(reverse(list(seq)))
    else:
        seq.reverse();
        return seq

def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements.
    Ex: unique([1, 2, 3, 2, 1]) ==> [1, 2, 3] # order may vary"""
    return list(set(seq))


def count_if(predicate, seq):
    """Count the number of elements of seq for which the predicate is true.
    count_if(callable, [42, None, max, min]) ==> 2"""
    f = lambda count, x: count + (not not predicate(x))
    return reduce(f, seq, 0)

def find_if(predicate, seq):
    """If there is an element of seq that satisfies predicate, return it.
    Ex: find_if(callable, [3, min, max]) ==> min
    find_if(callable, [1, 2, 3]) ==> None"""
    for x in seq:
        if predicate(x): return x
    return None

def every(predicate, seq):
    """True if every element of seq satisfies predicate.
    Ex: every(callable, [min, max]) ==> 1; every(callable, [min, 3]) ==> 0"""
    for x in seq:
        if not predicate(x): return False
    return True

def some(predicate, seq):
    """If some element x of seq satisfies predicate(x), return predicate(x).
    Ex: some(callable, [min, 3]) ==> 1; some(callable, [2, 3]) ==> 0"""
    for x in seq:
        px = predicate(x)
        if  px: return px
    return False

# Added by Brandon
def flatten(x):
    if type(x) != type([]): return [x]
    if x == []: return x
    return flatten(x[0]) + flatten(x[1:])

#______________________________________________________________________________
# Functions on sequences of numbers
# NOTE: these take the sequence argument first, like min and max,
# and like standard math notation: \sigma (i = 1..n) fn(i)
# A lot of programming is finding the best value that satisfies some condition;
# so there are three versions of argmin/argmax, depending on what you want to
# do with ties: return the first one, return them all, or pick at random.


def sum(seq, fn=None):
    """Sum the elements seq[i], or fn(seq[i]) if fn is given.
    Ex: sum([1, 2, 3]) ==> 6; sum(range(8), lambda x: 2**x) ==> 255"""
    if fn: seq = map(fn, seq)
    return reduce(operator.add, seq, 0)


def product(seq, fn=None):
    """Multiply the elements seq[i], or fn(seq[i]) if fn is given.
    product([1, 2, 3]) ==> 6; product([1, 2, 3], lambda x: x*x) ==> 1*4*9"""
    if fn:
        seq = map(fn, seq)
    return reduce(operator.mul, seq, 1)


def argmin_list(seq, fn):
    """Return a list of elements of seq[i] with the lowest fn(seq[i]) scores.
    Ex: argmin_list(['one', 'to', 'three', 'or'], len) ==>  ['to', 'or']"""
    best_score, best = fn(seq[0]), []
    for x in seq:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = [x], x_score
        elif x_score == best_score:
            best.append(x)
    return best


def argmin_gen(gen, fn):
    """Return a list of elements of gen with the lowest fn(x) scores.
    Ex: argmin_list(['one', 'to', 'three', 'or'], len) ==>  ['to', 'or']"""
    best_score, best = fn(gen.next()), []
    for x in gen:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = [x], x_score
        elif x_score == best_score:
            best.append(x)
    return best


def argmin_random_tie_gen(gen, fn):
    """Return an element with lowest fn(x) score; break ties at random.
    Thus, for all s,f: argmin_random_tie(s, f) in argmin_list(s, f)"""
    try:
        best = gen.next(); best_score = fn(best); n = 0
    except StopIteration:
        return []

    for x in gen:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score; n = 1
        elif x_score == best_score:
            n += 1
            if random.randrange(n) == 0:
                best = x
    return best

def argmin_random_tie(seq, fn):
    """Return an element with lowest fn(seq[i]) score; break ties at random.
    Thus, for all s,f: argmin_random_tie(s, f) in argmin_list(s, f)"""
    best_score = fn(seq[0]); n = 0
    for x in seq:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score; n = 1
        elif x_score == best_score:
            n += 1
            if random.randrange(n) == 0:
                best = x
    return best

def argmax(gen, fn):
    """Return an element with highest fn(x) score; tie goes to first one.
    Ex: argmax(['one', 'to', 'three'], len) ==> 'three'"""
    return argmin_gen(gen, lambda x: -fn(x))

def argmax_list(seq, fn):
    """Return a list of elements of gen with the highest fn(x) scores.
    Ex: argmax_list(['one', 'three', 'seven'], len) ==> ['three', 'seven']"""
    return argmin_list(seq, lambda x: -fn(x))

def argmax_random_tie(seq, fn):
    "Return an element with highest fn(x) score; break ties at random."
    return argmin_random_tie(seq, lambda x: -fn(x))

def argmax_random_tie_gen(gen, fn):
    "Return an element with highest fn(x) score; break ties at random."
    return argmin_random_tie_gen(gen, lambda x: -fn(x))
#______________________________________________________________________________
# Statistical and mathematical functions

def histogram(values, mode=0, bin_function=None):
    """Return a list of (value, count) pairs, summarizing the input values.
    Sorted by increasing value, or if mode=1, by decreasing count.
    If bin_function is given, map it over values first.
    Ex: vals = [100, 110, 160, 200, 160, 110, 200, 200, 220]
    histogram(vals) ==> [(100, 1), (110, 2), (160, 2), (200, 3), (220, 1)]
    histogram(vals, 1) ==> [(200, 3), (160, 2), (110, 2), (100, 1), (220, 1)]
    histogram(vals, 1, lambda v: round(v, -2)) ==> [(200.0, 6), (100.0, 3)]"""
    if bin_function: values = map(bin_function, values)
    bins = {}
    for val in values:
        bins[val] = bins.get(val, 0) + 1
    if mode:
        return sort(bins.items(), lambda x,y: cmp(y[1],x[1]))
    else:
        return sort(bins.items())

def log2(x):
    """Base 2 logarithm.
    Ex: log2(1024) ==> 10.0; log2(1.0) ==> 0.0; log2(0) raises OverflowError"""
    return math.log10(x) / math.log10(2)

def mode(values):
    """Return the most common value in the list of values.
    Ex: mode([1, 2, 3, 2]) ==> 2"""
    return histogram(values, mode=1)[0][0]

def median(values):
    """Return the middle value, when the values are sorted.
    If there are an odd number of elements, try to average the middle two.
    If they can't be averaged (e.g. they are strings), choose one at random.
    Ex: median([10, 100, 11]) ==> 11; median([1, 2, 3, 4]) ==> 2.5"""
    n = len(values)
    values = sort(values[:])
    if n % 2 == 1:
        return values[n/2]
    else:
        middle2 = values[(n/2)-1:(n/2)+1]
        try:
            return mean(middle2)
        except TypeError:
            return random.choice(middle2)

def mean(values):
    """Return the arithmetic average of the values."""
    return sum(values) / float(len(values))

def stddev(values, meanval=None):
    """The standard deviation of a set of values.
    Pass in the mean if you already know it."""
    if meanval == None: meanval = mean(values)
    return math.sqrt(sum([(x - meanval)**2 for x in values]))

def dotproduct(X, Y):
    """Return the sum of the element-wise product of vectors x and y.
    Ex: dotproduct([1, 2, 3], [1000, 100, 10]) ==> 1230"""
    return sum([x * y for x, y in zip(X, Y)])

def vector_add(a, b):
    """Component-wise addition of two vectors.
    Ex: vector_add((0, 1), (8, 9)) ==> (8, 10)"""
    return tuple(map(operator.add, a, b))

def probability(p):
    "Return true with probability p."
    return p > random.uniform(0.0, 1.0)

def num_or_str(x):
    """The argument is a string; convert to a number if possible, or strip it.
    Ex: num_or_str('42') ==> 42; num_or_str(' 42x ') ==> '42x' """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
                return str(x).strip()

def distance((ax, ay), (bx, by)):
    "The distance between two (x, y) points."
    return math.hypot((ax - bx), (ay - by))

def distance2((ax, ay), (bx, by)):
    "The square of the distance between two (x, y) points."
    return (ax - bx)**2 + (ay - by)**2

def normalize(numbers, total=1.0):
    """Multiply each number by a constant such that the sum is 1.0 (or total).
    Ex: normalize([1,2,1]) ==> [0.25, 0.5, 0.25]"""
    k = total / sum(numbers)
    return [k * n for n in numbers]
#______________________________________________________________________________
# Misc Functions

def printf(format, *args):
    """Format args with the first argument as format string, and write.
    Return the last arg, or format itself if there are no args."""
    sys.stdout.write(str(format) % args)
    return if_(args, args[-1], format)

def print_(*args):
    """Print the args and return the last one."""
    for arg in args: print arg,
    print
    return if_(args, args[-1], None)

def memoize(fn, slot=None):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, store results in a dictionary.
    Ex: def fib(n): return (n<=1 and 1) or (fib(n-1) + fib(n-2)); fib(9) ==> 55
    # Now we make it faster:
    fib = memoize(fib); fib(9) ==> 55"""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        def memoized_fn(*args):
            if not memoized_fn.cache.has_key(args):
                memoized_fn.cache[args] = fn(*args)
            return memoized_fn.cache[args]
        memoized_fn.cache = {}
    return memoized_fn

def method(name, *args):
    """Return a function that invokes the named method with the optional args.
    Ex: map(method('upper'), ['a', 'b', 'cee']) ==> ['A', 'B', 'CEE']
    map(method('count', 't'), ['this', 'is', 'a', 'test']) ==> [1, 0, 0, 2]"""
    return lambda x: getattr(x, name)(*args)

def method2(name, *static_args):
    """Return a function that invokes the named method with the optional args.
    Ex: map(method('upper'), ['a', 'b', 'cee']) ==> ['A', 'B', 'CEE']
    map(method('count', 't'), ['this', 'is', 'a', 'test']) ==> [1, 0, 0, 2]"""
    return lambda x, *dyn_args: getattr(x, name)(*(dyn_args + static_args))

def abstract():
    """Indicate abstract methods that should be implemented in a subclass.
    Ex: def m(): abstract() # Similar to Java's 'abstract void m()'"""
    raise NotImplementedError(caller() + ' must be implemented in subclass')

def caller(n=1):
    """Return the name of the calling function n levels up in the frame stack.
    Ex: caller(0) ==> 'caller'; def f(): return caller(); f() ==> 'f'"""
    import inspect
    return  inspect.getouterframes(inspect.currentframe())[n][3]

def indexed(seq):
    """Like [(i, seq[i]) for i in range(len(seq))], but with yield.
    Ex: for i, c in indexed('abc'): print i, c"""
    i = 0
    for x in seq:
        yield i, x
        i += 1

def if_(test, result, alternative):
    """Like C++ and Java's (test ? result : alternative), except
    both result and alternative are always evaluated. However, if
    either evaluates to a function, it is applied to the empty arglist,
    so you can delay execution by putting it in a lambda.
    Ex: if_(2 + 2 == 4, 'ok', lambda: expensive_computation()) ==> 'ok' """
    if test:
        if callable(result): return result()
        return result
    else:
        if callable(alternative): return alternative()
        return alternative

def name(object):
    "Try to find some reasonable name for the object."
    return (getattr(object, 'name', 0) or getattr(object, '__name__', 0)
            or getattr(getattr(object, '__class__', 0), '__name__', 0)
            or str(object))

def isnumber(x):
    "Is x a number? We say it is if it has a __int__ method."
    return hasattr(x, '__int__')

def issequence(x):
    "Is x a sequence? We say it is if it has a __getitem__ method."
    return hasattr(x, '__getitem__')

def print_table(table, header=None, sep=' ', numfmt='%g'):
    """Print a list of lists as a table, so that columns line up nicely.
    header, if specified, will be printed as the first row.
    numfmt is the format for all numbers; you might want e.g. '%6.2f'.
    (If you want different formats in differnt columns, don't use print_table.)
    sep is the separator between columns."""
    justs = [if_(isnumber(x), 'rjust', 'ljust') for x in table[0]]
    if header:
        table = [header] + table
    table = [[if_(isnumber(x), lambda: numfmt % x, x)  for x in row]
             for row in table]
    maxlen = lambda seq: max(map(len, seq))
    sizes = map(maxlen, zip(*[map(str, row) for row in table]))
    for row in table:
        for (j, size, x) in zip(justs, sizes, row):
            print getattr(str(x), j)(size), sep,
        print

def AIMAFile(components, mode='r'):
    "Open a file based at the AIMA root directory."
    dir = os.path.dirname(__file__)
    return open(apply(os.path.join, [dir] + components), mode)

def DataFile(name, mode='r'):
    "Return a file in the AIMA /data directory."
    return AIMAFile(['data', name], mode)


#______________________________________________________________________________
# Queues: Stack, FIFOQueue, PriorityQueue

#______________________________________________________________________________
# Queues: Stack, FIFOQueue, PriorityQueue

class Queue:
    """Queue is an abstract class/interface. There are three types:
        Stack(): A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(order, f): Queue in sorted order (default min-first).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
        item in q       -- does q contain item?
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def __init__(self):
        abstract

    def extend(self, items):
        for item in items: self.append(item)

def Stack():
    """Return an empty list, suitable as a Last-In-First-Out Queue."""
    return []

class FIFOQueue(Queue):
    """A First-In-First-Out Queue."""
    def __init__(self):
        self.A = []; self.start = 0
    def append(self, item):
        self.A.append(item)
    def __len__(self):
        return len(self.A) - self.start
    def extend(self, items):
        self.A.extend(items)
    def pop(self):
        e = self.A[self.start]
        self.start += 1
        if self.start > 5 and self.start > len(self.A)/2:
            self.A = self.A[self.start:]
            self.start = 0
        return e
    def __contains__(self, item):
        return item in self.A[self.start:]


class PriorityQueue(Queue):
    """A queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first. If order is min, the item with minimum f(x) is
    returned first; if order is max, then it is the item with maximum f(x).
    Also supports dict-like lookup."""
    def __init__(self, order=min, f=lambda x: x):
        update(self, A=[], order=order, f=f)
    def append(self, item):
        bisect.insort(self.A, (self.f(item), item))
    def __len__(self):
        return len(self.A)
    def pop(self):
        if self.order == min:
            return self.A.pop(0)[1]
        else:
            return self.A.pop()[1]
    def __contains__(self, item):
        return some(lambda (_, x): x == item, self.A)
    def __getitem__(self, key):
        for _, item in self.A:
            if item == key:
                return item
    def __delitem__(self, key):
        for i, (value, item) in enumerate(self.A):
            if item == key:
                self.A.pop(i)
                return


def manhattan_distance(start_row, start_col, end_row, end_col):
    return abs(start_row - end_row) + abs(start_col - end_col)

#______________________________________________________________________________
# Additional tests

_docex = """
def is_even(x): return x % 2 == 0
sort([1, 2, -3]) ==> [-3, 1, 2]
sort(range(10), comparer(key=is_even)) ==> [1, 3, 5, 7, 9, 0, 2, 4, 6, 8]
sort(range(10), lambda x,y: y-x) ==> [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

removeall(4, []) ==> []
removeall('s', 'This is a test. Was a test.') ==> 'Thi i a tet. Wa a tet.'
removeall('s', 'Something') ==> 'Something'
removeall('s', '') ==> ''

reverse([]) ==> []
reverse('') ==> ''

count_if(is_even, [1, 2, 3, 4]) ==> 2
count_if(is_even, []) ==> 0

sum([]) ==> 0

product([]) ==> 1

argmax([1], lambda x: x*x) ==> 1
argmin([1], lambda x: x*x) ==> 1
argmax([]) raises TypeError
argmin([]) raises TypeError


# Test of memoize with slots in structures
countries = [Struct(name='united states'), Struct(name='canada')]
# Pretend that 'gnp' was some big hairy operation:
def gnp(country): return len(country.name) * 1e10
gnp = memoize(gnp, '_gnp')
map(gnp, countries) ==> [13e10, 6e10]
countries # note the _gnp slot.
# This time we avoid re-doing the calculation
map(gnp, countries) ==> [13e10, 6e10]

# Test Queues:
nums = [1, 8, 2, 7, 5, 6, -99, 99, 4, 3, 0]
def qtest(q): return [q.extend(nums), [q.pop() for i in range(len(q))]][1]
qtest(Stack()) ==> reverse(nums)
qtest(FIFOQueue()) ==> nums
qtest(PriorityQueue(min)) ==> [-99, 0, 1, 2, 3, 4, 5, 6, 7, 8, 99]
qtest(PriorityQueue(max)) ==> [99, 8, 7, 6, 5, 4, 3, 2, 1, 0, -99]
qtest(PriorityQueue(min, abs)) ==> [0, 1, 2, 3, 4, 5, 6, 7, 8, -99, 99]
qtest(PriorityQueue(max, abs)) ==> [99, -99, 8, 7, 6, 5, 4, 3, 2, 1, 0]
"""
