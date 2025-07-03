from dataclasses import dataclass, fields
from typing import Optional, Dict, Any
import requests


@dataclass(frozen=True)
class Query:
    """Base class for RESTful ModelServer queries."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name != "id" and f.name != "query" and getattr(self, f.name) is not None
        }

    def build_url(self, base_url: str) -> str:
        raise NotImplementedError

    def exec(self, base_url: str) -> Any:
        url = self.build_url(base_url)
        response = requests.get(url, params=self.to_dict())
        response.raise_for_status()
        return response.content
    
    def get_editor_link(self) -> str:
        # To be implemented
    

@dataclass(frozen=True)
class Assembly(Query):
    id: str
    name: Optional[str] = "1"
    model_nums: Optional[str] = None
    encoding: Optional[str] = "cif"
    copy_all_categories: Optional[bool] = False
    data_source: Optional[str] = ""
    transform: Optional[str] = None
    download: Optional[bool] = False
    filename: Optional[str] = ""

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/assembly"


@dataclass(frozen=True)
class Atoms(Query):
    id: str
    label_entity_id: Optional[str] = None
    label_asym_id: Optional[str] = None
    auth_asym_id: Optional[str] = None
    label_comp_id: Optional[str] = None
    auth_comp_id: Optional[str] = None
    label_seq_id: Optional[int] = None
    auth_seq_id: Optional[int] = None
    pdbx_PDB_ins_code: Optional[str] = None
    label_atom_id: Optional[str] = None
    auth_atom_id: Optional[str] = None
    type_symbol: Optional[str] = None
    model_nums: Optional[str] = None
    encoding: Optional[str] = "cif"
    copy_all_categories: Optional[bool] = False
    data_source: Optional[str] = ""
    transform: Optional[str] = None
    download: Optional[bool] = False
    filename: Optional[str] = ""

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/atoms"


@dataclass(frozen=True)
class FullStructure(Query):
    id: str
    model_nums: Optional[str] = None
    encoding: Optional[str] = "cif"
    copy_all_categories: Optional[bool] = False
    data_source: Optional[str] = ""
    transform: Optional[str] = None
    download: Optional[bool] = False
    filename: Optional[str] = ""

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/full"


@dataclass(frozen=True)
class Ligand(Query):
    id: str
    label_entity_id: Optional[str] = None
    label_asym_id: Optional[str] = None
    auth_asym_id: Optional[str] = None
    label_comp_id: Optional[str] = None
    auth_comp_id: Optional[str] = None
    label_seq_id: Optional[int] = None
    auth_seq_id: Optional[int] = None
    pdbx_PDB_ins_code: Optional[str] = None
    label_atom_id: Optional[str] = None
    auth_atom_id: Optional[str] = None
    type_symbol: Optional[str] = None
    model_nums: Optional[str] = None
    encoding: Optional[str] = "cif"
    copy_all_categories: Optional[bool] = False
    data_source: Optional[str] = ""
    transform: Optional[str] = None
    download: Optional[bool] = False
    filename: Optional[str] = ""

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/ligand"


@dataclass(frozen=True)
class ResidueInteraction(Query):
    id: str
    label_entity_id: Optional[str] = None
    label_asym_id: Optional[str] = None
    auth_asym_id: Optional[str] = None
    label_comp_id: Optional[str] = None
    auth_comp_id: Optional[str] = None
    label_seq_id: Optional[int] = None
    auth_seq_id: Optional[int] = None
    pdbx_PDB_ins_code: Optional[str] = None
    label_atom_id: Optional[str] = None
    auth_atom_id: Optional[str] = None
    type_symbol: Optional[str] = None
    radius: Optional[float] = 5.0
    assembly_name: Optional[str] = None
    model_nums: Optional[str] = None
    encoding: Optional[str] = "cif"
    copy_all_categories: Optional[bool] = False
    data_source: Optional[str] = ""
    transform: Optional[str] = None
    download: Optional[bool] = False
    filename: Optional[str] = ""

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/residueInteraction"


@dataclass(frozen=True)
class ResidueSurroundings(ResidueInteraction):
    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/residueSurroundings"


@dataclass(frozen=True)
class SurroundingLigands(ResidueInteraction):
    omit_water: Optional[bool] = False

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/surroundingLigands"


@dataclass(frozen=True)
class SymmetryMates(Query):
    id: str
    radius: Optional[float] = 5.0
    model_nums: Optional[str] = None
    encoding: Optional[str] = "cif"
    copy_all_categories: Optional[bool] = False
    data_source: Optional[str] = ""
    transform: Optional[str] = None
    download: Optional[bool] = False
    filename: Optional[str] = ""

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/{self.id}/symmetryMates"


@dataclass(frozen=True)
class QueryMany(Query):
    query: str  # this will be a JSON string or already-encoded

    def to_dict(self) -> Dict[str, Any]:
        return {"query": self.query}

    def build_url(self, base_url: str) -> str:
        return f"{base_url}/v1/query-many"
