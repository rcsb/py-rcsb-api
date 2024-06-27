##
# File:    testschema.py
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
# import platform
# import resource
import time
import unittest
import requests


from schema import Schema  # do I need the other stuff too?
from schema import pdb_url

SCHEMA = Schema(pdb_url)


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self) -> None:
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testFetch(self):  # modify the corresponding function to handle an error better
        fetched_schema = SCHEMA.fetch_schema(pdb_url)
        self.assertIsInstance(fetched_schema, dict)

    def testConstructRootDict(self):
        pass

    def testConstructTypeDict(self):
        type_fields_dict = {}
        type_fields_dict = SCHEMA.construct_type_dict(SCHEMA.schema, type_fields_dict)
        entry_dict_from_func = type_fields_dict['CoreEntry']
        type_dict_list = SCHEMA.schema["data"]["__schema"]["types"]
        entry_found = False
        i = 0
        while entry_found is False and i < len(type_dict_list):
            type_dict = type_dict_list[i]
            name = str(type_dict["name"])
            if name == 'CoreEntry':
                fields = type_dict["fields"]
                field_dict = {}
                for field in fields:
                    field_dict[str(field["name"])] = dict(field["type"])
                entry_dict = field_dict
                entry_found = True
            i += 1
        self.assertEqual(entry_dict_from_func, entry_dict)
        self.assertEqual(len(type_dict_list), len(SCHEMA.type_fields_dict.keys()))

    def testConstructQueryRustworkX(self):
        with self.subTest(msg="1.  singular input_type (entry)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids="4HHB", input_type="entry", return_data_list=["exptl"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdb_url).json()
            self.assertNotIn('errors', response_json.keys())
        with self.subTest(msg="2. plural input_type (entries)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids=["4HHB", "1IYE"], input_type="entries", return_data_list=["exptl"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdb_url).json()
            self.assertNotIn('errors', response_json.keys())
        with self.subTest(msg="3. two arguments (polymer_entity_instance)"): #TODO: do I have to test mult arg + plural?
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={'asym_id': "A", "entry_id": "4HHB"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdb_url).json()
            self.assertNotIn('errors', response_json.keys())
        with self.subTest(msg="4. three arguments (interface)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={'assembly_id': "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["rcsb_id"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdb_url).json()
            self.assertNotIn('errors', response_json.keys())
        with self.subTest(msg="5. request multiple return fields"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids="4HHB", input_type="entry", return_data_list=["exptl","rcsb_polymer_instance_annotation"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdb_url).json()
            self.assertNotIn('errors', response_json.keys())
        with self.subTest(msg="6. request scalar field"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids="4HHB", input_type="entry", return_data_list=["rcsb_id"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdb_url).json()
            self.assertNotIn('errors', response_json.keys())
        # Test error handling
        with self.subTest(msg="7. too many input ids passed in"):
            with self.assertRaises(Exception):
                SCHEMA._Schema__construct_query_rustworkx(input_ids=["4HHB","1IYE"], input_type="entry", return_data_list=["rcsb_id"])
        with self.subTest(msg="too few inputs keys provided"):
            with self.assertRaises(Exception):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_id": "4HHB"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
        with self.subTest(msg="8. incorrect input keys provided"):
            with self.assertRaises(Exception):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={"assembly_id": "1"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
        with self.subTest(msg="10. no path exists"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={'assembly_id': "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["exptl"])
        with self.subTest(msg="11. return data not specific enough"):
            with self.assertRaises(Exception):
                SCHEMA._Schema__construct_query_rustworkx(input_ids="4HHB", input_type="entry", return_data_list=["id"])


def buildSchema():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SchemaTests("testFetch"))
    suiteSelect.addTest(SchemaTests("testConstructRootDict"))
    suiteSelect.addTest(SchemaTests("testConstructTypeDict"))
    suiteSelect.addTest(SchemaTests("testConstructQueryRustworkX"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildSchema()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
