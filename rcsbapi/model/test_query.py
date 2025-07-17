# from rcsbapi.model import model_query

# # Create an instance of ModelQuery
# model_query_instance = model_query.ModelQuery()

# # Now call the method on the instance
# response = model_query_instance.get_full_structure(
#     entry_id="1tqn",
#     model_nums="1,2",
#     encoding="cif",
#     copy_all_categories=False,
#     transform=None,
#     download=False,
#     # file_directory="C:/Users/Krish/Documents/gitRCSB/py-rcsb-api/tests/test-output",
#     # filename="1tqn_full_structure.cif",
#     compress_gzip=True,
# )
# print(response)

from rcsbapi.model import ModelQuery

# Fetch ligand data for the entry "2HHB"
query = ModelQuery()
ligand_result = query.get_ligand(entry_id="2HHB", label_comp_id="HEM")
print(ligand_result)


# file_directory = os.path.abspath("./test-out")
# print(file_directory)
# file_path = model_query_instance.get_full_structure(
#     entry_id="1tqn", encoding="cif", download=True, filename="1tqn_full_structure.cif", file_directory=file_directory
# )

# self.assertIsNotNone(file_path, f"Expected a {file_path}, but got None.")
# print(os.path.exists(file_path), f"File was not downloaded successfully: {file_path}")


# # Create an instance of the ModelQuery class
# model_query_instance = model_query.ModelQuery()

# # List of structure IDs to query
# entry_ids = ["1cbs", "1tqn"]

# # Fetch multiple structures (e.g., "full" type) and save the result
# results = model_query_instance.get_multiple_structures(entry_ids, query_type="full", encoding="cif", download=True)

# print(results)
