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
# import importlib
# import platform
# import resource
import time
import unittest
import requests

# from rcsbapi.data import query
from rcsbapi.data.query import Query
from rcsbapi.data.query import PDB_URL
from rcsbapi.data.query import SCHEMA
from rcsbsearchapi import rcsb_attributes as attrs

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
        # query_str = '{ entries(entry_ids: ["4HHB", "1IYE"]) {\n  exptl {\n     method_details\n     method\n     details\n     crystals_number\n  }\n}}'
        query_obj = Query({"entry_ids": ["4HHB","1IYE"]}, "entries",["exptl"])
        url = query_obj.get_editor_link()
        response_json = requests.get(url, timeout=10)
        self.assertEqual(response_json.status_code, 200)

    def testPostQuery(self):
        with self.subTest("1. Batching into requests with fewer Ids"):
            input_ids = []
            for _ in range(165):
                input_ids.append("4HHB")
            query_obj = Query({"entry_ids": input_ids}, "entries", ["exptl"])
            query_obj.post_query()
            # assert that the batch and merge functions are called
            # assert len of results is same as num of input ids

    def testParseGQLError(self):
        pass

    def testBatchIDs(self):
        input_ids = []
        for _ in range(165):
            input_ids.append("4HHB")
        query_obj = Query({"entry_ids": input_ids}, "entries", ["exptl"])
        batch_size = 50
        batched_ids = query_obj.batch_ids(batch_size)
        total_ids = 0
        for batch in batched_ids:
            len_id_batch = len(batch)
            self.assertLessEqual(len_id_batch, batch_size)
            total_ids += len_id_batch
        self.assertEqual(len(query_obj.get_input_ids_list()), total_ids)

    def testMergeResponse(self):
        # assert that the lengths are combined and all ids are present?
        pass

    def testReadMe(self):
        with self.subTest(msg="1. Background 1"):
            query_obj = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Exptl.method"])
            try:
                query_obj.post_query()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. Background 2"):
            query_obj = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
            try:
                query_obj.post_query()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="3. Helpful methods, get_editor_link()"):
            query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
            response = requests.get(query.get_editor_link(),timeout=5)
            self.assertEqual(response.status_code, 200)
        with self.subTest(msg="4. Helpful methods, get_unique_fields()"):
            try:
                SCHEMA.get_unique_fields("id")
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="5. Helpful methods, get_input_id_dict"):
            test_dict = SCHEMA.get_input_id_dict("polymer_entity_instance") 
            polymer_instance_keys = ["entry_id", "asym_id"]
            for key in polymer_instance_keys:
                self.assertIn(key ,test_dict.keys())
            for value in test_dict.values():
                self.assertIsNotNone(value)
        with self.subTest(msg="6. Troubleshooting, Not a unique field"):
            with self.assertRaises(ValueError):
                Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["id"])
            try:
                Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Entry.id"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testReadMeAddExamples(self):
        with self.subTest(msg="1. Entries"):
            try:
                Query(input_ids={"entry_ids": ["1STP","2JEF","1CDG"]},input_type="entries", return_data_list=[
                    "CoreEntry.rcsb_id", "Struct.title", "Exptl.method"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. Primary Citation"):
            try:
                Query(input_ids={"entry_ids": ["1STP","2JEF","1CDG"]},input_type="entries", return_data_list=[
                    "CoreEntry.rcsb_id", "RcsbAccessionInfo.initial_release_date", "AuditAuthor.name", "RcsbPrimaryCitation.pdbx_database_id_PubMed", "RcsbPrimaryCitation.pdbx_database_id_DOI"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="3. Polymer Entities"):
            try:
                Query(input_ids={"entity_ids":["2CPK_1","3WHM_1","2D5Z_1"]},input_type="polymer_entities", return_data_list=[
                    "CorePolymerEntity.rcsb_id", "RcsbEntitySourceOrganism.ncbi_taxonomy_id", "RcsbEntitySourceOrganism.ncbi_scientific_name", "cluster_id", "identity"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="4. Polymer Instances"):
            try:
                Query(input_ids={"instance_ids":["4HHB.A", "12CA.A", "3PQR.A"]},input_type="polymer_entity_instances", return_data_list=[
                    "CorePolymerEntityInstance.rcsb_id", "RcsbPolymerInstanceAnnotation.annotation_id", "RcsbPolymerInstanceAnnotation.name", "RcsbPolymerInstanceAnnotation.type"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="5. Carbohydrates"):
            try:
                Query(input_ids={"entity_ids":["5FMB_2", "6L63_3"]},input_type="branched_entities", return_data_list=[
                    "PdbxEntityBranch.type","PdbxEntityBranchDescriptor.type","PdbxEntityBranchDescriptor.descriptor"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="6. Sequence Positional Features"):
            try:
                Query(input_ids={"instance_ids":["1NDO.A"]},input_type="polymer_entity_instances", return_data_list=[
                    "CorePolymerEntityInstance.rcsb_id", "RcsbPolymerInstanceFeature.type", "RcsbPolymerInstanceFeatureFeaturePositions.beg_seq_id", "RcsbPolymerInstanceFeatureFeaturePositions.end_seq_id"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="7. Reference Sequence Identifiers"):
            try:
                Query(input_ids={"entry_ids": ["7NHM", "5L2G"]}, input_type="entries", return_data_list=[
                    "CoreEntry.rcsb_id", "RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers.database_accession", "RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers.database_name"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="8. Chemical Components"):
            try:
                Query(input_ids={"comp_ids":["NAG", "EBW"]}, input_type="chem_comps", return_data_list=[
                    "CoreChemComp.rcsb_id","ChemComp.type","ChemComp.formula_weight","ChemComp.name","ChemComp.formula","RcsbChemCompInfo.initial_release_date"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="9. Computed Structure Models"):
            try:
                Query(input_ids={"entry_ids": ["AF_AFP68871F1"]}, input_type="entries", return_data_list=["RcsbMaQaMetricGlobalMaQaMetricGlobal.type", "RcsbMaQaMetricGlobalMaQaMetricGlobal.value"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testQuickstartNotebook(self):
        with self.subTest(msg="1. GraphQL example query"):
            query = '''
            {
            entry(entry_id: "4HHB") {
                rcsb_entry_info {
                nonpolymer_bound_components
                }
            }
            }
            '''
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=PDB_URL, timeout=10).json()
            self.assertNotIn("errors", response_json.keys())
        with self.subTest(msg="1. Making Queries"):
            try:
                query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["nonpolymer_bound_components"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. input_ids, mult args"):
            try:
                query = Query(input_ids={"entry_id":"4HHB","asym_id":"A"},input_type="polymer_entity_instance", return_data_list=["nonpolymer_bound_components"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. input_ids, mult args"):
            try:
                query = Query(input_ids={"entry_id":"4HHB","asym_id":"A"},input_type="polymer_entity_instance", return_data_list=["nonpolymer_bound_components"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="3. input_ids, list as entry input_ids"):
            try:
                query = Query(input_ids=["4HHB"],input_type="entry", return_data_list=["nonpolymer_bound_components"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="4. input_ids, list as polymer instance input_ids"):
            try:
                query = Query(input_ids=["4HHB.A"],input_type="polymer_entity_instance", return_data_list=["nonpolymer_bound_components"])  # error
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="5. return_data_list, Not a unique field error"):
            with self.assertRaises(ValueError):
                Query(input_ids=["4HHB.A"],input_type="polymer_entity_instance", return_data_list=["nonpolymer_bound_components", "polymer_composition"])
        with self.subTest(msg="6. return_data_list, get_unique_fields() methods"):
            try:
                SCHEMA.get_unique_fields("polymer_composition")
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="7. return_data_list, corrected query with non-redundant field"):
            try:
                Query(input_ids={"entry_id": "4HHB"},input_type="entry", return_data_list=["nonpolymer_bound_components", "RcsbEntryInfo.polymer_composition"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="8. More complex queries, multiple ids"):
            try:
                Query(input_ids={"entry_ids": ["4HHB", "12CA", "3PQR"]},input_type="entries", return_data_list=["nonpolymer_bound_components"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="8. More complex queries, multiple return data"):
            try:
                Query(input_ids={"entry_id": "4HHB"},input_type="entry", return_data_list=["Citation.title", "nonpolymer_bound_components", "RcsbEntryInfo.polymer_composition", ])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testSearchDataNotebook(self):
        with self.subTest(msg="1. Construct search API query and request"):
            try:
                q1 = attrs.rcsb_entity_source_organism.taxonomy_lineage.name == "COVID-19 virus"
                q2 = attrs.rcsb_nonpolymer_entity_annotation.type == "SUBJECT_OF_INVESTIGATION"
                q3 = attrs.rcsb_polymer_entity_feature_summary.type == "modified_monomer"
                query = q1 & q2 & q3
                result_list = query()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
            self.assertGreaterEqual(len(list(result_list)), 10)
        with self.subTest(msg="2. Construct data API query and request"):
            try:
                data_query = Query(input_ids={"entry_ids":['6W61', '7ARF', '7AWU', '7C8B', '7JP0', '7JPZ', '7JQ0', '7JQ1', '7JQ2', '7JQ3']}, input_type="entries", return_data_list=[
                "CoreEntry.rcsb_id", "is_subject_of_investigation", "RcsbNonpolymerEntityInstanceContainerIdentifiers.comp_id", "Citation.title", "Citation.pdbx_database_id_DOI"])
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="3. Parse result"):
            try:
                json = data_query.get_response()["data"]["entries"]
                json[0]["rcsb_id"]
                json[0]["nonpolymer_entities"]
                json[0]["nonpolymer_entities"][0]["nonpolymer_entity_instances"]
                json[0]["nonpolymer_entities"][0]["nonpolymer_entity_instances"][0]["rcsb_nonpolymer_instance_validation_score"][0]["is_subject_of_investigation"]
                json[0]["nonpolymer_entities"][0]["nonpolymer_entity_instances"][0]["rcsb_nonpolymer_entity_instance_container_identifiers"]["comp_id"]
                json[0]["citation"][0]["title"]
                json[0]["citation"][0]["pdbx_database_id_DOI"]
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")            


        

def buildQuery():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(QueryTests("testBatchIDs"))
    suiteSelect.addTest(QueryTests("testReadMe"))
    suiteSelect.addTest(QueryTests("testReadMeAddExamples"))
    suiteSelect.addTest(QueryTests("testQuickstartNotebook"))
    suiteSelect.addTest(QueryTests("testSearchDataNotebook"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildQuery()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
