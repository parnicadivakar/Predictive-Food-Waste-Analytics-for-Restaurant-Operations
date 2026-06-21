import json
from db_connection import get_db
import pandas as pd

def generate_recommendations():
    db = get_db()
    collection = db['food_wastage_data']
    data = list(collection.find())

    if not data:
        return json.dumps([])  # Return empty list instead of an error

    df = pd.DataFrame(data)

    required_columns = ['Wastage_Food_Amount', 'Type_of_Food', 'Geographical_Location']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return json.dumps([])  # Return empty list if columns are missing

    recommendations = []

    if df['Wastage_Food_Amount'].sum() > 10000:
        recommendations.append("Consider implementing portion control measures.")

    high_waste_food = df.groupby('Type_of_Food')['Wastage_Food_Amount'].sum().idxmax()
    recommendations.append(f"Consider better inventory management for {high_waste_food}.")

    high_waste_location = df.groupby('Geographical_Location')['Wastage_Food_Amount'].sum().idxmax()
    recommendations.append(f"Optimize waste management strategies in {high_waste_location} areas.")

    print(json.dumps(recommendations))  # Print a clean list

if __name__ == "__main__":
    generate_recommendations()
