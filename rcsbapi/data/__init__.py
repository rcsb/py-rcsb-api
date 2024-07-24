"""RCSB PDB Search API"""
__version__ = "0.1.0"

from .schema import Schema

SCHEMA = Schema()

from .query import Query

__all__ = ["Query", "Schema"]