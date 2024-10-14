"""RCSB PDB Search API"""

from typing import List
# from .search_query import Terminal, Group, SearchQuery, SEARCH_SCHEMA  # noqa: F401
from .search_query import SEARCH_SCHEMA  # noqa: F401
from .search_query import Attr, AttributeQuery, TextQuery
from .search_query import SequenceQuery, SeqMotifQuery, ChemSimilarityQuery, StructSimilarityQuery, StructureMotifResidue, StructMotifQuery
from .search_query import Facet, Range, TerminalFilter, GroupFilter, FilterFacet, Sort, GroupBy, RankingCriteriaType

rcsb_attributes = SEARCH_SCHEMA.rcsb_attributes


def __dir__() -> List[str]:
    return sorted(__all__)


__all__ = [
    # "SearchQuery",
    # "Group",
    "rcsb_attributes",
    "Attr",
    # "Terminal",
    "TextQuery",
    "AttributeQuery",
    "SequenceQuery",
    "SeqMotifQuery",
    "ChemSimilarityQuery",
    "StructSimilarityQuery",
    "StructureMotifResidue",  # Change this to StructMotifResidue
    "StructMotifQuery",
    "Facet",
    "Range",  # Rename to prevent overlap?
    "TerminalFilter",
    "GroupFilter",
    "FilterFacet",
    "Sort",  # Rename to prevent overlap?
    "GroupBy",
    "RankingCriteriaType",
]
