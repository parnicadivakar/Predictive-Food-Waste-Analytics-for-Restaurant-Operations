

# Install Flask if not already installed: pip install flask

from flask import Flask, jsonify, request, render_template, send_file
import subprocess
import os
import json
import pandas as pd
import plotly.express as px
from plotly.io import to_html
import joblib
import numpy as np


app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

def run_script(script_name):
    try:
        script_path = os.path.abspath(f"backend/{script_name}.py")
        result = subprocess.run(['python', script_path], capture_output=True, text=True, shell=True)

        try:
            output_json = json.loads(result.stdout.strip())  # Parse JSON correctly
        except json.JSONDecodeError:
            output_json = {"error": "Invalid JSON response"}

        return {'output': output_json, 'error': result.stderr.strip()}
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def home():
    return render_template('landing.html')  # Serve the landing page by default

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')  # Serve the main dashboard page

@app.route('/run_analysis', methods=['GET'])
def run_analysis():
    return jsonify(run_script("data_analysis"))

@app.route('/run_ml', methods=['GET'])
def run_ml():
    return jsonify(run_script("ml_model"))

@app.route('/run_recommendations', methods=['GET'])
def run_recommendations():
    return jsonify(run_script("recommendations"))

@app.route('/run_all', methods=['GET'])
def run_all():
    analysis = run_script("data_analysis")
    ml = run_script("ml_model")
    recommendations = run_script("recommendations")

    errors = {
        'data_analysis': analysis.get('error', ""),
        'ml_model': ml.get('error', ""),
        'recommendations': recommendations.get('error', "")
    }
    
    # Remove empty errors from response
    errors_if_any = {k: v for k, v in errors.items() if v.strip() != ""}

    return jsonify({
        'data_analysis': analysis.get('output', ""),
        'ml_model': ml.get('output', ""),
        'recommendations': recommendations.get('output', ""),
        'errors': errors_if_any  # Will be omitted if no errors exist
    })
@app.route('/dataset_overview')
def dataset_overview():
    df = pd.read_csv("food_wastage_data.csv")

    shape_info = f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns."

    # 1. Data Types Chart
    data_types = df.dtypes.value_counts().reset_index()
    data_types.columns = ['Data Type', 'Count']
    data_types['Data Type'] = data_types['Data Type'].astype(str)  # ✅ Fix added
    fig_data_types = px.bar(data_types, x='Data Type', y='Count', title='Column Data Types')
    html_data_types = to_html(fig_data_types, full_html=False)

    # 2. Missing Values Chart
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    html_missing = None
    if not missing.empty:
        fig_missing = px.bar(x=missing.index, y=missing.values, title='Missing Values by Column',
                             labels={'x': 'Column', 'y': 'Missing Values'})
        html_missing = to_html(fig_missing, full_html=False)

    # 3. Categorical Distributions
    category_plots = []
    for col in ['Event_Type', 'Storage_Conditions', 'Type_of_Food', 'Geographical_Location']:
        if col in df.columns:
            dist = df[col].value_counts().reset_index()
            dist.columns = [col, 'Count']
            fig = px.bar(dist, x=col, y='Count', title=f'Distribution of {col}')
            category_plots.append(to_html(fig, full_html=False))

    # 4. Average Wastage per Event Type
    if 'Event_Type' in df.columns and 'Wastage_Food_Amount' in df.columns:
        avg_waste = df.groupby('Event_Type')['Wastage_Food_Amount'].mean().reset_index()
        fig_avg = px.bar(avg_waste, x='Event_Type', y='Wastage_Food_Amount',
                         title='Average Wastage per Event Type',
                         labels={'Wastage_Food_Amount': 'Average Waste (kg)'})
        html_avg_waste = to_html(fig_avg, full_html=False)
    else:
        html_avg_waste = None

    return render_template(
        'dataset_overview.html',
        shape_info=shape_info,
        html_data_types=html_data_types,
        html_missing=html_missing,
        category_plots=category_plots,
        html_avg_waste=html_avg_waste
    )
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    recommendations = []

    if request.method == 'POST':
        guests = int(request.form['guests'])
        event_type = request.form['event_type']
        storage = request.form['storage']

        # Prepare the input DataFrame
        df_input = pd.DataFrame([{
            'Number_of_Guests': guests,
            'Event_Type': event_type,
            'Storage_Conditions': storage
        }])

        # One-hot encode and align with model columns
        df_encoded = pd.get_dummies(df_input)
        expected_cols = joblib.load('model_columns.pkl')
        for col in expected_cols:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[expected_cols]

        # Scale and predict
        scaler = joblib.load("scaler.pkl")
        X_scaled = scaler.transform(df_encoded)

        model = joblib.load("ml_model.pkl")
        prediction = round(model.predict(X_scaled)[0], 2)

        # 💡 Rule-based recommendations
        if guests > 100:
            recommendations.append("Consider portion control for large guest counts.")
        if event_type == "Wedding":
            recommendations.append("Weddings often result in higher waste — plan for donations.")
        if storage == "Ambient":
            recommendations.append("Use cold storage where possible to reduce spoilage.")
        if prediction > 30:
            recommendations.append("Expected waste is high — evaluate menu and quantity planning.")

    return render_template('predict.html', prediction=prediction, recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug=True)
    