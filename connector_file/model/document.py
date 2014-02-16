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

import cStringIO
import contextlib

from openerp.osv import orm, fields

from openerp.addons.connector.session import ConnectorSession

from ..connector import get_environment
from ..unit.document import DirectFileParser


class ir_attachment(orm.Model):

    """Attachment."""

    _inherit = 'ir.attachment'

    _columns = {
        'binding_ids': fields.one2many(
            'ir.attachment.binding',
            'openerp_id'
        ),
    }


class attachment_binding(orm.Model):

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
        'prepared_header': fields.char('Prepared Header, JSON'),
        'chunk_binding_ids': fields.one2many(
            'file.chunk.binding',
            'attachment_binding_id',
            'Chunk Bindings',
        ),
        'sync_date': fields.datetime('Last synchronization date'),
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

    def parse_now_button(self, cr, uid, ids, context=None):
        """Load the chunk, return true."""
        session = ConnectorSession(cr, uid, context=context)

        for attachment_binding in self.browse(cr, uid, ids, context=context):
            env = get_environment(
                session,
                self._name,
                attachment_binding.backend_id.id)
            parser = env.get_connector_unit(DirectFileParser)
            parser.parse_one_file(attachment_binding.id)

    # def parse_async(self, cr, uid, ids, context=None):
    #     """Split in chunks, return true."""
    #     session = ConnectorSession(cr, uid, context=context)
    #     for attachment in self.browse(cr, uid, ids, context=context):
    #         parse_attachment.delay(
    #             session,
    #             self._name,
    #             attachment.id,
    #         )
    #     return True

    def get_file_like(self, cr, uid, ids, context=None):
        """Return an open file-like object with the attachment content.

        That can be implemented as a stringIO or as a real file.

        ids is a list of one element, and not an integer: that way we can call
        this method with no parameters from a browse_record object.

        """
        assert len(ids) == 1, 'ids should be a list of one element'
        if context is None:
            context = {}
        attachment = self.browse(cr, uid, ids[0], context=context)

        # this is weird, but correct: attachment.datas is base64 data
        # represented by an unicode object.
        # python 2 does encode('ascii') automatically but I prefer to
        # make that more explicit.
        file_like = cStringIO.StringIO(
            attachment.datas.encode('ascii').decode('base64')
        )

        # in py2, a StringIO cannot be used in a 'with' context manager
        # contextlib.closing is there just for that
        return contextlib.closing(file_like)
