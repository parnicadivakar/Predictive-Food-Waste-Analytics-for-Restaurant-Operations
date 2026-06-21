import json
import joblib
import os
from db_connection import get_db
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

def train_model():
    db = get_db()
    collection = db['food_wastage_data']
    data = list(collection.find())

    if not data:
        return json.dumps({"error": "MongoDB collection is empty."})

    df = pd.DataFrame(data)

    # Drop MongoDB _id field if present
    if '_id' in df.columns:
        df.drop(columns=['_id'], inplace=True)

    features = ['Number_of_Guests', 'Event_Type', 'Storage_Conditions']
    target = 'Wastage_Food_Amount'

    if not all(col in df.columns for col in features + [target]):
        return json.dumps({"error": f"Missing columns. Available columns: {df.columns.tolist()}"} )

    df = df.fillna(0)  # Handle missing values
    X = pd.get_dummies(df[features], drop_first=True)
    y = df[target]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)

    # Save the model and scaler
    joblib.dump(model, "ml_model.pkl")
    joblib.dump(scaler, "scaler.pkl")

    # Correlation Analysis (only numeric columns)
    numeric_df = df.select_dtypes(include=['number'])
    correlation_matrix = numeric_df.corr()
    top_correlated = correlation_matrix[target].sort_values(ascending=False).to_dict()

       # Actual vs predicted samples (first 10)
    actual_vs_predicted = [
        {"actual": float(a), "predicted": float(p)}
        for a, p in zip(y_test[:10], y_pred[:10])
    ]

    # Food Type vs Average Waste
    food_type_efficiency = (
        df.groupby("Type_of_Food")["Wastage_Food_Amount"]
        .mean()
        .sort_values(ascending=False)
        .to_dict()
    )

    output = {
        "model_status": "Training complete (with visual enhancements)",
        "r2_score": round(r2, 4),
        "top_correlated_factors": top_correlated,
        "sample_predictions": y_pred[:5].tolist(),
        "actual_vs_predicted": actual_vs_predicted,
        "food_type_efficiency": food_type_efficiency
    }


    return json.dumps(output)

if __name__ == "__main__":
    print(train_model())
