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
# import rustworkx as rx
# import networkx as nx

from rcsbapi.data import schema
from rcsbapi.data.schema import Schema
# from rcsbapi.data.schema import use_networkx
from rcsbapi.data.schema import pdbUrl

SCHEMA = Schema(pdbUrl)


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id().split('.')[-1], time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        self.original_networkx_flag = schema.use_networkx

    def tearDown(self) -> None:
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id().split('.')[-1], time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)
        schema.use_networkx = self.original_networkx_flag

    def testFetch(self): 
        fetched_schema = SCHEMA.fetch_schema(pdbUrl)
        self.assertNotIn("errors", fetched_schema.keys())

    def testConstructRootDict(self):
        with self.subTest(msg="1. root dict for singular type (interface)"):
            interface_dict = SCHEMA.root_dict['interface']
            self.assertEqual(len(interface_dict), 3)
            arg_names = []
            for arg_dict in interface_dict:
                arg_names.append(arg_dict['name'])
            self.assertIn("assembly_id", arg_names)
            self.assertIn("interface_id", arg_names)
            self.assertIn("entry_id", arg_names)
        with self.subTest(msg="2. root dict for plural type (entries)"):
            entries_dict = SCHEMA.root_dict['entries']
            self.assertEqual(len(entries_dict), 1)
            self.assertEqual(entries_dict[0]['name'], 'entry_ids')
            self.assertEqual(entries_dict[0]['kind'], 'LIST')
        with self.subTest(msg="3. root dict has the same number of types as schema"):
            schema_list = SCHEMA.root_introspection["data"]["__schema"]["queryType"]["fields"]
            self.assertEqual(len(schema_list), len(list(SCHEMA.root_dict.keys())))

    def testConstructTypeDict(self):
        type_fields_dict = {}
        entry_dict = {}
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

    # def testRecurseBuildSchema(self):  # doesn't work right now
    #     original_networkx_flag = schema.use_networkx
    #     schema.use_networkx = False
    #     importlib.reload(schema)
    #     SCHEMA = Schema(pdbUrl)
    #     SCHEMA.recurse_build_schema(SCHEMA.schema_graph, 'Query')
    #     self.assertIsInstance(SCHEMA.schema_graph, rx.PyDiGraph)
    #     schema.use_networkx = True
    #     importlib.reload(schema)
    #     SCHEMA = Schema(pdbUrl)
    #     SCHEMA.recurse_build_schema(SCHEMA.schema_graph, 'Query')
    #     self.assertIsInstance(SCHEMA.schema_graph, nx.classes.digraph.DiGraph)
    #     # reset to original
    #     schema.use_networkx = original_networkx_flag
    #     importlib.reload(schema)
    #     SCHEMA = Schema(pdbUrl)

    def testConstructQueryRustworkX(self):
        with self.subTest(msg="1.  singular input_type (entry)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_id": "4HHB"}, input_type="entry", return_data_list=["exptl"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="2. plural input_type (entries)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_ids": ["4HHB", "1IYE"]}, input_type="entries", return_data_list=["exptl"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="3. two arguments (polymer_entity_instance)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={'asym_id': "A", "entry_id": "4HHB"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="4. three arguments (interface)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={'assembly_id': "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["CoreInterface.rcsb_id"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="5. request multiple return fields"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_id": "4HHB"}, input_type="entry", return_data_list=["exptl","rcsb_polymer_instance_annotation"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="6. request scalar field"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_id": "4HHB"}, input_type="entry", return_data_list=["CoreEntry.rcsb_id"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="12. two arguments (polymer_entity_instances)"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_ids={'instance_ids': ["4HHB.A", "4HHB.C"]}, input_type="polymer_entity_instances", return_data_list=["rcsb_polymer_instance_annotation"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="20. nested query"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="interfaces", return_data_list=["rcsb_interface_partner"], input_ids=["MA_MACOFFESLACC100000G1I2-1.1", "7XIW-1.2"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="20. requesting scalars under same field"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="entry", return_data_list=["Exptl.method", "Exptl.details"], input_ids=["4HHB"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        # Test error handling
        with self.subTest(msg="7. too many input ids passed in"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_id": ["4HHB","1IYE"]}, input_type="entry", return_data_list=["exptl"])
        with self.subTest(msg="8. too few inputs keys provided"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={"entry_id": "4HHB"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
        with self.subTest(msg="9. incorrect input keys provided"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={"assembly_id": "1"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
        with self.subTest(msg="10. no path exists"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={'assembly_id': "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["exptl"])
        with self.subTest(msg="11. field doesn't exist"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_ids={'assembly_id': "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["aaa"])

    def regexChecks(self):
        with self.subTest(msg="1. regex for _entity_instances"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="polymer_entity_instances", return_data_list=["rcsb_polymer_instance_annotation"], input_ids=["4HHB.A", "AF_AFA0A009IHW8F1.B"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="2. regex for _entities"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="polymer_entities", return_data_list=["rcsb_polymer_entity_feature", "CorePolymerEntity.rcsb_id"], input_ids=["AF_AFA0A009IHW8F1_1", "4HHB_1"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="3. regex for entries"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="entries", return_data_list=["exptl"], input_ids=["7XIW", "4HHB"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="4. regex for assemblies"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="assemblies", return_data_list=["rcsb_struct_symmetry_lineage"], input_ids=["4HHB-1", "MA_MACOFFESLACC100000G1I2-2"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="5. regex for interfaces"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="interfaces", return_data_list=["RcsbInterfaceContainerIdentifiers.assembly_id"], input_ids=["MA_MACOFFESLACC100000G1I2-1.1", "7XIW-1.2"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="6. regex with a singular type"):
            query = SCHEMA._Schema__construct_query_rustworkx(input_type="entry", return_data_list=["exptl"], input_ids=["4HHB"])
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=pdbUrl, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="7. wrong format for CSM entry id"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_type="entry", return_data_list=["Exptl.method", "Exptl.details"], input_ids=["MA_MACOFFESLACC100000G1I2-1.1"])
        with self.subTest(msg="8. id_list provided with incorrect input_type"):
            with self.assertRaises(ValueError):
                SCHEMA._Schema__construct_query_rustworkx(input_type="assemblies", return_data_list=["exptl"], input_ids=["4HHB", "1IYE"])

    def testConstructQuery(self):
        with self.subTest(msg="1. return data not specific enough"):
            with self.assertRaises(ValueError):
                SCHEMA.construct_query(input_ids="4HHB", input_type="entry", return_data_list=["id"])

    def testVerifyUniqueField(self):
        with self.subTest(msg="1. unique field with dot notation"):
            field = "Entry.id"
            self.assertTrue(SCHEMA.verify_unique_field(field))
        with self.subTest(msg="2. unique field no dot notation"):
            field = "rcsb_polymer_instance_annotation"
            self.assertTrue(SCHEMA.verify_unique_field(field))
        with self.subTest(msg="3. redundant field"):
            field = "id"
            self.assertFalse(SCHEMA.verify_unique_field(field))
        with self.subTest(msg="4. field doesn't exists"):
            field = "foo"
            self.assertIsNone(SCHEMA.verify_unique_field(field))

    def testExtractNameDescription(self):
        SCHEMA.extract_name_description(SCHEMA.schema)
        self.assertIn('nonpolymer_comp', SCHEMA.name_description_dict)
        description = SCHEMA.name_description_dict.get('nonpolymer_comp')
        logger.info("Description for 'nonpolymer_comp': %s", description)
        self.assertEqual(description, 'Get a non-polymer chemical components described in this molecular entity.')

    def testFindFieldNames(self):
        with self.subTest(msg="1. search for rcsb"):
            result = SCHEMA.find_field_names("rcsb")
            self.assertIn("CoreChemComp.rcsb_id", result)
        with self.subTest(msg="1. search for nonexistent field"):
            with self.assertRaises(ValueError):
                SCHEMA.find_field_names("foo")
        with self.subTest(msg="2. search for field list"):
            with self.assertRaises(ValueError):
                SCHEMA.find_field_names(["rcsb", "exptl"])


def buildSchema():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SchemaTests("testFetch"))
    suiteSelect.addTest(SchemaTests("testConstructRootDict"))
    suiteSelect.addTest(SchemaTests("testConstructTypeDict"))
    # suiteSelect.addTest(SchemaTests("testRecurseBuildSchema"))
    suiteSelect.addTest(SchemaTests("regexChecks"))
    suiteSelect.addTest(SchemaTests("testConstructQuery"))
    suiteSelect.addTest(SchemaTests("testConstructQueryRustworkX"))
    suiteSelect.addTest(SchemaTests("testVerifyUniqueField"))
    suiteSelect.addTest(SchemaTests("testExtractNameDescription"))
    suiteSelect.addTest(SchemaTests("testFindFieldNames"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildSchema()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
