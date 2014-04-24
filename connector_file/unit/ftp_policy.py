# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""FTP Policy."""

import ftputil
import os
import base64
import hashlib
import re
from psycopg2 import IntegrityError

from ..backend import file_import
from .policy import FileGetterPolicy
from ..exceptions import InvalidFileError


@file_import
class FTPFileGetterPolicy(FileGetterPolicy):

    """FTP File Getter Policy.

    Manages our interactions with a FTP server.

    """

    _model_name = 'ir.attachment.binding'

    def _get_host(self):
        pass

    @staticmethod
    def _ask_files(ftp_host, ftp_user, ftp_password, ftp_input_folder,
                   file_name_regexp):
        with ftputil.FTPHost(
            ftp_host,
            ftp_user,
            ftp_password,
        ) as host:
            file_list = host.listdir(ftp_input_folder)
            for file_name in file_list:
                if re.search(file_name_regexp, file_name):
                    basename, extension = os.path.splitext(file_name)
                    if extension == '.csv':
                        hash_file_name = basename + '.md5'
                        if hash_file_name in file_list:
                            yield (
                                os.path.join(ftp_input_folder, file_name),
                                os.path.join(ftp_input_folder, hash_file_name),
                            )

    def ask_files(self):
        """Return a generator of tuples (data_file_name, hash_file_name)."""
        return self._ask_files(
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend_record.ftp_password,
            self.backend_record.ftp_input_folder,
            self.backend_record.file_name_regexp)

    @staticmethod
    def _get_content(data_file_name, ftp_host, ftp_user, ftp_password,
                     ftp_input_folder):
        with ftputil.FTPHost(
            ftp_host,
            ftp_user,
            ftp_password,
        ) as host:
            return host.open(data_file_name).read()

    def get_content(self, data_file_name):
        """Return the raw content of the file."""
        return self._get_content(
            data_file_name,
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend_record.ftp_password,
            self.backend_record.ftp_input_folder)

    @staticmethod
    def _get_hash(hash_file_name, ftp_host, ftp_user, ftp_password,
                  ftp_input_folder):
        with ftputil.FTPHost(
            ftp_host,
            ftp_user,
            ftp_password,
        ) as host:
            with host.open(hash_file_name) as f:
                return f.read().rstrip('\r\n')

    def get_hash(self, hash_file_name):
        """Return the external hash of the file."""
        return self._get_hash(
            hash_file_name,
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend_record.ftp_password,
            self.backend_record.ftp_input_folder)

    @staticmethod
    def _compute_internal_hash(content):
        """Return a hex md5 hash, like md5sum from GNU coreutils does."""
        return hashlib.md5(content).hexdigest()

    def manage_exception(self, e, data_file_name, hash_file_name):
        """In case of trouble, try to move the file away."""
        if isinstance(e, InvalidFileError):
            self.move_one(
                data_file_name,
                self.backend_record.ftp_input_folder,
                self.backend_record.ftp_failed_folder,
            )
            self.move_one(
                hash_file_name,
                self.backend_record.ftp_input_folder,
                self.backend_record.ftp_failed_folder,
            )
        else:
            raise

    def create_one(self, data_file_name, hash_file_name, external_hash,
                   content):
        """Create one file in OpenERP.

        Return id of the created object.

        """
        self.session.cr.execute('SAVEPOINT create_attachment')
        initial_log_exceptions = self.session.cr._default_log_exceptions
        self.session.cr._default_log_exceptions = False
        internal_hash = self._compute_internal_hash(content)
        if internal_hash != external_hash:
            raise InvalidFileError(
                '''Hash check failed.
                internal hash:
                {0}

                external hash:
                {1}
                '''.format(internal_hash, external_hash)
            )
        try:
            created_id = self.session.create(self.model._name, {
                'name': data_file_name,
                'datas_fname': os.path.basename(data_file_name),
                'external_hash': external_hash,
                'internal_hash': internal_hash,
                'datas': base64.b64encode(content),
                'backend_id': self.backend_record.id,
            })
        except IntegrityError as e:
            if 'ir_attachment_binding_document_binding_uniq' in e.message:
                # we want our job to be idempotent: if the attachment cannot be
                # created because it already exists, we do nothing.
                # TODO: this actually is inefficient because we download the
                # whole file content and then decide not to create it.
                self.session.cr.execute(
                    'ROLLBACK TO SAVEPOINT create_attachment'
                )
                return None
            else:
                self.session.cr.execute('RELEASE SAVEPOINT create_attachment')
                raise
        finally:
            self.session.cr._default_log_exceptions = initial_log_exceptions

        if self.backend_record.ftp_archive_folder:
            self.move_one(
                data_file_name,
                self.backend_record.ftp_input_folder,
                self.backend_record.ftp_archive_folder,
            )
            self.move_one(
                hash_file_name,
                self.backend_record.ftp_input_folder,
                self.backend_record.ftp_archive_folder,
            )

        return created_id

    def move_one(self, file_name, folder_from, folder_to):
        """Move a file. Return whatever comes from the library."""
        return self._move_one(
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend_record.ftp_password,
            file_name,
            folder_from,
            folder_to)

    @staticmethod
    def _move_one(ftp_host, ftp_user, ftp_password,
                  file_name, folder_from, folder_to):
        with ftputil.FTPHost(
            ftp_host,
            ftp_user,
            ftp_password,
        ) as host:
            host.rename(
                os.path.join(folder_from, os.path.basename(file_name)),
                os.path.join(folder_to, os.path.basename(file_name)),
            )
