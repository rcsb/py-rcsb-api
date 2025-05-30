"""RCSB PDB Sequence Coordinates API."""
from rcsbapi.sequence.seq_schema import SeqSchema

SEQ_SCHEMA = SeqSchema()

from rcsbapi.sequence.seq_query import Alignments, GroupAlignments, Annotations, GroupAnnotations, GroupAnnotationsSummary, AnnotationFilterInput  # noqa: E402

__all__ = [
    "AnnotationFilterInput",
    "SeqSchema",
    "Alignments",
    "Annotations",
    "GroupAlignments",
    "GroupAnnotations",
    "GroupAnnotationsSummary",
]
