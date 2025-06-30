from typing import Dict, List
from rich import print


class ModelServerSchema:
    def __init__(self, attr_data: Dict):
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
                "in": param.get("in"),
                "required": param.get("required", False),
                "type": param.get("schema", {}).get("type"),
                "enum": param.get("schema", {}).get("enum"),
                "default": param.get("schema", {}).get("default"),
                # "description": param.get("description", "")
            })
        return result

    def to_internal_schema(self) -> Dict[str, Dict[str, Dict]]:
        """Build a dictionary of endpoint"""

        internal_schema = {}
        for path, methods in self.paths.items():
            post_method = methods.get("post")
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
