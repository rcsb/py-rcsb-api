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

    def testGetEditorLink(self):
        query_str = '{ entries(entry_ids: ["4HHB", "1IYE"]) {\n  exptl {\n     method_details\n     method\n     details\n     crystals_number\n  }\n}}'
        query_obj = Query({"entry_ids": ["4HHB","1IYE"]}, "entries",["exptl"])
        url = query_obj.get_editor_link()
        response_json = requests.GET(url)
        self.assertEqual(response_json.status_code, 200)


    def testPostQuery(self):
        with self.subTest("1. Batching into requests with fewer Ids"):
            input_ids = []
            for i in range(165):
                input_ids.append("4HHB")
            query_obj = Query({"entry_ids": input_ids}, "entries",["exptl"])
            query_obj.post_query()
            #assert that the batch and merge functions are called

    def testParseGQLError(self):
        pass

    def testBatchIDs(self):
        input_ids = []
        for i in range(165):
            input_ids.append("4HHB")
        query_obj = Query({"entry_ids": input_ids}, "entries",["exptl"])
        batch_size = 50
        batched_ids = query_obj.batch_ids(batch_size)
        total_ids = 0
        for batch in batched_ids:
            len_id_batch = len(batch["entry_ids"])
            self.assertLessEqual(len_id_batch, batch_size)
            total_ids += len_id_batch
        self.assertEqual(len(query_obj.input_ids_list), total_ids)

    def testMergeResponse(self):
        #assert that the lengths are combined and all ids are present?
        pass

    def testEditortoQuery(self):
        pass


def buildQuery():
    suiteSelect = unittest.TestSuite()
    # suiteSelect.addTest(QueryTests("testGetEditorLink"))
    suiteSelect.addTest(QueryTests("testBatchIDs"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildQuery()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
