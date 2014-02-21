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
"""Unit and integrated tests for the file connector."""

from . import test_csv_parse_policy
# This tests need a properly set up real FTP server to pass.
# TODO: mock the FTP server out.
# from . import test_ftp_get_policy
from . import test_chunk

fast_suite = [
]

checks = [
    test_csv_parse_policy,
    # test_ftp_get_policy,
    test_chunk,
]
