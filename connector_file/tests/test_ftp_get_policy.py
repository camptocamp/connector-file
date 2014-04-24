"""FTP tests.

These tests rely on a local FTP server containing the correct files.
I should eventually mock that out.

"""

import unittest2
from mock import Mock
import base64
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.connector import Environment
from openerp.tests import common
from ..unit.ftp_policy import FTPFileGetterPolicy
from ..unit.document import create_one_file
from .common import expand_path


class TestFTPGetPolicyWithoutOE(unittest2.TestCase):

    """Unit Tests for the FTP Get Policy that do not use OpenERP."""

    def test__ask_files(self):
        actual_file_generator = FTPFileGetterPolicy._ask_files(
            'localhost',
            'ftpuser',
            'ftppass',
            'to_openerp',
            '',
        )
        self.assertEquals(
            actual_file_generator.next(),
            ('to_openerp/s1.csv', 'to_openerp/s1.md5'))

        with self.assertRaises(StopIteration):
            actual_file_generator.next()

    def test__get_hash(self):
        actual_hash_string = FTPFileGetterPolicy._get_hash(
            'to_openerp/s1.md5',
            'localhost',
            'ftpuser',
            'ftppass',
            'to_openerp',
        )
        self.assertEquals(
            actual_hash_string,
            '4033316ec0c9dd8692972457944aafd9'
        )

    def test__get_content(self):
        actual_content = FTPFileGetterPolicy._get_content(
            'to_openerp/s1.csv',
            'localhost',
            'ftpuser',
            'ftppass',
            'to_openerp',
        )
        with open(expand_path('two_chunks.csv')) as expected_file_like:
            self.assertEquals(
                actual_content,
                expected_file_like.read()
            )


class TestFTPGetPolicyWithOE(common.TransactionCase):

    """Integrated Tests for the FTP Get Policy that do use OpenERP."""

    def setUp(self):
        super(TestFTPGetPolicyWithOE, self).setUp()
        self.backend_record = Mock()
        self.session = ConnectorSession(self.cr, self.uid)
        self.model_name = 'ir.attachment.binding'
        self.backend_model = self.registry('file_import.backend')
        self.backend_id = self.backend_model.create(
            self.cr,
            self.uid,
            {
                'name': 'Test File Import',
                'ftp_host': 'localhost',
                'ftp_user': 'ftpuser',
                'ftp_password': 'ftppass',
                'ftp_input_folder': 'to_openerp',
                'ftp_failed_folder': 'from_openerp',
            },
            self.session.context)
        self.env = Environment(
            self.backend_record,
            self.session,
            self.model_name
        )
        self.policy = FTPFileGetterPolicy(self.env)

    def test_create_one_file(self):
        actual_attachment_b_id = create_one_file(
            self.session,
            self.model_name,
            self.backend_id,
            'to_openerp/s1.csv',
            'to_openerp/s1.md5')

        actual_attachment_b_browse = self.session.browse(
            self.model_name,
            actual_attachment_b_id)
        self.assertEquals(actual_attachment_b_browse.datas_fname, 's1.csv')

        with open(expand_path('two_chunks.csv')) as expected_file_like:
            self.assertEquals(
                base64.b64decode(actual_attachment_b_browse.datas),
                expected_file_like.read()
            )

    def test_create_file_uniq(self):
        """Test idempotency of file creation.

        We check that if the job to create a file is executed many times,
        just one file is created, without raising exceptions.

        """

        actual_attachment_b_id = create_one_file(
            self.session,
            self.model_name,
            self.backend_id,
            'to_openerp/s1.csv',
            'to_openerp/s1.md5')

        actual_attachment_b_id_second_time = create_one_file(
            self.session,
            self.model_name,
            self.backend_id,
            'to_openerp/s1.csv',
            'to_openerp/s1.md5')

        self.assertIsInstance(actual_attachment_b_id, (int, long))
        self.assertIs(actual_attachment_b_id_second_time, None)
