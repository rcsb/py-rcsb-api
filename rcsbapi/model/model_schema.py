from typing import Dict, List, Optional
import requests
from rcsbapi.const import const
from rcsbapi.config import config


class ModelSchema:
    def __init__(self, attr_data: Optional[Dict] = None, url: Optional[str] = None):
        """
        Initialize ModelSchema.
        """
        try:
            response = requests.get(const.JSON_MODELSERVER_URL, timeout=config.API_TIMEOUT, headers={"Content-Type": "application/json", "User-Agent": const.USER_AGENT})
            response.raise_for_status()
            attr_data = response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch schema from {url}: {e}")

        self.Attr = attr_data
        self.paths = attr_data.get("paths", {})
        self.components = attr_data.get("components", {}).get("parameters", {})

    def resolve_parameter(self, param: Dict) -> Dict:
        """Resolve $ref if necessary"""
        if "$ref" in param:
            ref_name = param["$ref"].split("/")[-1]
            return self.components.get(ref_name, {})
        return param

    def extract_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Get key fields from parameters"""
        result = []
        for param in parameters:
            param = self.resolve_parameter(param)
            result.append({
                "name": param.get("name"),
                # "in": param.get("in"),
                # "required": param.get("required", False),
                "type": param.get("schema", {}).get("type"),
                # "enum": param.get("schema", {}).get("enum"),
                "default": param.get("schema", {}).get("default"),
                # "description": param.get("description", "")
            })
        return result

    def to_internal_schema(self) -> Dict[str, Dict[str, Dict]]:
        """Build a dictionary of endpoint"""

        internal_schema = {}
        for path, methods in self.paths.items():
            post_method = methods.get("get")
            entry = {
                # "summary": post_method.get("summary", ""),
                "operation_id": post_method.get("operationId"),
                # "tags": post_method.get("tags", []),
                "parameters": self.extract_parameters(post_method.get("parameters", [])),
                # "request_body_example": None,
                # "responses": list(post_method.get("responses", {}).keys())
            }

            # Extract example request body, if available
            # request_body = post_method.get("requestBody", {}).get("content", {})
            # if "application/json" in request_body:
            #     entry["request_body_example"] = request_body["application/json"].get("example")

            internal_schema[path] = entry

        return internal_schema

    def get_param_dict(self) -> Dict[str, List[str]]:
        """
        Return a dictionary mapping query types to a list of attribute names used as parameters.
        """
        query_map = {}
        for path, method_data in self.to_internal_schema().items():
            op_id = method_data.get("operation_id", path)
            param_names = [param["name"] for param in method_data["parameters"] if param.get("name")]
            query_map[op_id] = param_names
        return query_map


# if __name__ == "__main__":
#     # Instantiate the ModelServerSchema class
#     schema_data = {}
#     try:
#         schema = ModelSchema(schema_data)

#         # Fetch the parameter dictionary which maps query types to their attributes
#         param_dict = schema.get_param_dict()

#         print(param_dict)

#         # # Print out the query type and its corresponding attributes
#         # for query_type, attributes in param_dict.items():
#         #     print(f"\nQuery Type: {query_type}")
#         #     for attr in attributes:
#         #         print(f"  - {attr}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
