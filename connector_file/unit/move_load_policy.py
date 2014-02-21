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
"""Module for the MoveLoadPolicy."""
import simplejson as json

from ..backend import file_import
from .policy import LoadPolicy
from ..exceptions import MoveLoadFailedJobError


@file_import
class MoveLoadPolicy(LoadPolicy):

    """Policy to load a chunk into an account.move.

    This uses the openerp standard load().

    """

    _model_name = 'file.chunk.binding'

    def get_chunks_to_load(self):
        """Return a list of ids of chunks to be loaded."""
        return self.session.search(self._model_name, [
            ('sync_date', '=', False)
        ])

    def load_one_chunk(self, chunk_b_id):
        """Load a chunk into an OpenERP Journal Entry."""

        s = self.session
        move_obj = s.pool['account.move']
        chunk_b_obj = s.pool[self._model_name]
        chunk_b = chunk_b_obj.browse(s.cr, s.uid, chunk_b_id,
                                     context=s.context)
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
            chunk_b.write({
                'move_id': load_result['ids'][0]
            }, context=s.context)
        else:
            raise MoveLoadFailedJobError(
                u'Error during load() of the account.move',
                load_result['messages']
            )
