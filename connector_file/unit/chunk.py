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

import logging

from openerp.addons.connector.queue.job import job

from openerp.addons.connector.connector import ConnectorUnit
from ..backend import file_import
from ..connector import get_environment

from ..unit.move_load_policy import MoveLoadPolicy

_logger = logging.getLogger(__name__)
LOG_EVERY = 100


class BaseChunkLoader(ConnectorUnit):

    """Base Chunk Loader.

    Classes to load chunk should inherit from here.

    """

    def __init__(self, environment):
        super(BaseChunkLoader, self).__init__(environment)
        self._load_policy_instance = None


class ChunkLoader(BaseChunkLoader):

    """Create jobs to manage chunk loading."""

    _model_name = 'file.chunk.binding'

    def get_chunks_to_load(self):
        """Return a list of chunks that need to be loaded."""
        policy = self.load_policy_instance
        return policy.get_chunks_to_load()

    def load_one_chunk(self, chunk_binding_id):
        """Load a chunk in OpenERP. Normally called by a job."""
        policy = self.load_policy_instance
        _logger.info(u'Loading chunk binding %s now', chunk_binding_id)
        policy.load_one_chunk(chunk_binding_id)

    def load_all(self):
        """Create jobs for loading all chunks."""
        ids = self.get_chunks_to_load()
        _logger.info(u'I will now create %s jobs for loading.', len(ids))
        # I take that out of the loop to make it a bit faster.
        backend_record_id = self.backend_record.id
        for count, chunk_binding_id in enumerate(ids):
            if count % LOG_EVERY == 0:
                _logger.info('%s jobs created', count)
            load_one_chunk.delay(
                self.session,
                self._model_name,
                backend_record_id,
                chunk_binding_id)
        _logger.info(u'Jobs to load {0} chunks put in queue'.format(len(ids)))

    @property
    def load_policy_instance(self):
        """ Return an instance of ``CSVParsePolicy``.

        The instantiation is delayed because some synchronisations do
        not need such a unit and the unit may not exist.

        """
        if self._load_policy_instance is None:
            self._load_policy_instance = (
                self.environment.get_connector_unit(MoveLoadPolicy)
            )
        return self._load_policy_instance


@job
def load_one_chunk(session, model_name, backend_id, chunk_binding_id):
    """Load one chunk to produce Journal Entries in OpenERP."""
    env = get_environment(session, model_name, backend_id)
    parser = env.get_connector_unit(ChunkLoader)
    parser.load_one_chunk(chunk_binding_id)


@file_import
class AsyncChunkLoader(ChunkLoader):

    """Async-specific code."""

    pass
