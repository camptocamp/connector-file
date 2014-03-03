import base64
from mock import Mock

from openerp.tests import common
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import Environment

from .common import expand_path
from ..unit.csv_policy import CSVParsePolicy


class TestDocumentParseState(common.TransactionCase):

    def setUp(self):
        super(TestDocumentParseState, self).setUp()
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

        self.policy = CSVParsePolicy(self.env)

    def test_new_attachment_binding_state_pending(self):
        """A new file should have state pending."""
        with open(expand_path('two_chunks.csv')) as input_file:
            file_content = input_file.read()

        document_id = self.session.create(
            'ir.attachment.binding', {
                'datas': base64.b64encode(file_content),
                'datas_fname': 'two_chunks.csv',
                'name': 'two_chunks.csv',
                'backend_id': self.backend_id,
            })

        document = self.session.browse(
            'ir.attachment.binding',
            document_id)

        self.assertEquals(document.parse_state, 'pending')

    def test_parse_one_state_done(self):
        """If a file is parsed, the state of the file should be 'done'."""

        with open(expand_path('two_chunks.csv')) as input_file:
            file_content = input_file.read()

        document_id = self.session.create(
            'ir.attachment.binding', {
                'datas': base64.b64encode(file_content),
                'datas_fname': 'two_chunks.csv',
                'name': 'two_chunks.csv',
                'backend_id': self.backend_id,
            })

        document = self.session.browse(
            'ir.attachment.binding',
            document_id)
        self.policy.parse_one(document_id)

        self.assertEquals(document.parse_state, 'done')
