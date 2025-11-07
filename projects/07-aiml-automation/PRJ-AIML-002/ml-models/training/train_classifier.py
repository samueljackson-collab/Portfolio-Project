#!/usr/bin/env python3
"""
Train tab classification model using DistilBERT
"""

import os
import numpy as np
import tensorflow as tf
from transformers import DistilBertTokenizer, TFDistilBertModel
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Configuration
MODEL_NAME = 'distilbert-base-uncased'
MAX_LENGTH = 512
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 2e-5
NUM_CATEGORIES = 9

# Categories
CATEGORIES = [
    'Work',
    'Research',
    'Shopping',
    'Social Media',
    'Entertainment',
    'News',
    'Finance',
    'Education',
    'Other',
]


class TabClassifierModel:
    """Tab classification model"""

    def __init__(self):
        self.tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
        self.model = None
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(CATEGORIES)

    def create_model(self):
        """Create the classification model"""
        # Load pre-trained DistilBERT
        bert_model = TFDistilBertModel.from_pretrained(MODEL_NAME)

        # Input layer
        input_ids = tf.keras.Input(shape=(MAX_LENGTH,), dtype=tf.int32, name='input_ids')
        attention_mask = tf.keras.Input(shape=(MAX_LENGTH,), dtype=tf.int32, name='attention_mask')

        # BERT encoder
        bert_output = bert_model(input_ids, attention_mask=attention_mask)[0]

        # Pooling (use CLS token)
        pooled = bert_output[:, 0, :]

        # Classification head
        dense = tf.keras.layers.Dense(256, activation='relu')(pooled)
        dropout = tf.keras.layers.Dropout(0.3)(dense)
        outputs = tf.keras.layers.Dense(NUM_CATEGORIES, activation='softmax')(dropout)

        # Create model
        self.model = tf.keras.Model(
            inputs=[input_ids, attention_mask],
            outputs=outputs
        )

        # Compile
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.F1Score(average='macro')]
        )

        print("Model created successfully")
        self.model.summary()

    def prepare_dataset(self, df):
        """Prepare dataset for training"""
        # Combine text fields
        texts = df['title'] + ' ' + df['url'] + ' ' + df['description'].fillna('')

        # Tokenize
        encodings = self.tokenizer(
            texts.tolist(),
            truncation=True,
            padding='max_length',
            max_length=MAX_LENGTH,
            return_tensors='tf'
        )

        # Encode labels
        labels = tf.keras.utils.to_categorical(
            self.label_encoder.transform(df['category']),
            num_classes=NUM_CATEGORIES
        )

        return {
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask']
        }, labels

    def train(self, train_data, val_data):
        """Train the model"""
        X_train, y_train = train_data
        X_val, y_val = val_data

        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                'best_model.h5',
                monitor='val_f1_score',
                mode='max',
                save_best_only=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=2,
                min_lr=1e-7
            )
        ]

        # Train
        history = self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )

        return history

    def convert_to_tflite(self, output_path='tab_classifier.tflite'):
        """Convert model to TensorFlow Lite"""
        print("Converting to TensorFlow Lite...")

        # Convert
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)

        # Optimizations
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.int8]

        # Convert
        tflite_model = converter.convert()

        # Save
        with open(output_path, 'wb') as f:
            f.write(tflite_model)

        print(f"TFLite model saved to {output_path}")
        print(f"Model size: {len(tflite_model) / (1024 * 1024):.2f} MB")

    def evaluate(self, test_data):
        """Evaluate model on test set"""
        X_test, y_test = test_data
        results = self.model.evaluate(X_test, y_test, verbose=1)

        print("\nTest Results:")
        print(f"Loss: {results[0]:.4f}")
        print(f"Accuracy: {results[1]:.4f}")
        print(f"F1 Score: {results[2]:.4f}")

        return results


def load_dataset(dataset_path='dataset.csv'):
    """Load tab dataset"""
    # In production, load from actual dataset file
    # For this demo, create a sample dataset
    print("Loading dataset...")

    # Sample data (in production, load from CSV/database)
    sample_data = {
        'title': [
            'LinkedIn - Professional Network',
            'Wikipedia - Free Encyclopedia',
            'Amazon - Online Shopping',
            'Facebook - Social Network',
            'YouTube - Video Platform',
        ],
        'url': [
            'https://linkedin.com',
            'https://wikipedia.org',
            'https://amazon.com',
            'https://facebook.com',
            'https://youtube.com',
        ],
        'description': [
            'Professional networking site',
            'Free online encyclopedia',
            'Online shopping and e-commerce',
            'Social media platform',
            'Video sharing platform',
        ],
        'category': [
            'Work',
            'Research',
            'Shopping',
            'Social Media',
            'Entertainment',
        ]
    }

    df = pd.DataFrame(sample_data)

    print(f"Loaded {len(df)} samples")
    print(f"Categories: {df['category'].unique()}")

    return df


def main():
    """Main training pipeline"""
    print("=" * 50)
    print("Tab Classifier Training Pipeline")
    print("=" * 50)

    # Load dataset
    df = load_dataset()

    # Split dataset
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    train_df, val_df = train_test_split(train_df, test_size=0.2, random_state=42)

    print(f"\nDataset split:")
    print(f"Training: {len(train_df)} samples")
    print(f"Validation: {len(val_df)} samples")
    print(f"Test: {len(test_df)} samples")

    # Create model
    classifier = TabClassifierModel()
    classifier.create_model()

    # Prepare datasets
    print("\nPreparing datasets...")
    train_data = classifier.prepare_dataset(train_df)
    val_data = classifier.prepare_dataset(val_df)
    test_data = classifier.prepare_dataset(test_df)

    # Train model
    print("\nTraining model...")
    history = classifier.train(train_data, val_data)

    # Evaluate
    print("\nEvaluating model...")
    classifier.evaluate(test_data)

    # Convert to TFLite
    print("\nConverting to TensorFlow Lite...")
    classifier.convert_to_tflite('../tab_classifier.tflite')

    print("\nTraining complete!")


if __name__ == '__main__':
    main()
