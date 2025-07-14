import unittest
import os
from rcsbapi.model import model_query


class ModelQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model_query = model_query.ModelQuery()
        self.test_directory = "./tests/test-out"
        self.entry_id = "1tqn"
        self.entry_ids = ["1tqn", "4HHB", "1STP"]

    def test_get_full_structure(self) -> None:
        with self.subTest(msg="1. Full structure query with additional parameters"):
            try:
                result = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", model_nums="1", transform="rotate", copy_all_categories=True
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

        with self.subTest(msg="2. Full structure query with additional parameters"):
            try:
                result = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", model_nums="2", copy_all_categories=False
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_ligand(self) -> None:
        with self.subTest(msg="1. Ligand query with additional parameters"):
            try:
                result = self.model_query.get_ligand(
                    entry_id=self.entry_id, label_entity_id="A", encoding="cif", label_seq_id=10, auth_comp_id="A00"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

        with self.subTest(msg="2. Ligand query with additional parameters"):
            try:
                result = self.model_query.get_ligand(
                    entry_id=self.entry_id, label_entity_id="B", encoding="mol", auth_comp_id="A00"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_atoms(self) -> None:
        with self.subTest(msg="1. Atoms query with additional parameters"):
            try:
                result = self.model_query.get_atoms(
                    entry_id=self.entry_id, label_entity_id="A", encoding="cif", label_atom_id="CA", model_nums="1"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

        with self.subTest(msg="2. Atoms query with additional parameters"):
            try:
                result = self.model_query.get_atoms(
                    entry_id=self.entry_id, label_entity_id="B", encoding="cif", label_atom_id="CA",
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_residue_interaction(self) -> None:
        with self.subTest(msg="1. Residue interaction query with expanded parameters"):
            try:
                result = self.model_query.get_residue_interaction(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", assembly_name="1", model_nums="1"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

        with self.subTest(msg="2. Residue interaction query with expanded parameters"):
            try:
                result = self.model_query.get_residue_interaction(
                    entry_id=self.entry_id, radius=5.0, encoding="bcif", assembly_name="2"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_residue_surroundings(self) -> None:
        with self.subTest(msg="1. Residue surroundings query with expanded parameters"):
            try:
                result = self.model_query.get_residue_surroundings(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", label_entity_id="A", auth_comp_id="A00"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

        with self.subTest(msg="2. Residue surroundings query with expanded parameters"):
            try:
                result = self.model_query.get_residue_surroundings(
                    entry_id=self.entry_id, radius=5.0, encoding="cif", label_entity_id="B"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_surrounding_ligands(self) -> None:
        with self.subTest(msg="1. Surrounding ligands query with additional parameters"):
            try:
                result = self.model_query.get_surrounding_ligands(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", omit_water=True
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_symmetry_mates(self) -> None:
        with self.subTest(msg="1. Symmetry mates query with expanded parameters"):
            try:
                result = self.model_query.get_symmetry_mates(
                    entry_id=self.entry_id, radius=10.0, encoding="cif", model_nums="1"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_get_assembly(self) -> None:
        with self.subTest(msg="1. Assembly query with additional parameters"):
            try:
                result = self.model_query.get_assembly(
                    entry_id=self.entry_id, name="1", encoding="cif", model_nums="1", transform="rotate"
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Failed: {e}")

    def test_download_file(self) -> None:
        with self.subTest(msg="1. Full structure download with compression and extra params"):
            try:
                file_path = self.model_query.get_full_structure(
                    entry_id=self.entry_id, encoding="cif", download=True, filename="1tqn_full_structure.cif",
                    file_directory=self.test_directory, model_nums="1"
                )
                self.assertIsNotNone(file_path)
                self.assertTrue(os.path.exists(file_path), "File was not downloaded.")
            except Exception as e:
                self.fail(f"Download failed: {e}")

    def test_get_multiple_structures(self) -> None:
        with self.subTest(msg="1. Get multiple structures with expanded parameters"):
            try:
                result = self.model_query.get_multiple_structures(
                    entry_ids=self.entry_ids, query_type="full", encoding="cif", model_nums="1", transform="rotate"
                )
                for a, value in result.items():
                    self.assertIsNone(value, f"Expected None for entry {a}")
            except Exception as e:
                self.fail(f"Failed: {e}")

        with self.subTest(msg="2. Get multiple structures with invalid entries"):
            try:
                result = self.model_query.get_multiple_structures(
                    entry_ids=["invalid_id"], query_type="full", encoding="cif", model_nums="1"
                )
                self.assertIsNone(result["invalid_id"])
            except Exception as e:
                self.assertIn("error", str(e).lower(), "Expected error for invalid entries")


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
    suiteSelect.addTest(ModelQueryTests("test_get_multiple_structures"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildQuery()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
