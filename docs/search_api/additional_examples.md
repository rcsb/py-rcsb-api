# Additional Examples
For a walk through of each query type go to [Query Construction](query_construction.md)

## Sequence Motif Search Examples

In [Query Construction](query_construction.md#sequence-motif-search), you saw an example query using a PROSITE signature.
You can also use a regular expression (RegEx) to make a sequence motif search. As an example, here is a query for the zinc finger motif that binds Zn in a DNA-binding domain:
```python
from rcsbapi.search import SeqMotifQuery

results = SeqMotifQuery(
    "C.{2,4}C.{12}H.{3,5}H",
    pattern_type="regex",
    sequence_type="protein")

for polyid in results("polymer_entity"):
    print(polyid)
```

You can use a standard amino acid sequence to make a sequence motif search. 
X can be used to allow any amino acid in that position. 
As an example, here is a query for SH3 domains:
```python
from rcsbapi.search import SeqMotifQuery

# The default pattern_type argument is "simple" and the sequence_type argument is "protein".
# X is used as a "variable residue" and can be any amino acid. 
results = SeqMotifQuery("XPPXP")

for polyid in results("polymer_entity"):
    print(polyid)
```

All 3 of these pattern types can be used to search for DNA and RNA sequences as well.
Demonstrated are 2 queries, one DNA and one RNA, using the simple pattern type:
```python
from rcsbapi.search import SeqMotifQuery

# DNA query: this is a query for a T-Box.
dna = SeqMotifQuery("TCACACCT", sequence_type="dna")

print("DNA results:")
for polyid in dna("polymer_entity"):
    print(polyid)

# RNA query: 6C RNA motif
rna = SeqMotifQuery("CCCCCC", sequence_type="rna")
print("RNA results:")
for polyid in rna("polymer_entity"):
    print(polyid)
```
## Structure Similarity Search Examples
This is a more complex example that utilizes `chain_id`, the `relaxed_shape_match` operator, and a `target_search_space` of `polymer_entity_instance`. Specifying whether the input structure type is `chain_id` or `assembly_id` is very important. For example, specifying `chain_id` as the input structure type but inputting an assembly ID can lead to
an error.
```python
from rcsbapi.search import StructSimilarityQuery

# More complex query:
# Entry ID value "4HHB", chain ID "B", operator "relaxed", and target search space "Chains"
q2 = StructSimilarityQuery(
    structure_search_type="entry_id",
    entry_id="4HHB",
    structure_input_type="chain_id",
    chain_id="B",
    operator="relaxed_shape_match",
    target_search_space="polymer_entity_instance"
)
list(q2())
```
Structure similarity queries also allow users to upload a file from their local computer or input a file url from the website to query the PDB archive for similar proteins. The file represents a target protein structure in the file formats "cif", "bcif", "pdb", "cif.gz", or "pdb.gz". If a user wants to use a file url for queries, the user must specify the `structure_search_type`, the `file_url`, and the `file_format` of the file. This is the same case for file upload, except the user must provide the absolute path leading to the file that is in the local machine.
```python
from rcsbapi.search import StructSimilarityQuery

# Using file_url
q3 = StructSimilarityQuery(
    structure_search_type="file_url",
    file_url="https://files.rcsb.org/view/4HHB.cif",
    file_format="cif"
)
list(q3())

# Using `file_path`
q4 = StructSimilarityQuery(
    structure_search_type="file_upload",
    file_path="/PATH/TO/FILE.cif",  # specify local model file path
    file_format="cif"
)
list(q4())
```

## Structure Motif Search Examples

Like with Structure Similarity Queries, a `file_url` or `file_path` can also be provided to the program. These can take the place of an entry_id. 

For a `file_url` query, you *must* provide both a valid file URL (a string) and the file's file extension (also as a string). Failure to provide these elements will cause the package to throw an `AssertionError`. 

Below is an example of the same query as above, only this time providing a file url:
```python
link = "https://files.rcsb.org/view/2MNR.cif"
q2 = StructMotifQuery(
    structure_search_type="file_url",
    url=link, file_extension="cif",
    residue_ids=ResList
)
# structure_search_type MUST be provided. A mismatched query type will cause an error. 
list(q2())
```

A query using `file_path` would look something like this:
```python
file_path = "/absolute/path/to/file.cif"
q3 = StructMotifQuery(
    structure_search_type="file_upload",
    file_path=file_path,
    file_extension="cif",
    residue_ids=ResList
)
list(q3())
```
There are many additional parameters that Structure Motif Query supports. These include a variety of features such as `backbone_distance_tolerance`, `side_chain_distance_tolerance`, `angle_tolerance`, `rmsd_cutoff`, `limit` (stop searching after this many hits), `atom_pairing_scheme`, `motif_pruning_strategy`, `allowed_structures`, and `excluded_structures`. These can be mixed and matched as needed to make accurate and useful queries. All of these have some default value which is used when a parameter isn't provided (See [Query Construction](query_construction.md#structure-motif-search)). These parameters conform to the defaults used by the Search API. 

Below will demonstrate how to define these parameters:
```python
# Specifying backbone distance tolerance: 0-3, default is 1
# Allowed backbone distance tolerance in Angstrom. 
backbone = StructMotifQuery(
    entry_id="2MNR",
    backbone_distance_tolerance=2,
    residue_ids=ResList
)
list(backbone())

# Specifying sidechain distance tolerance: 0-3, default is 1
# Allowed side-chain distance tolerance in Angstrom.
sidechain = StructMotifQuery(
    entry_id="2MNR",
    side_chain_distance_tolerance=2,
    residue_ids=ResList
)
list(sidechain())

# Specifying angle tolerance: 0-3, default is 1
# Allowed angle tolerance in multiples of 20 degrees. 
angle = StructMotifQuery(
    entry_id="2MNR",
    angle_tolerance=2,
    residue_ids=ResList
)
list(angle())

# Specifying RMSD cutoff: >=0, default is 2
# Threshold above which hits will be filtered by RMSD
rmsd = StructMotifQuery(
    entry_id="2MNR",
    rmsd_cutoff=1,
    residue_ids=ResList
)
list(rmsd())

# Specifying limit: >=0, default excluded
# Stop accepting results after this many hits. 
limit = StructMotifQuery(
    entry_id="2MNR",
    limit=100,
    residue_ids=ResList
)
list(limit())

# Specifying atom pairing scheme, default = "SIDE_CHAIN"
# ENUM: "ALL", "BACKBONE", "SIDE_CHAIN", "PSUEDO_ATOMS"
# This is typechecked by a literal. 
# Which atoms to consider to compute RMSD scores and transformations. 
atom = StructMotifQuery(
    entry_id="2MNR",
    atom_pairing_scheme="ALL",
    residue_ids=ResList
)
list(atom())

# Specifying motif pruning strategy, default = "KRUSKAL"
# ENUM: "NONE", "KRUSKAL"
# This is typechecked by a literal in the package. 
# Specifies how many query motifs are "pruned".
# KRUSKAL leads to less stringent queries, and faster results.
pruning = StructMotifQuery(
    entry_id="2MNR",
    motif_pruning_strategy="NONE",
    residue_ids=ResList
)
list(pruning())

# Specifying allowed structures, default excluded
# Specify the structures you wish to allow in the return result. As an example,
# We could only allow the results from the limited query we ran earlier. 
allowed = StructMotifQuery(
    entry_id="2MNR",
    allowed_structures=list(limit()),
    residue_ids=ResList
)
list(allowed())

# Specifying structures to exclude, default excluded
# Specify structures to exclude from a query. We could, for example,
# Exclude the results of the previous allowed query. 
excluded = StructMotifQuery(
    entry_id="2MNR",
    excluded_structures=list(allowed()),
    residue_ids=ResList
)
list(excluded())
```
The Structure Motif Query can be used to make some very specific queries. Below is an example of a query that retrieves occurrences of the enolase superfamily, a group of proteins diverse in sequence and structure that are all capable of abstracting a proton from a carboxylic acid. Position-specific exchanges are crucial to represent this superfamily accurately.
```python
Res1 = StructMotifResidue("A", "1", 162, ["LYS", "HIS"])
Res2 = StructMotifResidue("A", "1", 193)
Res3 = StructMotifResidue("A", "1", 219)
Res4 = StructMotifResidue("A", "1", 245, ["GLU", "ASP", "ASN"])
Res5 = StructMotifResidue("A", "1", 295, ["HIS", "LYS"])

ResList = [Res1, Res2, Res3, Res4, Res5]

query = StructMotifQuery(entry_id="2MNR", residue_ids=ResList)

list(query())
```
## Chemical Similarity Search Examples

```python
from rcsbapi.search import ChemSimilarityQuery

# Basic query with default values: query type = formula and match subset = False
q1 = ChemSimilarityQuery(value="C12 H17 N4 O S")

# Same example but with all the parameters listed
q1 = ChemSimilarityQuery(
    value="C12 H17 N4 O S",
    query_type="formula",
    match_subset=False
)
list(q1())
```
Below are two examples of using the query option `descriptor`. Both `descriptor_type`s are shown.
```python
from rcsbapi.search import ChemSimilarityQuery

# Query with descriptor_type SMILES,
# match_type = "graph-relaxed-stereo" (similar ligands (stereospecific))
q2 = ChemSimilarityQuery(
    value="Cc1c(sc[n+]1Cc2cnc(nc2N)C)CCO",
    query_type="descriptor",
    descriptor_type="SMILES",
    match_type="graph-relaxed-stereo"
)
list(q2())
```
```python
from rcsbapi.search import ChemSimilarityQuery

# Query descriptor_type InChI,
# match_type = "sub-struct-graph-relaxed-stereo" (substructure (stereospecific))
q3 = ChemSimilarityQuery(
    value="InChI=1S/C13H10N2O4/c16-10-6-5-9(11(17)14-10)15-12(18)7-3-1-2-4-8(7)13(15)19/h1-4,9H,5-6H2,(H,14,16,17)/t9-/m0/s1",
    query_type="descriptor",
    descriptor_type="InChI",
    match_type="sub-struct-graph-relaxed-stereo"
)
list(q3())
```
## Faceted Query Examples
For more details on arguments, see the [API reference](api.rst)

### Terms Facets
Terms faceting is a multi-bucket aggregation where buckets are dynamically built - one per unique value. We can specify the minimum count (`>= 0`) for a bucket to be returned using the parameter `min_interval_population` (default value `1`). We can also control the number of buckets returned using the parameter `max_num_intervals` (default value `65336`).
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet

# This is the default query used by the RCSB Search API when no query is specified.
# This default query will be used for most of the examples found below for faceted queries.
q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental",
) 

q(
    facets= Facet(
        name="Journals",
        aggregation_type="terms",
        attribute="rcsb_primary_citation.rcsb_journal_abbrev",
        min_interval_population=1000
    )
).facets
```

### Histogram Facets
Histogram facets build fixed-sized buckets (intervals) over numeric values. The size of the intervals must be specified in the parameter `interval`. We can also specify `min_interval_population` if desired.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental"
) 

q(
    return_type="polymer_entity",
    facets=Facet(
        name="Formula Weight",
        aggregation_type="histogram",
        attribute="rcsb_polymer_entity.formula_weight",
        interval=50,
        min_interval_population=1
    )
).facets
```

### Date Histogram Facets
Similar to histogram facets, date histogram facets build buckets over date values. For date histogram aggregations, we must specify `interval="year"`. Again, we may also specify `min_interval_population`.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental"
) 

q(
    facets=Facet(
        name="Release Date",
        aggregation_type="date_histogram",
        attribute="rcsb_accession_info.initial_release_date",
        interval="year",
        min_interval_population=1
    )
).facets
```

### Range Facets
We can define the buckets ourselves by using range facets. In order to specify the ranges, we use the `FacetRange` class. Note that the range includes the `start` value and excludes the `end` value (`include_lower` and `include_upper` should not be specified). If the `start` or `end` is omitted, the minimum or maximum boundaries will be used by default. The buckets should be provided as a list of `FacetRange` objects to the `ranges` parameter.  
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet, FacetRange

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental"
)

q(
    facets=Facet(
        name="Resolution Combined",
        aggregation_type="range",
        attribute="rcsb_entry_info.resolution_combined",
        ranges=[
            FacetRange(start=None,end=2),
            FacetRange(start=2, end=2.2),
            FacetRange(start=2.2, end=2.4),
            FacetRange(start=4.6, end=None)
        ]
    )
).facets
```

### Date Range Facets
Date range facets allow us to specify date values as bucket ranges, using [date math expressions](https://search.rcsb.org/#date-math-expressions).
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet, FacetRange

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental"
)

q(
    facets=Facet(
        name="Release Date",
        aggregation_type="date_range",
        attribute="rcsb_accession_info.initial_release_date",
        ranges=[
            FacetRange(start=None,end="2020-06-01||-12M"),
            FacetRange(start="2020-06-01", end="2020-06-01||+12M"),
            FacetRange(start="2020-06-01||+12M", end=None)
        ]
    )
).facets
```

### Cardinality Facets 
Cardinality facets return a single value: the count of distinct values returned for a given field. A `precision_threshold` (`<= 40000`, default value `40000`) may be specified.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental",
) 

q(
    facets=Facet(
        name="Organism Names Count",
        aggregation_type="cardinality",
        attribute="rcsb_entity_source_organism.ncbi_scientific_name"
    )
).facets
```

### Multidimensional Facets
Complex, multi-dimensional aggregations are possible by specifying additional facets in the `nested_facets` parameter, as in the example below:
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Facet

f1 = Facet(
    name="Polymer Entity Types",
    aggregation_type="terms",
    attribute="rcsb_entry_info.selected_polymer_entity_types"
)
f2 = Facet(
    name="Release Date",
    aggregation_type="date_histogram",
    attribute="rcsb_accession_info.initial_release_date",
    interval="year"
)

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental",
) 

q(
    facets=Facet(
        name="Experimental Method",
        aggregation_type="terms",
        attribute="rcsb_entry_info.experimental_method",
        nested_facets=[f1, f2]
    )
).facets
```

### Filter Facets
Filters allow us to filter documents that contribute to bucket count. Similar to queries, we can group several `TerminalFilter`s into a single `GroupFilter`. We can combine a filter with a facet using the `FilterFacet` class. Terminal filters should specify an `attribute` and `operator`, as well as possible a `value` and whether or not it should be a `negation` and/or `case_sensitive`. Group filters should specify a `logical_operator` (which should be either `"and"` or `"or"`) and a list of filters (`nodes`) that should be combined. Finally, the `FilterFacet` should be provided with a filter and a (list of) facet(s).

Here is an example that filters only protein chains which adopt 2 different beta propeller arrangements according to the CATH classification.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import TerminalFilter, GroupFilter, FilterFacet, Facet

tf1 = TerminalFilter(
    attribute="rcsb_polymer_instance_annotation.type",
    operator="exact_match",
    value="CATH"
)
tf2 = TerminalFilter(
    attribute="rcsb_polymer_instance_annotation.annotation_lineage.id",
    operator="in",
    value=["2.140.10.30", "2.120.10.80"]
)
ff2 = FilterFacet(
    filter=tf2,
    facets=Facet(
        name="CATH Domains",
        aggregation_type="terms",
        attribute="rcsb_polymer_instance_annotation.annotation_lineage.id",
        min_interval_population=1
    )
)

q = AttributeQuery(
    attribute="rcsb_entry_info.structure_determination_methodology",
    operator="exact_match",
    value="experimental"
) 

q(
    return_type="polymer_instance",
    facets=FilterFacet(filter=tf1, facets=ff2
)).facets
```

This example shows how to get assembly counts per symmetry types, further broken down by Enzyme Classification (EC) classes.
The assemblies are first filtered to homo-oligomers only.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import TerminalFilter, GroupFilter, FilterFacet, Facet

tf1 = TerminalFilter(
    attribute="rcsb_struct_symmetry.kind",
    operator="exact_match",
    value="Global Symmetry",
    negation=False
)
f2 = Facet(
    name="ec_terms",
    aggregation_type="terms",
    attribute="rcsb_polymer_entity.rcsb_ec_lineage.id"
)
f1 = Facet(
    name="sym_symbol_terms",
    aggregation_type="terms",
    attribute="rcsb_struct_symmetry.symbol",
    nested_facets=f2
)

ff = FilterFacet(filter=tf1, facets=f1)
q1 = AttributeQuery(
    attribute="rcsb_assembly_info.polymer_entity_count",
    operator="equals",
    value=1
)
q2 = AttributeQuery(
    attribute="rcsb_assembly_info.polymer_entity_instance_count",
    operator="greater",
    value=1
)
q = q1 & q2
q(return_type="assembly", facets=ff).facets
```

This example shows how to get the number of distinct protein sequences in the PDB archive.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import TerminalFilter, GroupFilter, FilterFacet, Facet

tf1 = TerminalFilter(
    attribute="rcsb_polymer_entity_group_membership.aggregation_method",
    operator="exact_match",
    value="sequence_identity"
)
tf2 = TerminalFilter(
    attribute="rcsb_polymer_entity_group_membership.similarity_cutoff",
    operator="equals",
    value=100)
gf = GroupFilter(logical_operator="and", nodes=[tf1, tf2])
ff = FilterFacet(
    filter=gf,
    facets=Facet(
        "Distinct Protein Sequence Count",
        "cardinality",
        "rcsb_polymer_entity_group_membership.group_id"
    )
)
q = AttributeQuery(
    attribute="rcsb_assembly_info.polymer_entity_count",
    operator="equals",
    value=1,
)
q(return_type="polymer_entity", facets=ff).facets
```

## GroupBy Example
For more details on arguments to create `RequestOption` objects, see the [API reference](api.rst).

Sequence Identity and Matching Uniprot Accession examples from [Search API Documentation](https://search.rcsb.org/#group-by-return-type).

### Matching Deposit Group ID
Aggregation method `matching_deposit_group_id` groups on the basis of a common identifier for a group of entries deposited as a collection.

This example searches for entries associated with "interleukin" from humans with investigational or experimental drugs bound.
Since `group_by_return_type` is specified as `representatives`, one representative structure per group is returned.

```python
from rcsbapi.search import AttributeQuery, TextQuery
from rcsbapi.search import search_attributes as attrs
from rcsbapi.search import GroupBy

q1 = TextQuery("interleukin")
q2 = attrs.rcsb_entity_source_organism.scientific_name == "Homo sapiens"
q3 = attrs.drugbank_info.drug_groups == "investigational"
q4 = attrs.drugbank_info.drug_groups == "experimental"

query = q1 & q2 & (q3 | q4)
list(
    query(
        group_by=GroupBy(aggregation_method="matching_deposit_group_id"),
        # "representatives" means that only a single search hit is returned per group
        group_by_return_type="representatives"
    )
)
```

### Sequence Identity
Aggregation method `sequence_identity` is used to group search hits on the basis of protein sequence clusters that meet a predefined identity threshold.

This example groups together identical human sequences from high-resolution (1.0-2.0Å) structures determined by X-ray crystallography. Among the resulting groups, there is a cluster of human glutathione transferases in complex with different substrates.
```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import search_attributes as attrs
from rcsbapi.search import GroupBy, RankingCriteriaType

q1 = attrs.rcsb_entity_source_organism.taxonomy_lineage.name == "Homo sapiens"
q2 = attrs.exptl.method == "X-RAY DIFFRACTION"
q3 = attrs.rcsb_entry_info.resolution_combined >= 1
q4 = attrs.rcsb_entry_info.resolution_combined <= 2

query = q1 & q2 & q3 & q4

list(query(
    # "sequence_identity" aggregation method must use return_type "polymer_entity"
    # If not return_type will be changed and a warning will be raised.
    return_type="polymer_entity",
    group_by=GroupBy(
        aggregation_method="sequence_identity",
        similarity_cutoff=100,  # 100, 95, 90, 70, 50, or 30
        ranking_criteria_type=RankingCriteriaType(
                sort_by="entity_poly.rcsb_sample_sequence_length",
                direction="desc"
        )
    ),
    group_by_return_type="groups"  # divide into groups returned with all associated hits
))
```

### Matching Uniprot Accession
This example demonstrates how to use `matching_uniprot_accession` grouping to get distinct Spike protein S1 proteins released from the beginning of 2020. Here, all entities are represented by distinct groups of SARS-CoV, SARS-CoV-2 and Pangolin coronavirus spike proteins.

```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import search_attributes as attrs
from rcsbapi.search import GroupBy, RankingCriteriaType

q1 = AttributeQuery(
    attribute="rcsb_polymer_entity.pdbx_description",
    operator="contains_phrase",
    value="Spike protein S1"
)
q2 = attrs.rcsb_accession_info.initial_release_date > "2020-01-01"

query = q1 & q2
list(query(
    # "matching_uniprot_accession" aggregation method
    # must use return type "polymer_entity"
    return_type="polymer_entity",
    group_by=GroupBy(
        aggregation_method="matching_uniprot_accession",
        ranking_criteria_type= RankingCriteriaType(
            sort_by="coverage"
        )
    ),
    group_by_return_type="groups"
))
```

## Sort Example
The `sort` request option can be used to control sorting of results. By default, results are sorted by `score` in descending order.
You can also sort by attribute name and apply filters.

Example from [RCSB PDB Search API](https://search.rcsb.org/#sorting) page.

```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import Sort

query = AttributeQuery(
    attribute="struct.title",
    operator="contains_phrase",
    value="hiv protease",
)

list(query(sort=
    Sort(
        sort_by="rcsb_accession_info.initial_release_date",
        direction="desc"
    )
))
```
