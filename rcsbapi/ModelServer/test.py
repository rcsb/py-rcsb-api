query_obj = Alignments(
    from_="NCBI_PROTEIN",
    to="PDB_ENTITY",
    queryId="XP_642496",
    range=[1, 100],
    return_data_list=["target_alignments"],
    field_args={
        "target_alignments": {
            "first": 10,
            "offset": 5
        },
    }
)
query_obj.exec()
