"""Provide some widely useful utilities. Safe for "from utils import *"."""

from __future__ import generators
import operator
import math
import random
import copy
import sys
import os.path
import bisect
from functools import reduce

# Simple Data Structures: booleans, infinity, Dict, Struct

infinity = 1.0e400


def cmp(a, b):
    return (a > b) - (a < b)


def Dict(**entries):
    """Create a dct out of the argument=value arguments.
    Ex: Dict(a=1, b=2, c=3) ==> {'a':1, 'b':2, 'c':3}"""
    return entries


class DefaultDict(dict):
    """Dictionary with a default value for unknown keys.
    Ex: d = DefaultDict(0); d['x'] += 1; d['x'] ==> 1
    d =  DefaultDict([]); d['x'] += [1]; d['y'] += [2]; d['x'] ==> [1]"""
    def __init__(self, default):
        super(DefaultDict, self).__init__()
        self.default = default

    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return self.setdefault(key, copy.deepcopy(self.default))


class Struct:
    """Create an instance with argument=value slots.
    This is for making a lightweight obj whose class doesn't matter.
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
    """Update a dct, or an obj with slots, according to entries.
    Ex: update({'a': 1}, a=10, b=20) ==> {'a': 10, 'b': 20}
    update(Struct(a=1), a=10, b=20) ==> Struct(a=10, b=20)"""
    if isinstance(x, dict):
        x.update(entries)
    else:
        x.__dict__.update(entries)
    return x


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
    if key is None:
        return cmp
    else:
        return lambda x, y: cmp(key(x), key(y))


def remove_all(item, seq):
    """Return a copy of seq (or string) with all occurrences of item removed.
    Ex: remove_all(3, [1, 2, 3, 3, 2, 1, 3]) ==> [1, 2, 2, 1]
    remove_all(4, [1, 2, 3]) ==> [1, 2, 3]"""
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
        seq.reverse()
        return seq


def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements.
    Ex: unique([1, 2, 3, 2, 1]) ==> [1, 2, 3] # order may vary"""
    return list(set(seq))


def count_if(predicate, seq):
    """Count the number of elements of seq for which the predicate is true.
    count_if(callable, [42, None, max, min]) ==> 2"""
    def count_func(count, x):
        return count + (not not predicate(x))
    return reduce(count_func, seq, 0)


def find_if(predicate, seq):
    """If there is an element of seq that satisfies predicate, return it.
    Ex: find_if(callable, [3, min, max]) ==> min
    find_if(callable, [1, 2, 3]) ==> None"""
    for x in seq:
        if predicate(x):
            return x
    return None


def every(predicate, seq):
    """True if every element of seq satisfies predicate.
    Ex: every(callable, [min, max]) ==> 1; every(callable, [min, 3]) ==> 0"""
    for x in seq:
        if not predicate(x):
            return False
    return True


def some(predicate, seq):
    """If some element x of seq satisfies predicate(x), return predicate(x).
    Ex: some(callable, [min, 3]) ==> 1; some(callable, [2, 3]) ==> 0"""
    for x in seq:
        px = predicate(x)
        if px:
            return px
    return False


# Added by Brandon
def flatten(x):
    if not isinstance(x, list):
        return [x]
    if not x:
        return x
    return flatten(x[0]) + flatten(x[1:])


# Functions on sequences of numbers
# NOTE: these take the sequence argument first, like min and max,
# and like standard math notation: \sigma (i = 1..n) fn(i)
# A lot of programing is finding the best value that satisfies some condition;
# so there are three versions of argmin/argmax, depending on what you want to
# do with ties: return the first one, return them all, or pick at random.
def sum_seq(seq, fn=None):
    """Sum the elements seq[i], or fn(seq[i]) if fn is given.
    Ex: sum_seq([1, 2, 3]) ==> 6; sum_seq(range(8), lambda x: 2**x) ==> 255"""
    if fn:
        seq = map(fn, seq)
    return reduce(operator.add, seq, 0)


def product(seq, fn=None):
    """Multiply the elements seq[i], or fn(seq[i]) if fn is given.
    product([1, 2, 3]) ==> 6; product([1, 2, 3], lambda x: x*x) ==> 1*4*9"""
    if fn:
        seq = map(fn, seq)
    return reduce(operator.mul, seq, 1)


def argmin(gen, fn):
    """Return an element with lowest fn(x) score; tie goes to first one.
    Gen must be a generator.
    Ex: argmin(['one', 'to', 'three'], len) ==>  'to'"""
    best = gen.next()
    best_score = fn(best)
    for x in gen:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score
    return best


def argmin_list(gen, fn):
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


def argmin_random_tie(gen, fn):
    """Return an element with lowest fn(x) score; break ties at random.
    Thus, for all s,f: argmin_random_tie(s, f) in argmin_list(s, f)"""
    try:
        best = next(gen)
        best_score = fn(best)
        n = 0
    except StopIteration:
        return []

    for x in gen:
        x_score = fn(x)
        if x_score < best_score:
            best, best_score = x, x_score
            n = 1
        elif x_score == best_score:
            n += 1
            if random.randrange(n) == 0:
                best = x
    return best


def argmax(gen, fn):
    """Return an element with highest fn(x) score; tie goes to first one.
    Ex: argmax(['one', 'to', 'three'], len) ==> 'three'"""
    return argmin(gen, lambda x: -fn(x))


def argmax_list(seq, fn):
    """Return a list of elements of gen with the highest fn(x) scores.
    Ex: argmax_list(['one', 'three', 'seven'], len) ==> ['three', 'seven']"""
    return argmin_list(seq, lambda x: -fn(x))


def argmax_random_tie(seq, fn):
    """Return an element with highest fn(x) score; break ties at random."""
    return argmin_random_tie(seq, lambda x: -fn(x))


def log2(x):
    """Base 2 logarithm.
    Ex: log2(1024) ==> 10.0; log2(1.0) ==> 0.0; log2(0) raises OverflowError"""
    return math.log10(x) / math.log10(2)


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
    return sum_seq(values) / float(len(values))


def stddev(values, mean_val=None):
    """The standard deviation of a set of values.
    Pass in the mean if you already know it."""
    if mean_val is None:
        mean_val = mean(values)
    return math.sqrt(sum_seq([(x - mean_val) ** 2 for x in values]))


def dot_product(xi, yi):
    """Return the sum_seq of the element-wise product of vectors x and y.
    Ex: dotproduct([1, 2, 3], [1000, 100, 10]) ==> 1230"""
    return sum_seq([x * y for x, y in zip(xi, yi)])


def vector_add(a, b):
    """Component-wise addition of two vectors.
    Ex: vector_add((0, 1), (8, 9)) ==> (8, 10)"""
    return tuple(map(operator.add, a, b))


def probability(p):
    """Return true with probability p."""
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


def distance(a, b):
    """The dist between two (x, y) points."""
    ax, ay = a
    bx, by = b
    return math.hypot((ax - bx), (ay - by))


def distance2(a, b):
    """"The square of the dist between two (x, y) points."""
    ax, ay = a
    bx, by = b
    return (ax - bx)**2 + (ay - by)**2


def normalize(numbers, total=1.0):
    """Multiply each number by a constant such that the sum_seq is 1.0 (or total).
    Ex: normalize([1,2,1]) ==> [0.25, 0.5, 0.25]"""
    k = total / sum_seq(numbers)
    return [k * n for n in numbers]


# Misc Functions
def printf(fmt, *args):
    """Format args with the first argument as fmt string, and write.
    Return the last arg, or fmt itself if there are no args."""
    sys.stdout.write(str(fmt) % args)
    return if_(args, args[-1], fmt)


def print_(*args):
    """Print the args and return the last one."""
    for arg in args:
        print(arg,)
    print()
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
            if args not in memoized_fn.cache:
                memoized_fn.cache[args] = fn(*args)
            return memoized_fn.cache[args]
        memoized_fn.cache = {}
    return memoized_fn


def method(nm, *args):
    """Return a function that invokes the named method with the optional args.
    Ex: map(method('upper'), ['a', 'b', 'cee']) ==> ['A', 'B', 'CEE']
    map(method('count', 't'), ['this', 'is', 'a', 'test']) ==> [1, 0, 0, 2]"""
    return lambda x: getattr(x, nm)(*args)


def method2(nm, *static_args):
    """Return a function that invokes the named method with the optional args.
    Ex: map(method('upper'), ['a', 'b', 'cee']) ==> ['A', 'B', 'CEE']
    map(method('count', 't'), ['this', 'is', 'a', 'test']) ==> [1, 0, 0, 2]"""
    return lambda x, *dyn_args: getattr(x, nm)(*(dyn_args + static_args))


def abstract():
    """Indicate abstract methods that should be implemented in a subclass.
    Ex: def m(): abstract() # Similar to Java's 'abstract void m()'"""
    raise NotImplementedError(caller() + ' must be implemented in subclass')


def caller(n=1):
    """Return the filename of the calling function n levels up in the frame stack.
    Ex: caller(0) ==> 'caller'; def f(): return caller(); f() ==> 'f'"""
    import inspect
    return inspect.getouterframes(inspect.currentframe())[n][3]


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
    either evaluates to a function, it is applied to the empty arg list,
    so you can delay execution by putting it in a lambda.
    Ex: if_(2 + 2 == 4, 'ok', lambda: expensive_computation()) ==> 'ok' """
    if test:
        if callable(result):
            return result()
        return result
    else:
        if callable(alternative):
            return alternative()
        return alternative


def name(obj):
    """Try to find some reasonable filename for the obj."""
    return (getattr(obj, 'filename', 0) or getattr(obj, '__name__', 0)
            or getattr(getattr(obj, '__class__', 0), '__name__', 0)
            or str(obj))


def is_number(x):
    """Is x a number? We say it is if it has a __int__ method."""
    return hasattr(x, '__int__')


def is_sequence(x):
    """Is x a sequence? We say it is if it has a __getitem__ method."""
    return hasattr(x, '__getitem__')


def print_table(table, header=None, sep=' ', numfmt='%g'):
    """Print a list of lists as a table, so that columns line up nicely.
    header, if specified, will be printed as the first row.
    numfmt is the fmt for all numbers; you might want e.g. '%6.2f'.
    (If you want different formats in different columns, don't use print_table.)
    sep is the separator between columns."""
    justs = [if_(is_number(x), 'rjust', 'ljust') for x in table[0]]
    if header:
        table = [header] + table
    table = [[if_(is_number(x), lambda: numfmt % x, x) for x in row]
             for row in table]

    def max_length(seq):
        return max(map(len, seq))
    sizes = map(max_length, zip(*[map(str, row) for row in table]))
    for row in table:
        for (j, size, x) in zip(justs, sizes, row):
            print(getattr(str(x), j)(size), sep,)
        print()


def AIMAFile(components, file_mode='r'):
    """Open a file based at the AIMA root directory."""
    directory = os.path.dirname(__file__)
    return open(os.path.join(*([directory] + components)), file_mode)


def DataFile(filename, file_mode='r'):
    """Return a file in the AIMA /data directory."""
    return AIMAFile(['data', filename], file_mode)


# Queues: Stack, FIFOQueue, PriorityQueue

class Queue:
    """Queue is an abstract class/interface. There are three types:
        Stack(): A Last In First Out Queue.
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(lt): Queue where items are sorted by lt, (default <).
    Each square_type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())
    Note that isinstance(Stack(), Queue) is false, because we implement stacks
    as lists.  If Python ever gets interfaces, Queue will be an interface."""

    def __init__(self):
        abstract()

    def extend(self, items):
        for item in items:
            self.append(item)


def Stack():
    """Return an empty list, suitable as a Last-In-First-Out Queue.
    Ex: q = Stack(); q.append(1); q.append(2); q.pop(), q.pop() ==> (2, 1)"""
    return []


class FIFOQueue(Queue):
    """A First-In-First-Out Queue.
    Ex: q = FIFOQueue();q.append(1);q.append(2); q.pop(), q.pop() ==> (1, 2)"""
    def __init__(self):
        Queue.__init__(self)
        self.A = []
        self.start = 0

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


class PriorityQueue(Queue):
    """A queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first. If order is min, the item with minimum f(x) is
    returned first; if order is max, then it is the item with maximum f(x)."""
    def __init__(self, order=min, f=lambda x: x):
        Queue.__init__(self)
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


# Additional tests

_docex = """
def is_even(x): return x % 2 == 0
sort([1, 2, -3]) ==> [-3, 1, 2]
sort(range(10), comparer(key=is_even)) ==> [1, 3, 5, 7, 9, 0, 2, 4, 6, 8]
sort(range(10), lambda x,y: y-x) ==> [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

remove_all(4, []) ==> []
remove_all('s', 'This is a test. Was a test.') ==> 'Thi i a tet. Wa a tet.'
remove_all('s', 'Something') ==> 'Something'
remove_all('s', '') ==> ''

reverse([]) ==> []
reverse('') ==> ''

count_if(is_even, [1, 2, 3, 4]) ==> 2
count_if(is_even, []) ==> 0

sum_seq([]) ==> 0

product([]) ==> 1

argmax([1], lambda x: x*x) ==> 1
argmin([1], lambda x: x*x) ==> 1
argmax([]) raises TypeError
argmin([]) raises TypeError


# Test of memoize with slots in structures
countries = [Struct(filename='united states'), Struct(filename='canada')]
# Pretend that 'gnp' was some big hairy operation:
def gnp(country): return len(country.filename) * 1e10
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
