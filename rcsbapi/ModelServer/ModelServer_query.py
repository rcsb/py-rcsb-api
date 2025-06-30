import json
from .ModelServer_schema import ModelServerSchema


def load_schema_from_json(json_file_path: str) -> ModelServerSchema:
    """Load schema from a JSON file and return a ModelServerSchema instance."""
    with open(json_file_path) as file:
        spec_data = json.load(file)
    return ModelServerSchema(spec_data)


schema = load_schema_from_json("ModelServer.json")
internal = schema.to_internal_schema()
print(internal)
