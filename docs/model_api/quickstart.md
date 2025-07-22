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
The RCSB [ModelServer API](https://models.rcsb.org/) provides access to molecular structure data (e.g., atomic coordinates) and related information. The Model Server API allows you to query for various structural data types, such as full structure, ligands, atoms, residue interactions, and more.

Key Features
- Full Structure Data: Access complete structural information about biomolecules in different formats (e.g., CIF, BCIF).
- Ligand Information: Retrieve detailed data about ligands, including their chemical structure and interactions with other components.
- Atoms and Residue Data: Query for atom-level or residue-level data, including surrounding residues, interactions, and symmetries.
- Symmetry Mates and Assemblies: Obtain symmetry mates or assembly data, important for understanding molecular structures in different environments.

The API supports queries for Experimental Structures. (Support for Computed Structure Models (CSMs) is not yet available.)

### Query Types

The Model Server API supports multiple query types, including:

- `full`: Fetches the full structure for a given entry.
- `ligand`: Retrieves ligand-related information, including components and interactions.
- `atoms`: Fetches atom-level details.
- `residue_interaction`: Retrieves data on interactions between residues.
- `residue_surroundings`: Provides information about residues surrounding a given structure.
- `surrounding_ligands`: Provides information about residues surrounding a given structure.
- `symmetry_mates`: Retrieves symmetry-related data.
- `assembly`: Fetches information about molecular assemblies.

This package provides an interface to the Model Server API, making it easy to send requests and retrieve data in various formats.


### API Usage
The API is based on standard HTTP requests, and you can specify different parameters depending on the query type. For example, you can query specific structures, specify encoding formats (like CIF or BCIF), request data downloads, or even compress data using GZIP.

You can use this API to automate data retrieval and integrate it into your bioinformatics or structural biology workflow.


## Full Structure

Use the `.get_full_structure()` method to fetch complete structural data for a given entry.

```python
from rcsbapi.model import ModelQuery

# Fetch the full structure for the entry "2HHB" and store content in `result` variable
query = ModelQuery()
result = query.get_full_structure(entry_id="2HHB")
print(result[:500])

# Or, download the structure:
result = query.get_full_structure(
    entry_id="2HHB",
    encoding="cif",
    download=True,
    file_directory="model-output"
)
print(result)
```

| Argument              | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                     |
| `model_nums`          | The model numbers to fetch (optional). If set, only include atoms with the corresponding `_atom_site.pdbx_PDB_model_num` field.                    |
| `encoding`            | The encoding format for the response (`cif` (default), `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)            |
| `data_source`         | The data source for the structure                          |
| `transform`           | Apply any transformations (optional)                       |
| `download`            | Whether to download the file (True/False)                  |
| `filename`            | The name of the file to save                               |
| `file_directory`      | Directory to save the file                                 |
| `compress_gzip`       | Whether to compress the file (default: False)              |


## Ligand Data

Use the `.get_ligand()` method to fetch ligand-related data (metadata and coordinates) within a given structure.

Note that by default this returns only the first instance of the specified ligand (e.g., if there are 10 `HEM` ligands in the structure, only the first one is returned). If you want a specific instance of the ligand, you can specify `label_asym_id` and/or `label_entity_id`. If you want *all* occurrences of a specific ligand, you should use the `.get_atoms()` [method below](#atoms-data).

```python
from rcsbapi.model import ModelQuery

# Fetch the first occurrence of the `HEM` ligand for entry "4HHB"
query = ModelQuery()
result = query.get_ligand(entry_id="4HHB", label_comp_id="HEM", download=True, filename="4HHB_HEM_ligand.cif", file_directory="model-output")
print(result)
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

Use the `.get_atoms()` method to fetch atom-level data (coordinates and metadata) from a given structure. This can be used to fetch all `atom_site` data for a particular component using `label_comp_id` (e.g., all `HEM` ligands, all water molecules `HOH`, or all `CYS` residues), a given entity, a specific residue in the sequence, and/or a combination of these criteria.

```python
from rcsbapi.model import ModelQuery

# Fetch the metadata and `atom_site` coordinates of ALL occurrence of `HEM` in entry "4HHB"
query = ModelQuery()
result = query.get_atoms(entry_id="4HHB", label_comp_id="HEM", download=True, filename="4HHB_HEM_atoms.cif", file_directory="model-output")
print(result)
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


## Residue Interaction

Use the `.get_residue_interaction()` method to fetch data (metadata and coordinates) on the surrounding residues of a given ligand or residue. If you only provide the `label_comp_id`, the server will return the interaction data for *all* occurrences of the component. This method takes crystal symmetry into account (returned data includes `_molstar_atom_site_operator_mapping`).

```python
from rcsbapi.model import ModelQuery

# Fetch surrounding residues for ALL `HEM` ligands in entry "4HHB"
query = ModelQuery()
result = query.get_residue_interaction(entry_id="4HHB", label_comp_id="HEM", radius=5.0, download=True, file_directory="model-output")
print(result)

# Fetch surrounding residues for `HEM` chain `E` in entry "4HHB"
query = ModelQuery()
result = query.get_residue_interaction(
    entry_id="4HHB",
    label_comp_id="HEM",
    label_asym_id="E",
    radius=5.0,
    download=True,
    filename="4HHB_HEM_E_residue_interaction.cif",
    file_directory="model-output"
)
print(result)
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

Use the `.get_residue_surroundings()` method to fetch data (metadata and coordinates) on the surrounding residues of a given ligand or residue. If you only provide the `label_comp_id`, the server will return the interaction data for *all* occurrences of the component. Similar to [Residue Interaction](#residue-interaction), but doesn't take crystal symmetry into account (returned data does *not* include `_molstar_atom_site_operator_mapping`).

```python
from rcsbapi.model import ModelQuery

# Fetch surrounding residues for `HEM` chain `E` in entry "4HHB"
query = ModelQuery()
result = query.get_residue_surroundings(
    entry_id="4HHB",
    label_comp_id="HEM",
    label_asym_id="E",
    radius=5.0,
    download=True,
    filename="4HHB_HEM_E_residue_surroundings.cif",
    file_directory="model-output"
)
print(result)
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

Use the `.get_surrounding_ligands()` method to fetch data on ligands that are within a certain proximity of a residue in a structure. This method takes crystal symmetry into account (returned data includes `_molstar_atom_site_operator_mapping`).

```python
from rcsbapi.model import ModelQuery

# Fetch surrounding ligands for `ALA 284` in entry "1TQN"
query = ModelQuery()
result = query.get_surrounding_ligands(
    entry_id="1TQN",
    label_comp_id="ALA",
    label_seq_id=284,
    radius=5.0,
    download=True,
    file_directory="model-output"
)
print(result)
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
| `omit_water`          | Whether to exclude water molecules from the surrounding ligands (default: False). (*Note: this does not appear to be functional on the ModelServer API yet*) |
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

Use the `.get_symmetry_mates()` method to compute crystal symmetry mates within a specified radius.

```python
from rcsbapi.model import ModelQuery

# Generate the symmetry mates (unit cell replications) for the entry "1TQN"
query = ModelQuery()
result = query.get_symmetry_mates(entry_id="1TQN", download=True, file_directory="model-output")
print(result)
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


## Assembly Data

Use the `.get_assembly()` method to extract a structural assembly (select group of instances or "chains") from an entry.

```python
from rcsbapi.model import ModelQuery

# Fetch assembly "3" for the entry "13PK"
query = ModelQuery()
result = query.get_assembly(entry_id="13PK", name="3", download=True, file_directory="model-output")
print(result)
```

| Argument              | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")               |
| `name`                | The assembly id (default: "1")                       |
| `model_nums`          | The model numbers to fetch (optional)                |
| `encoding`            | The encoding format for the response (`cif`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)      |
| `data_source`         | The data source for the assembly                     |
| `transform`           | Apply any transformations (optional)                 |
| `download`            | Whether to download the file (True/False)            |
| `filename`            | The name of the file to save                         |
| `file_directory`      | Directory to save the file                           |
| `compress_gzip`       | Whether to compress the file (default: False)        |


## Working with Multiple Structures

Let's say you want to download or fetch data for several structures at once. You can do so by providing a list to the `.get_multiple_structures()` method:

```python

# List of structure IDs to query
entry_ids = ["1CBS", "4HHB"]

# Fetch multiple structures (e.g., "full" type) and save the result
results = query.get_multiple_structures(
    entry_ids,
    query_type="full",
    encoding="cif",
    download=True,
    compress_gzip=True,
    file_directory="model-output"
)

print(results)
```

The `.get_multiple_structures()` method is ammenable to any of the available types of queries via the `query_type` argument:

| Query type method             | Corresponding `query_type` value     |
|-------------------------------|--------------------------------------|
| `.get_full_structure()`       | `full`                               |
| `.get_ligand()`               | `ligand`                             |
| `.get_atoms()`                | `atoms`                              |
| `.get_residue_interaction()`  | `residue_interaction`                |
| `.get_residue_surroundings()` | `residue_surroundings`               |
| `.get_surrounding_ligands()`  | `surrounding_ligands`                |
| `.get_symmetry_mates()`       | `symmetry_mates`                     |
| `.get_assembly()`             | `assembly`                           |
