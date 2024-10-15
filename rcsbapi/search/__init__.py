"""RCSB PDB Search API"""

from typing import List
from .search_query import SEARCH_SCHEMA  # noqa: F401
from .search_query import Attr, AttributeQuery, TextQuery
from .search_query import SeqSimilarityQuery, SeqMotifQuery, ChemSimilarityQuery, StructSimilarityQuery, StructMotifResidue, StructMotifQuery
from .search_query import Facet, FacetRange, TerminalFilter, GroupFilter, FilterFacet, Sort, GroupBy, RankingCriteriaType

rcsb_attributes = SEARCH_SCHEMA.rcsb_attributes


def __dir__() -> List[str]:
    return sorted(__all__)


__all__ = [
    "rcsb_attributes",
    "Attr",
    "TextQuery",
    "AttributeQuery",
    "SeqSimilarityQuery",
    "SeqMotifQuery",
    "ChemSimilarityQuery",
    "StructSimilarityQuery",
    "StructMotifResidue",
    "StructMotifQuery",
    "Facet",
    "FacetRange",
    "TerminalFilter",
    "GroupFilter",
    "FilterFacet",
    "Sort",  # Rename to prevent overlap?
    "GroupBy",
    "RankingCriteriaType",
]
