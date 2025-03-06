"""RCSB PDB Data API"""
import sys
import requests
import ast
from typing import Optional, Dict, List
from ..const import const
from .data_schema import DataSchema

DATA_SCHEMA = DataSchema()

_all_structures: Optional[Dict[str, List[str]]] = None


def __getattr__(name: str):
    """Overloading __getattr__ so that when ALL_STRUCTURES is accessed for the first time,
    ALL_STRUCTURES dictionary will be built. ALL_STRUCTURES is stored in global _all_structures

    Args:
        name (str): attribute name
    """
    # Edit global variable _all_structures
    global _all_structures

    if name == "ALL_STRUCTURES":
        if _all_structures is None:
            ALL_STRUCTURES = {}
            for input_type, endpoints in const.INPUT_TYPE_TO_ALL_STRUCTURES_ENDPOINT.items():
                all_ids = []
                for endpoint in endpoints:
                    all_ids.extend(ast.literal_eval(requests.get(endpoint, timeout=60).text))
                ALL_STRUCTURES[input_type] = all_ids
            setattr(sys.modules[__name__], "_all_structures", ALL_STRUCTURES)
        return _all_structures

    # keep
    raise AttributeError(f"Module {repr(__name__)} has no attribute {repr(name)}")


from .data_query import DataQuery  # noqa:E402

__all__ = ["DataQuery", "DataSchema", "_all_structures"]
