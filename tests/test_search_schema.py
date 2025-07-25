##
# File:    test_search_schema.py
# Author:  Spencer Bliven/Santiago Blaumann/RCSB PDB contributors
# Date:    6/7/23
#
# Update:
#
#
##
"""
Tests for all functions of the schema file.
"""

import logging
import time
import unittest
import os

from rcsbapi.search import search_attributes as attrs
from rcsbapi.search import SEARCH_SCHEMA
from rcsbapi.const import const

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self) -> None:
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testSchema(self) -> None:
        ok = attrs.rcsb_id.attribute == "rcsb_id"
        self.assertTrue(ok)
        ok2 = attrs.rcsb_struct_symmetry.symbol.attribute == "rcsb_struct_symmetry.symbol"
        self.assertTrue(ok2)
        logger.info("Schema test results: ok : (%r), ok2: (%r)", ok, ok2)

    def testSchemaVersion(self) -> None:
        # Check structure attribute schema version
        webSchema = SEARCH_SCHEMA._fetch_schema(const.SEARCH_API_STRUCTURE_ATTRIBUTE_SCHEMA_URL)
        localSchema = SEARCH_SCHEMA._load_json_schema(os.path.join(const.SEARCH_API_SCHEMA_DIR, const.SEARCH_API_STRUCTURE_ATTRIBUTE_SCHEMA_FILENAME))
        webVer = webSchema.get("$comment").split()[-1]
        localVer = localSchema.get("$comment").split()[-1]
        ok = len(localVer.split(".")) == 3 and len(webVer.split(".")) == 3
        self.assertTrue(ok)
        logger.info("ok is %r", ok)
        webVerMajorMinor = float(".".join(webVer.split(".")[0:2]))
        localVerMajorMinor = float(".".join(localVer.split(".")[0:2]))
        ok = localVerMajorMinor <= webVerMajorMinor and localVerMajorMinor >= webVerMajorMinor - 0.10
        logger.info("ok is %r", ok)
        self.assertTrue(ok)
        logger.info("Metadata schema tests results: local version (%r) and web version (%s)", localVer, webVer)
        # Check chemical attribute schema version
        webSchema = SEARCH_SCHEMA._fetch_schema(const.SEARCH_API_CHEMICAL_ATTRIBUTE_SCHEMA_URL)
        localSchema = SEARCH_SCHEMA._load_json_schema(os.path.join(const.SEARCH_API_SCHEMA_DIR, const.SEARCH_API_CHEMICAL_ATTRIBUTE_SCHEMA_FILENAME))
        webVer = webSchema.get("$comment").split()[-1]
        localVer = localSchema.get("$comment").split()[-1]
        ok = len(localVer.split(".")) == 3 and len(webVer.split(".")) == 3
        self.assertTrue(ok)
        logger.info("ok is %r", ok)
        webVerMajorMinor = float(".".join(webVer.split(".")[0:2]))
        localVerMajorMinor = float(".".join(localVer.split(".")[0:2]))
        ok = localVerMajorMinor <= webVerMajorMinor and localVerMajorMinor >= webVerMajorMinor - 0.10
        logger.info("ok is %r", ok)
        self.assertTrue(ok)
        logger.info("Chemical schema tests results: local version (%r) and web version (%s)", localVer, webVer)

    def testFetchSchema(self) -> None:
        # check fetching of structure attribute schema
        fetchSchema = SEARCH_SCHEMA._fetch_schema(const.SEARCH_API_STRUCTURE_ATTRIBUTE_SCHEMA_URL)
        ok = fetchSchema is not None
        logger.info("ok is %r", ok)
        self.assertTrue(ok)
        fetchSchema = SEARCH_SCHEMA._fetch_schema(const.SEARCH_API_CHEMICAL_ATTRIBUTE_SCHEMA_URL)
        ok = fetchSchema is not None
        logger.info("ok is %r", ok)
        self.assertTrue(ok)
        errorURL = "https://httpbin.org/status/404"
        fetchSchema = SEARCH_SCHEMA._fetch_schema(errorURL)
        ok = fetchSchema is None
        logger.info("ok is %r", ok)
        self.assertTrue(ok)

    def testRcsbAttrs(self) -> None:
        with self.subTest(msg="1. Check type and descriptions exist for attributes"):
            for attr in attrs:
                attr_dict = vars(attr)
                desc = attr_dict["description"]
                self.assertIsNotNone(desc)

        with self.subTest(msg="2. Check searching for attribute details"):
            attr_details = attrs.get_attribute_details("drugbank_info.drug_groups")
            for obj_attr in ["attribute", "type", "description"]:
                self.assertIn(obj_attr, vars(attr_details).keys())

            # special case because rcsb_id is in both structure and chemical attributes
            attr_dict = vars(attrs.get_attribute_details("rcsb_id"))
            self.assertIsInstance(attr_dict["type"], list)
            self.assertIsInstance(attr_dict["description"], list)

            attr_details = attrs.get_attribute_details("foo")
            self.assertIsNone(attr_details)

    def testNestedAttrs(self):
        with self.subTest(msg="3. Check nested attribute indexing dictionary length"):
            nested_dict = SEARCH_SCHEMA.nested_attribute_schema
            self.assertGreaterEqual(len(nested_dict), 15)

        with self.subTest(msg="3. Check for a specific nested attribute"):
            expected_tuple = ('rcsb_uniprot_annotation.name', 'rcsb_uniprot_annotation.type')
            self.assertIn(expected_tuple, SEARCH_SCHEMA.nested_attribute_schema)

            not_expected_tuple = ('drugbank_info.drug_groups', 'rcsb_uniprot_annotation.type')
            self.assertNotIn(not_expected_tuple, SEARCH_SCHEMA.nested_attribute_schema)


def buildSchema() -> unittest.TestSuite:
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SchemaTests("testSchema"))
    suiteSelect.addTest(SchemaTests("testSchemaVersion"))
    suiteSelect.addTest(SchemaTests("testFetchSchema"))
    suiteSelect.addTest(SchemaTests("testRcsbAttrs"))
    suiteSelect.addTest(SchemaTests("testNestedAttrs"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildSchema()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
