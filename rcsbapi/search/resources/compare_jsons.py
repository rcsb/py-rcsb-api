import json
from deepdiff import DeepDiff  # pip install deepdiff

file1 = "structure_schema_pre.json"
file2 = "structure_schema_jul8.json"

with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
    json1 = json.load(f1)
    json2 = json.load(f2)

diff = DeepDiff(json1, json2, ignore_order=True)

if diff:
    print("Differences found:")
    print(diff.pretty())
else:
    print("The JSON files are identical.")
