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

import ftputil
import os
import base64

from ..backend import file_import
from .policy import FileGetterPolicy


@file_import
class FTPFileGetterPolicy(FileGetterPolicy):

    _model_name = 'ir.attachment.binding'

    def _get_host(self):
        pass

    @staticmethod
    def _ask_files(ftp_host, ftp_user, ftp_password, ftp_input_folder):
        with ftputil.FTPHost(
            ftp_host,
            ftp_user,
            ftp_password,
        ) as host:
            file_list = host.listdir(ftp_input_folder)
            for file_name in file_list:
                if file_name[-4:] == '.csv':
                    hash_file_name = file_name[:-4] + '.md5'
                    if hash_file_name in file_list:
                        yield (
                            os.path.join(ftp_input_folder, file_name),
                            os.path.join(ftp_input_folder, hash_file_name),
                        )

    def ask_files(self):
        """Yield tuples (data_file_name, hash_file_name)."""

        return self._ask_files(
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend_record.ftp_password,
            self.backend_record.ftp_input_folder)

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
                return f.read()

    def get_hash(self, hash_file_name):
        return self._get_hash(
            hash_file_name,
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend_record.ftp_password,
            self.backend_record.ftp_input_folder)

    def create_one(self, file_name, hash_string, content):
        return self.session.create(self.model._name, {
            'name': file_name,
            'datas_fname': os.path.basename(file_name),
            'external_hash': hash_string,
            'datas': base64.b64encode(content),
            'backend_id': self.backend_record.id,
        })
