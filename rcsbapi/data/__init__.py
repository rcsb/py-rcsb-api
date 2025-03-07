"""RCSB PDB Data API"""
import sys
import requests
import json
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
    global _all_structures  # pylint: disable=W0602

    # When user tries to import ALL_STRUCTURES, below branch is entered
    if name == "ALL_STRUCTURES":
        # If _all_structures is None, create ALL_STRUCTURES dictionary and assign to _all_structures
        # ALL_STRUCTURES dict keys are `input_type`s and values are lists of corresponding IDs
        if _all_structures is None:
            ALL_STRUCTURES = {}
            for input_type, endpoints in const.INPUT_TYPE_TO_ALL_STRUCTURES_ENDPOINT.items():
                all_ids: List[str] = []
                for endpoint in endpoints:
                    response = requests.get(endpoint, timeout=60)
                    if response.status_code == 200:
                        all_ids.extend(json.loads(response.text))
                    else:
                        response.raise_for_status()
                ALL_STRUCTURES[input_type] = all_ids
            # Since ALL_STRUCTURES is assigned to _all_structures, IDs will be available next time ALL_STRUCTURES is used
            setattr(sys.modules[__name__], "_all_structures", ALL_STRUCTURES)

        return _all_structures

    # keep functionality of original __getattr__
    raise AttributeError(f"Module {repr(__name__)} has no attribute {repr(name)}")


from .data_query import DataQuery  # noqa:E402

__all__ = ["DataQuery", "DataSchema", "_all_structures"]
