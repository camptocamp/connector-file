from os import path


def expand_path(filename):
    """Return the full path for a data file."""
    return path.abspath(
        path.join(
            path.dirname(__file__),
            'test_data',
            filename)
    )
