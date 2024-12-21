import json
from notion_client import Client

NOTION_API_KEY = "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"
DATABASE_ID = "155774409b8b80769272eb301a27461b"

notion = Client(auth=NOTION_API_KEY)


def load_json_file(filepath):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def get_notion_data(database_id):
    results = []
    next_cursor = None

    while True:
        response = notion.databases.query(
            **{"database_id": database_id, "start_cursor": next_cursor}
            if next_cursor
            else {"database_id": database_id}
        )
        results.extend(response.get("results", []))
        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break

    return results


def update_notion_page(page_id, updated_fields):
    notion.pages.update(page_id=page_id, properties=updated_fields)


def format_field_value(key, value):
    if key == "Status":
        return {"select": {"name": value}}
    elif key == "Publication Date":
        return {"date": {"start": value}}
    elif key in ["Relevant Links", "DOI"]:
        return {"url": value}
    elif key in ["Venue", "Affiliation", "Abstract", "Authors", "Notes"]:
        return {"rich_text": [{"text": {"content": value}}]}
    elif key == "Citation Count":
        return {"number": value}
    elif key == "Tags":
        return {"multi_select": [{"name": tag} for tag in value.split(",")]}
    elif key == "Contributor":
        return {"people": [{"object": "user", "id": value}]}
    elif key == "Paper Title":
        return {"title": [{"text": {"content": value}}]}
    return None


def add_to_notion(entry):
    new_fields = {}
    for key, value in entry.items():
        formatted_value = format_field_value(key, value)
        if formatted_value:
            new_fields[key] = formatted_value

    print(f"Adding new entry to Notion with DOI: {entry.get('DOI', 'Unknown')}")
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties=new_fields,
    )
    print(f"Successfully added DOI {entry.get('DOI')} to Notion.")


def sync_data(json_data, notion_data, json_file_path):
    json_dois = {record.get("DOI"): record for record in json_data if "DOI" in record}

    notion_dois = {
        page["properties"]["DOI"]["url"]: page
        for page in notion_data
        if "DOI" in page["properties"] and page["properties"]["DOI"]["url"]
    }

    for doi, record in json_dois.items():
        if doi in notion_dois:
            page = notion_dois[doi]
            updates = {}

            for key, value in record.items():
                if key in page["properties"]:
                    property_data = page["properties"][key]
                    if (
                        property_data["type"]
                        in [
                            "rich_text",
                            "url",
                            "date",
                            "select",
                            "number",
                            "multi_select",
                        ]
                        and not property_data[property_data["type"]]
                    ):
                        updates[key] = format_field_value(key, value)

            if updates:
                print(f"Updating Notion page for DOI: {doi}")
                update_notion_page(page["id"], updates)

    for doi, record in json_dois.items():
        if doi not in notion_dois:
            print(f"Adding missing JSON entry to Notion: DOI = {doi}")
            add_to_notion(record)

    with open(json_file_path, "w") as file:
        json.dump(json_data, file, indent=4)
    print("Sync completed. Entries from JSON added to Notion where necessary.")


def main():
    json_file_path = "data.json"
    json_data = load_json_file(json_file_path)

    print("Fetching data from Notion...")
    notion_data = get_notion_data(DATABASE_ID)

    print("Syncing data...")
    sync_data(json_data, notion_data, json_file_path)

    print("Data sync completed.")


if __name__ == "__main__":
    main()