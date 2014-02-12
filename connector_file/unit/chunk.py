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
"""Units for processing chunks."""

import simplejson as json

from openerp.addons.connector.queue.job import job

from openerp.addons.connector.connector import ConnectorUnit
from ..exceptions import MoveLoadFailedJobError


class BaseChunkProcessor(ConnectorUnit):
    def __init__(self, environment):
        super(ConnectorUnit, self).__init__(environment)
        self._load_policy = None


class ChunkProcessor(BaseChunkProcessor):

    """create jobs to manage chunk loading"""

    def get_chunk_to_load(self):
        pass

    def load_chunk(self):
        pass

    def run(self):
        pass


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
