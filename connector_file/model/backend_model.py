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
from .document import AsyncFileParser
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
        'file_regexp': fields.char('File regexp', size=64),
        'user_id': fields.many2one('res.users', 'User'),
        'ftp_host': fields.char('FTP Host'),
        'ftp_user': fields.char('FTP User'),
        'ftp_password': fields.char('FTP Password'),
        'ftp_input_folder': fields.char('FTP Input folder'),
        'ftp_output_folder': fields.char('FTP Output folder'),
        'use_sftp': fields.boolean('Use SFTP'),
        'model_id': fields.many2one('ir.model', 'Model'),
    }

    _defaults = {
        'version': '1',
    }

    def get_all(self, cr, uid, ids, context=None):
        pass

    def parse_all_now(self, cr, uid, ids, context=None):
        pass
#        parser = #get unit FileParser
#        parser.parse_all()

    def parse_all_async(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        session = ConnectorSession(cr, uid, context=context)
        for backend_id in ids:
            env = get_environment(session, 'ir.attachment.binding', backend_id)
            parser = env.get_connector_unit(AsyncFileParser)
            parser.parse_all()
        return True

    def load_all_async(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        session = ConnectorSession(cr, uid, context=context)
        for backend_id in ids:
            env = get_environment(session, 'file.chunk.binding', backend_id)
            loader = env.get_connector_unit(AsyncChunkLoader)
            loader.load_all()
        return True
