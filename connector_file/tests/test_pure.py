"""This includes pure tests on the logic, not using the OpenERP framework."""
import unittest2
import contextlib
from cStringIO import StringIO
import textwrap
from mock import Mock

from ..unit.backend_adapter import ParsePolicy


class TestSplitDataInChunks(unittest2.TestCase):

    """Test the split and parse of a file in chunks.

    This test uses purely values, is independent from OpenERP (i.e. no import
    openerp) and is very fast.

    """

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        # TODO factor out
        return contextlib.closing(StringIO(textwrap.dedent(string)))

    def setUp(self):
        """We do not need a real environment here."""
        # TODO factor out
        super(TestSplitDataInChunks, self).setUp()
        env = Mock()
        self.parse_policy = ParsePolicy(env)

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

        input_file = self._prep_data("""\
            ref;date;period_id;journal_id;"line_id/account_id";"line_id/partner_id";"line_id/name";"line_id/
            """)

        result = self.parse_policy._split_data_in_chunks(input_file)

        self.assertEquals(list(result), [])

    def test_one_chunk(self):
        """It should return one chunk when given such a CSV."""

        input_file = self._prep_data("""\
            ref;date;period_id;journal_id;"line_id/account_id";"line_id/partner_id";"line_id/name";"line_id/analytic_account_id";"line_id/debit";"line_id/credit";line_id/tax_code_id
            1728274;2014-02-02;"02\/2014";"Sales Journal - (test)";X11001;"Bank";"Camptocamp";;37.8;;
            ;;;;X1111;"Bank";"Camptocamp";AA009;;31.5;taxcode1
            ;;;;X2001;"Bank";"Camptocamp";AA001;;3.83;taxcode1
            ;;;;X2110;"Bank";"Camptocamp";AA001;3.83;;taxcode1
            ;;;;X1000;"Bank";"Camptocamp";;;6.3;taxcode2
            ;;;;X1000;"Bank";"Camptocamp";;;-0;taxcode2""")

        result = self.parse_policy._split_data_in_chunks(input_file)
        result_list = list(result)

        self.assertEquals(1, len(result_list))

        result_chunk = result_list[0]

        self.assertItemsEqual([
            'line_start', 'line_stop', 'prepared_data'
        ], result_chunk.keys())

        self.assertEquals(2, result_chunk['line_start'])
        self.assertEquals(8, result_chunk['line_stop'])
        self.assertEquals('[["1728274", "2014-02-02", "02\\\\/2014", "Sales Journal - (test)", "X11001", "Bank", "Camptocamp", "", "37.8", "", ""], ["", "", "", "", "X1111", "Bank", "Camptocamp", "AA009", "", "31.5", "taxcode1"], ["", "", "", "", "X2001", "Bank", "Camptocamp", "AA001", "", "3.83", "taxcode1"], ["", "", "", "", "X2110", "Bank", "Camptocamp", "AA001", "3.83", "", "taxcode1"], ["", "", "", "", "X1000", "Bank", "Camptocamp", "", "", "6.3", "taxcode2"], ["", "", "", "", "X1000", "Bank", "Camptocamp", "", "", "-0", "taxcode2"]]', result_chunk['prepared_data'])


class TestParseHeaderData(unittest2.TestCase):

    """Test _parse_header_data.

    These tests only use values and do not import openerp.

    """

    def setUp(self):
        """We do not need a real environment here."""
        super(TestParseHeaderData, self).setUp()
        env = Mock()
        self.parse_policy = ParsePolicy(env)

    def _prep_data(self, string):
        """Return a file-like object from the trimmed string."""
        # TODO factor out
        return contextlib.closing(StringIO(textwrap.dedent(string)))

    def test_empty_file(self):
        """An empty file should return an empty string."""

        input_file = self._prep_data("")

        result = self.parse_policy._parse_header_data(input_file)

        self.assertEquals('', result)

    def test_realistic_header(self):
        """It should return parse a realistic header."""

        input_file = self._prep_data("""\
            ref;date;period_id;journal_id;"line_id/account_id";"line_id/partner_id";"line_id/name";"line_id/
            """)

        result = self.parse_policy._parse_header_data(input_file)

        self.assertEquals(result, '["ref", "date", "period_id", "journal_id", "line_id/account_id", "line_id/partner_id", "line_id/name", "line_id/\\n"]')
