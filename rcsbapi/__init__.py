__docformat__ = "restructuredtext en"
__author__ = "Dennis Piehl"
__email__ = "dennis.piehl@rcsb.org"
__license__ = "MIT"
__version__ = "1.1.4"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
