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

from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

import ftputil

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
                        yield (file_name, hash_file_name)

    def ask_files(self):
        """Yield tuples (data_file_name, hash_file_name)."""

        return self._ask_files(
            self.backend_record.ftp_host,
            self.backend_record.ftp_user,
            self.backend.record.ftp_password,
            self.backend.record.ftp_input_folder)

    def parse_one(self, attachment_b_id):
        """Parse the attachment and split it into chunks."""
        s = self.session
        chunk_b_obj = s.pool['file.chunk.binding']
        attachment_b = s.browse(self.model._name, attachment_b_id)
        backend_id = attachment_b.backend_id.id

        file_like = self.model.get_file_like(
            s.cr,
            s.uid,
            [attachment_b_id],
            context=s.context
        )

        self.model.write(s.cr, s.uid, attachment_b_id, {
            'prepared_header': self._parse_header_data(file_like),
            'sync_date': datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT
            )
        })

        file_like_2 = self.model.get_file_like(
            s.cr,
            s.uid,
            [attachment_b_id],
            context=s.context
        )

        for chunk_data in self._split_data_in_chunks(file_like_2):

            chunk_data.update({
                'attachment_binding_id': attachment_b_id,
                'backend_id': backend_id,
            })

            chunk_b_obj.create(s.cr, s.uid, chunk_data, context=s.context)
