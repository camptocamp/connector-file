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
"""Backend adapters."""

from openerp.addons.connector.connector import ConnectorUnit


class Policy(ConnectorUnit):

    """Abstract Policy.

    A Policy is a generic unit containing the specific logic to handle
    a step of the file import process.

    """

    pass


class FileGetterPolicy(Policy):

    """Abstract FileGetterPolicy.

    Base class for policies that handle getting a file from an external source
    into an OpenERP attachment.

    """

    pass


class FileGetterErrorPolicy(Policy):

    """Base class for policies to handle errors in the FileGetter."""

    pass


class ParsePolicy(Policy):

    """Abstract ParsePolicy.

    A ParsePolicy deals with splitting a file (ir.attachment) into chunks.

    """

    pass


class ParseErrorPolicy(Policy):

    """Base class for policies that handle errors in the Parse."""

    pass


class LoadPolicy(Policy):

    """Base class for policies that load a chunk into OpenERP."""

    pass
