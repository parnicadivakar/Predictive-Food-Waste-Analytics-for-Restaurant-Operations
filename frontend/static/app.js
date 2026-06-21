app.js
async function fetchAndVisualize(endpoint) {
    const runButton = document.getElementById('runButton');
    runButton.innerText = "Processing...";
    runButton.disabled = true;

    try {
        console.log(`Fetching data from: ${endpoint}`);
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`Failed to fetch data from ${endpoint}`);

        const data = await response.json();
        console.log("API Response:", data); // Debugging

        // Error display
        if (data.errors) {
            document.getElementById('error-messages').innerText = `Errors: ${JSON.stringify(data.errors, null, 2)}`;
        }

        // Charts from data_analysis
        if (data.data_analysis) {
            console.log("Updating charts...");
            if (data.data_analysis.waste_by_location) {
                visualizeBarChart('wasteChart', data.data_analysis.waste_by_location);
            }
            if (data.data_analysis.top_food_types) {
                visualizePieChart('foodTypeChart', data.data_analysis.top_food_types);
            }
        }

        // ML model output
        if (data.ml_model) {
            console.log("Updating ML model insights...");
            document.getElementById('r2-score').innerText = data.ml_model.r2_score ?? '-';

            // Correlation Factors: bullet list + chart
            if (data.ml_model.top_correlated_factors) {
                const correlationList = document.getElementById('correlation-factors');
                correlationList.innerHTML = '';
                Object.entries(data.ml_model.top_correlated_factors).forEach(([factor, value]) => {
                    const li = document.createElement('li');
                    li.innerText = `${factor}: ${value.toFixed(4)}`;
                    correlationList.appendChild(li);
                });

                // Render correlation chart
                renderCorrelationChart('correlationChart', data.ml_model.top_correlated_factors);
            }

            // Sample predictions
            if (Array.isArray(data.ml_model.sample_predictions)) {
                const predictionsList = document.getElementById('sample-predictions');
predictionsList.innerHTML = 'These values represent the predicted food wastage (in kilograms) for a sample of upcoming events, based on features such as the number of guests, event type, and storage conditions.<br><br>';

data.ml_model.sample_predictions.forEach(prediction => {
    const li = document.createElement('li');
    li.innerText = `Predicted Waste: ${prediction.toFixed(2)} kg`;
    predictionsList.appendChild(li);
});

            }
            // Actual vs Predicted Chart
if (data.ml_model.actual_vs_predicted) {
    renderActualVsPredictedChart('actualPredictedChart', data.ml_model.actual_vs_predicted);
}

// Food Type Efficiency Chart
if (data.ml_model.food_type_efficiency) {
    renderFoodEfficiencyChart('foodEfficiencyChart', data.ml_model.food_type_efficiency);
}

        }



        // Display recommendations
        if (Array.isArray(data.recommendations)) {
            displayRecommendations(data.recommendations);
        }

    } catch (error) {
        console.error("Error fetching data:", error);
        document.getElementById('error-messages').innerText = `Error: ${error.message}`;
    } finally {
        runButton.innerText = "Run Data Analysis, ML Model & Recommendations";
        runButton.disabled = false;
    }
}

function runAllProcesses() {
    fetchAndVisualize('/run_all');
}

// --- Chart Rendering Helpers ---

function visualizeBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Food Waste Amount',
                data: Object.values(data),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function visualizePieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Food Types',
                data: Object.values(data),
                backgroundColor: [
                    '#ff6384', '#36a2eb', '#cc65fe', '#ffce56',
                    '#2ecc71', '#e67e22', '#95a5a6', '#f39c12'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

function renderCorrelationChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    const labels = Object.keys(data);
    const values = Object.values(data).map(v => parseFloat(v.toFixed(4)));

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Correlation with Wastage_Food_Amount',
                data: values,
                backgroundColor: 'rgba(255, 159, 64, 0.6)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1
                }
            }
        }
    });
}

function displayRecommendations(data) {
    const container = document.getElementById('recommendations');
    container.innerHTML = '';
    data.forEach(rec => {
        const li = document.createElement('li');
        li.innerText = rec;
        container.appendChild(li);
    });
}
function renderBarChart(canvasId, data, label = 'Value') {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: label,
                data: Object.values(data),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function renderActualVsPredictedChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const labels = data.map((_, i) => `Sample ${i + 1}`);
    const actual = data.map(d => d.actual);
    const predicted = data.map(d => d.predicted);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Waste',
                    data: actual,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)'
                },
                {
                    label: 'Predicted Waste',
                    data: predicted,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderFoodEfficiencyChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Avg Waste per Food Type',
                data: Object.values(data),
                backgroundColor: 'rgba(255, 206, 86, 0.7)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}
