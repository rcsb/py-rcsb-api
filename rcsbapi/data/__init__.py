"""RCSB PDB Search API"""
__version__ = "0.3.0"

import logging
from .schema import Schema

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()

SCHEMA = Schema()

from .query import Query  # noqa:E402

__all__ = ["Query", "Schema"]
