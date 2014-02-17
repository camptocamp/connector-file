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

    _model_name = 'ir.attachment.binding'

    def get_files_to_create(self):
        """search if there are new files to get
        return iterator of file identifiers.
        """

        policy = self.file_getter_policy_instance
        return policy.ask_files()

    def create_one_file(self, data_file_name, hash_file_name):
        """create ir.attachment.binding"""
        try:
            policy = self.file_getter_policy_instance

            # content is a big string
            content = policy.get_content(
                data_file_name)

            hash_string = policy.get_hash(hash_file_name)

            # creates an attachment.binding.id with given content
            # returns attachment_binding_id
            return policy.create_one(data_file_name, hash_string, content)
        except InvalidFileError as e:
            self.file_getter_policy_instance.manage_exception(
                e,
                data_file_name, hash_file_name
            )

    def manage_file_retrieval_error(self):
        pass

    def get_all(self):
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
    pass


@file_import
class AsyncFileSynchronizer(FileSynchronizer):
    pass


# no decorator here
class FileParser(BaseParser):
    _model_name = 'ir.attachment.binding'

    def get_files_to_parse(self):
        policy = self.parse_policy_instance
        return policy.ask_files()

    def parse_one_file(self, attachment_binding_id):
        policy = self.parse_policy_instance
        _logger.info(
            u'Parsing attachment binding {0} now'.format(attachment_binding_id)
        )
        policy.parse_one(attachment_binding_id)

    def parse_all(self):
        ids = self.get_files_to_parse()
        _logger.info(u'Jobs to parse {0} files put in queue'.format(len(ids)))
        for attachment_binding_id in ids:
            create_one_file.delay(
                self.session,
                self._model_name,
                self.backend_record.id,
                attachment_binding_id)

    @property
    def parse_policy_instance(self):
        """ Return an instance of ``CSVParsePolicy`` for the
        synchronization.

        The instanciation is delayed because some synchronisations do
        not need such an unit and the unit may not exist.

        """
        if self._parse_policy_instance is None:
            self._parse_policy_instance = (
                self.environment.get_connector_unit(CSVParsePolicy)
            )
        return self._parse_policy_instance


@job
def create_one_file(session, model_name, backend_id, data_file_name,
                    hash_file_name):
    """Get one file and create an attachment binding."""
    env = get_environment(session, model_name, backend_id)
    synchronizer = env.get_connector_unit(AsyncFileSynchronizer)
    return synchronizer.create_one_file(data_file_name, hash_file_name)


@job
def parse_one_file(session, model_name, backend_id, attachment_binding_id):
    """Parse one file to produce chunks."""
    env = get_environment(session, model_name, backend_id)
    parser = env.get_connector_unit(AsyncFileParser)
    parser.create_one_file(attachment_binding_id)


@file_import
class DirectFileParser(FileParser):
    pass


@file_import
class AsyncFileParser(FileParser):
    pass
