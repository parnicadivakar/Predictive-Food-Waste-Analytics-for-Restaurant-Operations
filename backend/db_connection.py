from pymongo import MongoClient
import pandas as pd

def get_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['food_waste_db']  # Ensure correct database name
    return db

def import_data():
    db = get_db()
    collection = db['food_wastage_data']  # Correct collection name

    # Check if collection is empty before inserting data
    if collection.count_documents({}) == 0:
        df = pd.read_csv('../food_wastage_data.csv')  # Ensure correct path
        collection.insert_many(df.to_dict('records'))
        print("Data imported successfully!")
    else:
        print("MongoDB already contains data.")

if __name__ == "__main__":
    import_data()
