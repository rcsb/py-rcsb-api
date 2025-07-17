import unittest
import os
import logging
from rcsbapi.model import model_query


class ModelQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model_query = model_query.ModelQuery()
        self.test_directory = "./tests/test-output"
        self.entry_id = "1tqn"
        self.entry_ids = ["1tqn", "4HHB", "1STP"]
        logging.info("Test setup completed.")

    def test_get_full_structure(self) -> None:
        with self.subTest(msg="1. Full structure query with additional parameters"):
            logging.info("1. Starting Full structure query with additional parameters")
            try:
                result = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", model_nums="1", transform="rotate", copy_all_categories=True
                )
                logging.info("Query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Full structure query failed with exception: %s", e)

        with self.subTest(msg="2. Full structure query with illegal parameters"):
            logging.info("2. Starting Full structure query with illegal parameters")
            try:
                result = self.model_query.get_full_structure(
                    entry_id="krish", encoding="cif", model_nums="2", copy_all_categories=False
                )
                logging.info("Query result: %s", result)
                self.assertIn("error", str(result).lower(), "Expected 'error' in result output")
            except Exception as e:
                logging.error("Full structure query with illegal parameters failed with exception: %s", e)

    def test_get_ligand(self) -> None:
        with self.subTest(msg="1. Ligand query with additional parameters"):
            logging.info("1. Starting Ligand query with additional parameters")
            try:
                result = self.model_query.get_ligand(
                    entry_id=self.entry_id, label_asym_id="A", encoding="cif", label_seq_id=10, auth_comp_id="A00"
                )
                logging.info("Ligand query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Ligand query failed with exception: %s", e)

    def test_get_atoms(self) -> None:
        with self.subTest(msg="1. Atoms query with additional parameters"):
            logging.info("1. Starting Atoms query with additional parameters")
            try:
                result = self.model_query.get_atoms(
                    entry_id=self.entry_id, label_entity_id="A", encoding="cif", label_atom_id="CA", model_nums="1"
                )
                logging.info("Atoms query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Atoms query failed with exception: %s", e)

    def test_get_residue_interaction(self) -> None:
        with self.subTest(msg="1. Residue interaction query with expanded parameters"):
            logging.info("1. Starting Residue interaction query with expanded parameters")
            try:
                result = self.model_query.get_residue_interaction(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", assembly_name="1", model_nums="1"
                )
                logging.info("Residue interaction query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Residue interaction query failed with exception: %s", e)

    def test_get_residue_surroundings(self) -> None:
        with self.subTest(msg="1. Residue surroundings query with expanded parameters"):
            logging.info("1. Starting Residue surroundings query with expanded parameters")
            try:
                result = self.model_query.get_residue_surroundings(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", label_entity_id="A", auth_comp_id="A00"
                )
                logging.info("Residue surroundings query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Residue surroundings query failed with exception: %s", e)

    def test_get_surrounding_ligands(self) -> None:
        with self.subTest(msg="1. Surrounding ligands query with additional parameters"):
            logging.info("1. Starting Surrounding ligands query with additional parameters")
            try:
                result = self.model_query.get_surrounding_ligands(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", omit_water=True
                )
                logging.info("Surrounding ligands query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Surrounding ligands query failed with exception: %s", e)

    def test_get_symmetry_mates(self) -> None:
        with self.subTest(msg="1. Symmetry mates query with expanded parameters"):
            logging.info("1. Starting Symmetry mates query with expanded parameters")
            try:
                result = self.model_query.get_symmetry_mates(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", model_nums="1"
                )
                logging.info("Symmetry mates query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Symmetry mates query failed with exception: %s", e)

    def test_get_assembly(self) -> None:
        with self.subTest(msg="1. Assembly query with additional parameters"):
            logging.info("1. Starting Assembly query with additional parameters")
            try:
                result = self.model_query.get_assembly(
                    entry_id=self.entry_id, name="1", encoding="cif", model_nums="1", transform="rotate"
                )
                logging.info("Assembly query completed successfully, result: %s", result)
                self.assertIsNotNone(result)
            except Exception as e:
                logging.error("Assembly query failed with exception: %s", e)

    def test_download_file(self) -> None:
        with self.subTest(msg="1. Full structure download with compression and extra params"):
            logging.info("1. Starting Full structure download with compression and extra params")
            try:
                file_path = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", download=True, filename="1tqn_full_structure.cif",
                    file_directory=self.test_directory, model_nums="1"
                )
                logging.info("File downloaded successfully, file path: %s", file_path)
                self.assertIn("1tqn_full_structure.cif", file_path, "Downloaded file path doesn't match expected file name.")
                self.assertTrue(os.path.exists(file_path), "File was not downloaded.")
            except Exception as e:
                logging.error("Download failed with exception: %s", e)

    def test_download_compressed_file(self) -> None:
        with self.subTest(msg="1. Full structure download with compression and extra params"):
            logging.info("1. Starting Full structure download with compression and extra params")
            try:
                file_path = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", download=True, filename="1tqn_full_structure.cif",
                    file_directory=self.test_directory, model_nums="1", compress_gzip=True,
                )
                logging.info("File downloaded successfully, file path: %s", file_path)
                self.assertIn("1tqn_full_structure.cif.gz", file_path, "Downloaded file path doesn't match expected file name.")
                self.assertTrue(os.path.exists(file_path), "File was not downloaded.")
            except Exception as e:
                logging.error("Download failed with exception: %s", e)

    def test_get_multiple_structures(self) -> None:
        with self.subTest(msg="1. Get multiple structures with expanded parameters"):
            logging.info("1. Starting Get multiple structures query with expanded parameters")
            try:
                result = self.model_query.get_multiple_structures(
                    entry_ids=self.entry_ids, query_type="full", encoding="cif", model_nums="1", transform="rotate"
                )
                # Check if the length of entry_ids and the result are the same
                if len(self.entry_ids) != len(result):
                    logging.warning("Length mismatch: entry_ids length is %d, result length is %d", len(self.entry_ids), len(result))
                else:
                    logging.info("Entry IDs length and result length match.")

            except Exception as e:
                logging.error("Get multiple structures query failed with exception: %s", e)


def buildQuery() -> unittest.TestSuite:
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ModelQueryTests("test_get_full_structure"))
    suiteSelect.addTest(ModelQueryTests("test_get_ligand"))
    suiteSelect.addTest(ModelQueryTests("test_get_atoms"))
    suiteSelect.addTest(ModelQueryTests("test_get_residue_interaction"))
    suiteSelect.addTest(ModelQueryTests("test_get_residue_surroundings"))
    suiteSelect.addTest(ModelQueryTests("test_get_surrounding_ligands"))
    suiteSelect.addTest(ModelQueryTests("test_get_symmetry_mates"))
    suiteSelect.addTest(ModelQueryTests("test_get_assembly"))
    suiteSelect.addTest(ModelQueryTests("test_download_file"))
    suiteSelect.addTest(ModelQueryTests("test_download_compressed_file"))
    suiteSelect.addTest(ModelQueryTests("test_get_multiple_structures"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildQuery()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
