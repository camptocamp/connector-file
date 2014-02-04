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
"""Unit tests for chunks."""

from functools import partial

import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


class test_file_import(common.SingleTransactionCase):

    """Test import from a chunk."""

    def setUp(self):
        """Initialize the test."""
        super(test_file_import, self).setUp()
        self.backend_model = self.registry('file_import.backend')
        self.session = ConnectorSession(self.cr, self.uid)
        data_model = self.registry('ir.model.data')
        self.get_ref = partial(data_model.get_object_reference,
                               self.cr, self.uid)
        backend_ids = self.backend_model.search(
            self.cr,
            self.uid,
            [('name', '=', 'Test File Import')])
        if backend_ids:
            self.backend_id = backend_ids[0]
        else:
            self.backend_id = self.backend_model.create(
                self.cr,
                self.uid,
                {'name': 'Test File Import',
                 'version': '1',
                 'company_id': 1,  # FIXME
                 'user_id': 1  # FIXME
                 }
            )
