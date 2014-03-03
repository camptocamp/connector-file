import base64

from openerp.tests import common
from openerp.addons.connector.session import ConnectorSession

from .common import expand_path

# create a attachmend.binding that gives a parse error

# FileParser.parse_one_file()

# no exception raised

# document binding should have state and message.


class TestFileParserError(common.TransactionCase):

    def setUp(self):
        super(TestFileParserError, self).setUp()
        self.session = ConnectorSession(self.cr, self.uid)

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

    def test_new_binding_state_pending(self):
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
