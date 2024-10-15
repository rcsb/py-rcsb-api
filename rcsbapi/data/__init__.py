"""RCSB PDB Data API"""

from .data_schema import DataSchema

DATA_SCHEMA = DataSchema()

from .data_query import DataQuery  # noqa:E402

__all__ = ["DataQuery", "DataSchema"]
