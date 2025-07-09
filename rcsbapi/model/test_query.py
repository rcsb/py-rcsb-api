from rcsbapi.model import model_query

# Create an instance of ModelQuery
model_query_instance = model_query.ModelQuery()

# Now call the method on the instance
response = model_query_instance.get_full_structure(
    entry_id="1tqn",            # PDB entry ID
    # model_nums="1,2",             # Model number to query (optional)
    # encoding="cif",             # File format (can be "pdb" or "cif")
    # copy_all_categories=False,  # Whether to copy all categories (optional)
    # transform=None,             # Transformation to apply (optional)
    download=True,              # Whether to download the structure (optional)
    filename="1tqn_structure.cif"  # Output filename for download (optional)
)

print(response)
