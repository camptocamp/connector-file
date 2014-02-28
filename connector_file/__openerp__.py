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

{
    'name': 'Connector for importing files',
    'version': '0.1',
    'category': 'Connector',
    'author': 'Camptocamp',
    'website': 'camptocamp.com',
    'license': 'AGPL-3',
    'description': """
Connector File Import
=====================

Asynchronous, fault-tolerant import of external files using the OpenERP
Connector.

This module uses many components of the OpenERP Connector (backends, jobs,
bindings, units, synchronizers).

At the moment it does a specific job, but its components are designed to be
very detached, and adapting that for other use cases should be reasonable.

The use case that is covered at the moment is the import of a large amount
of Journal Entries from CSV files published on a FTP server.

The focus in on the asynchronous, decoupled nature of the process. The actual
import of the file is performed by the standard load() method, the same used
by the built-in import feature of OpenERP.

At the moment, the process is split in three phases, each handled by its own
jobs, Synchronizers and Units:

* The loading of a file from a FTP server. Each file must come with its own
  hash file - at the moment, a MD5 in hex format, with the same file name as
  the CSV and with extension .md5. Each job handles a file.
* The parsing of the file into Chunks, one per Journal Entry. Each chunk
  contains the data serialized into a JSON string. A chunk also has a method
  to reconstruct the corresponding piece of the original file (that could
  be unwieldy). Here, each job handles a file.
* The loading of each chunk in a Journal Entry. Each job handles a Chunk.
""",
    'depends': [
        'connector',
        'account',
    ],
    'external_dependencies': {
        'python': ['ftputil'],
    },
    'data': [
        'view/backend_model_view.xml',
        'view/document_view.xml',
        'view/chunk_view.xml',
        'action.xml',
        'menu.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
    ],
    'installable': True,
}
