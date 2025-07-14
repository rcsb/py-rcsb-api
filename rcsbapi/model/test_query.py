from rcsbapi.model import model_query

# Create an instance of ModelQuery
# model_query_instance = model_query.ModelQuery()

# Now call the method on the instance
# response = model_query_instance.get_full_structure(
#     entry_id="1tqn",
#     model_nums="1,2",
#     encoding="bcif",
#     copy_all_categories=False,
#     transform=None,
#     download=True,
#     compress_gzip=True,
# )
# print(response)

# Create an instance of the ModelQuery class
model_query_instance = model_query.ModelQuery()

# List of structure IDs to query
entry_ids = ["1tqn", "1tqn", "1tqn"]

# Fetch multiple structures (e.g., "full" type) and save the result
results = model_query_instance.get_multiple_structures(entry_ids, query_type="full", encoding="cif", download=True)
