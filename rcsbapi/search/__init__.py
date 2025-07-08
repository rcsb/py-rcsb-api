"""RCSB PDB Search API"""

from typing import List
from rcsbapi.search.search_query import SEARCH_SCHEMA  # noqa: F401
from rcsbapi.search.search_query import Attr, AttributeQuery, TextQuery, NestedAttributeQuery
from rcsbapi.search.search_query import SeqSimilarityQuery, SeqMotifQuery, ChemSimilarityQuery, StructSimilarityQuery, StructMotifResidue, StructMotifQuery
from rcsbapi.search.search_query import Facet, FacetRange, TerminalFilter, GroupFilter, FilterFacet, Sort, GroupBy, RankingCriteriaType
from rcsbapi.search.search_query import Group

search_attributes = SEARCH_SCHEMA.search_attributes
group = Group.group


def __dir__() -> List[str]:
    return sorted(__all__)


__all__ = [
    "search_attributes",
    "Attr",
    "TextQuery",
    "AttributeQuery",
    "NestedAttributeQuery",
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
