import base64
from mock import Mock

from openerp.tests import common
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import Environment

from .common import expand_path
from ..unit.csv_policy import CSVParsePolicy


class TestIntCSVParse(common.TransactionCase):

    """Test that parsing a file creates unique chunks in the database."""

    def setUp(self):
        super(TestIntCSVParse, self).setUp()
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

        with open(expand_path('two_chunks.csv')) as input_file:
            file_content = input_file.read()

        self.document_id = self.session.create(
            'ir.attachment.binding', {
                'datas': base64.b64encode(file_content),
                'datas_fname': 'two_chunks.csv',
                'name': 'two_chunks.csv',
                'backend_id': self.backend_id,
            })

        self.document = self.session.browse(
            'ir.attachment.binding',
            self.document_id)

    def test_parse_document_create_chunks(self):
        """Parsing a file should create 2 chunks in the database."""

        self.policy.parse_one(self.document_id)
        chunk_ids = self.session.search('file.chunk.binding', [
            ('attachment_binding_id', '=', self.document_id)
        ])
        self.assertEquals(len(chunk_ids), 2)
