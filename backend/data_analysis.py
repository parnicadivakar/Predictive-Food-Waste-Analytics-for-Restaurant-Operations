import json
from db_connection import get_db
import pandas as pd

def analyze_waste():
    db = get_db()
    collection = db['food_wastage_data']
    data = list(collection.find())

    if not data:
        return json.dumps({"error": "MongoDB collection is empty."})

    df = pd.DataFrame(data)

    total_waste = int(df['Wastage_Food_Amount'].sum())
    waste_by_location = df.groupby('Geographical_Location')['Wastage_Food_Amount'].sum().to_dict()
    top_food_types = df.groupby('Type_of_Food')['Wastage_Food_Amount'].sum().sort_values(ascending=False).to_dict()

    output = {
        'total_waste': total_waste,
        'waste_by_location': {k: int(v) for k, v in waste_by_location.items()},
        'top_food_types': {k: int(v) for k, v in top_food_types.items()}
    }

    print(json.dumps(output))  # Ensure output is printed as JSON

if __name__ == "__main__":
    analyze_waste()
