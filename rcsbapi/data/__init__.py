"""RCSB PDB Data API"""
from .schema import Schema

SCHEMA = Schema()

from .query import Query  # noqa:E402

__all__ = ["Query", "Schema"]
