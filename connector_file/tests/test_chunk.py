"""Tests for the Chunk and Chunk Binding objects."""
import unittest2
import contextlib
from cStringIO import StringIO
import textwrap

from .common import expand_path
from ..model.chunk import file_chunk_binding


class TestGetRawData(unittest2.TestCase):

    """Get Raw Data unit tests.

    These tests are independent from OpenERP, and very fast.

    """

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        return contextlib.closing(StringIO(textwrap.dedent(string)))

    def test__get_raw_data(self):
        input_file = open(expand_path('two_chunks.csv'))

        actual_raw = file_chunk_binding._get_raw_data(input_file, 8, 13)

        self.assertEquals(
            actual_raw,
            """\
1728277;2014-02-02;"02\/2014";"Sales Journal - (test)";X11001;\
"Bank Wealthy and sons";"OpenERP SA";;56.4;;
;;;;X1111;"Bank Wealthy and sons";"OpenERP SA";AA009;;43.17;taxcode1
;;;;X2001;"Bank Wealthy and sons";"OpenERP SA";AA001;;3.83;taxcode1
;;;;X1000;"Bank Wealthy and sons";"OpenERP SA";;;8.63;taxcode2
;;;;X1000;"Bank Wealthy and sons";"OpenERP SA";;;0.77;taxcode2
""")
