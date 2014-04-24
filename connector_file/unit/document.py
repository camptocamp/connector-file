# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone, Nicolas Bessi
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

"""Units for Attachments, aka Documents, aka files.

Here we find the logic that takes care of documents. The specific units for
doing low level work lie in different modules.

"""

import logging

from openerp.addons.connector.queue.job import job

from ..backend import file_import
from ..connector import get_environment
from ..unit.csv_policy import CSVParsePolicy
from ..unit.base_synchronizer import BaseFileSynchronizer
from ..unit.parser import BaseParser
from ..exceptions import InvalidFileError

_logger = logging.getLogger(__name__)


# no decorator here
class FileSynchronizer(BaseFileSynchronizer):

    """File Synchronizer.

    This takes care of bringing data from an external
    file repository to OpenERP models.

    """

    _model_name = 'ir.attachment.binding'

    def get_files_to_create(self):
        """Return an iterator of file identifiers we want to import."""

        policy = self.file_getter_policy_instance
        return policy.ask_files()

    def create_one_file(self, data_file_name, hash_file_name):
        """Create ir.attachment.binding. Return created OpenERP id."""
        try:
            policy = self.file_getter_policy_instance

            # this can be improved by only getting the content lazily if we
            # do actually create the attachment.
            # content is a big string.
            content = policy.get_content(
                data_file_name)

            hash_string = policy.get_hash(hash_file_name)

            # creates an attachment.binding.id with given content
            # returns attachment_binding_id
            return policy.create_one(
                data_file_name,
                hash_file_name,
                hash_string,
                content)
        except InvalidFileError as e:
            self.file_getter_policy_instance.manage_exception(
                e,
                data_file_name,
                hash_file_name
            )

    def get_all(self):
        """Import all external files we have to import."""
        file_names = self.get_files_to_create()
        for data_file_name, hash_file_name in file_names:
            create_one_file.delay(
                self.session,
                self._model_name,
                self.backend_record.id,
                data_file_name,
                hash_file_name)


@file_import
class DirectFileSynchronizer(FileSynchronizer):

    """File Synchronizer, synchronous version."""

    pass


@file_import
class AsyncFileSynchronizer(FileSynchronizer):

    """File Synchronizer, asynchronous version."""

    pass


# no decorator here
class FileParser(BaseParser):

    """The Parser parses a file into chunchs, headers, and json data."""

    _model_name = 'ir.attachment.binding'

    def get_files_to_parse(self):
        """Return a list of files to parse."""
        policy = self.parse_policy_instance
        return policy.ask_files()

    def parse_one_file(self, attachment_binding_id):
        """Parse one file and create the appropriate chunks."""
        policy = self.parse_policy_instance
        _logger.info(
            u'Parsing attachment binding %s now', attachment_binding_id
        )
        policy.parse_one(attachment_binding_id)

    def parse_all(self):
        """Parse all files into chunks."""
        ids = self.get_files_to_parse()
        _logger.info(u'Jobs to parse %s files put in queue', len(ids))
        for attachment_binding_id in ids:
            parse_one_file.delay(
                self.session,
                self._model_name,
                self.backend_record.id,
                attachment_binding_id)

    @property
    def parse_policy_instance(self):
        """Return an instance of ``CSVParsePolicy``.

        The instantiation is delayed because some synchronizations do
        not need such a unit and the unit may not exist.

        """
        if self._parse_policy_instance is None:
            self._parse_policy_instance = (
                self.environment.get_connector_unit(CSVParsePolicy)
            )
        return self._parse_policy_instance


@job
def create_one_file(session, model_name, backend_id, data_file_name,
                    hash_file_name):
    """Get one file and create an attachment binding. Return created ID."""
    env = get_environment(session, model_name, backend_id)
    synchronizer = env.get_connector_unit(AsyncFileSynchronizer)
    return synchronizer.create_one_file(data_file_name, hash_file_name)


@job
def parse_one_file(session, model_name, backend_id, attachment_binding_id):
    """Parse one file to produce chunks."""
    env = get_environment(session, model_name, backend_id)
    parser = env.get_connector_unit(AsyncFileParser)
    parser.parse_one_file(attachment_binding_id)


@file_import
class DirectFileParser(FileParser):

    """Parser, synchronous version."""

    pass


@file_import
class AsyncFileParser(FileParser):

    """Parser, asynchronous version."""

    pass
