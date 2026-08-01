# Auto-generated Code Vault for 'RandomForestClassifier (Scikit-learn)' [Python]

from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import glob
import os
import zipfile

def download_dataset():
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files('uciml/breast-cancer-wisconsin-data', path='D:/graph/data/datasets', unzip=True)

def load_data():
    csv_files = glob.glob('D:/graph/data/datasets/**/*.csv', recursive=True)
    data = pd.read_csv(csv_files[0])
    return data

def prepare_data(data):
    X = data.drop('class', axis=1)
    y = data['class']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    matrix = confusion_matrix(y_test, y_pred)
    return accuracy, report, matrix

def main():
    download_dataset()
    data = load_data()
    X_train, X_test, y_train, y_test = prepare_data(data)
    model = train_model(X_train, y_train)
    accuracy, report, matrix = evaluate_model(model, X_test, y_test)
    print(f'Accuracy: {accuracy:.3f}')
    print('Classification Report:')
    print(report)
    print('Confusion Matrix:')
    print(matrix)

if __name__ == '__main__':
    main()
