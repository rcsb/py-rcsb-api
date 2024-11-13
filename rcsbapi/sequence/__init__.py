"""RCSB PDB Sequence Coordinates API"""
from .schema import CoordSchema

COORD_SCHEMA = CoordSchema()

from .query import alignments, annotations, AnnotationFilterInput  # noqa:E402 (ignore that import is not at top)

__all__ = [
    "CoordSchema",
    "alignments",
    "annotations",
    "AnnotationFilterInput",
]
