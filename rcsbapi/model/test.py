from rcsbapi.model import ModelQuery
query = ModelQuery(compress_gzip=True, download=True, encoding='bcif', file_directory="model-output")  # setting 'bcif' up front, not propagated to result
result = query.get_assembly(entry_id="13PK", name="3")
print(result)