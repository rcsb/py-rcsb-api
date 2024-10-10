from enum import Enum
from typing import Dict


class ApiSettings(Enum):
    API_ENDPOINT: str = "https://data.rcsb.org/graphql"
    TIMEOUT: int = 60


SINGULAR_TO_PLURAL: Dict[str, str] = {
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
}

ID_TO_SEPARATOR: Dict[str, str] = {
    "entity_id": "_",
    "asym_id": ".",
    "assembly_id": "-",
    "interface_id": "."
}
