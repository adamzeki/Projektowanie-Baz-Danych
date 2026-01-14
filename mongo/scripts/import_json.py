import json
import pymongo
from pymongo import MongoClient, InsertOne
from pathlib import Path

# --- CONFIGURATION ---
FOLDER_PATH = Path("../jsons")
CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "pbd"

def import_data():
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client[DATABASE_NAME]

    if not FOLDER_PATH.exists():
        print(f"Error: Folder '{FOLDER_PATH.resolve()}' does not exist.")
        return

    print(f"Scanning folder: {FOLDER_PATH.resolve()}")

    for file_path in FOLDER_PATH.glob("*.json"):
        collection_name = file_path.stem
        collection = db[collection_name]

        requesting = []
        print(f"Processing: {file_path.name} -> Collection: {collection_name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # FIX: Use json.load(f) to read the WHOLE file at once
                file_data = json.load(f)

                if isinstance(file_data, list):
                    # It's an array of objects [ {}, {} ]
                    for item in file_data:
                        requesting.append(InsertOne(item))
                elif isinstance(file_data, dict):
                    # It's a single object {}
                    requesting.append(InsertOne(file_data))

            if requesting:
                result = collection.bulk_write(requesting)
                print(f"  -> Successfully inserted {result.inserted_count} documents.")
            else:
                print(f"  -> File was empty or contained no valid data.")

        except json.JSONDecodeError as e:
            print(f"  -> [Error] Invalid JSON format in {file_path.name}: {e}")
        except Exception as e:
            print(f"  -> [Error] processing {file_path.name}: {e}")

    client.close()
    print("All done!")

if __name__ == "__main__":
    import_data()
