"""RCSB PDB Sequence Coordinates API"""
from .schema import SeqSchema

SEQ_SCHEMA = SeqSchema()

from .query import alignments, group_alignments, annotations, group_annotations, group_annotations_summary, AnnotationFilterInput  # noqa:E402

__all__ = [
    "SeqSchema",
    "alignments",
    "annotations",
    "group_alignments",
    "group_annotations",
    "group_annotations_summary",
    "AnnotationFilterInput",
]
