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
import csv
import simplejson

from openerp.osv import orm, fields

from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job

# from ..connector import get_environment

# from ..unit.backend_adapter import ParsePolicy


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
        'prepared_header': fields.char('Prepared Header, JSON'),
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

    def parse_sync(self, cr, uid, ids, context=None):
        """Split in chunks, return true."""
        session = ConnectorSession(cr, uid, context=context)
        for attachment in self.browse(cr, uid, ids, context=context):
            backend_id = attachment.backend_id.id
            parse_attachment(
                session,
                self._name,
                backend_id,
                attachment.id
            )

        return True

    def parse_async(self, cr, uid, ids, context=None):
        """Split in chunks, return true."""
        session = ConnectorSession(cr, uid, context=context)
        for attachment in self.browse(cr, uid, ids, context=context):
            backend_id = attachment.backend_id.id

            parse_attachment.delay(
                session,
                self._name,
                backend_id,
                attachment.id,
            )
        return True

    def get_file_like(self, cr, uid, attachment_id, context=None):
        """Return an open file-like object with the attachment content.

        That can be implemented as a stringIO or as a real file.

        """
        if context is None:
            context = {}
        attachment = self.browse(cr, uid, attachment_id, context=context)

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


@job
def parse_attachment(s, model_name, backend_id,
                     attachment_b_id):
    """Parse one attachment, and produces chunks.

    I use some short variable names:
    _b is the binding.
    s is the session

    """
    # these should be configured in the ParsePolicy
    delimiter = ';'
    quotechar = '"'

    # env = get_environment(s, model_name, backend_id)
    # importer = env.get_connector_unit(ParsePolicy)
    # importer.run(attachment_binding_id)
    attachment_b_obj = s.pool[model_name]
    chunk_b_obj = s.pool['file.chunk.binding']
    # attachment_b = attachment_b_obj.browse(
    #     s.cr,
    #     s.uid,
    #     attachment_b_id,
    #     context=s.context
    # )
    with attachment_b_obj.get_file_like(
        s.cr,
        s.uid,
        attachment_b_id,
        context=s.context
    ) as file_like:

        reader = csv.reader(
            file_like,
            delimiter=delimiter,
            quotechar=quotechar
        )

        header_list = reader.next()
        attachment_b_obj.write(s.cr, s.uid, [attachment_b_id], {
            'prepared_header': simplejson.dumps(header_list)
        })

        chunk_array = []
        line_start = 1

        for line in reader:
            # it is a move, not a move line: write a chunk and create a
            # new one
            if line[0]:
                # if we have a previous chunk, write it
                # TODO duplicated code, maybe refactor
                if chunk_array:
                    chunk_b_obj.create(s.cr, s.uid, {
                        'backend_id': backend_id,
                        'attachment_binding_id': attachment_b_id,
                        'prepared_data': simplejson.dumps(chunk_array),
                        'line_start': line_start,
                        'line_stop': reader.line_num,
                    }, context=s.context)
                # reader.line_num is not the same as enumerate(reader): a field
                # could contain newlines. We use line_num because we then
                # use it to recover lines from the original file.
                line_start = reader.line_num
                chunk_array = [line]
            else:
                chunk_array.append(line)

        # write the last chunk
        # TODO duplicated code, maybe refactor
        if chunk_array:
            chunk_b_obj.create(s.cr, s.uid, {
                'backend_id': backend_id,
                'attachment_binding_id': attachment_b_id,
                'prepared_data': simplejson.dumps(chunk_array),
                'line_start': line_start,
                'line_stop': reader.line_num,
            }, context=s.context)
