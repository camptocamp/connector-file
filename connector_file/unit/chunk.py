

import logging

from openerp.addons.connector.connector import ConnectorUnit

class BaseChunkProcessor(ConnectorUnit):
    def __init__(self, environment):
        super(BaseParser, self).__init__(environment)
        self._load_policy = None  
