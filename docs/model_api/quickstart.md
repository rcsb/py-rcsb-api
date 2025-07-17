# Quickstart
This is a quickstart guide to interacting with the RCSB PDB [ModelServer Coordinates API](https://models.rcsb.org/) using the *rcsb-api* Python package.

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

## Import
To import this module, use:
```python
import rcsbapi.model
```

## Getting Started
The RCSB [ModelServer API](https://models.rcsb.org/) provides access to molecular structure data and related information. The Model Server API allows you to query for various structural data types, such as full structure, ligands, atoms, residue interactions, and more.

Key Features
- Full Structure Data: Access complete structural information about biomolecules in different formats (e.g., CIF, BCIF).
- Ligand Information: Retrieve detailed data about ligands, including their chemical structure and interactions with other components.
- Atoms and Residue Data: Query for atom-level or residue-level data, including surrounding residues, interactions, and symmetries.
- Symmetry Mates and Assemblies: Obtain symmetry mates or assembly data, important for understanding molecular structures in different environments.

The API supports queries for Experimental Structures but not Computed Structure Models (CSMs).

### Query Types

The Model Server API supports multiple query types, including:

- full: Fetches the full structure for a given entry.
- ligand: Retrieves ligand-related information, including components and interactions.
- atoms: Fetches atom-level details.
- residue_interaction: Retrieves data on interactions between residues.
- residue_surroundings: Provides information about residues surrounding a given structure.
- symmetry_mates: Retrieves symmetry-related data.
- assembly: Fetches information about molecular assemblies.

This package provides an interface to the Model Server API, making it easy to send requests and retrieve data in various formats.


### API Usage
The API is based on standard HTTP requests, and you can specify different parameters depending on the query type. For example, you can query specific structures, specify encoding formats (like CIF or BCIF), request data downloads, or even compress data using GZIP.

You can use this API to automate data retrieval and integrate it into your bioinformatics or structural biology workflow.


## Full Structure

`Full Structure` queries fetch complete structural data for a given entry.

```python
from rcsbapi.model_query import ModelQuery

# Fetch the full structure for the entry "2HHB"
query = ModelQuery()
result = query.get_full_structure(entry_id="2HHB")
print(result)
```

| Argument              | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                     |
| `model_nums`          | The model numbers to fetch (optional)                      |
| `encoding`            | The encoding format for the response (`cif`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)            |
| `data_source`         | The data source for the structure                          |
| `transform`           | Apply any transformations (optional)                       |
| `download`            | Whether to download the file (True/False)                  |
| `filename`            | The name of the file to save                               |
| `file_directory`      | Directory to save the file                                 |
| `compress_gzip`       | Whether to compress the file (default: False)              |


## Ligand Data

`Ligand` queries fetch ligand-related data for a given structure.

```python
from rcsbapi.model_query import ModelQuery

# Fetch ligand data for the entry "2HHB"
query = ModelQuery()
ligand_result = query.get_ligand(entry_id="2HHB", label_comp_id="HEM")
print(ligand_result)
```

| Argument              | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                                     |
| `label_entity_id`     | The entity label for the ligand                                            |
| `label_asym_id`       | The asymmetric ID for the ligand                                           |
| `auth_asym_id`        | The author asymmetric ID                                                   |
| `label_comp_id`       | The label for the component                                                |
| `auth_comp_id`        | The author component ID                                                    |
| `label_seq_id`        | The label sequence ID                                                      |
| `auth_seq_id`         | The author sequence ID                                                     |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                              |
| `label_atom_id`       | The label for the atom                                                     |
| `auth_atom_id`        | The author atom ID                                                         |
| `type_symbol`         | The chemical type symbol for the ligand (optional)                         |
| `model_nums`          | The model numbers to fetch (optional)                                      |
| `encoding`            | The encoding format for the response (`cif`, `sdf`, `mol`, `mol2`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)                            |
| `data_source`         | The data source for the ligand                                             |
| `transform`           | Apply any transformations (optional)                                       |
| `download`            | Whether to download the file (True/False)                                  |
| `filename`            | The name of the file to save                                               |
| `file_directory`      | Directory to save the file                                                 |
| `compress_gzip`       | Whether to compress the file (default: False)                              |

## Atoms Data

`Atoms` queries fetch atom-level data from a given structure.

```python
from rcsbapi.model_query import ModelQuery

# Fetch atoms data for the entry "2HHB"
query = ModelQuery()
atoms_result = query.get_atoms(entry_id="2HHB")
print(atoms_result)
```

| Argument              | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")               |
| `label_entity_id`     | The entity label for the atom                        |
| `label_asym_id`       | The asymmetric ID for the atom                       |
| `auth_asym_id`        | The author asymmetric ID                             |
| `label_comp_id`       | The label for the component                          |
| `auth_comp_id`        | The author component ID                              |
| `label_seq_id`        | The label sequence ID                                |
| `auth_seq_id`         | The author sequence ID                               |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                        |
| `label_atom_id`       | The label for the atom                               |
| `auth_atom_id`        | The author atom ID                                   |
| `type_symbol`         | The chemical type symbol for the atom                |
| `model_nums`          | The model numbers to fetch (optional)                |
| `encoding`            | The encoding format for the response (`cif`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)      |
| `data_source`         | The data source for the atom                         |
| `transform`           | Apply any transformations (optional)                 |
| `download`            | Whether to download the file (True/False)            |
| `filename`            | The name of the file to save                         |
| `file_directory`      | Directory to save the file                           |
| `compress_gzip`       | Whether to compress the file (default: False)        |


Here is the **ReadTheDocs**-formatted section for the **Residue Interaction** query using the updated parameters:

---

## Residue Interaction

`Residue Interaction` queries fetch data on interactions between residues in a structure.

```python
from rcsbapi.model_query import ModelQuery

# Fetch residue interaction data for the entry "2HHB"
query = ModelQuery()
residue_interaction_result = query.get_residue_interaction(entry_id="2HHB")
print(residue_interaction_result)
```

| Argument              | Description                                                   |
| --------------------- | ------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                        |
| `label_entity_id`     | The entity label for the residue interaction                  |
| `label_asym_id`       | The asymmetric ID for the residue interaction                 |
| `auth_asym_id`        | The author asymmetric ID                                      |
| `label_comp_id`       | The label for the component                                   |
| `auth_comp_id`        | The author component ID                                       |
| `label_seq_id`        | The label sequence ID                                         |
| `auth_seq_id`         | The author sequence ID                                        |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                 |
| `label_atom_id`       | The label for the atom                                        |
| `auth_atom_id`        | The author atom ID                                            |
| `type_symbol`         | The chemical type symbol for the residue                      |
| `radius`              | The interaction radius for residue interaction (default: 5.0) |
| `assembly_name`       | The assembly name (optional)                                  |
| `model_nums`          | The model numbers to fetch (optional)                         |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)          |
| `copy_all_categories` | Whether to copy all categories (default: False)               |
| `data_source`         | The data source for the residue interaction                   |
| `transform`           | Apply any transformations (optional)                          |
| `download`            | Whether to download the file (True/False)                     |
| `filename`            | The name of the file to save                                  |
| `file_directory`      | Directory to save the file                                    |
| `compress_gzip`       | Whether to compress the file (default: False)                 |

## Residue Surroundings

`Residue Surroundings` queries fetch data on residues surrounding a specific residue in a structure.

```python
from rcsbapi.model_query import ModelQuery

# Fetch residue surrounding data for the entry "2HHB"
query = ModelQuery()
residue_surroundings_result = query.get_residue_surroundings(entry_id="2HHB", radius=6.0)
print(residue_surroundings_result)
```

| Argument              | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                         |
| `label_entity_id`     | The entity label for the residue                               |
| `label_asym_id`       | The asymmetric ID for the residue                              |
| `auth_asym_id`        | The author asymmetric ID                                       |
| `label_comp_id`       | The label for the component                                    |
| `auth_comp_id`        | The author component ID                                        |
| `label_seq_id`        | The label sequence ID                                          |
| `auth_seq_id`         | The author sequence ID                                         |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                  |
| `label_atom_id`       | The label for the atom                                         |
| `auth_atom_id`        | The author atom ID                                             |
| `type_symbol`         | The chemical type symbol for the residue                       |
| `radius`              | The interaction radius for residue surroundings (default: 5.0) |
| `assembly_name`       | The assembly name (optional)                                   |
| `model_nums`          | The model numbers to fetch (optional)                          |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)           |
| `copy_all_categories` | Whether to copy all categories (default: False)                |
| `data_source`         | The data source for the residue surroundings                   |
| `transform`           | Apply any transformations (optional)                           |
| `download`            | Whether to download the file (True/False)                      |
| `filename`            | The name of the file to save                                   |
| `file_directory`      | Directory to save the file                                     |
| `compress_gzip`       | Whether to compress the file (default: False)                  |


## Surrounding Ligands

`Surrounding Ligands` queries fetch data on ligands that are within a certain proximity of a residue in a structure.

```python
from rcsbapi.model_query import ModelQuery

# Fetch surrounding ligands data for the entry "2HHB"
query = ModelQuery()
surrounding_ligands_result = query.get_surrounding_ligands(entry_id="2HHB", radius=5.0, omit_water=True)
print(surrounding_ligands_result)
```

| Argument              | Description                                                                      |
| --------------------- | -------------------------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                                           |
| `label_entity_id`     | The entity label for the ligand                                                  |
| `label_asym_id`       | The asymmetric ID for the ligand                                                 |
| `auth_asym_id`        | The author asymmetric ID                                                         |
| `label_comp_id`       | The label for the ligand component                                               |
| `auth_comp_id`        | The author component ID                                                          |
| `label_seq_id`        | The label sequence ID for the ligand                                             |
| `auth_seq_id`         | The author sequence ID for the ligand                                            |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                                    |
| `label_atom_id`       | The label for the ligand atom                                                    |
| `auth_atom_id`        | The author atom ID for the ligand                                                |
| `type_symbol`         | The chemical type symbol for the ligand                                          |
| `omit_water`          | Whether to exclude water molecules from the surrounding ligands (default: False) |
| `radius`              | The interaction radius for surrounding ligands (default: 5.0)                    |
| `assembly_name`       | The assembly name (optional)                                                     |
| `model_nums`          | The model numbers to fetch (optional)                                            |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)                             |
| `copy_all_categories` | Whether to copy all categories (default: False)                                  |
| `data_source`         | The data source for the surrounding ligands                                      |
| `transform`           | Apply any transformations (optional)                                             |
| `download`            | Whether to download the file (True/False)                                        |
| `filename`            | The name of the file to save                                                     |
| `file_directory`      | Directory to save the file                                                       |
| `compress_gzip`       | Whether to compress the file (default: False)                                    |


## Symmetry Mates

`Symmetry Mates` queries fetch data on symmetry-related structures within a specified radius.

```python
from rcsbapi.model_query import ModelQuery

# Fetch symmetry mates data for the entry "2HHB"
query = ModelQuery()
symmetry_mates_result = query.get_symmetry_mates(entry_id="2HHB", radius=5.0)
print(symmetry_mates_result)
```

| Argument              | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                   |
| `radius`              | The interaction radius for symmetry mates (default: 5.0) |
| `model_nums`          | The model numbers to fetch (optional)                    |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)     |
| `copy_all_categories` | Whether to copy all categories (default: False)          |
| `data_source`         | The data source for the symmetry mates                   |
| `transform`           | Apply any transformations (optional)                     |
| `download`            | Whether to download the file (True/False)                |
| `filename`            | The name of the file to save                             |
| `file_directory`      | Directory to save the file                               |
| `compress_gzip`       | Whether to compress the file (default: False)            |


## Assembly

`Assembly` queries fetch data on the structure's assembly, useful for obtaining the full model or chain assembly.

```python
from rcsbapi.model_query import ModelQuery

# Fetch assembly data for the entry "2HHB"
query = ModelQuery()
assembly_result = query.get_assembly(entry_id="2HHB", name="1")
print(assembly_result)
```

| Argument              | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")               |
| `name`                | The assembly name (default: "1")                     |
| `model_nums`          | The model numbers to fetch (optional)                |
| `encoding`            | The encoding format for the response (`cif`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)      |
| `data_source`         | The data source for the assembly                     |
| `transform`           | Apply any transformations (optional)                 |
| `download`            | Whether to download the file (True/False)            |
| `filename`            | The name of the file to save                         |
| `file_directory`      | Directory to save the file                           |
| `compress_gzip`       | Whether to compress the file (default: False)        |
