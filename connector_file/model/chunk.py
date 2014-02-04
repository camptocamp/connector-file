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

from openerp.osv import orm, fields


class file_chunk(orm.Model):

    """File Chunk."""

    _name = 'file.chunk'

    _description = 'File Chunk'

    _columns = {
        'name': fields.char('Name'),
        'line_start': fields.integer('Line Start'),
        'line_stop': fields.integer('Line Stop'),
        'prepared_header': fields.char('Prepared Header, JSON'),
        'prepared_data': fields.char('Prepared Data, JSON'),
    }

    def load_data(self):
        """TODO. This will load the chunk using load().

        Like load(), this returns a list of the ids of the created objects
        and a list of error messages

        """
        raise NotImplementedError

    def get_raw(self):
        """TODO. Return the original raw data for this chunk from the file.

        This will use the line_start e line_stop to get the raw data
        for this chunk from the original file, without header.

        """
        return NotImplementedError


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
        }

    _defaults = {
    }

    _sql_constraints = [
    ]
