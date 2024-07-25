"""RCSB PDB Search API"""
__version__ = "0.1.0"

from .schema import Schema

SCHEMA = Schema()

from .query import Query  # nopep8:E402

__all__ = ["Query", "Schema"]
