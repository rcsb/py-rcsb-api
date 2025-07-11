from rcsbapi.model import model_query

# Create an instance of ModelQuery
model_query_instance = model_query.ModelQuery()

# Now call the method on the instance
response = model_query_instance.get_full_structure(
    entry_id="1tqn",
    model_nums="1,2",
    encoding="bcif",
    copy_all_categories=False,
    transform=None,
    download=True,
    compress_gzip=True,
)
# print(response)
