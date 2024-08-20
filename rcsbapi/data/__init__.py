"""RCSB PDB Search API"""
__version__ = "0.3.0"

from .schema import Schema

SCHEMA = Schema()

from .query import Query  # noqa:E402

__all__ = ["Query", "Schema"]
