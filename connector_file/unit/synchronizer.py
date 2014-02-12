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

_logger = logging.getLogger(__name__)

from openerp.addons.connector.unit.synchronizer import Synchronizer
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer


class BaseFileSynchronizer(ImportSynchronizer):
    def __init__(self, environment):
        super(Synchronizer, self).__init__(environment)
        self._file_getter_policy = None
        self._file_getter_error_policy = None


    # property file_getter_policy like on connector/synchronizer.py....

