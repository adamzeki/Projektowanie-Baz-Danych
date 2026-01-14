import pymongo
import json
import os


def import_jsons_to_mongo(directory_path, db_name, mongo_uri="mongodb://localhost:27017/"):
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]

    print(f"Connected to database: {db_name}")

    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)

            collection_name = os.path.splitext(filename)[0]
            collection = db[collection_name]

            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)

                    if isinstance(data, list):
                        if len(data) > 0:
                            result = collection.insert_many(data)
                            print(f"Successfully inserted {len(result.inserted_ids)} docs into '{collection_name}'")
                    else:
                        result = collection.insert_one(data)
                        print(f"Successfully inserted 1 doc into '{collection_name}'")

                except Exception as e:
                    print(f"Failed to process {filename}: {e}")

    print("\nImport process complete.")


if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    JSON_DIR = os.path.join(PROJECT_DIR, "jsons")

    import_jsons_to_mongo(JSON_DIR, "ProjectDb")