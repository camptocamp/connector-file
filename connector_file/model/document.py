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
from openerp.addons.connector.queue.job import job

from ..backend import file_import
from ..connector import get_environment
from ..unit.csv_policy import CSVParsePolicy
from ..unit.synchronizer import BaseFileSynchronizer
from ..unit.parser import BaseParser


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
            parse_attachment(
                session,
                self._name,
                attachment.id
            )

        return True

    def parse_async(self, cr, uid, ids, context=None):
        """Split in chunks, return true."""
        session = ConnectorSession(cr, uid, context=context)
        for attachment in self.browse(cr, uid, ids, context=context):
            parse_attachment.delay(
                session,
                self._name,
                attachment.id,
            )
        return True

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


# no decorator here
class FileSynchronizer(BaseFileSynchronizer):

    def get_files_to_create(self):
        """search if there are new files to get"""
        pass

    def create_file(self):
        """create ir.attachment.binding"""
        pass

    def manage_file_retrieval_error(self):
        pass

    def run(self):
        pass


@file_import
class DirectFileSynchronizer(FileSynchronizer):
    pass


@file_import
class AsyncFileSynchronizer(FileSynchronizer):
    pass


# no decorator here
class FileParser(BaseParser):
    def get_file_to_parse(self):
        pass

    def parse_file(self, attachment_binding_id):
        pass

    def run(self):
        pass


@file_import
class DirectFileParser(FileParser):
    pass


@file_import
class AsyncFileParser(FileParser):
    pass


@job
def parse_attachment(s, model_name, record_id):
    """Parse one attachment, and produces chunks.

    I use some short variable names:
    _b is the binding.
    s is the session

    """

    attachment_b = s.browse(model_name, record_id)
    backend_id = attachment_b.backend_id.id
    env = get_environment(s, model_name, backend_id)
    parse_policy = env.get_connector_unit(CSVParsePolicy)
    parse_policy.run(record_id)
