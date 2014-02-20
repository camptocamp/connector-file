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
"""Specific exceptions for the OpenERP File Import Connector."""

from openerp.addons.connector.exception import FailedJobError


class MoveLoadFailedJobError(FailedJobError):
    """This exception is raised if the load() of a move fails."""

    pass


class InvalidFileError(FailedJobError):
    """This exception is raised if the file in invalid
    That means that the file is corrupted or can not be parsed"""

    pass


class MoveFileError(FailedJobError):

    """This exception is raised if we fail to move a file."""

    pass


class ParseError(FailedJobError):
    pass
