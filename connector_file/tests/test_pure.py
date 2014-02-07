"""This includes pure tests on the logic, not using the OpenERP framework."""
import unittest2

from ..model.document import split_data_in_chunks


class TestSplitDataInChunks(unittest2.TestCase):

    """Test class independent from OpenERP from the split file logic."""

    def test_empty_iterator(self):
        """An empty file should create no chunks."""
        data = iter([])

        result = split_data_in_chunks(data)

        self.assertEquals(list(result), [])
