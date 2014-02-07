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
import simplejson as json

from openerp.osv import orm, fields

from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job

from ..exceptions import MoveLoadFailedJobError


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
    }

    def load_data(self):
        """TODO. This will load the chunk using load().

        Like load(), this returns a list of the ids of the created objects
        and a list of error messages

        """
        raise NotImplementedError


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

    def get_raw_button(self, cr, uid, ids, context=None):
        """Return the original raw data for this chunk from the file.

        This will use the line_start e line_stop to get the raw data
        for this chunk from the original file, without header.

        Note that line numbers are 1-based, while islice is 0-based.

        Return True

        """
        for chunk in self.browse(cr, uid, ids, context=context):
            chunk.attachment_binding_id.get_file_like()
            with chunk.attachment_binding_id.get_file_like() as file_like:
                myslice = itertools.islice(
                    file_like,
                    chunk.line_start - 1,
                    chunk.line_stop - 1
                )
                raw_chunk_io = cStringIO.StringIO()
                raw_chunk_io.writelines(myslice)
                chunk.write({
                    'raw_data': base64.encodestring(raw_chunk_io.getvalue())
                })
        return True

    def load_sync(self, cr, uid, ids, context=None):
        """Load the chunk, return true."""
        session = ConnectorSession(cr, uid, context=context)
        for chunk in self.browse(cr, uid, ids, context=context):
            backend_id = chunk.backend_id.id

            load_chunk(
                session,
                self._name,
                backend_id,
                chunk.id
            )

        return True

    def load_async(self, cr, uid, ids, context=None):
        """Load the chunk, return true."""
        session = ConnectorSession(cr, uid, context=context)
        for chunk in self.browse(cr, uid, ids, context=context):
            backend_id = chunk.backend_id.id

            load_chunk.delay(
                session,
                self._name,
                backend_id,
                chunk.id,
            )

        return True


@job
def load_chunk(s, model_name, backend_id, chunk_b_id):
    """Load a chunk into an OpenERP Journal Entry."""

    """
    I use some short variable names:
    _b is the binding.
    s is the session

    """

    move_obj = s.pool['account.move']
    chunk_b_obj = s.pool[model_name]
    chunk_b = chunk_b_obj.browse(s.cr, s.uid, chunk_b_id, context=s.context)
    prepared_header = json.loads(chunk_b.prepared_header)
    prepared_data = json.loads(chunk_b.prepared_data)
    load_result = move_obj.load(
        s.cr,
        s.uid,
        prepared_header,
        prepared_data,
        context=s.context,
    )

    assert not load_result['ids'] or len(load_result['ids']) <= 1, """
        One chunk should always generate one move, or an error.
        More than one should not happen.
    """

    if load_result['ids']:
        chunk_b.write({'move_id': load_result['ids'][0]}, context=s.context)
    else:
        raise MoveLoadFailedJobError(
            u'Error during load() of the account.move',
            load_result['messages']
        )
