"""RCSB PDB Search API"""

from typing import List
from .search_query import SEARCH_SCHEMA  # noqa: F401
from .search_query import Attr, AttributeQuery, TextQuery
from .search_query import SeqSimilarityQuery, SeqMotifQuery, ChemSimilarityQuery, StructSimilarityQuery, StructMotifResidue, StructMotifQuery
from .search_query import Facet, FacetRange, TerminalFilter, GroupFilter, FilterFacet, Sort, GroupBy, RankingCriteriaType
from .search_query import Group

search_attributes = SEARCH_SCHEMA.search_attributes
group = Group.group


def __dir__() -> List[str]:
    return sorted(__all__)


__all__ = [
    "search_attributes",
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
