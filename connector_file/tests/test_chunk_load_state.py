import base64
from mock import Mock

from openerp.tests import common
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import Environment

from .common import expand_path
from ..unit.move_load_policy import MoveLoadPolicy


class TestChunkLoadState(common.TransactionCase):

    def setUp(self):
        super(TestChunkLoadState, self).setUp()
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

        self.parsed_chunk = '[["1728274", "2014-02-02", "02\\\\/2014", "Sales Journal - (test)", "X11001", "Bank Wealthy and sons", "Camptocamp", "", "37.8", "", ""], ["", "", "", "", "X1111", "Bank Wealthy and sons", "Camptocamp", "AA009", "", "31.5", "taxcode1"], ["", "", "", "", "X2001", "Bank Wealthy and sons", "Camptocamp", "AA001", "", "3.83", "taxcode1"], ["", "", "", "", "X2110", "Bank Wealthy and sons", "Camptocamp", "AA001", "3.83", "", "taxcode1"], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "6.3", "taxcode2"], ["", "", "", "", "X1000", "Bank Wealthy and sons", "Camptocamp", "", "", "-0", "taxcode2"]]'  # noqa

        with open(expand_path('two_chunks.csv')) as input_file:
            file_content = input_file.read()

        self.document_id = self.session.create(
            'ir.attachment.binding', {
                'datas': base64.b64encode(file_content),
                'datas_fname': 'two_chunks.csv',
                'name': 'two_chunks.csv',
                'backend_id': self.backend_id,
            })

    def test_new_chunk_binding_state_pending(self):
        """A new chunk should have state pending."""
        chunk_id = self.session.create(
            'file.chunk.binding', {
                'prepared_data': self.parsed_chunk,
                'backend_id': self.backend_id,
                'attachment_binding_id': self.document_id,
            })

        chunk = self.session.browse(
            'file.chunk.binding',
            chunk_id)

        self.assertEquals(chunk.load_state, 'pending')
