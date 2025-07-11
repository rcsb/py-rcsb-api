import unittest
from rcsbapi.model import model_query


class ModelQueryTests(unittest.TestCase):

    def setUp(self):
        self.model_query = model_query.ModelQuery()

    def test_get_full_structure(self):
        try:
            result = self.model_query.get_full_structure(entry_id="1tqn", encoding="cif")
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_full_structure raised an exception: {e}")

    def test_get_ligand(self):
        try:
            result = self.model_query.get_ligand(entry_id="1tqn", label_entity_id="A")
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_ligand raised an exception: {e}")

    def test_get_atoms(self):
        try:
            result = self.model_query.get_atoms(entry_id="1tqn", label_entity_id="A")
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_atoms raised an exception: {e}")

    def test_get_residue_interaction(self):
        try:
            result = self.model_query.get_residue_interaction(entry_id="1tqn", radius=5.0)
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_residue_interaction raised an exception: {e}")

    def test_get_residue_surroundings(self):
        try:
            result = self.model_query.get_residue_surroundings(entry_id="1tqn", radius=5.0)
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_residue_surroundings raised an exception: {e}")

    def test_get_surrounding_ligands(self):
        try:
            result = self.model_query.get_surrounding_ligands(entry_id="1tqn", radius=5.0)
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_surrounding_ligands raised an exception: {e}")

    def test_get_symmetry_mates(self):
        try:
            result = self.model_query.get_symmetry_mates(entry_id="1tqn", radius=5.0)
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_symmetry_mates raised an exception: {e}")

    def test_get_assembly(self):
        try:
            result = self.model_query.get_assembly(entry_id="1tqn", name="1")
            self.assertIsNotNone(result, "Expected result, but got None.")
        except Exception as e:
            self.fail(f"get_assembly raised an exception: {e}")


def buildQuery():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ModelQueryTests("test_get_full_structure"))
    suiteSelect.addTest(ModelQueryTests("test_get_ligand"))
    suiteSelect.addTest(ModelQueryTests("test_get_atoms"))
    suiteSelect.addTest(ModelQueryTests("test_get_residue_interaction"))
    suiteSelect.addTest(ModelQueryTests("test_get_residue_surroundings"))
    suiteSelect.addTest(ModelQueryTests("test_get_surrounding_ligands"))
    suiteSelect.addTest(ModelQueryTests("test_get_symmetry_mates"))
    suiteSelect.addTest(ModelQueryTests("test_get_assembly"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = buildQuery()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
