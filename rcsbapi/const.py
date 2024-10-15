from enum import Enum
# from typing import Dict


class Const(Enum):
    REQUESTS_PER_SECOND: int = 10
    STRUCTURE_INDEX: int = 0
    CHEMICAL_INDEX: int = 0
    STRUCTURE_ATTRIBUTE_SCHEMA_URL: str = "http://search.rcsb.org/rcsbsearch/v2/metadata/schema"
    STRUCTURE_ATTRIBUTE_SCHEMA_FILE: str = "resources/metadata_schema.json"
    CHEMICAL_ATTRIBUTE_SCHEMA_URL: str = "https://search.rcsb.org/rcsbsearch/v2/metadata/chemical/schema"
    CHEMICAL_ATTRIBUTE_SCHEMA_FILE: str = "resources/chemical_schema.json"
    SEARCH_SCHEMA_URL: str = "https://search.rcsb.org/schema/search/request/json-schema-rcsb_search_query.json"
    SEARCH_OPENAPI_SCHEMA_URL: str = "https://search.rcsb.org/openapi.json"
    STRUCTURE_ATTRIBUTE_SEARCH_SERVICE: str = "text"
    CHEMICAL_ATTRIBUTE_SEARCH_SERVICE: str = "text_chem"
    FULL_TEXT_SEARCH_SERVICE: str = "full_text"
    SEQUENCE_SEARCH_SERVICE: str = "sequence"
    SEQMOTIF_SEARCH_SERVICE: str = "seqmotif"
    STRUCT_SIM_SEARCH_SERVICE: str = "structure"
    STRUCTMOTIF_SEARCH_SERVICE: str = "strucmotif"
    CHEM_SIM_SEARCH_SERVICE: str = "chemical"
    SEQUENCE_SEARCH_MIN_NUM_OF_RESIDUES: int = 25
    SEQMOTIF_SEARCH_MIN_CHARACTERS: int = 2
    STRUCT_MOTIF_MIN_RESIDUES: int = 2
    STRUCT_MOTIF_MAX_RESIDUES: int = 10
    RCSB_SEARCH_API_QUERY_URL: str = "https://search.rcsb.org/rcsbsearch/v2/query"
    UPLOAD_URL: str = "https://user-upload.rcsb.org/v1/putMultipart"
    RETURN_UP_URL: str = "https://user-upload.rcsb.org/v1/download/"
