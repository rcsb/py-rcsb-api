##
# File:    testquery.py
# Author:  
# Date:    
# Version: 
#
# Update:
#
#
##
"""
Tests for all functions of the schema file. (Work in progress)
"""

__docformat__ = "google en"
__author__ = ""
__email__ = ""
__license__ = ""

import logging
import importlib
# import platform
# import resource
import time
import unittest
import requests

from rcsbapi.data import query
from rcsbapi.data.query import Query
from rcsbapi.data.query import PDB_URL
from rcsbapi.data.query import SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id().split('.')[-1], time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self) -> None:
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id().split('.')[-1], time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

def buildSchema():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(QueryTests(""))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildSchema()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
