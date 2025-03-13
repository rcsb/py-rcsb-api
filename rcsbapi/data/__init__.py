"""RCSB PDB Data API"""
from .data_schema import DataSchema

DATA_SCHEMA = DataSchema()

# This is needed because __getattr__ will be called twice on import,
# so ALL_STRUCTURES should be cached to avoid initializing twice
_import_cache: dict = {}


def __getattr__(name: str):
    """Overloading __getattr__ so that when ALL_STRUCTURES is accessed for the first time,
    ALL_STRUCTURES object will be built.

    Args:
        name (str): attribute name
    """
    if name == "ALL_STRUCTURES":
        if name not in _import_cache:
            from .data_query import AllStructures
            ALL_STRUCTURES = AllStructures()
            _import_cache[name] = ALL_STRUCTURES

        return _import_cache[name]  # Return cached instance

    # keep functionality of original __getattr__
    raise AttributeError(f"Module {repr(__name__)} has no attribute {repr(name)}")


from .data_query import DataQuery  # noqa:E402

__all__ = ["DataQuery", "DataSchema"]
