"""This includes pure tests on the logic, not using the OpenERP framework."""
import unittest2
import contextlib
from cStringIO import StringIO
import textwrap
from os import path

from ..unit.csv_policy import CSVParsePolicy


class TestCSVParsePolicy(unittest2.TestCase):

    """Parse Policy unit tests.

    These tests are independent from OpenERP, and very fast.

    """

    def _expand_path(self, filename):
        """Return the full path for a data file."""
        return path.abspath(
            path.join(
                path.dirname(__file__),
                'test_data',
                filename)
        )

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        return contextlib.closing(StringIO(textwrap.dedent(string)))

    def setUp(self):
        """We do not need a real environment here."""
        super(TestCSVParsePolicy, self).setUp()
        self.expected_parsed_header = '["ref", "date", "period_id", "journal_id", "line_id/account_id", "line_id/partner_id", "line_id/name", "line_id/analytic_account_id", "line_id/debit", "line_id/credit", "line_id/tax_code_id"]'  # noqa
        self.expected_parsed_chunk = '[["1728274", "2014-02-02", "02\\\\/2014", "Sales Journal - (test)", "X11001", "Bank Wealthy and sons", "Camptocamp", "", "37.8", "", ""], ["", "", "", "", "X1111", "Bank Wealthy and sons", "Camptocamp", "AA009", "", "31.5", "taxcode1"], ["", "", "", "", "X2001", "Bank Wealthy and sons", "Camptocamp", "AA001", "", "3.83", "taxcode1"], ["", "", "", "", "X2110", "Bank Wealthy and sons", "Camptocamp", "AA001", "3.83", "", "taxcode1"], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "6.3", "taxcode2"], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "-0", "taxcode2"]]'  # noqa
        self.expected_parsed_chunk_2 = '[["1728277", "2014-02-02", "02\\\\/2014", "Sales Journal - (test)", "X11001", "Bank Wealthy and sons", "OpenERP SA", "", "56.4", "", ""], ["", "", "", "", "X1111", "Bank Wealthy and sons", "OpenERP SA", "AA009", "", "43.17", "taxcode1"], ["", "", "", "", "X2001", "Bank Wealthy and sons", "OpenERP SA", "AA001", "", "3.83", "taxcode1"], ["", "", "", "", "X1000", "Bank Wealthy and sons", "OpenERP SA", "", "", "8.63", "taxcode2"], ["", "", "", "", "X1000", "Bank Wealthy and sons", "OpenERP SA", "", "", "0.77", "taxcode2"]]'  # noqa


class TestSplitDataInChunks(TestCSVParsePolicy):

    """Test the split and parse of a file in chunks."""

    def test_empty_file(self):
        """An empty file should create no chunks."""

        input_file = self._prep_data("")

        result = CSVParsePolicy._split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_only_header(self):
        """It should return no chunks with only a header."""

        input_file = self._prep_data("""\
            header,of,any,kind
            """)

        result = CSVParsePolicy._split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_realistic_header(self):
        """It should return no chunks with a realistic header."""

        input_file = open(self._expand_path('header.csv'))
        result = CSVParsePolicy._split_data_in_chunks(input_file)

        with self.assertRaises(StopIteration):
            result.next()

    def test_one_chunk(self):
        """It should return one chunk when given such a CSV."""

        input_file = open(self._expand_path('one_chunk.csv'))

        result = CSVParsePolicy._split_data_in_chunks(input_file)

        result_chunk = result.next()

        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_chunk.keys())

        self.assertEquals(2, result_chunk['line_start'])
        self.assertEquals(8, result_chunk['line_stop'])
        self.assertEquals(
            self.expected_parsed_chunk,
            result_chunk['prepared_data']
        )

        with self.assertRaises(StopIteration):
            result.next()

    def test_two_chunks(self):
        """It should return two chunks when given such a CSV."""

        input_file = open(self._expand_path('two_chunks.csv'))

        result = CSVParsePolicy._split_data_in_chunks(input_file)

        result_chunk = result.next()

        # first chunk
        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_chunk.keys())

        self.assertEquals(2, result_chunk['line_start'])
        self.assertEquals(8, result_chunk['line_stop'])
        self.assertEquals(
            self.expected_parsed_chunk,
            result_chunk['prepared_data']
        )

        result_chunk = result.next()

        # second chunk
        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_chunk.keys())

        self.assertEquals(8, result_chunk['line_start'])
        self.assertEquals(13, result_chunk['line_stop'])
        self.assertEquals(
            self.expected_parsed_chunk_2,
            result_chunk['prepared_data']
        )

        with self.assertRaises(StopIteration):
            result.next()


class TestParseHeaderData(TestCSVParsePolicy):

    """Test _parse_header_data."""

    def test_empty_file(self):
        """An empty file should return an empty string."""

        input_file = self._prep_data("")

        result = CSVParsePolicy._parse_header_data(input_file)

        self.assertEquals('', result)

    def test_realistic_header(self):
        """It should return parse a realistic header."""

        input_file = open(self._expand_path('header.csv'))

        result = CSVParsePolicy._parse_header_data(input_file)

        self.assertEquals(result, self.expected_parsed_header)

    def test_one_chunk(self):
        """It should return the header when given one chunk."""

        input_file = open(self._expand_path('one_chunk.csv'))

        result = CSVParsePolicy._parse_header_data(input_file)

        self.assertEquals(result, self.expected_parsed_header)

    def test_two_chunks(self):
        """It should return the header when given two chunks."""

        input_file = open(self._expand_path('two_chunks.csv'))

        result = CSVParsePolicy._parse_header_data(input_file)

        self.assertEquals(result, self.expected_parsed_header)
