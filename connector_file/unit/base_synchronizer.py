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
"""Base classes for connector synchronizers."""

from openerp.addons.connector.unit.synchronizer import Synchronizer
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer

from .ftp_policy import FTPFileGetterPolicy
from .policy import FileGetterErrorPolicy


class BaseFileSynchronizer(ImportSynchronizer):

    """Base Synchronizer for file import."""

    def __init__(self, environment):
        super(Synchronizer, self).__init__(environment)
        self._file_getter_policy_instance = None
        self._file_getter_error_policy = None

    @property
    def file_getter_policy_instance(self):
        """ Return an instance of ``FTPFileGetterPolicy``.

        The instanciation is delayed because some synchronisations do
        not need such an unit and the unit may not exist.

        """
        if self._file_getter_policy_instance is None:
            self._file_getter_policy_instance = (
                self.environment.get_connector_unit(FTPFileGetterPolicy)
            )
        return self._file_getter_policy_instance

    @property
    def file_getter_error_policy(self):
        """ Return an instance of ``FileGetterErrorPolicy``.

        The instanciation is delayed because some synchronisations do
        not need such an unit and the unit may not exist.

        :rtype: :py:class:`connector_file.unit.policy.FileGetterErrorPolicy`

        """
        if self._file_getter_error_policy is None:
            self._file_getter_error_policy = (
                self.environment.get_connector_unit(FileGetterErrorPolicy)
            )
        return self._file_getter_error_policy
