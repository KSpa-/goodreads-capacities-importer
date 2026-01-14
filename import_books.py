import pandas as pd
import requests
import time
import os

# --- CONFIGURATION ---
API_TOKEN = os.getenv("CAPACITIES_API_TOKEN", "")
SPACE_ID = os.getenv("CAPACITIES_SPACE_ID", "")
STRUCTURE_ID = os.getenv("CAPACITIES_STRUCTURE_ID", "")

# Property IDs from Capacities Book structure
# Will need to find your own property ids, can use find_properties.py 
# Also assumes that you have already created all the properties on an Object alreayd 
PROP_IDS = {
    "author": "AUTHOR_PROPERTY_ID",
    "isbn": "ISBN_PROPERTY_ID",
    "rating": "RATING_PROPERTY_ID",
    "publisher": "PUBLISHER_PROPERTY_ID",
    "date_read": "DATE_READ_PROPERTY_ID",
    "pages": "PAGES_PROPERTY_ID",
    "description": "description",
    "notes": "NOTES_PROPERTY_ID",
    "cover_image": "",
    "tags": "tags",
    "bookshelves": "BOOKSHELVES_PROPERTY_ID",
}


def clean_isbn(val):
    """Remove GoodReads CSV formatting artifacts from ISBN field"""
    if pd.isna(val) or val == "":
        return ""
    return str(val).replace('="', "").replace('"', "")


def load_csv_data():
    """Load GoodReads export and filter to read books only"""
    df = pd.read_csv("goodreads_library_export.csv")

    # Only import books with a read date or rating
    df_read = df[(df["Date Read"].notna()) | (df["My Rating"] > 0)].copy()
    df_read["Bookshelves"] = df_read["Bookshelves"].fillna("Read")

    print(f"Total books in export: {len(df)}")
    print(f"Books you've read: {len(df_read)}")
    print(f"Skipping {len(df) - len(df_read)} unread books\n")

    return df_read


def preview_import(df, num_books=3):
    """Show preview of books to be imported"""
    print(f"📋 Preview of first {num_books} books to be imported:\n")

    for index, row in df.head(num_books).iterrows():
        print(f"Book #{index + 1}: {row['Title']}")
        print(f"  Author: {row['Author']}")
        print(f"  ISBN: {clean_isbn(row['ISBN13'])}")
        print(f"  Rating: {row['My Rating'] if row['My Rating'] > 0 else 'No rating'}")
        print(
            f"  Pages: {row['Number of Pages'] if pd.notna(row['Number of Pages']) else 'Unknown'}"
        )
        print(
            f"  Date Read: {row['Date Read'] if pd.notna(row['Date Read']) and str(row['Date Read']).strip() else 'Not read'}"
        )
        print(
            f"  Publisher: {row['Publisher'] if pd.notna(row['Publisher']) else 'Unknown'}"
        )
        print(
            f"  Bookshelves: {row['Bookshelves'] if pd.notna(row['Bookshelves']) else 'None'}"
        )
        print(
            f"  Review: {'Yes' if pd.notna(row['My Review']) and str(row['My Review']).strip() else 'No'}"
        )
        print("-" * 50)


def import_to_capacities(df):
    """Import books to Capacities via API"""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    for index, row in df.iterrows():
        properties = {
            PROP_IDS["author"]: row["Author"] if pd.notna(row["Author"]) else "",
            PROP_IDS["isbn"]: clean_isbn(row["ISBN13"]),
            PROP_IDS["rating"]: int(row["My Rating"])
            if pd.notna(row["My Rating"]) and row["My Rating"] > 0
            else None,
            PROP_IDS["publisher"]: row["Publisher"]
            if pd.notna(row["Publisher"])
            else "",
            PROP_IDS["pages"]: int(row["Number of Pages"])
            if pd.notna(row["Number of Pages"])
            else None,
        }

        # Convert date from YYYY/MM/DD to YYYY-MM-DD
        if pd.notna(row["Date Read"]) and str(row["Date Read"]).strip() != "":
            try:
                date_str = str(row["Date Read"]).replace("/", "-")
                properties[PROP_IDS["date_read"]] = date_str
            except Exception as e:
                print(
                    f"Warning: Could not parse date '{row['Date Read']}' for {row['Title']}"
                )

        # Add reviews to notes field
        if pd.notna(row["My Review"]) and str(row["My Review"]).strip() != "":
            properties[PROP_IDS["notes"]] = str(row["My Review"])

        if pd.notna(row["Private Notes"]) and str(row["Private Notes"]).strip() != "":
            existing_notes = properties.get(PROP_IDS["notes"], "")
            if existing_notes:
                properties[PROP_IDS["notes"]] = (
                    f"{existing_notes}\n\nPrivate Notes:\n{row['Private Notes']}"
                )
            else:
                properties[PROP_IDS["notes"]] = (
                    f"Private Notes:\n{row['Private Notes']}"
                )

        # Add shelf info to description
        if pd.notna(row["Bookshelves"]) and str(row["Bookshelves"]).strip() != "":
            shelf_info = f"Bookshelves: {row['Bookshelves']}"
            properties[PROP_IDS["description"]] = shelf_info

        # Add publication year to description
        if (
            pd.notna(row["Year Published"])
            and PROP_IDS["description"] not in properties
        ):
            properties[PROP_IDS["description"]] = (
                f"Published: {int(row['Year Published'])}"
            )
        elif pd.notna(row["Year Published"]) and properties.get(
            PROP_IDS["description"]
        ):
            properties[PROP_IDS["description"]] += (
                f" | Published: {int(row['Year Published'])}"
            )

        # Clean up empty values
        properties = {
            k: v
            for k, v in properties.items()
            if v is not None and str(v).strip() != ""
        }

        payload = {
            "spaceId": SPACE_ID,
            "structureId": STRUCTURE_ID,
            "title": row["Title"],
            "properties": properties,
        }

        try:
            response = requests.post(
                "https://api.capacities.io/objects", headers=headers, json=payload
            )
            if response.status_code == 200 or response.status_code == 201:
                print(f"[{index + 1}/{len(df)}] Successfully imported: {row['Title']}")
            else:
                print(
                    f"FAILED {row['Title']}: {response.status_code} - {response.text}"
                )
        except Exception as e:
            print(f"Error on {row['Title']}: {e}")

        # Rate limiting: ~50 requests/min
        time.sleep(1.2)


if __name__ == "__main__":
    # Check for required environment variables
    if not API_TOKEN or not SPACE_ID or not STRUCTURE_ID:
        print("❌ Error: Missing required environment variables")
        print("Please set: CAPACITIES_API_TOKEN, CAPACITIES_SPACE_ID, CAPACITIES_STRUCTURE_ID")
        exit(1)

    df = load_csv_data()

    print(f"📚 Goodreads to Capacities Import Tool")
    print(f"Space ID: {SPACE_ID}")
    print(f"Structure ID: {STRUCTURE_ID} (Book)")
    print(f"Total books to import: {len(df)}")
    print("\n" + "=" * 50)

    df = df.reset_index(drop=True)
    rows_to_preview = 10
    preview_import(df, rows_to_preview)

    response = (
        input(
            "\nDo you want to proceed with import? (y/n, or 'test' for first 10 only): "
        )
        .lower()
        .strip()
    )

    if response == "test":
        print(f"\n🧪 Test mode: Importing first {rows_to_preview} books only...")
        df_subset = df.head(rows_to_preview)
        import_to_capacities(df_subset)
    elif response == "y" or response == "yes":
        print("\n🚀 Starting full import...")
        import_to_capacities(df)
    else:
        print("\n❌ Import cancelled.")

    print("\n" + "=" * 50)
    print("✅ Process completed!")
