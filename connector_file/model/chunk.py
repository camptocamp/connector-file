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
"""Chunk of a file."""

import itertools
import cStringIO
import base64

from openerp.osv import orm, fields

from openerp.addons.connector.session import ConnectorSession

from ..connector import get_environment
from ..unit.chunk import ChunkLoader


class file_chunk(orm.Model):

    """File Chunk."""

    _name = 'file.chunk'

    _description = 'File Chunk'

    name_get = lambda self, cr, uid, ids, c: 'What shall we use as name_get?'

    _columns = {
        'line_start': fields.integer('Line Start', help="1-based"),
        'line_stop': fields.integer('Line Stop', help="1-based"),
        'prepared_data': fields.char('Prepared Data, JSON'),
        'raw_data': fields.binary('Raw data, press button to update'),
        'sync_date': fields.datetime('Last synchronization date'),
    }


class file_chunk_binding(orm.Model):

    """File Chunk Binding."""

    _name = 'file.chunk.binding'
    _inherit = 'external.binding'

    _inherits = {'file.chunk': 'openerp_id'}

    _description = 'File Chunk Binding'

    _columns = {
        'openerp_id': fields.many2one(
            'file.chunk',
            string='OpenERP Chunk',
            required=True,
            ondelete='restrict'
        ),
        'backend_id': fields.many2one(
            'file_import.backend',
            'File Exchange Backend',
            required=True,
            ondelete='restrict'),
        'attachment_binding_id': fields.many2one(
            'ir.attachment.binding',
            'File Binding',
            required=True,
            ondelete='restrict'),
        'move_id': fields.many2one(
            'account.move',
            'Journal Entry'),
        'prepared_header': fields.related(
            'attachment_binding_id',
            'prepared_header',
            type='char',
            string='Prepared Header (JSON)',
        ),
    }

    _defaults = {
    }

    _sql_constraints = [
    ]

    @staticmethod
    def _get_raw_data(file_like, line_start, line_stop):
        """Return raw data from the file_like, from line_start to line_stop.

        Note that line numbers are 1-based, while islice is 0-based.

        """

        myslice = itertools.islice(
            file_like,
            line_start - 1,
            line_stop - 1
        )
        raw_chunk_io = cStringIO.StringIO()
        raw_chunk_io.writelines(myslice)
        return raw_chunk_io.getvalue()

    def get_raw_button(self, cr, uid, ids, context=None):
        """Extract the original raw data for this chunk from the file.

        This will use the line_start e line_stop to get the raw data
        for this chunk from the original file, without header.

        Return True

        """
        for chunk in self.browse(cr, uid, ids, context=context):
            with chunk.attachment_binding_id.get_file_like() as file_like:
                chunk.write({
                    'raw_data': base64.encodestring(self._get_raw_data(
                        file_like,
                        chunk.line_start,
                        chunk.line_stop,
                    ))
                })
        return True

    def load_now_button(self, cr, uid, ids, context=None):
        """Load the chunk, return true."""
        session = ConnectorSession(cr, uid, context=context)

        for chunk_b in self.browse(cr, uid, ids, context=context):
            env = get_environment(session, self._name, chunk_b.backend_id.id)
            parser = env.get_connector_unit(ChunkLoader)
            parser.load_one_chunk(chunk_b.id)

        return True
