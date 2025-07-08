"""Fetching and Parsing API's GraphQL schema."""

from __future__ import annotations
from typing import List, Dict, Any

from rcsbapi.const import const
from rcsbapi.config import config
from rcsbapi.graphql_schema import GQLSchema


class SeqSchema(GQLSchema):
    """GraphQL schema defining available fields, types, and how they are connected."""

    def __init__(self) -> None:
        super().__init__(
            endpoint=const.SEQUENCE_API_GRAPHQL_ENDPOINT,
            timeout=config.API_TIMEOUT,
            fallback_file=const.SEQUENCE_API_SCHEMA_FILENAME,
            weigh_nodes=[]
        )

    # pylint: disable=arguments-differ
    def construct_query(  # type: ignore[override]
        self,
        query_type: str,
        query_args: Dict[str, str] | dict[str, list[Any]],
        return_data_list: List[str],
        suppress_autocomplete_warning: bool = False
    ) -> Dict[str, Any]:
        """
        Construct a GraphQL query - currently only uses rustworkx.

        Args:
            query_type (str): type of query to make (ex: Alignments, Annotations, etc)
            query_args (dict[str, str] | dict[str, list[Any]]): dict of query_type-specific args
            return_data_list (list[str]): list of fields to request data for
            suppress_autocomplete_warning (bool, optional): Whether to suppress warning when
                autocompletion of paths is used. Defaults to False.

        Raises:
            ValueError: unknown field in the return_data_list

        Returns:
            dict: GraphQL query in JSON format
        """
        suppress_autocomplete_warning = config.SUPPRESS_AUTOCOMPLETE_WARNING if config.SUPPRESS_AUTOCOMPLETE_WARNING else suppress_autocomplete_warning

        unknown_return_list: List[str] = []
        for field in return_data_list:
            if "." in field:
                separate_fields = field.split(".")
                for sep_field in separate_fields:
                    if sep_field not in self._field_names_list:
                        unknown_return_list.append(sep_field)  # noqa: PERF401
            elif field not in self._field_names_list:
                unknown_return_list.append(field)
        if unknown_return_list:
            error_msg = f"Unknown item in return_data_list: {unknown_return_list}"
            raise ValueError(error_msg)
        query = self._construct_query_rustworkx(
            query_type=query_type,
            query_args=query_args,
            return_data_list=return_data_list,
            suppress_autocomplete_warning=suppress_autocomplete_warning,
        )
        return query

    def _construct_query_rustworkx(
        self,
        query_type: str,
        query_args: Dict[str, str] | dict[str, list[Any]],
        return_data_list: List[str],
        suppress_autocomplete_warning: bool = False
    ) -> Dict[str, Any]:
        """Construct a GraphQL query as a dict, if using rustworkx.

        Args:
            query_type (str): type of query to make (ex: Alignments, Annotations, etc)
            query_args (dict[str, str] | dict[str, list[Any]]): dict of query_type-specific args
            return_data_list (list[str]): list of fields to request data for
            suppress_autocomplete_warning (bool, optional): Whether to suppress warning when
                autocompletion of paths is used. Defaults to False.

        Returns:
            dict[str, Any]: GraphQL query as dict.
                Dict is JSON format needed for POST requests (https://sequence-coordinates.rcsb.org/#gql-api)
        """
        return super()._construct_query_rustworkx(
            query_type=query_type,
            query_args=query_args,
            return_data_list=return_data_list,
            suppress_autocomplete_warning=suppress_autocomplete_warning,
        )

    def find_field_names(self, search_string: str) -> list[str]:
        """Find field names that fully or partially match the search string.

        Args:
            search_string (str): string to search field names for

        Raises:
            ValueError: thrown when a type other than string is passed in for search_string
            ValueError: thrown when no fields match search_string

        Returns:
            list[str]: list of matching field names
        """
        return super().find_field_names(search_string)

    def fetch_schema(self) -> Dict[str, Any]:
        """Get the JSON schema defining the Sequence Coordinates API. Fallback to local file if necessary.

        Returns:
            Dict[str, Any]: JSON schema for Sequence Coordinates
        """
        return super()._abstract_fetch_schema(const.SEQUENCE_API_SCHEMA_FILENAME)
