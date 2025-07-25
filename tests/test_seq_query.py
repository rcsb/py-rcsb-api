##
# File:    test_seq_query.py
# Author:  Ivana Truong/RCSB PDB contributors
# Date:
#
# Update:
#
#
##
"""
Tests for all functions of the sequence-coordinates API module.
"""

import logging
import time
import unittest

from rcsbapi.sequence.seq_query import Alignments, GroupAlignments, Annotations, GroupAnnotations, GroupAnnotationsSummary, AnnotationFilterInput

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SeqTests(unittest.TestCase):
    def setUp(self) -> None:
        self.__startTime = time.time()
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self) -> None:
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testAnnotations(self) -> None:
        with self.subTest(msg="1. Annotations query with filter"):
            try:
                query_obj = Annotations(
                    reference="NCBI_GENOME",
                    sources=["PDB_INSTANCE"],
                    query_id="NC_000001",
                    filters=[
                        AnnotationFilterInput(
                            field="TYPE",
                            operation="EQUALS",
                            values=["BINDING_SITE"],
                            source="PDB_INSTANCE"
                        )
                    ],
                    return_data_list=["features.description"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testAlignments(self) -> None:
        with self.subTest(msg="1. Alignments query without filter"):
            try:
                query_obj = Alignments(
                    db_from="NCBI_PROTEIN",
                    db_to="PDB_ENTITY",
                    query_id="XP_642496",
                    return_data_list=["target_id"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="2. Alignments query with range"):
            try:
                query_obj = Alignments(
                    db_from="NCBI_PROTEIN",
                    db_to="PDB_ENTITY",
                    query_id="XP_642496",
                    range=[1, 10],
                    return_data_list=["target_id"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="3. Alignments query with target_alignments args"):
            try:
                query_obj = Alignments(
                    db_from="NCBI_PROTEIN",
                    db_to="PDB_ENTITY",
                    query_id="XP_642496",
                    range=[1, 100],
                    return_data_list=["target_alignments"],
                    data_list_args={
                        "target_alignments": {
                            "first": 10,
                            "offset": 5
                        },
                    }
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testGroupAlignments(self) -> None:
        with self.subTest(msg="1. group_alignments query without filter"):
            try:
                query_obj = GroupAlignments(
                    group="MATCHING_UNIPROT_ACCESSION",
                    group_id="P01112",
                    return_data_list=["target_alignments.aligned_regions", "target_id"],
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. group_alignments query with filter"):
            try:
                query_obj = GroupAlignments(
                    group="MATCHING_UNIPROT_ACCESSION",
                    group_id="P01112",
                    return_data_list=["target_alignments.aligned_regions", "target_id"],
                    filter=["8CNJ_1", "8FG4_1"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testGroupAnnotations(self) -> None:
        with self.subTest(msg="1. group_annotations query without filter"):
            try:
                query_obj = GroupAnnotations(
                    group="MATCHING_UNIPROT_ACCESSION",
                    group_id="P01112",
                    sources=["PDB_ENTITY"],
                    return_data_list=["features.name", "features.feature_positions", "target_id"],
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. group_annotations query with filter"):
            try:
                query_obj = GroupAnnotations(
                    group="MATCHING_UNIPROT_ACCESSION",
                    group_id="P01112",
                    sources=["PDB_ENTITY"],
                    filters=[
                        AnnotationFilterInput(
                            field="TYPE",
                            operation="EQUALS",
                            values=["BINDING_SITE"],
                            source="PDB_INSTANCE"
                        )
                    ],
                    return_data_list=["features.name", "features.feature_positions", "target_id"],
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testGroupAnnotationsSummary(self) -> None:
        with self.subTest(msg="1. group_annotations_summary query without filter"):
            try:
                query_obj = GroupAnnotationsSummary(
                    group="MATCHING_UNIPROT_ACCESSION",
                    group_id="P01112",
                    sources=["PDB_INSTANCE"],
                    return_data_list=["target_id", "features.type"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")
        with self.subTest(msg="2. group_annotations_summary query with filter"):
            try:
                query_obj = GroupAnnotationsSummary(
                    group="MATCHING_UNIPROT_ACCESSION",
                    group_id="P01112",
                    sources=["PDB_INSTANCE"],
                    filters=[
                        AnnotationFilterInput(
                            field="TYPE",
                            operation="EQUALS",
                            values=["BINDING_SITE"],
                            source="PDB_INSTANCE"
                        )
                    ],
                    return_data_list=["target_id", "features.type"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

    def testDocExamples(self) -> None:
        # These examples come from:
        # https://sequence-coordinates.rcsb.org/#examples

        with self.subTest(msg="1. UniProt - PDB Entity alignment"):
            try:
                query_obj = Alignments(
                    db_from="UNIPROT",
                    db_to="PDB_ENTITY",
                    query_id="P01112",
                    return_data_list=["query_sequence", "target_alignments", "aligned_regions"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="2. Computed Structure Model - NCBI protein alignment"):
            try:
                query_obj = Alignments(
                    db_from="PDB_ENTITY",
                    db_to="NCBI_PROTEIN",
                    query_id="AF_AFP68871F1_1",
                    return_data_list=["query_sequence", "target_alignments", "aligned_regions"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="3. Mapping UniProt annotations to a PDB Instance"):
            try:
                query_obj = Annotations(  # type: ignore
                    reference="PDB_INSTANCE",
                    sources=["UNIPROT"],
                    query_id="2UZI.C",
                    return_data_list=["target_id", "features"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="4. Human Chromosome 1 - PDB Entity alignment"):
            try:
                query_obj = Alignments(
                    db_from="NCBI_GENOME",
                    db_to="PDB_ENTITY",
                    query_id="NC_000001",
                    return_data_list=[
                        "target_alignments.target_id",
                        "target_alignments.orientation",
                        "target_alignments.aligned_regions"
                    ]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="5. Mapping PDB Instance ligands binding sites to Human Chromosome 1"):
            try:
                query_obj = Annotations(  # type: ignore
                    reference="NCBI_GENOME",
                    sources=["PDB_INSTANCE"],
                    query_id="NC_000001",
                    filters=[
                        AnnotationFilterInput(
                            field="TYPE",
                            operation="EQUALS",
                            values=["BINDING_SITE"],
                        )
                    ],
                    return_data_list=["target_id", "features"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")

        with self.subTest(msg="6. Mapping a PDB Instance to NCBI RefSeq proteins"):
            try:
                query_obj = Alignments(
                    db_from="PDB_INSTANCE",
                    db_to="NCBI_PROTEIN",
                    query_id="4Z36.A",
                    return_data_list=["query_sequence", "target_alignments"]
                )
                query_obj.exec()
            except Exception as error:
                self.fail(f"Failed unexpectedly: {error}")


def buildQuery() -> unittest.TestSuite:
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(SeqTests("testAnnotations"))
    suiteSelect.addTest(SeqTests("testAlignments"))
    suiteSelect.addTest(SeqTests("testGroupAlignments"))
    suiteSelect.addTest(SeqTests("testGroupAnnotations"))
    suiteSelect.addTest(SeqTests("testGroupAnnotationsSummary"))
    suiteSelect.addTest(SeqTests("testDocExamples"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildQuery()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
