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
"""Binding for file, aka attachment, aka document."""

from openerp.osv import orm, fields

from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job

from .connector import get_environment

from ..unit.backend_adapter import ParsePolicy


class AttachmentBinding(orm.Model):

    """Binding for the attachment."""

    _name = 'ir.attachment.binding'
    _inherit = 'external.binding'

    _inherits = {'ir.attachment': 'openerp_id'}

    _description = 'File Attachment Binding'

    _columns = {
        'openerp_id': fields.many2one(
            'ir.attachment',
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
        'chunk_binding_ids': fields.one2many(
            'file.chunk.binding',
            'attachment_binding_id',
            'Chunk Bindings',
        ),
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

    def parse(self, cr, uid, ids, context=None):
        """Split in chunks, return true."""
        session = ConnectorSession(cr, uid, context=context)
        for attachment in self.browse(cr, uid, ids, context=context):
            backend_id = attachment.backend_id.id

            parse_attachment.delay(
                session,
                'ir.attachment.binding',
                backend_id,
                attachment.id,
            )
        return True


@job
def parse_attachment(session, model_name, backend_id,
                     attachment_binding_id):
    """ Prepare a batch import of records from Magento """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(ParsePolicy)
    importer.run(attachment_binding_id)
