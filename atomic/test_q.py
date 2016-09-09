import random
import string

from q import q
from q.todo import Todo


def rand_select(items, seed=None):
    """Randomly select a subset of items as (item, pos) tuples.

    Builds a random bit mask of length equivalent to the number of items, and
    returns items whose position is 1 in the mask.

    Note: This does *not* return the items in a random order. This can be
    accomplished by running the output through ``random.shuffle``.
    """
    rand = random.Random(seed)
    n = len(items)
    r = rand.getrandbits(n)
    for i in range(n):
        if r & 0b1:
            yield i, items[i]
        r >>= 1


def alpha_q(seed=None):
    """Create mock Todo data using alphabet.

    Returns a list of unique alphabetical characters.
    """
    alphabits = rand_select(string.ascii_lowercase, seed)
    # Drop the indices
    return list(zip(*alphabits))[1]


class TestQ(q.Q):

    def __init__(self):
        super().__init__(alpha_q(), filename='test_q.json')


def test_Q_json():
    kuew = q.Q(filename='test_q_init.json')
    kuew2 = q.Q.from_json(kuew.to_json())
    assert kuew.graph == kuew2.graph


def test_Q_add():
    kuew = q.Q()
    kuew.add(Todo('Nothing much'))
    assert 1 in kuew.graph.node
    td = kuew.get(1)
    assert td is not None
    assert td.uid == 1
    assert td.name == 'Nothing much'


def test_Q_add_ordering():
    kuew = q.Q()
    kuew.add(Todo('Middling importance'))
    kuew.add(Todo('not important'))
    kuew.add(Todo('Very important'), priority=0)
    # Compare iteration order by UIDs
    uids = [td.uid for td in kuew]
    assert uids == [3, 1, 2], "Iteration order is out of whack"


def test_ordering():
    """Test nodes are sorted by their edges' 'order=' parameter."""
    root_todo = Todo('root')
    alphabits = [
        (root_todo, Todo('a'), {"order": 1}),
        (root_todo, Todo('c'), {"order": 5}),
        (root_todo, Todo('f', done=True), {"order": 4}),
        (root_todo, Todo('m'), {"order": 3}),
        (root_todo, Todo('z'), {"order": 2}),
    ]
    kuew = q.Q(items=alphabits)
    prev = ''
    seen = 0
    for td in kuew:
        assert prev < td.name
        prev = td.name
        seen += 1
    assert seen == 4, "Failed to skip 'done' Todo"
