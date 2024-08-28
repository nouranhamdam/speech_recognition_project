# -*- coding: utf-8 -*-
"""speech recognition .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1e-emrie82qqSpMJA45olbjmECAVYvuA2

# **1-Import Libraries and Define Paths**
"""

!pip install kaggle
!kaggle datasets download -d mmoreaux/audio-cats-and-dogs
!pip install numpy pandas tensorflow scikit-learn librosa
import os
import zipfile
import numpy as np
import librosa
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import Input
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns
zip_file_path = '/content/audio-cats-and-dogs.zip'
extracted_path = '/content/extracted_dataset'
audio_path = os.path.join(extracted_path, 'cats_dogs')
os.makedirs(extracted_path, exist_ok=True)

"""# **2-Data Visualization**"""

def plot_data_distribution(labels):
    sns.countplot(x=labels)
    plt.title('Distribution of Labels')
    plt.xlabel('Label')
    plt.ylabel('Count')
    plt.show()
plot_data_distribution(y)

"""# **3-Data Processing**"""

def preprocess_data(features, labels):
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(labels)
    y_categorical = to_categorical(y_encoded)

    X_train, X_test, y_train, y_test = train_test_split(features, y_categorical, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test, label_encoder

X_train, X_test, y_train, y_test, label_encoder = preprocess_data(X, y)

"""# **4-Data Extraction**"""

def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_data(audio_path):
    labels = []
    features = []

    for file_name in os.listdir(audio_path):
        file_path = os.path.join(audio_path, file_name)
        if file_name.startswith('cat'):
            label = 'cat'
        elif file_name.startswith('dog'):
            label = 'dog'
        else:
            continue

        feature = extract_features(file_path)
        if feature is not None:
            features.append(feature)
            labels.append(label)

    return np.array(features), np.array(labels)
X, y = load_data(audio_path)

"""# **5-Data Augmentation**"""

def augment_audio(y, noise_factor=0.005):
    noise = np.random.randn(len(y))
    augmented_y = y + noise_factor * noise
    return augmented_y

"""# **6-Model Building**"""

def build_model(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(2, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model
model = build_model(X_train.shape[1:])

"""# **7- Model Evaluation**"""

def evaluate_model(model, X_test, y_test):
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f'Test Loss: {loss:.4f}')
    print(f'Test Accuracy: {accuracy:.4f}')

    y_pred = model.predict(X_test)
    cm = confusion_matrix(np.argmax(y_test, axis=1), np.argmax(y_pred, axis=1))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_encoder.classes_)
    disp.plot(cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.show()

evaluate_model(model, X_test, y_test)

"""---

# **Comparing Models:**

# **1-Defining Functions for Training and Evaluation**
"""

def train_and_evaluate_model(model, X_train, y_train, X_test, y_test):
    history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=0)
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    return history, loss, accuracy

"""# **2-Defining Function to Compare Models**"""

def compare_models(models, names, X_train, y_train, X_test, y_test, label_encoder):
    results = []

    for model, name in zip(models, names):
        print(f"Training and evaluating {name}...")
        history, loss, accuracy = train_and_evaluate_model(model, X_train, y_train, X_test, y_test)
        results.append((name, accuracy))
        print(f"{name} - Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}")
        y_pred = model.predict(X_test)
        cm = confusion_matrix(np.argmax(y_test, axis=1), np.argmax(y_pred, axis=1))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_encoder.classes_)
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f'Confusion Matrix - {name}')
        plt.show()
    names, accuracies = zip(*results)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=names, y=accuracies, palette='viridis')
    plt.title('Model Accuracy Comparison')
    plt.xlabel('Model')
    plt.ylabel('Accuracy')
    plt.ylim(0, 1)
    plt.show()

"""# **3- Building Models**"""

model_1 = build_model(X_train.shape[1:])
model_2 = build_model(X_train.shape[1:])
models = [model_1, model_2]
names = ['Model 1', 'Model 2']

"""# **4-Comparing Models**"""

compare_models(models, names, X_train, y_train, X_test, y_test, label_encoder)