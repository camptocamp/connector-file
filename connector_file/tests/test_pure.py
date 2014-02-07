"""This includes pure tests on the logic, not using the OpenERP framework."""
import unittest2
import contextlib
from cStringIO import StringIO
import textwrap

from ..model.document import split_data_in_chunks


class TestSplitDataInChunks(unittest2.TestCase):

    """Test class independent from OpenERP from the split file logic."""

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        return contextlib.closing(StringIO(textwrap.dedent(string)))

    def test_empty_iterator(self):
        """An empty iterator should create no chunks."""
        data = iter([])

        result = split_data_in_chunks(data)

        self.assertEquals(list(result), [])

    def test_empty_file(self):
        """An empty file should create no chunks."""

        input_file = self._prep_data("")

        result = split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_only_header(self):
        """It should return no chunks with only a header."""

        input_file = self._prep_data("""\
            header,of,any,kind
            """)

        result = split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])
