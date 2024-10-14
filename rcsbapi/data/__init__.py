"""RCSB PDB Data API"""

from .data_schema import DataSchema
from .data_query import DataQuery  # noqa:E402

DATA_SCHEMA = DataSchema()


__all__ = ["DataQuery", "DataSchema"]
