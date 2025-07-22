from rcsbapi.data import DataQuery as Query
from rich import print
# from rcsbapi.data import ALL_STRUCTURES

# Initialize the query
query = Query(
    input_type="entries",
    input_ids=["1A07"],
    return_data_list=[
        "rcsb_id",
        "polymer_entities.chem_comp_nstd_monomers.chem_comp.id",
        "branched_entities.chem_comp_monomers.chem_comp.id",
        "nonpolymer_entities.nonpolymer_comp.chem_comp.id",
        # "exptl.method"
    ]
)

# query = Query(
#     input_type="polymer_entities",
#     input_ids=["2CPK_1", "3WHM_1", "2D5Z_1"],
#     return_data_list=[
#         "polymer_entities.rcsb_id",
#         "rcsb_entity_source_organism.ncbi_taxonomy_id",
#         "rcsb_entity_source_organism.ncbi_scientific_name",
#         "cluster_id",
#         "identity",
#     ],
# )

# Execute the query
result = query.exec()
print(query.get_query())

# from rcsbapi.data import DataSchema
# schema = DataSchema()
# print(schema.find_paths("entries", "chem_comp"))


# query = Query(
#     input_type="entries",
#     input_ids=["2CPK", "3WHM", "2D5Z"],
#     return_data_list=[
#         "polymer_entities.rcsb_id",
#         "rcsb_entity_source_organism.ncbi_taxonomy_id",
#         "rcsb_entity_source_organism.ncbi_scientific_name",
#         "cluster_id",
#         "identity",
#     ],
# )
