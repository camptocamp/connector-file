"""This includes pure tests on the logic, not using the OpenERP framework."""
import unittest2
import contextlib
from cStringIO import StringIO
import textwrap
import os
from mock import Mock

from ..unit.backend_adapter import ParsePolicy


class TestParsePolicy(unittest2.TestCase):

    """Parse Policy unit tests.

    These tests are independent from OpenERP, and very fast.

    """

    def _expand_path(self, filename):
        """Return the full path for a data file.

        The file is in the same directory as __name__.

        """
        return os.path.join(os.path.dirname(__file__), filename)

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        return contextlib.closing(StringIO(textwrap.dedent(string)))

    def setUp(self):
        """We do not need a real environment here."""
        super(TestParsePolicy, self).setUp()
        env = Mock()
        self.parse_policy = ParsePolicy(env)
        self.expected_parsed_header = '["ref", "date", "period_id", "journal_id", "line_id/account_id", "line_id/partner_id", "line_id/name", "line_id/analytic_account_id", "line_id/debit", "line_id/credit", "line_id/tax_code_id"]'  # noqa
        self.expected_parsed_chunk = '[["1728274", "2014-02-02", "02\\\\/2014", "Sales Journal - (test)", "X11001", "Bank", "Camptocamp", "", "37.8", "", ""], ["", "", "", "", "X1111", "Bank", "Camptocamp", "AA009", "", "31.5", "taxcode1"], ["", "", "", "", "X2001", "Bank", "Camptocamp", "AA001", "", "3.83", "taxcode1"], ["", "", "", "", "X2110", "Bank", "Camptocamp", "AA001", "3.83", "", "taxcode1"], ["", "", "", "", "X1000", "Bank", "Camptocamp", "", "", "6.3", "taxcode2"], ["", "", "", "", "X1000", "Bank", "Camptocamp", "", "", "-0", "taxcode2"]]'  # noqa
        self.expected_parsed_chunk_2 = '[["1728277", "2014-02-02", "02\\\\/2014", "Sales Journal - (test)", "X11001", "Bank", "OpenERP SA", "", "56.4", "", ""], ["", "", "", "", "X1111", "Bank", "OpenERP SA", "AA009", "", "43.17", "taxcode1"], ["", "", "", "", "X2001", "Bank", "OpenERP SA", "AA001", "", "3.83", "taxcode1"], ["", "", "", "", "X1000", "Bank", "OpenERP SA", "", "", "8.63", "taxcode2"], ["", "", "", "", "X1000", "Bank", "OpenERP SA", "", "", "0.77", "taxcode2"]]'  # noqa


class TestSplitDataInChunks(TestParsePolicy):

    """Test the split and parse of a file in chunks."""

    def test_empty_file(self):
        """An empty file should create no chunks."""

        input_file = self._prep_data("")

        result = self.parse_policy._split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_only_header(self):
        """It should return no chunks with only a header."""

        input_file = self._prep_data("""\
            header,of,any,kind
            """)

        result = self.parse_policy._split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_realistic_header(self):
        """It should return no chunks with a realistic header."""

        input_file = open(self._expand_path('header.csv'))
        result = self.parse_policy._split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_one_chunk(self):
        """It should return one chunk when given such a CSV."""

        input_file = open(self._expand_path('one_chunk.csv'))

        result = self.parse_policy._split_data_in_chunks(input_file)
        result_list = list(result)

        self.assertEquals(1, len(result_list))

        result_chunk = result_list[0]

        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_chunk.keys())

        self.assertEquals(2, result_chunk['line_start'])
        self.assertEquals(8, result_chunk['line_stop'])
        self.assertEquals(
            self.expected_parsed_chunk,
            result_chunk['prepared_data']
        )

    def test_two_chunks(self):
        """It should return two chunks when given such a CSV."""

        input_file = open(self._expand_path('two_chunks.csv'))

        result = self.parse_policy._split_data_in_chunks(input_file)
        result_list = list(result)

        self.assertEquals(2, len(result_list))

        # first chunk
        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_list[0].keys())

        self.assertEquals(2, result_list[0]['line_start'])
        self.assertEquals(8, result_list[0]['line_stop'])
        self.assertEquals(
            self.expected_parsed_chunk,
            result_list[0]['prepared_data']
        )

        # second chunk
        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_list[1].keys())

        self.assertEquals(8, result_list[1]['line_start'])
        self.assertEquals(13, result_list[1]['line_stop'])
        self.assertEquals(
            self.expected_parsed_chunk_2,
            result_list[1]['prepared_data']
        )


class TestParseHeaderData(TestParsePolicy):

    """Test _parse_header_data."""

    def test_empty_file(self):
        """An empty file should return an empty string."""

        input_file = self._prep_data("")

        result = self.parse_policy._parse_header_data(input_file)

        self.assertEquals('', result)

    def test_realistic_header(self):
        """It should return parse a realistic header."""

        input_file = open(self._expand_path('header.csv'))

        result = self.parse_policy._parse_header_data(input_file)

        self.assertEquals(result, self.expected_parsed_header)

    def test_one_chunk(self):
        """It should return the header when given one chunk."""

        input_file = open(self._expand_path('one_chunk.csv'))

        result = self.parse_policy._parse_header_data(input_file)

        self.assertEquals(result, self.expected_parsed_header)
