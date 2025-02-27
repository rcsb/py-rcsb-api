"""RCSB PDB Data API"""

from rcsbapi.const import const
from .data_schema import DataSchema

DATA_SCHEMA = DataSchema()
ALL_STRUCTURES = const.ALL_STRUCTURES

from .data_query import DataQuery  # noqa:E402

__all__ = ["DataQuery", "DataSchema", "ALL_STRUCTURES"]
