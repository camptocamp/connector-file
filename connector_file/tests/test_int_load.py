import base64
from mock import Mock

from openerp.tests import common
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import Environment

from .common import expand_path
from ..unit.move_load_policy import MoveLoadPolicy


class TestIntLoad(common.TransactionCase):

    """Integrated tests of the Load chunk. We hit the DB here."""

    def setUp(self):
        super(TestIntLoad, self).setUp()
        self.backend_record = Mock()
        self.session = ConnectorSession(self.cr, self.uid)
        self.model_name = 'ir.attachment.binding'
        self.backend_id = self.session.create(
            'file_import.backend',
            {
                'name': 'Test File Import',
                'ftp_host': 'localhost',
                'ftp_user': 'ftpuser',
                'ftp_password': 'ftppass',
                'ftp_input_folder': 'to_openerp',
                'ftp_failed_folder': 'from_openerp',
            })

        self.env = Environment(
            self.backend_record,
            self.session,
            self.model_name
        )

        self.policy = MoveLoadPolicy(self.env)

        self.parsed_header = '["ref", "date", "period_id", "journal_id", "line_id/account_id", "line_id/partner_id", "line_id/name", "line_id/analytic_account_id", "line_id/debit", "line_id/credit", "line_id/tax_code_id"]'  # noqa

        self.parsed_good_chunk = '[["1728274", "2014-02-02", "02/2014", "Sales Journal - (test)", "X11001", "Bank Wealthy and sons", "Camptocamp", "", "37.8", "", ""], ["", "", "", "", "X1111", "Bank Wealthy and sons", "Camptocamp", "AA009", "", "31.5", ""], ["", "", "", "", "X2001", "Bank Wealthy and sons", "Camptocamp", "AA001", "", "3.83", ""], ["", "", "", "", "X2110", "Bank Wealthy and sons", "Camptocamp", "AA001", "3.83", "", ""], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "6.3", ""], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "-0", ""]]'  # noqa

        self.parsed_chunk_missing_journal = '[["1728274", "2014-02-02", "02/2014", "Sales Journal - (test)", "X11001", "Bank Wealthy and sons", "Camptocamp", "", "37.8", "", ""], ["", "", "", "", "X1111", "Bank Wealthy and sons", "Camptocamp", "AA009", "", "31.5", ""], ["", "", "", "", "X2001", "Bank Wealthy and sons", "Camptocamp", "AA001", "", "3.83", ""], ["", "", "", "", "X2110", "Bank Wealthy and sons", "Camptocamp", "AA001", "3.83", "", ""], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "-6.3", ""], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "-0", ""]]'  # noqa

        with open(expand_path('two_chunks.csv')) as input_file:
            file_content = input_file.read()

        self.document_id = self.session.create(
            'ir.attachment.binding', {
                'datas': base64.b64encode(file_content),
                'datas_fname': 'two_chunks.csv',
                'name': 'two_chunks.csv',
                'backend_id': self.backend_id,
                'prepared_header': self.parsed_header,
            })

    def test_new_chunk_binding_state_pending(self):
        """A new chunk should have state pending."""
        chunk_id = self.session.create(
            'file.chunk.binding', {
                'prepared_data': self.parsed_good_chunk,
                'backend_id': self.backend_id,
                'attachment_binding_id': self.document_id,
            })

        chunk = self.session.browse(
            'file.chunk.binding',
            chunk_id)

        self.assertEquals(chunk.load_state, 'pending')

    def test_chunk_load_state_done(self):
        """Once loaded, a chunk should have state done."""
        chunk_id = self.session.create(
            'file.chunk.binding', {
                'prepared_data': self.parsed_good_chunk,
                'backend_id': self.backend_id,
                'attachment_binding_id': self.document_id,
            })

        chunk = self.session.browse(
            'file.chunk.binding',
            chunk_id)

        self.policy.load_one_chunk(chunk_id)

        self.assertEquals(chunk.load_state, 'done', msg=chunk.exc_info)

    def test_broken_chunk_state_failed(self):
        """If load fails, we should have load_state failed.

        Implicitly, the exception should pass (the job will be done).

        """

        chunk_id = self.session.create(
            'file.chunk.binding', {
                'prepared_data': self.parsed_chunk_missing_journal,
                'backend_id': self.backend_id,
                'attachment_binding_id': self.document_id,
            })

        chunk = self.session.browse(
            'file.chunk.binding',
            chunk_id)

        self.policy.load_one_chunk(chunk_id)

        self.assertEquals(chunk.load_state, 'failed')

        self.assertIn(u'Error during load', chunk.exc_info)
        self.assertIn(u'violates check constraint', chunk.exc_info)

    def test_one_chunk_creates_one_move(self):
        chunk_id = self.session.create(
            'file.chunk.binding', {
                'prepared_data': self.parsed_good_chunk,
                'backend_id': self.backend_id,
                'attachment_binding_id': self.document_id,
            })

        self.policy.load_one_chunk(chunk_id)

        move_ids = self.session.search('account.move', [
            ('ref', '=', '1728274')
        ])
        self.assertEquals(len(move_ids), 1)

    def test_load_one_chunk_twice_creates_one_move(self):
        chunk_id = self.session.create(
            'file.chunk.binding', {
                'prepared_data': self.parsed_good_chunk,
                'backend_id': self.backend_id,
                'attachment_binding_id': self.document_id,
            })

        self.policy.load_one_chunk(chunk_id)
        self.policy.load_one_chunk(chunk_id)

        move_ids = self.session.search('account.move', [
            ('ref', '=', '1728274')
        ])
        self.assertEquals(len(move_ids), 1)
