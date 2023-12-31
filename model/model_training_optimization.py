# -*- coding: utf-8 -*-
"""model_training_optimization.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16-c2lUlp0aycz2HqsmZPnNvbV4QleLcr
"""


import pandas as pd
import numpy as np
import pickle
df3 = pd.read_csv('featureEngineered_data.csv')
from data_preprocessing import X_train, X_test, y_train, y_test, df, X , y
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from tensorflow import keras
from sklearn.neural_network import MLPClassifier

#model training and evaluation
def train_and_evaluate_model(model, param_grid, X_train, y_train, X_test, y_test):
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1')
    grid_search.fit(X_train, y_train)

    best_params = grid_search.best_params_

    best_models = model.set_params(**best_params)
    best_models.fit(X_train, y_train)

    y_pred = best_models.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("Best Parameters:", best_params)
    print("Accuracy:", accuracy)
    print("Recall:", recall)
    print("Precision:", precision)
    print("F1-Score:", f1)

#parameter grids for Logistic Regression and Random Forest
param_grid_logistic = {
    'C': [0.001, 0.01, 0.1, 1, 10, 100],
    'penalty': ['l2']  # Use 'l2' or 'none' for lbfgs solver
}

param_grid_random_forest = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30]
}

logistic_model = LogisticRegression(solver='lbfgs')
random_forest_model = RandomForestClassifier()

# Train and evaluate models
train_and_evaluate_model(logistic_model, param_grid_logistic, X_train, y_train, X_test, y_test)
train_and_evaluate_model(random_forest_model, param_grid_random_forest, X_train, y_train, X_test, y_test)


#input shape for the neural network
input_shape = X_train.shape[1]

#parameter grid for Neural Network
param_grid_neural_network = {
    'hidden_layer_sizes': [(128, 64), (64, 32), (32, 16)],
    'alpha': [0.0001, 0.001, 0.01]
}

# Initialize Neural Network model
neural_network_model = MLPClassifier()

# GridSearchCV
grid_neural_network = GridSearchCV(neural_network_model, param_grid_neural_network, cv=5, scoring='f1')
grid_neural_network.fit(X_train, y_train)

#best hyperparameters
best_params_neural_network = grid_neural_network.best_params_

# train best model with best hyperparameters
best_model = keras.Sequential([
    keras.layers.Input(shape=(input_shape,)),
    keras.layers.Dense(best_params_neural_network['hidden_layer_sizes'][0], activation='relu'),
    keras.layers.Dense(best_params_neural_network['hidden_layer_sizes'][1], activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])
best_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
best_model.fit(X_train, y_train, epochs=10, batch_size=32)

# Make predictions
y_pred = best_model.predict(X_test)
y_pred_binary = (y_pred >= 0.5).astype(int)

accuracy = accuracy_score(y_test, y_pred_binary)
recall = recall_score(y_test, y_pred_binary)
precision = precision_score(y_test, y_pred_binary)
f1 = f1_score(y_test, y_pred_binary)


print("Best Parameters:", best_params_neural_network)
print("Accuracy:", accuracy)
print("Recall:", recall)
print("Precision:", precision)
print("F1-Score:", f1)

import matplotlib.pyplot as plt

# Results
model_names = ['Logistic Regression', 'Random Forest', 'Neural Network']
accuracy_scores = [0.4999, 0.4928, 0.5042]  # Replace with your actual accuracy scores
precision_scores = [0.49315531519351025, 0.48866754751499136, 0.5016139444803098]  # Replace with your actual precision scores
recall_scores = [0.29412357625239394, 0.4846285656687834, 0.5042]  # Replace with your actual recall scores
f1_scores = [0.3684808687965653, 0.48663967611336034, 0.13548387096774192]  # Replace with your actual F1 scores

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']

legend_data = [(model_name, accuracy_score * 100) for model_name, accuracy_score in zip(model_names, accuracy_scores)]
legend_data.sort(key=lambda x: x[1], reverse=True)

sorted_model_names = [data[0] for data in legend_data]
sorted_accuracy_percentages = [data[1] for data in legend_data]

fig, ax = plt.subplots(figsize=(10, 6))

def add_accuracy_percentage(legend_labels):
    for i in range(len(legend_labels)):
        legend_labels[i] = f'{legend_labels[i]} ({sorted_accuracy_percentages[i]:.2f}%)'

for i, model_name in enumerate(sorted_model_names):
    plt.plot(metrics, [accuracy_scores[model_names.index(model_name)],
                      precision_scores[model_names.index(model_name)],
                      recall_scores[model_names.index(model_name)],
                      f1_scores[model_names.index(model_name)]],
             marker='o', label=model_name)

plt.xlabel('Metrics')
plt.ylabel('Scores')
plt.title('Comparison of Model Metrics')

legend_labels = list(sorted_model_names)
add_accuracy_percentage(legend_labels)
plt.legend(legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.2))

plt.tight_layout()
plt.grid(True)
plt.show()

correlation_matrix = df.corr()

# correlation of each feature with Churn
correlation_with_churn = correlation_matrix['Churn']

# features by their correlation with Churn in descending order
sorted_correlation = correlation_with_churn.abs().sort_values(ascending=False)

print("Correlation with Churn:")
print(sorted_correlation)

plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Matrix")
plt.show()

# feature importances
import xgboost as xgb

model = xgb.XGBClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
feature_importances = model.feature_importances_

importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importances})
importance_df = importance_df.sort_values(by='Importance', ascending=False)

print(importance_df)

from keras.models import load_model

best_model.save('final_model.h5')

best_model = load_model('final_model.h5')

#function for churn prediction
def predict_churn(location, age, subscription_length, monthly_bill, total_usage_gb):
    
    data = pd.DataFrame({
        'Age': [age],
        'Subscription_Length_Months': [subscription_length],
        'Monthly_Bill': [monthly_bill],
        'Total_Usage_GB': [total_usage_gb]
    })

    # one-hot encoding to the 'Location' feature
    for category in location_categories:
        if location == category:
            data[category] = 1
        else:
            data[category] = 0

    # dummy values for the two gender features 
    data['is_0'] = 0
    data['is_1'] = 0

    # make predictions
    churn_prediction = best_model.predict(data)

    churn_result = "Churn" if churn_prediction == 1 else "No Churn"

    return churn_result

predicted_churn = predict_churn('Miami', 36, 3, 96 ,297 )
print(predicted_churn)
