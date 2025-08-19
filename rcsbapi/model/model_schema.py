from typing import Dict, List, Optional
import httpx
from rcsbapi.const import const
from rcsbapi.config import config


class ModelSchema:
    def __init__(self, attr_data: Optional[Dict] = None, url: Optional[str] = None):
        """
        Initialize ModelSchema.
        """
        try:
            url = url if url else const.MODELSERVER_API_SCHEMA_URL
            response = httpx.get(url, timeout=config.API_TIMEOUT, headers={"Content-Type": "application/json", "User-Agent": const.USER_AGENT})
            response.raise_for_status()
            attr_data = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
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
                "type": param.get("schema", {}).get("type"),
                "default": param.get("schema", {}).get("default"),
            })
        return result

    def to_internal_schema(self) -> Dict[str, Dict[str, Dict]]:
        """Build a dictionary of endpoint"""

        internal_schema = {}
        for path, methods in self.paths.items():
            post_method = methods.get("get")
            entry = {
                "operation_id": post_method.get("operationId"),
                "parameters": self.extract_parameters(post_method.get("parameters", [])),
            }
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
