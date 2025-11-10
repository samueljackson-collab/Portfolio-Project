#!/usr/bin/env python3
"""
Tab Classification Model Training Script
Trains a TensorFlow Lite model for categorizing browser tabs
"""

import tensorflow as tf
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Categories for classification
CATEGORIES = ['work', 'research', 'shopping', 'social', 'entertainment', 'news', 'custom']

# Feature extraction patterns
DOMAIN_PATTERNS = {
    'work': ['github.com', 'gitlab.com', 'stackoverflow.com', 'docs.google.com',
             'notion.so', 'slack.com', 'teams.microsoft.com', 'zoom.us'],
    'research': ['wikipedia.org', 'scholar.google.com', 'arxiv.org', 'medium.com', 'dev.to'],
    'shopping': ['amazon.com', 'ebay.com', 'etsy.com', 'shopify.com', 'walmart.com'],
    'social': ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'reddit.com'],
    'entertainment': ['youtube.com', 'netflix.com', 'spotify.com', 'twitch.tv', 'hulu.com'],
    'news': ['news.google.com', 'bbc.com', 'cnn.com', 'reuters.com', 'nytimes.com']
}

KEYWORD_PATTERNS = {
    'work': ['github', 'code', 'api', 'docs', 'documentation', 'developer', 'programming'],
    'research': ['research', 'study', 'paper', 'journal', 'academic', 'scholar'],
    'shopping': ['buy', 'shop', 'cart', 'price', 'order', 'product'],
    'social': ['social', 'friend', 'post', 'share', 'like', 'comment'],
    'entertainment': ['video', 'watch', 'movie', 'music', 'play', 'stream'],
    'news': ['news', 'article', 'breaking', 'latest', 'report']
}


def generate_synthetic_data(num_samples=10000):
    """
    Generate synthetic feature vectors and corresponding category labels for training.
    
    Generates approximately `num_samples` examples by evenly splitting the total across CATEGORIES and calling `extract_features_synthetic` for each sample to produce a feature vector.
    
    Parameters:
        num_samples (int): Approximate total number of samples to produce; samples are distributed evenly across categories.
    
    Returns:
        data (np.ndarray): 2D array of feature vectors with shape (N, D) where N is the total produced samples (approximately `num_samples`) and D is the feature dimension.
        labels (np.ndarray): 1D array of category strings with length N corresponding to each row in `data`.
    """
    data = []
    labels = []

    for category in CATEGORIES:
        num_category_samples = num_samples // len(CATEGORIES)

        for _ in range(num_category_samples):
            # Generate features
            features = extract_features_synthetic(category)
            data.append(features)
            labels.append(category)

    return np.array(data), np.array(labels)


def extract_features_synthetic(category):
    """
    Create a synthetic feature vector representing a browser tab for the given category.
    
    Parameters:
        category (str): Target category name (one of CATEGORIES) used to bias synthetic feature values.
    
    Returns:
        list: Feature vector containing:
            - domain-based features for each category in CATEGORIES except 'custom' (higher values when matching `category`),
            - keyword-based features for each category in CATEGORIES except 'custom' (higher values when matching `category`),
            - normalized path depth (float in [0,1]),
            - has query params indicator (0.0 or 1.0),
            - has fragment indicator (0.0 or 1.0).
    """
    features = []

    # Domain-based features (one-hot encoding)
    for cat in CATEGORIES[:-1]:  # Exclude 'custom'
        if cat == category:
            # High probability for matching category
            features.append(np.random.uniform(0.7, 1.0))
        else:
            # Low probability for non-matching
            features.append(np.random.uniform(0.0, 0.3))

    # Keyword-based features (normalized counts)
    for cat in CATEGORIES[:-1]:
        if cat == category:
            features.append(np.random.uniform(0.6, 1.0))
        else:
            features.append(np.random.uniform(0.0, 0.4))

    # URL structure features
    features.append(np.random.uniform(0.0, 1.0))  # Path depth (normalized)
    features.append(np.random.choice([0.0, 1.0]))  # Has query params
    features.append(np.random.choice([0.0, 1.0]))  # Has fragment

    return features


def extract_features_real(url, title, content):
    """
    Extracts a feature vector from a browser tab's URL, title, and content for category classification.
    
    The returned list contains features in the following order:
    1) Domain-match indicators: for each category in DOMAIN_PATTERNS, `1.0` if any pattern appears in the URL (case-insensitive), otherwise `0.0`.
    2) Keyword-match scores: for each category in KEYWORD_PATTERNS, a score in [0.0, 1.0] computed as (2 * title_matches + content_matches) / (len(keywords) * 3) and clipped to 1.0.
    3) URL-structure features:
       - Normalized path depth in [0.0, 1.0] (path segments beyond protocol+domain divided by 10, clipped to 1.0).
       - Query presence indicator: `1.0` if the URL contains '?', otherwise `0.0`.
       - Fragment presence indicator: `1.0` if the URL contains '#', otherwise `0.0`.
    
    Parameters:
        url (str): The full URL of the tab.
        title (str): The tab or page title.
        content (str): The page content or snippet.
    
    Returns:
        list: A 1D list of float features following the order described above.
    """
    features = []

    url_lower = url.lower()
    title_lower = title.lower()
    content_lower = content.lower()

    # Domain-based features
    for category, domains in DOMAIN_PATTERNS.items():
        match = any(domain in url_lower for domain in domains)
        features.append(1.0 if match else 0.0)

    # Keyword-based features
    for category, keywords in KEYWORD_PATTERNS.items():
        title_matches = sum(1 for kw in keywords if kw in title_lower)
        content_matches = sum(1 for kw in keywords if kw in content_lower)
        score = (title_matches * 2 + content_matches) / (len(keywords) * 3)
        features.append(min(score, 1.0))

    # URL structure features
    path_depth = len(url.split('/')) - 3  # Subtract protocol and domain
    features.append(min(path_depth / 10.0, 1.0))
    features.append(1.0 if '?' in url else 0.0)
    features.append(1.0 if '#' in url else 0.0)

    return features


def build_model(input_dim, num_classes):
    """
    Create and compile a Keras Sequential classification model with a small dense architecture.
    
    The model is configured with an input layer matching `input_dim`, three hidden dense layers (128, 64, 32 units) with ReLU activations and dropout between layers, and a softmax output layer sized for `num_classes`. The model is compiled with the Adam optimizer, `sparse_categorical_crossentropy` loss, and accuracy metric.
    
    Returns:
        keras.Model: A compiled Keras Sequential model ready for training.
    """
    model = models.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


def train_model(X_train, y_train, X_val, y_val):
    """
    Train a tab classification model and return the trained model, fitted label encoder, and training history.
    
    Parameters:
        X_train (np.ndarray): Training feature matrix with shape (n_samples, n_features).
        y_train (Sequence[str] | np.ndarray): Training labels as category strings.
        X_val (np.ndarray): Validation feature matrix with shape (n_val_samples, n_features).
        y_val (Sequence[str] | np.ndarray): Validation labels as category strings.
    
    Returns:
        tuple: A 3-tuple containing:
            - model: The compiled and trained Keras Sequential model.
            - label_encoder: A fitted sklearn LabelEncoder for mapping category strings to integer labels.
            - history: The Keras History object returned by model.fit containing training metrics.
    """
    # Encode labels
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_val_encoded = label_encoder.transform(y_val)

    # Build model
    input_dim = X_train.shape[1]
    num_classes = len(CATEGORIES)
    model = build_model(input_dim, num_classes)

    print(model.summary())

    # Callbacks
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )

    checkpoint = ModelCheckpoint(
        'tab_classifier_best.h5',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max'
    )

    # Train
    history = model.fit(
        X_train, y_train_encoded,
        validation_data=(X_val, y_val_encoded),
        epochs=100,
        batch_size=32,
        callbacks=[early_stopping, checkpoint],
        verbose=1
    )

    return model, label_encoder, history


def convert_to_tflite(model, output_path='tab_classifier.tflite'):
    """
    Convert a trained Keras model to TensorFlow Lite and save the converted file.
    
    This function creates a TFLiteConverter from the provided Keras model, applies default optimizations, converts the model to TFLite format, and writes the resulting .tflite file to the given output path. It also prints the save location and the written file's size.
    
    Parameters:
        model (tf.keras.Model): Trained Keras model to convert.
        output_path (str): Filesystem path where the .tflite file will be written.
    """
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Optimize the model
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Convert
    tflite_model = converter.convert()

    # Save
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    print(f"Model saved to {output_path}")

    # Get model size
    import os
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Model size: {size_kb:.2f} KB")


def evaluate_model(model, X_test, y_test, label_encoder):
    """
    Evaluate a trained classifier on test data and print performance metrics.
    
    Encodes true labels using the provided LabelEncoder, computes and prints test loss and accuracy, generates predictions to produce and print a classification report and a confusion matrix using the encoder's class names.
    
    Parameters:
        model: Trained Keras model used for evaluation.
        X_test (array-like): Feature matrix for the test set.
        y_test (array-like): True class labels for the test set (raw string/label form expected by `label_encoder`).
        label_encoder: Fitted sklearn.preprocessing.LabelEncoder used to transform `y_test` to integer class indices.
    
    """
    y_test_encoded = label_encoder.transform(y_test)

    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test_encoded, verbose=0)
    print(f"\nTest Loss: {loss:.4f}")
    print(f"Test Accuracy: {accuracy:.4f}")

    # Predictions
    predictions = model.predict(X_test)
    predicted_classes = np.argmax(predictions, axis=1)

    # Confusion matrix
    from sklearn.metrics import classification_report, confusion_matrix

    print("\nClassification Report:")
    print(classification_report(
        y_test_encoded,
        predicted_classes,
        target_names=label_encoder.classes_
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test_encoded, predicted_classes))


def main():
    """
    Orchestrates the end-to-end training, evaluation, and export pipeline for the tab classification model.
    
    Performs synthetic data generation, splits data into training/validation/test sets, trains the model (with early stopping and checkpointing), evaluates performance on the test set, converts the trained model to TensorFlow Lite, and saves the label encoder classes to `label_encoder.json`.
    """
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data(num_samples=10000)

    print(f"Generated {len(X)} samples")
    print(f"Feature dimension: {X.shape[1]}")
    print(f"Categories: {set(y)}")

    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    print(f"\nTraining samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")

    # Train model
    print("\nTraining model...")
    model, label_encoder, history = train_model(X_train, y_train, X_val, y_val)

    # Evaluate
    print("\nEvaluating model...")
    evaluate_model(model, X_test, y_test, label_encoder)

    # Convert to TFLite
    print("\nConverting to TensorFlow Lite...")
    convert_to_tflite(model)

    # Save label encoder
    with open('label_encoder.json', 'w') as f:
        json.dump({
            'classes': label_encoder.classes_.tolist()
        }, f)

    print("\nTraining complete!")


if __name__ == '__main__':
    main()