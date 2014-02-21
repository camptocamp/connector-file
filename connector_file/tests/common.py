"""Helpers shared by all tests.

These could go in a generic class that inherits from the testcase. At the
moment my cases do not have a common ancestor (some are pure unittest2, some
use OpenERP facilities.)

"""

from os import path


def expand_path(filename):
    """Return the full path for a data file."""
    return path.abspath(
        path.join(
            path.dirname(__file__),
            'test_data',
            filename)
    )
