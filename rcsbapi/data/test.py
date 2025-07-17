from rcsbapi.data import DataQuery as Query
from rcsbapi.data import ALL_STRUCTURES


def get_ccid_pdb_mapping_and_write_to_file():
    # Initialize the query for nonpolymer_entities
    query = Query(
        input_type="entries",
        input_ids=ALL_STRUCTURES,
        return_data_list=["nonpolymer_entities.rcsb_nonpolymer_entity_container_identifiers.nonpolymer_comp_id", "rcsb_id"]
    )

    # Exec the query
    result = query.exec(progress_bar=True)

    # Process the result
    ccid_pdb_map = {}
    entries = result.get('data', {}).get('entries', [])

    for entry in entries:
        pdb_id = entry.get('rcsb_id')
        nonpolymer_entities = entry.get('nonpolymer_entities', [])

        if nonpolymer_entities:
            for entity in nonpolymer_entities:
                container_identifiers = entity.get('rcsb_nonpolymer_entity_container_identifiers')
                if container_identifiers:
                    comp_id = container_identifiers.get('nonpolymer_comp_id')
                    if comp_id and pdb_id:
                        if comp_id not in ccid_pdb_map:
                            ccid_pdb_map[comp_id] = set()  # Use a set to ensure uniqueness
                        ccid_pdb_map[comp_id].add(pdb_id)  # Add pdb_id to the set

    # Writing the CCId to PDB ID mapping to a text file
    with open('ccid_pdb_mapping.txt', 'w') as file:
        for ccid, pdb_ids in ccid_pdb_map.items():
            file.write(f'{ccid}\t{" ".join(pdb_ids)}\n')

    return 'ccid_pdb_mapping.txt'


# Call the function and get the file path
output_file_path = get_ccid_pdb_mapping_and_write_to_file()
print(f"File saved at: {output_file_path}")
