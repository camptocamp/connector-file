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
"""Backend Model."""

from openerp.osv import orm, fields

from openerp.addons.connector.session import ConnectorSession

from ..connector import get_environment
from ..unit.document import AsyncFileSynchronizer
from ..unit.document import AsyncFileParser
from ..unit.chunk import AsyncChunkLoader


class file_import_backend(orm.Model):

    """File Import Backend."""

    _name = "file_import.backend"
    _description = 'File Import Backend'
    _inherit = "connector.backend"
    _backend_type = "file_import"

    def _select_versions(self, cr, uid, context=None):
        """Return available versions. Can be inherited to add custom ones."""
        return [('1', '1')]

    _columns = {
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'file_name_regexp': fields.char('File Name regexp', size=64),
        'user_id': fields.many2one('res.users', 'User'),
        'ftp_host': fields.char('FTP Host'),
        'ftp_port': fields.char('FTP Port (not implemented)'),
        'ftp_user': fields.char('FTP User'),
        'ftp_password': fields.char('FTP Password'),
        'ftp_input_folder': fields.char('FTP Input folder'),
        'ftp_failed_folder': fields.char('FTP Output folder'),
        'use_sftp': fields.boolean('Use SFTP (not implemented)'),
        'model_id': fields.many2one('ir.model', 'Model'),
    }

    _defaults = {
        'version': '1',
    }

    def get_all_async(self, cr, uid, ids, context=None):
        """Anynchronously get all files from the remote repository.

        This method is called by a button on the interface, or by a cron job.
        Return True action.

        """

        if context is None:
            context = {}

        for backend in self.browse(cr, uid, ids, context=context):
            # all the work is done by the user configured in the backend
            session = ConnectorSession(cr, backend.user_id.id, context=context)
            env = get_environment(session, 'ir.attachment.binding', backend.id)
            getr = env.get_connector_unit(AsyncFileSynchronizer)
            getr.get_all()
        return True

    def parse_all_async(self, cr, uid, ids, context=None):
        """Anynchronously parse all attachments into chunks.

        This method is called by a button on the interface, or by a cron job.
        Return True action.

        """
        if context is None:
            context = {}

        for backend in self.browse(cr, uid, ids, context=context):
            # all the work is done by the user configured in the backend
            session = ConnectorSession(cr, backend.user_id.id, context=context)
            env = get_environment(session, 'ir.attachment.binding', backend.id)
            parser = env.get_connector_unit(AsyncFileParser)
            parser.parse_all()
        return True

    def load_all_async(self, cr, uid, ids, context=None):
        """Anynchronously load all chunks in OpenERP.

        This method is called by a button on the interface, or by a cron job.
        Return True action.

        """
        if context is None:
            context = {}

        for backend in self.browse(cr, uid, ids, context=context):
            # all the work is done by the user configured in the backend
            session = ConnectorSession(cr, backend.user_id.id, context=context)
            env = get_environment(session, 'file.chunk.binding', backend.id)
            loader = env.get_connector_unit(AsyncChunkLoader)
            loader.load_all()
        return True
