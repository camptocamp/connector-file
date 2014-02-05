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
"""Backend adapters."""

import logging
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import ImportSynchronizer
from connector.unit.backend_adapter import BackendAdapter
from ..backend import file_import
from ..connector import get_environment

_logger = logging.getLogger(__name__)


@file_import
class ParsePolicy(BackendAdapter):
    def run(self, attachment_binding_id):
        """Parse the attachment and split it into chunks."""
        