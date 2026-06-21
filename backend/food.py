import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Step 1: Load the dataset
df = pd.read_csv('food_wastage_data.csv')

# Step 2: Connect to MongoDB and store data
client = MongoClient('mongodb://localhost:27017/')
db = client['food_waste_db']
collection = db['wastage_data']

# Insert data into MongoDB
collection.insert_many(df.to_dict('records'))

# Step 3: Retrieve data from MongoDB
data = pd.DataFrame(list(collection.find()))

# Step 4: Data Visualization
plt.figure(figsize=(10, 6))
sns.boxplot(x='Type of Food', y='Quantity of Food Wasted', data=data)
plt.title('Food Wastage by Type of Food')
plt.xticks(rotation=45)
plt.show()

# Step 5: Prepare Data for Machine Learning
features = ['Number of Guests', 'Event Type', 'Storage Conditions', 'Purchase History', 'Seasonality', 'Preparation Method']
X = pd.get_dummies(data[features])
y = data['Quantity of Food Wasted']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Feature Importance Analysis
feature_importances = pd.Series(model.feature_importances_, index=X.columns)
feature_importances.nlargest(10).plot(kind='barh')
plt.title('Top 10 Features Influencing Food Wastage')
plt.show()