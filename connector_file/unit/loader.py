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
"""Connector Synchronizers."""

from openerp.addons.connector.unit.synchronizer import ImportSynchronizer


class BaseLoader(ImportSynchronizer):

    """Base class for a Loader.

    The Loader takes care of loading a chunk into an OpenERP object.

    """

    def __init__(self, environment):
        super(BaseLoader, self).__init__(environment)
        self._load_policy_instance = None
        self._load_error_policy = None

    def ask_files(self):
        """Defined in specific loaders."""
        raise NotImplementedError

    def load_one(self, chunk_binding_id):
        """Defined in specific loaders."""
        raise NotImplementedError
