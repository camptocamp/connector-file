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
        'single_file_name': fields.char('Single File Name', size=64),
        'user_id': fields.many2one('res.users', 'User'),
    }

    _defaults = {
        'version': '1',
    }

    def import_one_file(self, cr, uid, ids, context=None):
        """Imports a single file specified in the backend."""
        session = ConnectorSession(cr, uid, context=context)
        import pdb;pdb.set_trace()
#        for current in self.browse(cr, uid, ids, context=context):
#            direct_sync_users(session, current.id)
        return ids
