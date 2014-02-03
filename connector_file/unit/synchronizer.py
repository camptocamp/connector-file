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
"""Connector Synchronizers."""

import logging
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer
from ..connector import get_environment

_logger = logging.getLogger(__name__)


class FileImportSynchronizer(ImportSynchronizer):

    """Base importer for a file."""

    def run(self, filename):
        """Run the file import. Return string."""
        _logger.error('Now I will import'.format(filename))


class BatchImportSynchronizer(ImportSynchronizer):
    """ The role of a BatchImportSynchronizer is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    def run(self, filters=None):
        """ Run the synchronization """
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, record_id):
        """ Import a record directly or delay the import of the record.

        Method to implement in sub-classes.
        """
        raise NotImplementedError


class DirectBatchImport(BatchImportSynchronizer):
    """ Import the records directly, without delaying the jobs. """
    _model_name = None

    def _import_record(self, record_id):
        """ Import the record directly """
        import_record(self.session,
                      self.model._name,
                      self.backend_record.id,
                      record_id)


class DelayedBatchImport(BatchImportSynchronizer):
    """ Delay import of the records """
    _model_name = None

    def _import_record(self, record_id, **kwargs):
        """ Delay the import of the records"""
        import_record.delay(self.session,
                            self.model._name,
                            self.backend_record.id,
                            record_id,
                            **kwargs)


@job
def import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Magento """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(BatchImportSynchronizer)
    importer.run(filters=filters)


@job
def import_record(session, model_name, backend_id, magento_id, force=False):
    """ Import a record from Magento """
    env = get_environment(session, model_name, backend_id)
    # importer = env.get_connector_unit(MagentoImportSynchronizer)
    # importer.run(magento_id, force=force)
