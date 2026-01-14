import http.client
import json
import os


def get_space_info():
    """Get space information including structures and properties."""
    
    # Get credentials from environment variables
    api_token = os.getenv("CAPACITIES_API_TOKEN", "")
    space_id = os.getenv("CAPACITIES_SPACE_ID", "")
    
    if not api_token or not space_id:
        print("❌ Error: Missing required environment variables")
        print("Please set: CAPACITIES_API_TOKEN and CAPACITIES_SPACE_ID")
        return None
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    path = f"/space-info?spaceid={space_id}"

    try:
        conn = http.client.HTTPSConnection("api.capacities.io")
        conn.request("GET", path, headers=headers)

        response = conn.getresponse()

        if response.status == 200:
            data_str = response.read().decode("utf-8")
            data = json.loads(data_str)

            print("✅ Success! Space info retrieved")
            print("=" * 60)

            # Extract and display structures
            structures = data.get("structures", [])
            if structures:
                print(f"\n📋 Found {len(structures)} structure(s) in your space:\n")
                for struct in structures:
                    print(f"🏗️  Structure: {struct.get('title', 'Unknown')}")
                    print(f"   ID: {struct.get('id', 'Unknown')}")
                    print(f"   Plural: {struct.get('pluralName', 'Unknown')}")

                    # Show property definitions
                    properties = struct.get("propertyDefinitions", [])
                    if properties:
                        print(f"   📝 {len(properties)} Properties:")
                        for prop in properties:
                            prop_name = prop.get("name", "Unknown")
                            prop_type = prop.get("dataType", "Unknown")
                            prop_id = prop.get("id", "Unknown")
                            print(f"      - {prop_name} ({prop_type})")
                            print(f"        ID: {prop_id}")
                    else:
                        print("   📝 No properties found")
                    print()

                # If looking for Book structure specifically
                book_structure = next(
                    (s for s in structures if s.get("title") == "Book"), None
                )
                if book_structure:
                    print("\n" + "=" * 60)
                    print("📚 Book Structure Details:")
                    print("=" * 60)
                    print(f"Structure ID: {book_structure.get('id')}")
                    print("\nProperty IDs for import_books.py:")
                    print("-" * 60)
                    for prop in book_structure.get("propertyDefinitions", []):
                        prop_name = prop.get("name", "Unknown")
                        prop_id = prop.get("id", "Unknown")
                        print(f'"{prop_name.lower().replace(" ", "_")}": "{prop_id}",')

            else:
                print("No structures found in this space")

            return data
        else:
            error_data = response.read().decode("utf-8")
            print(f"❌ Error {response.status}: {error_data}")
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None
    finally:
        conn.close()


if __name__ == "__main__":
    print("🔍 Capacities Property Finder")
    print("=" * 60)
    get_space_info()
