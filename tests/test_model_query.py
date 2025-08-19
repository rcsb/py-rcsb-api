import unittest
import os
import logging
from rcsbapi.model import ModelQuery

logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HERE = os.path.abspath(os.path.dirname(__file__))


class ModelQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model_query = ModelQuery()
        self.test_output_directory = os.path.join(HERE, "test-output")
        self.entry_id = "1tqn"
        self.entry_ids = ["1tqn", "4HHB", "1STP"]
        logger.info("Test setup completed.")

    def log_first_and_last_lines(self, result: str) -> str:
        """
        Return the first 10 and last 15 lines of the given multiline string.

        Useful for logging or previewing large content while skipping the middle portion.

        Parameters:
            result (str): The input string containing multiple lines.

        Returns:
            str: A string with the first 10 lines, an ellipsis separator if needed,
                and the last 15 lines (or fewer if not enough lines).
        """
        lines = result.splitlines()
        first_10 = lines[:10]
        last_15 = lines[-15:] if len(lines) > 10 else lines[10:]
        combined = first_10
        if len(lines) > 25:
            combined += ["...", *last_15]
        else:
            combined += last_15
        return "\n".join(combined)

    def test_get_full_structure(self) -> None:
        msg = "1. Full structure query with additional parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_full_structure(
                    entry_id="2HHB",
                    encoding="cif",
                )
                logger.info("Query completed successfully, result beginning and end: %s\n...\n%s", result[:500], result[-700:])
                self.assertTrue("_atom_site.Cartn_x" in result)
            except Exception as e:
                logger.error("Full structure query failed with exception: %s", e)

        msg = "2. Full structure query with illegal parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_full_structure(
                    entry_id="krish", encoding="cif", model_nums=[2], copy_all_categories=False
                )
                logger.info("Query result: %s", self.log_first_10_lines(result))
                self.assertIn("error", str(result).lower(), "Expected 'error' in result output")
            except Exception as e:
                logger.error("Full structure query with illegal parameters failed with exception: %s", e)

    def test_get_ligand(self) -> None:
        msg = "1. Ligand query with additional parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_ligand(entry_id="4HHB", label_comp_id="HEM")
                logger.info("Ligand query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Ligand query failed with exception: %s", e)

    def test_get_atoms(self) -> None:
        msg = "1. Atoms query with additional parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_atoms(entry_id="4HHB", label_comp_id="HEM")
                logger.info("Atoms query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Atoms query failed with exception: %s", e)

    def test_get_residue_interaction(self) -> None:
        msg = "1. Residue interaction query with expanded parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_residue_interaction(
                    entry_id="4HHB",
                    label_comp_id="HEM",
                    label_asym_id="E",
                    radius=5.0,
                )
                logger.info("Residue interaction query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Residue interaction query failed with exception: %s", e)

    def test_get_residue_surroundings(self) -> None:
        msg = "1. Residue surroundings query with expanded parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_residue_surroundings(
                    entry_id="4HHB",
                    label_comp_id="HEM",
                    label_asym_id="E",
                    radius=5.0,
                )
                logger.info("Residue surroundings query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Residue surroundings query failed with exception: %s", e)

    def test_get_surrounding_ligands(self) -> None:
        msg = "1. Surrounding ligands query with additional parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_surrounding_ligands(
                    entry_id="1TQN",
                    label_comp_id="ALA",
                    label_seq_id=284,
                    radius=5.0,
                )
                logger.info("Surrounding ligands query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Surrounding ligands query failed with exception: %s", e)

    def test_get_symmetry_mates(self) -> None:
        msg = "1. Symmetry mates query with expanded parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_symmetry_mates(entry_id="1TQN")
                logger.info("Symmetry mates query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Symmetry mates query failed with exception: %s", e)

    def test_get_assembly(self) -> None:
        msg = "1. Assembly query with additional parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_assembly(entry_id="13PK", name="3")
                logger.info("Assembly query completed successfully, result: %s", self.log_first_and_last_lines(result))
                self.assertIsNotNone(result)
            except Exception as e:
                logger.error("Assembly query failed with exception: %s", e)

    def test_download_file(self) -> None:
        msg = "1. Full structure download with extra params"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                file_path = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", download=True, filename="1tqn_full_structure.cif",
                    file_directory=self.test_output_directory, model_nums=[1]
                )
                logger.info("File downloaded successfully, file path: %s", file_path)
                self.assertIn("1tqn_full_structure.cif", file_path, "Downloaded file path doesn't match expected file name.")
                self.assertTrue(os.path.exists(file_path), "File was not downloaded.")
            except Exception as e:
                logger.error("Download failed with exception: %s", e)

    def test_download_compressed_file(self) -> None:
        msg = "1. Full structure download with compression and extra params"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                file_path = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", download=True, filename="1tqn_full_structure.cif",
                    file_directory=self.test_output_directory, model_nums=[1], compress_gzip=True,
                )
                logger.info("File downloaded successfully, file path: %s", file_path)
                self.assertIn("1tqn_full_structure.cif.gz", file_path, "Downloaded file path doesn't match expected file name.")
                self.assertTrue(os.path.exists(file_path), "File was not downloaded.")
            except Exception as e:
                logger.error("Download failed with exception: %s", e)

    def test_get_multiple_structures(self) -> None:
        msg = "1. Get multiple structures with expanded parameters"
        with self.subTest(msg=msg):
            logger.info("Running subtest %s", msg)
            try:
                result = self.model_query.get_multiple_structures(
                    entry_ids=self.entry_ids, query_type="full", encoding="cif", model_nums=[1], transform="rotate"
                )
                # Check if the length of entry_ids and the result are the same
                if len(self.entry_ids) != len(result):
                    logger.warning("Length mismatch: entry_ids length is %d, result length is %d", len(self.entry_ids), len(result))
                else:
                    logger.info("Entry IDs length and result length match.")

            except Exception as e:
                logger.error("Get multiple structures query failed with exception: %s", e)


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
