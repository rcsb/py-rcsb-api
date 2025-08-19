##
# File:    test_data_schema.py
# Author:  Ivana Truong/RCSB PDB contributors
# Date:
#
# Update:
#
#
##
"""
Tests for all functions of the Data API schema file.
"""

import logging
import time
import json
import os
import unittest
import httpx

from rcsbapi.data import DATA_SCHEMA
from rcsbapi.config import config
from rcsbapi.const import const

logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self) -> None:
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testSchemaVersion(self) -> None:
        msg = "1. Compare entry schema"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            entry_schema_path = os.path.join(os.path.dirname(__file__), "..", "rcsbapi", const.DATA_API_SCHEMA_DIR, const.DATA_API_SCHEMA_ENDPOINT_TO_FILE["entry"])
            with open(entry_schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            local_schema_version = schema_data.get("$comment").split(": ")[1]
            local_major_minor_version = ".".join(local_schema_version.split(".")[:2])

            online_schema_url = "https://data.rcsb.org/rest/v1/schema/entry"
            response = httpx.get(online_schema_url, timeout=config.API_TIMEOUT)
            online_schema_data = response.json()
            online_schema_version = online_schema_data.get("$comment").split(": ")[1]
            online_major_minor_version = ".".join(online_schema_version.split(".")[:2])
            self.assertEqual(local_major_minor_version, online_major_minor_version)

        msg = "2. Compare polymer_entity schema"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            polymer_entity_schema_path = os.path.join(os.path.dirname(__file__), "..", "rcsbapi", const.DATA_API_SCHEMA_DIR, const.DATA_API_SCHEMA_ENDPOINT_TO_FILE["polymer_entity"])
            with open(polymer_entity_schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            local_schema_version = schema_data.get("$comment").split(": ")[1]
            local_major_minor_version = ".".join(local_schema_version.split(".")[:2])

            online_schema_url = "https://data.rcsb.org/rest/v1/schema/polymer_entity"
            response = httpx.get(online_schema_url, timeout=config.API_TIMEOUT)
            online_schema_data = response.json()
            online_schema_version = online_schema_data.get("$comment").split(": ")[1]
            online_major_minor_version = ".".join(online_schema_version.split(".")[:2])
            self.assertEqual(local_major_minor_version, online_major_minor_version)

        msg = "3. Compare polymer_entity_instance schema"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            polymer_entity_schema_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "rcsbapi",
                const.DATA_API_SCHEMA_DIR,
                const.DATA_API_SCHEMA_ENDPOINT_TO_FILE["polymer_entity_instance"]
            )
            with open(polymer_entity_schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            local_schema_version = schema_data.get("$comment").split(": ")[1]
            local_major_minor_version = ".".join(local_schema_version.split(".")[:2])

            online_schema_url = "https://data.rcsb.org/rest/v1/schema/polymer_entity_instance"
            response = httpx.get(online_schema_url, timeout=config.API_TIMEOUT)
            online_schema_data = response.json()
            online_schema_version = online_schema_data.get("$comment").split(": ")[1]
            online_major_minor_version = ".".join(online_schema_version.split(".")[:2])
            self.assertEqual(local_major_minor_version, online_major_minor_version)

    def testFetch(self) -> None:
        fetched_schema = DATA_SCHEMA.fetch_schema()
        self.assertNotIn("errors", fetched_schema.keys())

    def testConstructRootDict(self) -> None:
        msg = "1. root dict for singular type (interface)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            interface_dict = DATA_SCHEMA._root_dict["interface"]
            self.assertEqual(len(interface_dict), 3)
            arg_names = []
            for arg_dict in interface_dict:
                arg_names.append(arg_dict["name"])
            self.assertIn("assembly_id", arg_names)
            self.assertIn("interface_id", arg_names)
            self.assertIn("entry_id", arg_names)

        msg = "2. root dict for plural type (entries)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            entries_dict = DATA_SCHEMA._root_dict["entries"]
            self.assertEqual(len(entries_dict), 1)
            self.assertEqual(entries_dict[0]["name"], "entry_ids")
            self.assertEqual(entries_dict[0]["ofKind"], "LIST")

        msg = "3. root dict has the same number of types as schema"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            schema_list = DATA_SCHEMA._root_introspection["data"]["__schema"]["queryType"]["fields"]
            self.assertEqual(len(schema_list), len(list(DATA_SCHEMA._root_dict.keys())))

    def testConstructTypeDict(self) -> None:
        type_fields_dict = {}
        entry_dict = {}
        type_fields_dict = DATA_SCHEMA._construct_type_dict()
        entry_dict_from_func = type_fields_dict["CoreEntry"]
        type_dict_list = DATA_SCHEMA.schema["data"]["__schema"]["types"]
        entry_found = False
        i = 0
        while entry_found is False and i < len(type_dict_list):
            type_dict = type_dict_list[i]
            name = str(type_dict["name"])
            if name == "CoreEntry":
                fields = type_dict["fields"]
                field_dict = {}
                for field in fields:
                    field_dict[str(field["name"])] = dict(field["type"])
                entry_dict = field_dict
                entry_found = True
            i += 1
        self.assertEqual(entry_dict_from_func, entry_dict)
        self.assertEqual(len(type_dict_list), len(DATA_SCHEMA._type_fields_dict.keys()))

    def testConstructQuery(self) -> None:
        msg = "1. return data not specific enough"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids=["4HHB"], input_type="entry", return_data_list=["id"])

        msg = "1. multiple ids, but entered singular input_type"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids=["4HHB", "1IYE"], input_type="entry", return_data_list=["id"])

    def testConstructQueryRustworkX(self) -> None:
        msg = "1.  singular input_type (entry)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_ids={"entry_id": "4HHB"}, input_type="entry", return_data_list=["exptl"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "2. plural input_type (entries)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_ids={"entry_ids": ["4HHB", "1IYE"]}, input_type="entries", return_data_list=["exptl"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "3. two arguments (polymer_entity_instance)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_ids={"asym_id": "A", "entry_id": "4HHB"}, input_type="polymer_entity_instance", return_data_list=["exptl"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "4. three arguments (interface)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(
                input_ids={"assembly_id": "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["interface.rcsb_id"]
            )
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "5. request multiple return fields"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_ids={"entry_id": "4HHB"}, input_type="entry", return_data_list=["exptl", "rcsb_polymer_instance_annotation"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "6. request scalar field"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_ids={"entry_id": "4HHB"}, input_type="entry", return_data_list=["entry.rcsb_id"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        # Test error handling
        msg = "7. too many input ids passed in"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids={"entry_id": ["4HHB", "1IYE"]}, input_type="entry", return_data_list=["exptl"])

        msg = "8. too few inputs keys provided"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids={"entry_id": "4HHB"}, input_type="polymer_entity_instance", return_data_list=["exptl"])

        msg = "9. incorrect input keys provided"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids={"assembly_id": "1"}, input_type="polymer_entity_instance", return_data_list=["exptl"])

        msg = "10. no path exists"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids={"assembly_id": "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["exptl"])

        # msg = "11. field doesn't exist"
        # with self.subTest(msg=msg):
        #     logger.info("Running subtest %s", msg)
        #     with self.assertRaises(ValueError):
        #         DATA_SCHEMA.construct_query(input_ids={"assembly_id": "1", "interface_id": "1", "entry_id": "4HHB"}, input_type="interface", return_data_list=["aaa"])

        msg = "12. two arguments (polymer_entity_instances)"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(
                input_ids={"instance_ids": ["4HHB.A", "4HHB.C"]}, input_type="polymer_entity_instances", return_data_list=["rcsb_polymer_instance_annotation"]
            )
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "13. nested query"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_type="interfaces", return_data_list=["rcsb_interface_partner"], input_ids=["MA_MACOFFESLACC100000G1I2-1.1", "7XIW-1.2"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

        msg = "14. requesting scalars under same field"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_type="entry", return_data_list=["exptl.method", "exptl.details"], input_ids=["4HHB"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            self.assertNotIn("errors", response_json.keys())

    def regexChecks(self) -> None:
        msg = "1. regex for _entity_instances"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(
                input_type="polymer_entity_instances", return_data_list=["rcsb_polymer_instance_annotation"], input_ids=["4HHB.A", "AF_AFA0A009IHW8F1.B"]
            )
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            logger.info("response: %r", response_json)
            self.assertNotIn("errors", response_json.keys())

        msg = "2. regex for _entities"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(
                input_type="polymer_entities", return_data_list=["rcsb_polymer_entity_feature"], input_ids=["AF_AFA0A009IHW8F1_1", "4HHB_1"]
            )
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            logger.info("response: %r", response_json)
            self.assertNotIn("errors", response_json.keys())

        msg = "3. regex for entries"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_type="entries", return_data_list=["exptl"], input_ids=["7XIW", "4HHB"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            logger.info("response: %r", response_json)
            self.assertNotIn("errors", response_json.keys())

        msg = "4. regex for assemblies"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(
                input_type="assemblies",
                return_data_list=["rcsb_struct_symmetry_lineage"],
                input_ids=["4HHB-1", "MA_MACOFFESLACC100000G1I2-2"]
            )
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            logger.info("response: %r", response_json)
            self.assertNotIn("errors", response_json.keys())

        msg = "5. regex for interfaces"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(
                input_type="interfaces", return_data_list=["rcsb_interface_container_identifiers.assembly_id"], input_ids=["MA_MACOFFESLACC100000G1I2-1.1", "7XIW-1.2"]
            )
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            logger.info("response: %r", response_json)
            self.assertNotIn("errors", response_json.keys())

        msg = "6. regex with a singular type"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            query = DATA_SCHEMA.construct_query(input_type="entry", return_data_list=["exptl"], input_ids=["4HHB"])
            response_json = httpx.post(headers={"Content-Type": "application/json"}, json=query, url=const.DATA_API_ENDPOINT, timeout=config.API_TIMEOUT).json()
            logger.info("response: %r", response_json)
            self.assertNotIn("errors", response_json.keys())
            self.assertNotIn("errors", response_json.keys())

        msg = "7. wrong format for CSM entry id"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_type="entry", return_data_list=["exptl.method", "exptl.details"], input_ids=["MA_MACOFFESLACC100000G1I2-1.1"])

        msg = "8. id_list provided with incorrect input_type"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_type="assemblies", return_data_list=["exptl"], input_ids=["4HHB", "1IYE"])

    def testAllRoots(self) -> None:  # incomplete
        msg = "1. uniprot"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                DATA_SCHEMA.construct_query(
                    input_type="uniprot", input_ids={"uniprot_id": "P01308"}, return_data_list=["uniprot.rcsb_id", "reference_sequence_identifiers.database_accession"]
                )
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testDotNotation(self) -> None:
        msg = "1. dot notation on deeply nested path"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                DATA_SCHEMA.construct_query(
                    input_ids={"entry_id": "4HHB"},
                    input_type="entry",
                    return_data_list=[
                        "entry.assemblies.polymer_entity_instances.polymer_entity.polymer_entity_groups.group_provenance.rcsb_group_provenance_container_identifiers.group_provenance_id"
                    ],
                )
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        msg = "2. query that loops back to input type"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                DATA_SCHEMA.construct_query(
                    input_ids={"entry_id": "4HHB"},
                    input_type="entry",
                    return_data_list=["polymer_entities.entry.assemblies.polymer_entity_instances.polymer_entity.polymer_entity_instances.polymer_entity.entry.rcsb_id"],
                )
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        msg = "3. request same field at many levels"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                DATA_SCHEMA.construct_query(
                    input_ids={"entry_id": "4HHB"},
                    input_type="entry",
                    return_data_list=[
                        "entry.rcsb_id",
                        "entry.assemblies.rcsb_id",
                        "entry.assemblies.polymer_entity_instances.rcsb_id",
                        "entry.assemblies.polymer_entity_instances.polymer_entity.rcsb_id",
                        "entry.assemblies.polymer_entity_instances.polymer_entity.polymer_entity_groups.rcsb_id",
                        "entry.assemblies.polymer_entity_instances.polymer_entity.polymer_entity_groups.group_provenance.rcsb_id",
                    ],
                )
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        msg = "4. throw error when multiple paths are available"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.construct_query(input_ids=["4HHB"], input_type="entry", return_data_list=["chem_comp.id"])

    def testDescription(self) -> None:
        msg = "1. check nonpolymer_comp description"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            nonpolymer_comp_idx = DATA_SCHEMA._field_to_idx_dict["nonpolymer_comp"][0]
            description = DATA_SCHEMA._schema_graph[nonpolymer_comp_idx].description
            logger.info("Description for 'nonpolymer_comp': %s", DATA_SCHEMA._schema_graph[nonpolymer_comp_idx].description)
            self.assertEqual(description, "Get a non-polymer chemical components described in this molecular entity.")

    def testFindFieldNames(self) -> None:
        msg = "1. search for rcsb"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            result = DATA_SCHEMA.find_field_names("rcsb")
            self.assertIn("rcsb_id", result)

        msg = "2. search for nonexistent field"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(ValueError):
                DATA_SCHEMA.find_field_names("foo")

        msg = "3. search for field list"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            with self.assertRaises(TypeError):
                DATA_SCHEMA.find_field_names(["rcsb", "exptl"])  # type: ignore

    def testWeigh(self) -> None:
        msg = "1. Remove assembly paths that have a parallel/equivalent path"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            paths = [
                "entry.polymer_entities.polymer_entity_instances",
                "entry.polymer_entities.polymer_entity_instances.rcsb_id",
                "entry.assemblies.polymer_entity_instances.rcsb_id",  # This one should be removed based on equivalent path through "polymer_entities"
                "entry.exptl.method"
            ]
            idx_path_list = []
            for field_path in paths:
                index_paths = DATA_SCHEMA._parse_dot_path(field_path)
                logger.info("Index paths for %r:", field_path)
                for index_path in index_paths:
                    logger.info("  %r: %r", index_path, DATA_SCHEMA._idx_path_to_name_path(index_path))
                    idx_path_list.append(index_path)

            # Remove paths that don't begin at 'entry' root node
            full_idx_paths = []
            input_type_idx = DATA_SCHEMA._root_to_idx["entry"]
            logger.info("Input type ('entry') index: %r", input_type_idx)
            for idx_path in idx_path_list:
                if idx_path[0] == input_type_idx:
                    full_idx_paths.append(idx_path)
            logger.info("Filtered index paths:")
            for index_path in full_idx_paths:
                logger.info("  %r: %r", index_path, DATA_SCHEMA._idx_path_to_name_path(index_path))

            # Get the weigh node indexes of the 'assemblies' node (note: the root node index is excluded)
            assemblies_node_index_list = DATA_SCHEMA._find_weigh_nodes(["assemblies"])
            logger.info("'assemblies' node index list: %r", assemblies_node_index_list)

            weigh_paths = DATA_SCHEMA._weigh_node(full_idx_paths, assemblies_node_index_list)
            logger.info("Weighed index paths:")
            for index_path in weigh_paths:
                logger.info("  %r: %r", index_path, DATA_SCHEMA._idx_path_to_name_path(index_path))

            self.assertEqual(len(weigh_paths), 3)

        msg = "2. Do not remove paths without an equivalent path"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            paths = [
                "entry.polymer_entities.polymer_entity_instances",
                "entry.polymer_entities.polymer_entity_instances.rcsb_id",
                "entry.assemblies.polymer_entity_instances.rcsb_polymer_instance_annotation.annotation_id",
                "entry.polymer_entities.polymer_entity_instances.rcsb_polymer_instance_annotation.type",
                "entry.exptl.method"
            ]
            idx_path_list = []
            for field_path in paths:
                index_paths = DATA_SCHEMA._parse_dot_path(field_path)
                logger.info("Index paths for %r:", field_path)
                for index_path in index_paths:
                    logger.info("  %r: %r", index_path, DATA_SCHEMA._idx_path_to_name_path(index_path))
                    idx_path_list.append(index_path)

            # Remove paths that don't begin at 'entry' root node
            full_idx_paths = []
            input_type_idx = DATA_SCHEMA._root_to_idx["entry"]
            logger.info("Input type ('entry') index: %r", input_type_idx)
            for idx_path in idx_path_list:
                if idx_path[0] == input_type_idx:
                    full_idx_paths.append(idx_path)
            logger.info("Filtered index paths:")
            for index_path in full_idx_paths:
                logger.info("  %r: %r", index_path, DATA_SCHEMA._idx_path_to_name_path(index_path))

            # Get the weigh node indexes of the 'assemblies' node (note: the root node index is excluded)
            assemblies_node_index_list = DATA_SCHEMA._find_weigh_nodes(["assemblies"])
            logger.info("'assemblies' node index list: %r", assemblies_node_index_list)

            weigh_paths = DATA_SCHEMA._weigh_node(full_idx_paths, assemblies_node_index_list)
            logger.info("Weighed index paths:")
            for index_path in weigh_paths:
                logger.info("  %r: %r", index_path, DATA_SCHEMA._idx_path_to_name_path(index_path))

            self.assertEqual(len(weigh_paths), 5)


def buildSchema() -> unittest.TestSuite:
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SchemaTests("testSchemaVersion"))
    suiteSelect.addTest(SchemaTests("testFetch"))
    suiteSelect.addTest(SchemaTests("testConstructRootDict"))
    suiteSelect.addTest(SchemaTests("regexChecks"))
    suiteSelect.addTest(SchemaTests("testConstructQuery"))
    suiteSelect.addTest(SchemaTests("testAllRoots"))
    suiteSelect.addTest(SchemaTests("testDotNotation"))
    suiteSelect.addTest(SchemaTests("testConstructQueryRustworkX"))
    suiteSelect.addTest(SchemaTests("testDescription"))
    suiteSelect.addTest(SchemaTests("testFindFieldNames"))
    suiteSelect.addTest(SchemaTests("testWeigh"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildSchema()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
