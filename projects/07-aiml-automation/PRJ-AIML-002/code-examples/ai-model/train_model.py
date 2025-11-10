#!/usr/bin/env python3
"""
Tab Classification Model Training Script
Trains a TensorFlow Lite model for categorizing browser tabs
"""

import os
import json
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
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
    Generate synthetic training data for tab classification
    In production, this would be replaced with real user data
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
    Extract features for synthetic data generation
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


def build_model(input_dim, num_classes):
    """
    Build neural network model for tab classification
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
    Train the classification model
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
    Convert Keras model to TensorFlow Lite format
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
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Model size: {size_kb:.2f} KB")


def evaluate_model(model, X_test, y_test, label_encoder):
    """
    Evaluate model performance
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
    Main training pipeline
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
