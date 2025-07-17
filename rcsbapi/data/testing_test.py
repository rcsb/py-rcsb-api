def parse_file(file_path):
    # Parse the file into a dictionary with identifier as the key and set of associated ids as the value.
    data = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            identifier = parts[0].lower()  # Normalize the identifier to lowercase
            associated_ids = set(part.lower() for part in parts[1:])  # Normalize all associated ids to lowercase
            data[identifier] = associated_ids
    return data


def compare_files(file1_data, file2_data):
    # Compare the sets of identifiers across both files.
    discrepancies = []
    
    # Get all unique identifiers from both files.
    all_identifiers = set(file1_data.keys()).union(set(file2_data.keys()))
    
    # Check if the identifiers in both files have the same set of associated IDs.
    for identifier in all_identifiers:
        file1_ids = file1_data.get(identifier, set())
        file2_ids = file2_data.get(identifier, set())
        
        if file1_ids != file2_ids:
            # Find the differences between the two sets
            diff_file1 = file1_ids - file2_ids  # Items in file1 but not in file2
            diff_file2 = file2_ids - file1_ids  # Items in file2 but not in file1
            discrepancies.append((identifier, diff_file1, diff_file2))
    
    return discrepancies


def log_discrepancies(discrepancies, output_path):
    # Log the discrepancies to a text file.
    with open(output_path, 'w') as log_file:
        if discrepancies:
            for identifier, diff_file1, diff_file2 in discrepancies:
                # Only log the differences, not the entire sets
                log_file.write(f"Identifier: {identifier}\n")
                if diff_file1:
                    log_file.write(f"Only in New File: {diff_file1}\n")
                if diff_file2:
                    log_file.write(f"Only in Old File: {diff_file2}\n")
                log_file.write("------\n")
        else:
            log_file.write("No discrepancies found. All identifiers are consistent.\n")


def main():
    # Paths to your files.
    file1_path = r'C:\Users\Krish\Documents\gitRCSB\py-rcsb-api\ccid_pdb_mapping.txt'
    file2_path = r'C:\Users\Krish\Documents\gitRCSB\py-rcsb-api\ligand_expo.txt'
    output_path = r'C:\Users\Krish\Documents\gitRCSB\py-rcsb-api\discrepancies.txt'  # Output file path
    
    # Parse both files.
    file1_data = parse_file(file1_path)
    file2_data = parse_file(file2_path)
    
    # Compare the two files.
    discrepancies = compare_files(file1_data, file2_data)
    
    # Log the discrepancies to a file.
    log_discrepancies(discrepancies, output_path)
    
    # Print confirmation
    print(f"Discrepancies have been written to: {output_path}")


if __name__ == "__main__":
    main()
