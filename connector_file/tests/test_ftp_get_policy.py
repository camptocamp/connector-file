"""FTP tests.

These tests rely on a local FTP server containing the correct files.
I should eventually mock that out.

"""

import unittest2
from mock import Mock

from openerp.addons.connector.connector import Environment
from ..unit.ftp_policy import FTPFileGetterPolicy
from .common import expand_path


class TestFTPGetPolicyWithoutOE(unittest2.TestCase):
    """Unit Tests for the FTP Get Policy that do not use OpenERP."""

    def test__ask_files(self):
        actual_file_generator = FTPFileGetterPolicy._ask_files(
            'localhost',
            'ftpuser',
            'ftppass',
            'to_openerp',
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
            '6f7fff2b3f9762a99688bfab52f06bac'
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


class TestFTPGetPolicyWithOE(unittest2.TestCase):
    """Unit Tests for the FTP Get Policy that do use OpenERP."""

    def setUp(self):
        super(TestFTPGetPolicyWithOE, self).setUp()
        self.backend_record = Mock()
        self.session = Mock()
        self.model_name = 'ir.attachment.binding'

        self.env = Environment(
            self.backend_record,
            self.session,
            self.model_name
        )
        self.policy = FTPFileGetterPolicy(self.env)
