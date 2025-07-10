import os
import requests
from typing import Optional
from model_schema import ModelSchema


BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"


class ModelQuery:
    def __init__(self):
        self.base_url = BASE_MODELSERVER_URL
        self.schema = ModelSchema()
        self.modelserver_endpoint_map = {
            "full": "full",
            "ligand": "ligand",
            "atoms": "atoms",
            "residue_interaction": "residueInteraction",
            "residue_surroundings": "residueSurroundings",
            "surrounding_ligands": "surroundingLigands",
            "symmetry_mates": "symmetryMates",
            "assembly": "assembly"
        }

        # This builds a map like {"full": ["encoding", ...], "ligand": [...], ...}
        self.full_param_map = self.schema.get_param_dict()

    def _exec(self, query_type: str, entry_id: str, **kwargs):
        """
        Execute the API call based on the query_type and parameters, including handling different encoding types.
        """
        endpoint = self._get_endpoint_for_type(query_type)
        url = f"{self.base_url}/{entry_id}/{endpoint}"

        # Prepare the query parameters
        query_params = {key: value for key, value in kwargs.items() if value is not None}

        try:
            response = requests.get(url, json=query_params)  # POST request with JSON params
            response.raise_for_status()  # Raise an error for bad responses

            # Get encoding type (defaults to CIF if not provided)
            encoding = kwargs.get('encoding', 'CIF').upper()

            # Handle response based on encoding type
            if encoding == 'BCIF':
                # Handle BCIF encoding
                file_content = response.text
                file_extension = 'bcif'
            elif encoding == 'SDF':
                # Handle SDF encoding
                file_content = response.text
                file_extension = 'sdf'
            elif encoding == 'MOL':
                # Handle MOL encoding
                file_content = response.text
                file_extension = 'mol'
            elif encoding == 'MOL2':
                # Handle MOL2 encoding
                file_content = response.text
                file_extension = 'mol2'
            else:
                # Default to CIF
                file_content = response.text
                file_extension = 'cif'

            filename = query_params.get('filename')
            file_directory = query_params.get('file_directory')

            if filename and file_directory:
                file_path = os.path.join(file_directory, filename)
            elif query_params.get('download') and filename:
                file_path = os.path.join(os.getcwd(), filename)
            elif query_params.get('download'):
                file_path = os.path.join(os.getcwd(), f"{entry_id}_{query_type}.{file_extension}")
            else:
                return file_content

            print("file_directory:", query_params.get('file_directory'))
            print("filename:", query_params.get('filename'))
            print("file_path:", file_path)

            # Write the content to the appropriate file
            with open(file_path, 'w' if encoding == 'BCIF' else 'w') as file:  # TODO: CHANGE 'w' TO APPROPRIATE
                file.write(file_content)
                print(f"Downloaded to {file_path}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def _get_endpoint_for_type(self, query_type: str) -> str:
        """
        Get the correct endpoint based on the query type.
        """
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

        if query_type not in modelserver_endpoint_map:
            raise ValueError(f"Unknown query type: {query_type}")

        return modelserver_endpoint_map[query_type]

    def get_full_structure(
            self,
            entry_id: str,
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            file_directory: Optional[str] = None,
            ):
        return self._exec(
            query_type="full",
            entry_id=entry_id,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
        )

    def get_ligand(
            self,
            entry_id: str,
            label_entity_id: Optional[str] = None,
            label_asym_id: Optional[str] = None,
            auth_asym_id: Optional[str] = None,
            label_comp_id: Optional[str] = None,
            auth_comp_id: Optional[str] = None,
            label_seq_id: Optional[int] = None,
            auth_seq_id: Optional[int] = None,
            pdbx_PDB_ins_code: Optional[str] = None,
            label_atom_id: Optional[str] = None,
            auth_atom_id: Optional[str] = None,
            type_symbol: Optional[str] = None,
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            file_directory: Optional[str] = None,
            ):

        return self._exec(
            query_type="ligand",
            entry_id=entry_id,
            label_entity_id=label_entity_id,
            label_asym_id=label_asym_id,
            auth_asym_id=auth_asym_id,
            label_comp_id=label_comp_id,
            auth_comp_id=auth_comp_id,
            label_seq_id=label_seq_id,
            auth_seq_id=auth_seq_id,
            pdbx_PDB_ins_code=pdbx_PDB_ins_code,
            label_atom_id=label_atom_id,
            auth_atom_id=auth_atom_id,
            type_symbol=type_symbol,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
        )

    # def get_atoms(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         type="atoms",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_residue_interaction(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         radius: Optional[float] = 5.0,
    #         assembly_name: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):
    #     return self._exec(
    #         query_type="residue_interaction",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         radius=radius,
    #         assembly_name=assembly_name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_residue_surroundings(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         radius: Optional[float] = 5.0,
    #         assembly_name: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):
    #     return self._exec(
    #         query_type="residue_surroundings",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         radius=radius,
    #         assembly_name=assembly_name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_surrounding_ligands(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         omit_water: Optional[bool] = False,
    #         radius: Optional[float] = 5.0,
    #         assembly_name: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         query_type="surrounding_ligands",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         omit_water=omit_water,
    #         assembly_name=assembly_name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_symmetry_mates(
    #         self,
    #         entry_id: str,
    #         radius: Optional[float] = 5.0,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         query_type="symmetry_mates",
    #         entry_id=entry_id,
    #         radius=radius,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_assembly(
    #         self,
    #         entry_id: str,
    #         name: Optional[str] = "1",
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         query_type="assembly",
    #         entry_id=entry_id,
    #         name=name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )
