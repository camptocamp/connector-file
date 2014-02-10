"""Tests for the Chunk and Chunk Binding objects."""
import unittest2
import contextlib
from cStringIO import StringIO
import textwrap


class TestGetRawData(unittest2.TestCase):

    """Get Raw Data unit tests.

    These tests are independent from OpenERP, and very fast.

    """

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        return contextlib.closing(StringIO(textwrap.dedent(string)))
