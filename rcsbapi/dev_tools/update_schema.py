"""Update the distribution json files; for developer use only
This is currently not in use. """
import json
from pathlib import Path
from typing import Dict, Literal, List

try:
    from rcsbapi.search.search_query import SEARCH_SCHEMA  # instance of SearchSchema
except Exception:
    # ignore errors that may occur parsing the schema
    pass

from rcsbapi.const import const
SEARCH_API_SCHEMAS = {
    "metadata_schema.json": const.STRUCTURE_ATTRIBUTE_SCHEMA_URL,
    "chemical_schema.json": const.CHEMICAL_ATTRIBUTE_SCHEMA_URL
}

DATA_API_SCHEMAS = {
    "entry.json": "https://data.rcsb.org/rest/v1/schema/entry",
    "polymer_entity.json": "https://data.rcsb.org/rest/v1/schema/polymer_entity",
    "branched_entity.json": "https://data.rcsb.org/rest/v1/schema/branched_entity",
    "nonpolymer_entity.json": "https://data.rcsb.org/rest/v1/schema/nonpolymer_entity",
    "polymer_entity_instance.json": "https://data.rcsb.org/rest/v1/schema/polymer_entity_instance",
    "branched_entity_instance.json": "https://data.rcsb.org/rest/v1/schema/branched_entity_instance",
    "nonpolymer_entity_instance.json": "https://data.rcsb.org/rest/v1/schema/nonpolymer_entity_instance",
    "assembly.json": "https://data.rcsb.org/rest/v1/schema/assembly",
    "chem_comp.json": "https://data.rcsb.org/rest/v1/schema/chem_comp",
    "pubmed.json": "https://data.rcsb.org/rest/v1/schema/pubmed",
    "uniprot.json": "https://data.rcsb.org/rest/v1/schema/uniprot",
    "drugbank.json": "https://data.rcsb.org/rest/v1/schema/drugbank",
}


def make_version_dict(file_list: List[str], package: Literal["search", "data"]) -> Dict:
    current_version_dict = {}
    for file_name in file_list:
        path = Path(__file__).parent.parent.joinpath(package, "resources", file_name)
        with open(path, "r", encoding="utf-8") as file:
            schema = json.load(file)
            if "$comment" in schema:
                if package == "search":
                    version = schema["$comment"].lower().replace("schema version: ", "")
                else:
                    version = schema["$comment"].lower().replace("schema_version: ", "")
                current_version_dict[file_name] = version
            else:
                current_version_dict[file_name] = ""
    return current_version_dict


def update_schema(
    file_name: str,
    url: str,
    package: Literal["search", "data"],
) -> str:
    # Define path: py-rcsb-api/rcsbapi/<package>/resources/<file_name>
    path = Path(__file__).parent.parent.joinpath(package, "resources", file_name)

    with open(path, "wt", encoding="utf-8") as file:
        new_schema = SEARCH_SCHEMA._fetch_schema(url)
        json.dump(new_schema, file, indent=2)
        if "$comment" in new_schema:
            if package == "search":
                version = new_schema["$comment"].lower().replace("schema version: ", "")
            else:
                version = new_schema["$comment"].lower().replace("schema_version: ", "")
        else:
            version = ""
    return version


def make_changelog_msg(
    file_list: List[str],
    package: Literal["search", "data"],
    current_ver_dict: Dict[str, str],
    new_ver_dict: Dict[str, str],
) -> str:
    msg = ""
    for file_name in file_list:
        if (current_ver_dict[file_name] == new_ver_dict[file_name]) or (current_ver_dict[file_name] == ""):
            continue

        if not msg:
            msg = f"Update {package} schemas: \n"
        msg += f"  {file_name.replace(".json", "")} schema {current_ver_dict[file_name]} --> {new_ver_dict[file_name]}\n"
    return msg


if __name__ == "__main__":
    # Find current schema versions
    search_current_ver_dict = make_version_dict(file_list=list(SEARCH_API_SCHEMAS.keys()), package="search")
    data_current_ver_dict = make_version_dict(file_list=list(DATA_API_SCHEMAS.keys()), package="data")

    # Update Search API schemas
    search_version_dict: dict[str, str] = {}
    for file_name, url in SEARCH_API_SCHEMAS.items():
        search_version = update_schema(file_name=file_name, url=url, package="search")
        search_version_dict[file_name] = search_version

    # Update Data API schemas
    data_version_dict: dict[str, str] = {}
    for file_name, url in DATA_API_SCHEMAS.items():
        data_version = update_schema(file_name=file_name, url=url, package="data")
        data_version_dict[file_name] = data_version

    # Check if search schema version numbers are the same as each other
    version_list = list(search_version_dict.values())
    curr_ver_list = list(search_current_ver_dict.values())
    if (
        all(ver == version_list[0] for ver in version_list)
        and all(curr_ver == curr_ver_list[0] for curr_ver in curr_ver_list)
    ):
        if not all(curr_ver == version_list[0] for curr_ver in list(search_current_ver_dict.values())):
            print(f"Update search schemas: {curr_ver_list[0]} --> {version_list[0]}")
        else:
            print("Search schemas are up-to-date")
    else:
        # Make search package CHANGELOG message
        search_file_list = list(search_version_dict.keys())
        update_msg = make_changelog_msg(
            file_list=search_file_list,
            package="search",
            current_ver_dict=search_current_ver_dict,
            new_ver_dict=search_version_dict
        )
        if update_msg:
            print(update_msg)
        else:
            print("Data schema are up-to-date")

    # Make data package CHANGELOG message
    version_list = list(data_version_dict.values())
    data_file_list = list(data_version_dict.keys())
    update_msg = make_changelog_msg(
        file_list=data_file_list,
        package="search",
        current_ver_dict=data_current_ver_dict,
        new_ver_dict=data_version_dict
    )
    if update_msg:
        print(update_msg)
    else:
        print("Data schema are up-to-date")
