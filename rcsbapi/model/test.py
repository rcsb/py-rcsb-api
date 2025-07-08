from dataclasses import dataclass, fields
from typing import Optional, Dict, Any
import requests


class BaseQuery:
    def to_dict(self) -> Dict[str, Any]:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name not in {"id", "query"} and getattr(self, f.name) is not None
        }

    def exec(self, base_url: str = "https://models.rcsb.org") -> Any:
        url = self.build_url(base_url)
        response = requests.get(url, params=self.to_dict())
        response.raise_for_status()
        return response.content


@dataclass(frozen=True)
class Assembly(BaseQuery):
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
class FullStructure(BaseQuery):
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
class Ligand(BaseQuery):
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
class Atoms(BaseQuery):
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
class ResidueInteraction(BaseQuery):
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
class SymmetryMates(BaseQuery):
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


# @dataclass(frozen=True)
# class QueryMany(BaseQuery):
#     query: str

#     def to_dict(self) -> Dict[str, Any]:
#         return {"query": self.query}

#     def build_url(self, base_url: str) -> str:
#         return f"{base_url}/v1/query-many"


# The container class
class ModelQuery:
    Assembly = Assembly
    FullStructure = FullStructure
    Ligand = Ligand
    Atoms = Atoms
    ResidueInteraction = ResidueInteraction
    ResidueSurroundings = ResidueSurroundings
    SurroundingLigands = SurroundingLigands
    SymmetryMates = SymmetryMates
    # QueryMany = QueryMany


# import os
# import requests
# from typing import Optional

# # Constants (can be moved to a separate const.py if desired)
# BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"

# # Endpoint mapping for model types
# modelserver_endpoint_map = {
#     "full": "full",
#     "ligand": "ligand",
#     "atoms": "atoms",
#     "residue_interaction": "residueInteraction",
#     "residue_surroundings": "residueSurroundings",
#     "surrounding_ligands": "surroundingLigands",
#     "symmetry_mates": "symmetryMates",
#     "assembly": "assembly"
# }


# class ModelQuery:
#     def __init__(self):
#         self.base_url = BASE_MODELSERVER_URL

#     def get_full_structure(
#             self,
#             entry_id: str,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):

#         return self._exec(
#             type="full",
#             entry_id=entry_id,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_ligand(
#             self,
#             entry_id: str,
#             label_entity_id: Optional[str] = None,
#             label_asym_id: Optional[str] = None,
#             auth_asym_id: Optional[str] = None,
#             label_comp_id: Optional[str] = None,
#             auth_comp_id: Optional[str] = None,
#             label_seq_id: Optional[int] = None,
#             auth_seq_id: Optional[int] = None,
#             pdbx_PDB_ins_code: Optional[str] = None,
#             label_atom_id: Optional[str] = None,
#             auth_atom_id: Optional[str] = None,
#             type_symbol: Optional[str] = None,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):

#         return self._exec(
#             type="ligand",
#             entry_id=entry_id,
#             label_entity_id=label_entity_id,
#             label_asym_id=label_asym_id,
#             auth_asym_id=auth_asym_id,
#             label_comp_id=label_comp_id,
#             auth_comp_id=auth_comp_id,
#             label_seq_id=label_seq_id,
#             auth_seq_id=auth_seq_id,
#             pdbx_PDB_ins_code=pdbx_PDB_ins_code,
#             label_atom_id=label_atom_id,
#             auth_atom_id=auth_atom_id,
#             type_symbol=type_symbol,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_atoms(
#             self,
#             entry_id: str,
#             label_entity_id: Optional[str] = None,
#             label_asym_id: Optional[str] = None,
#             auth_asym_id: Optional[str] = None,
#             label_comp_id: Optional[str] = None,
#             auth_comp_id: Optional[str] = None,
#             label_seq_id: Optional[int] = None,
#             auth_seq_id: Optional[int] = None,
#             pdbx_PDB_ins_code: Optional[str] = None,
#             label_atom_id: Optional[str] = None,
#             auth_atom_id: Optional[str] = None,
#             type_symbol: Optional[str] = None,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):

#         return self._exec(
#             type="atoms",
#             entry_id=entry_id,
#             label_entity_id=label_entity_id,
#             label_asym_id=label_asym_id,
#             auth_asym_id=auth_asym_id,
#             label_comp_id=label_comp_id,
#             auth_comp_id=auth_comp_id,
#             label_seq_id=label_seq_id,
#             auth_seq_id=auth_seq_id,
#             pdbx_PDB_ins_code=pdbx_PDB_ins_code,
#             label_atom_id=label_atom_id,
#             auth_atom_id=auth_atom_id,
#             type_symbol=type_symbol,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_residue_interaction(
#             self,
#             entry_id: str,
#             label_entity_id: Optional[str] = None,
#             label_asym_id: Optional[str] = None,
#             auth_asym_id: Optional[str] = None,
#             label_comp_id: Optional[str] = None,
#             auth_comp_id: Optional[str] = None,
#             label_seq_id: Optional[int] = None,
#             auth_seq_id: Optional[int] = None,
#             pdbx_PDB_ins_code: Optional[str] = None,
#             label_atom_id: Optional[str] = None,
#             auth_atom_id: Optional[str] = None,
#             type_symbol: Optional[str] = None,
#             radius: Optional[float] = 5.0,
#             assembly_name: Optional[str] = None,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):
#         return self._exec(
#             type="residue_interaction",
#             entry_id=entry_id,
#             label_entity_id=label_entity_id,
#             label_asym_id=label_asym_id,
#             auth_asym_id=auth_asym_id,
#             label_comp_id=label_comp_id,
#             auth_comp_id=auth_comp_id,
#             label_seq_id=label_seq_id,
#             auth_seq_id=auth_seq_id,
#             pdbx_PDB_ins_code=pdbx_PDB_ins_code,
#             label_atom_id=label_atom_id,
#             auth_atom_id=auth_atom_id,
#             type_symbol=type_symbol,
#             radius=radius,
#             assembly_name=assembly_name,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_residue_surroundings(
#             self,
#             entry_id: str,
#             label_entity_id: Optional[str] = None,
#             label_asym_id: Optional[str] = None,
#             auth_asym_id: Optional[str] = None,
#             label_comp_id: Optional[str] = None,
#             auth_comp_id: Optional[str] = None,
#             label_seq_id: Optional[int] = None,
#             auth_seq_id: Optional[int] = None,
#             pdbx_PDB_ins_code: Optional[str] = None,
#             label_atom_id: Optional[str] = None,
#             auth_atom_id: Optional[str] = None,
#             type_symbol: Optional[str] = None,
#             radius: Optional[float] = 5.0,
#             assembly_name: Optional[str] = None,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):
#         return self._exec(
#             type="residue_surroundings",
#             entry_id=entry_id,
#             label_entity_id=label_entity_id,
#             label_asym_id=label_asym_id,
#             auth_asym_id=auth_asym_id,
#             label_comp_id=label_comp_id,
#             auth_comp_id=auth_comp_id,
#             label_seq_id=label_seq_id,
#             auth_seq_id=auth_seq_id,
#             pdbx_PDB_ins_code=pdbx_PDB_ins_code,
#             label_atom_id=label_atom_id,
#             auth_atom_id=auth_atom_id,
#             type_symbol=type_symbol,
#             radius=radius,
#             assembly_name=assembly_name,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_surrounding_ligands(
#             self,
#             entry_id: str,
#             label_entity_id: Optional[str] = None,
#             label_asym_id: Optional[str] = None,
#             auth_asym_id: Optional[str] = None,
#             label_comp_id: Optional[str] = None,
#             auth_comp_id: Optional[str] = None,
#             label_seq_id: Optional[int] = None,
#             auth_seq_id: Optional[int] = None,
#             pdbx_PDB_ins_code: Optional[str] = None,
#             label_atom_id: Optional[str] = None,
#             auth_atom_id: Optional[str] = None,
#             type_symbol: Optional[str] = None,
#             omit_water: Optional[bool] = False,
#             radius: Optional[float] = 5.0,
#             assembly_name: Optional[str] = None,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):

#         return self._exec(
#             type="surrounding_ligands",
#             entry_id=entry_id,
#             label_entity_id=label_entity_id,
#             label_asym_id=label_asym_id,
#             auth_asym_id=auth_asym_id,
#             label_comp_id=label_comp_id,
#             auth_comp_id=auth_comp_id,
#             label_seq_id=label_seq_id,
#             auth_seq_id=auth_seq_id,
#             pdbx_PDB_ins_code=pdbx_PDB_ins_code,
#             label_atom_id=label_atom_id,
#             auth_atom_id=auth_atom_id,
#             type_symbol=type_symbol,
#             omit_water=omit_water,
#             assembly_name=assembly_name,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_symmetry_mates(
#             self,
#             entry_id: str,
#             radius: Optional[float] = 5.0,
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):

#         return self._exec(
#             type="symmetry_mates",
#             entry_id=entry_id,
#             radius=radius,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def get_assembly(
#             self,
#             entry_id: str,
#             name: Optional[str] = "1",
#             model_nums: Optional[str] = None,
#             encoding: Optional[str] = "cif",
#             copy_all_categories: Optional[bool] = False,
#             data_source: Optional[str] = "",
#             transform: Optional[str] = None,
#             download: Optional[bool] = False,
#             filename: Optional[str] = "",
#             ):

#         return self._exec(
#             type="assembly",
#             entry_id=entry_id,
#             name=name,
#             model_nums=model_nums,
#             encoding=encoding,
#             copy_all_categories=copy_all_categories,
#             data_source=data_source,
#             transform=transform,
#             download=download,
#             filename=filename
#         )

#     def _exec(self, type, entry_id=None, **params):
#         endpoint = modelserver_endpoint_map.get(type)
#         if not endpoint:
#             raise ValueError(f"Unsupported type: {type}")

#         if not entry_id:
#             entry_id = params.get("entry_id")

#         if not entry_id:
#             raise ValueError("entry_id is required")

#         url = os.path.join(self.base_url, entry_id, endpoint)
#         clean_params = {k: v for k, v in params.items() if v is not None and k != "type"}

#         response = requests.get(url, params=clean_params)
#         response.raise_for_status()
#         return response.content

import os
import requests
from typing import Optional, Dict
from model_schema import ModelServerSchema

BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"

modelserver_endpoint_map = {
    "full": "full",
    "ligand": "ligand",
    "atoms": "atoms",
    "residue_interaction": "residueInteraction",
    "residue_surroundings": "residueSurroundings",
    "surrounding_ligands": "surroundingLigands",
    "symmetry_mates": "symmetryMates",
    "assembly": "assembly"
}


class ModelQuery:
    def __init__(self, schema_data: Dict):
        self.base_url = BASE_MODELSERVER_URL
        self.schema = ModelServerSchema(schema_data)
        param_whitelist = #something to get all the attributes associated with a query

    def get_structure(
        self,
        type: str,
        entry_id: str,
        download: bool = False,
        filename: Optional[str] = None,
        download_dir: str = "downloads",
        **kwargs
    ):
        if type not in modelserver_endpoint_map:
            raise ValueError(f"Unsupported type: {type}")
        if not entry_id:
            raise ValueError("entry_id is required")

        endpoint = modelserver_endpoint_map[type]
        allowed_params = self.param_whitelist.get(endpoint, set())

        query_keys = set(kwargs)
        invalid_keys = query_keys - allowed_params
        if invalid_keys:
            raise ValueError(f"Invalid parameter(s) for '{type}': {invalid_keys}")

        url = os.path.join(self.base_url, entry_id, endpoint)
        clean_params = {k: v for k, v in kwargs.items() if v is not None}

        response = requests.get(url, params=clean_params)
        response.raise_for_status()

        if download:
            # Create folder if needed
            os.makedirs(download_dir, exist_ok=True)

            # Determine file extension based on encoding
            ext = ".bcif" if kwargs.get("encoding") == "bcif" else ".cif"
            if not filename:
                filename = f"{entry_id}_{endpoint}{ext}"

            full_path = os.path.join(download_dir, filename)

            # Save file
            with open(full_path, "wb") as f:
                f.write(response.content)

            print(f"Downloaded to: {full_path}")
            return full_path

        return response.content

    # Optional shortcut methods
    def get_full_structure(self, entry_id: str, **kwargs):
        return self.get_structure("full", entry_id, **kwargs)

    def get_ligand(self, entry_id: str, **kwargs):
        return self.get_structure("ligand", entry_id, **kwargs)

    def get_atoms(self, entry_id: str, **kwargs):
        return self.get_structure("atoms", entry_id, **kwargs)

    def get_residue_interaction(self, entry_id: str, **kwargs):
        return self.get_structure("residue_interaction", entry_id, **kwargs)

    def get_residue_surroundings(self, entry_id: str, **kwargs):
        return self.get_structure("residue_surroundings", entry_id, **kwargs)

    def get_surrounding_ligands(self, entry_id: str, **kwargs):
        return self.get_structure("surrounding_ligands", entry_id, **kwargs)

    def get_symmetry_mates(self, entry_id: str, **kwargs):
        return self.get_structure("symmetry_mates", entry_id, **kwargs)

    def get_assembly(self, entry_id: str, **kwargs):
        return self.get_structure("assembly", entry_id, **kwargs)


# import os
# import requests
# from typing import Optional, Dict
# from model_schema import ModelSchema

# BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"


# class ModelQuery:
#     def __init__(self, schema_data: Dict):
#         self.base_url = BASE_MODELSERVER_URL
#         self.schema = ModelSchema(schema_data)
#         modelserver_endpoint_map = {
#             "full": "full",
#             "ligand": "ligand",
#             "atoms": "atoms",
#             "residue_interaction": "residueInteraction",
#             "residue_surroundings": "residueSurroundings",
#             "surrounding_ligands": "surroundingLigands",
#             "symmetry_mates": "symmetryMates",
#             "assembly": "assembly"
#         }

#         # This builds a map like {"full": ["encoding", ...], "ligand": [...], ...}
#         self.full_param_map = self.schema.get_param_dict()

#     def get_structure(
#         self,
#         query_type: str,
#         entry_id: str,
#         download: bool = False,
#         filename: Optional[str] = None,
#         download_dir: str = "downloads",
#         **kwargs
#     ):

#     def get_full_structure(self, entry_id: str, **kwargs):
#         full_struct_query = FullStructure(**kwargs)
#         return self.get_structure("full", entry_id, **kwargs)

#     def get_ligand(self, entry_id: str, **kwargs):
#         return self.get_structure("ligand", entry_id, **kwargs)

#     def get_atoms(self, entry_id: str, **kwargs):
#         return self.get_structure("atoms", entry_id, **kwargs)

#     def get_residue_interaction(self, entry_id: str, **kwargs):
#         return self.get_structure("residue_interaction", entry_id, **kwargs)

#     def get_residue_surroundings(self, entry_id: str, **kwargs):
#         return self.get_structure("residue_surroundings", entry_id, **kwargs)

#     def get_surrounding_ligands(self, entry_id: str, **kwargs):
#         return self.get_structure("surrounding_ligands", entry_id, **kwargs)

#     def get_symmetry_mates(self, entry_id: str, **kwargs):
#         return self.get_structure("symmetry_mates", entry_id, **kwargs)

#     def get_assembly(self, entry_id: str, **kwargs):
#         return self.get_structure("assembly", entry_id, **kwargs)
