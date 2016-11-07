import os


def nearest_file(filename=None, root=None):
    """Return the closest filename match, ascending.

    `root` is the top-level directory to terminate the search. If not
    given, it defaults to $HOME.

    :param str filename: Filename to look for.
    :return: Absolute filepath or None.
    """
    if root is None:  # Default stop: Home directory
        root = os.path.expanduser('~')

    cwd = os.getcwd()
    if root not in cwd:
        raise os.PathError(
            "{} lives outside {}".format(cwd, root))

    curr = cwd
    while root != curr:
        f = os.path.join(curr, filename)
        if os.path.isfile(f):
            return f
        # Check the parent directory
        curr = os.path.dirname(curr)
    return None
