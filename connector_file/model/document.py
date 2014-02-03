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
"""File."""

from openerp.osv import orm, fields


class AttachmentBinding(orm.Model):

    """Binding for the attachment."""

    _name = 'ir.attachment.binding'
    _inherit = 'external.binding'

    _inherits = {'file.chunk': 'attachment_id'}

    _description = 'File Chunk Binding'

    _columns = {
        'openerp_id': fields.many2one(
            'file.chunk',
            string='OpenERP Attachment',
            required=True,
            ondelete='restrict'
        ),
        'backend_id': fields.many2one(
            'file_import.backend',
            'File Exchange Backend',
            required=True,
            ondelete='restrict'),
        'external_hash': fields.char('External Hash'),
    }

    _defaults = {
    }

    _sql_constraints = [
        (
            'document_binding_uniq',
            'unique(backend_id, external_hash)',
            'A file with the same hash already exist for this backend.'
        ),
    ]
