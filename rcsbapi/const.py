"""
Constants for rcsb-api (immutable and cannot be overridden)

These constants define fixed values used throughout the rcsb-api package,
including API endpoints, search services, and schema URLs. The values are
immutable and protected from modification during runtime.
"""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Const:
    # Search API constants
    STRUCTURE_INDEX: int = 0
    CHEMICAL_INDEX: int = 0
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

    SEARCH_API_SCHEMA_DIR = "search/resources"
    SEARCH_API_SCHEMA_BASE_URL = "http://search.rcsb.org/rcsbsearch/v2/metadata/"
    STRUCTURE_SCHEMA_FILE_NAME = "structure_schema.json"
    CHEMICAL_SCHEMA_FILE_NAME = "chemical_schema.json"
    SEARCH_API_SCHEMA_FILE_TO_ENDPOINT = MappingProxyType({
        STRUCTURE_SCHEMA_FILE_NAME: "schema",
        CHEMICAL_SCHEMA_FILE_NAME: "chemical/schema",
    })
    STRUCTURE_ATTRIBUTE_SCHEMA_URL: str = SEARCH_API_SCHEMA_BASE_URL + SEARCH_API_SCHEMA_FILE_TO_ENDPOINT[STRUCTURE_SCHEMA_FILE_NAME]
    STRUCTURE_ATTRIBUTE_SCHEMA_FILE: str = SEARCH_API_SCHEMA_DIR + "/" + STRUCTURE_SCHEMA_FILE_NAME
    CHEMICAL_ATTRIBUTE_SCHEMA_URL: str = SEARCH_API_SCHEMA_BASE_URL + SEARCH_API_SCHEMA_FILE_TO_ENDPOINT[CHEMICAL_SCHEMA_FILE_NAME]
    CHEMICAL_ATTRIBUTE_SCHEMA_FILE: str = SEARCH_API_SCHEMA_DIR + "/" + CHEMICAL_SCHEMA_FILE_NAME

    # Data API constants
    DATA_API_ENDPOINT: str = "https://data.rcsb.org/graphql"
    DATA_API_SCHEMA_DIR: str = "data/resources"
    DATA_API_SCHEMA_BASE_URL: str = "https://data.rcsb.org/rest/v1/schema/"
    DATA_API_SCHEMA_FILE_TO_ENDPOINT = MappingProxyType({
        "entry.json": "entry",
        "polymer_entity.json": "polymer_entity",
        "branched_entity.json": "branched_entity",
        "nonpolymer_entity.json": "nonpolymer_entity",
        "polymer_entity_instance.json": "polymer_entity_instance",
        "branched_entity_instance.json": "branched_entity_instance",
        "nonpolymer_entity_instance.json": "nonpolymer_entity_instance",
        "assembly.json": "assembly",
        "chem_comp.json": "chem_comp",
        "pubmed.json": "pubmed",
        "uniprot.json": "uniprot",
        "drugbank.json": "drugbank",
    })

    SINGULAR_TO_PLURAL = MappingProxyType({
        "entry": "entries",
        "polymer_entity": "polymer_entities",
        "branched_entity": "branched_entities",
        "nonpolymer_entity": "nonpolymer_entities",
        "polymer_entity_instance": "polymer_entity_instances",
        "nonpolymer_entity_instance": "nonpolymer_entity_instances",
        "branched_entity_instance": "branched_entity_instances",
        "assembly": "assemblies",
        "interface": "interfaces",
        "uniprot": "",
        "pubmed": "",
        "chem_comp": "chem_comps",
        "entry_group": "entry_groups",
        "polymer_entity_group": "polymer_entity_groups",
        "group_provenance": ""
    })
    #
    ID_TO_SEPARATOR = MappingProxyType({
        "entity_id": "_",
        "asym_id": ".",
        "assembly_id": "-",
        "interface_id": "."
    })


const = Const()
