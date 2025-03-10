"""RCSB PDB Data API"""
from .data_schema import DataSchema

DATA_SCHEMA = DataSchema()


def __getattr__(name: str):
    """Overloading __getattr__ so that when ALL_STRUCTURES is accessed for the first time,
    ALL_STRUCTURES object will be built.

    Args:
        name (str): attribute name
    """
    if name == "ALL_STRUCTURES":
        from .data_query import AllStructures
        ALL_STRUCTURES = AllStructures()
        return ALL_STRUCTURES

    # keep functionality of original __getattr__
    raise AttributeError(f"Module {repr(__name__)} has no attribute {repr(name)}")


from .data_query import DataQuery  # noqa:E402

__all__ = ["DataQuery", "DataSchema"]
