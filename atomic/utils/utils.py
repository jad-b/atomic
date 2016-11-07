import random
import string


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


def unique_alphabet(seed=None):
    """Returns a list of unique alphabetical characters."""
    alphabits = rand_select(string.ascii_lowercase, seed)
    # Drop the indices
    return list(zip(*alphabits))[1]
