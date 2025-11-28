"""
Generate sample datasets for MLOps platform demonstration.

Creates synthetic classification and regression datasets for:
- Model training and validation
- Drift detection testing
- MLflow experiment tracking
- Model serving demonstrations
"""

import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_classification_dataset(n_samples=10000, n_features=20, n_informative=15):
    """Generate synthetic classification dataset."""
    logger.info(f"Generating classification dataset with {n_samples} samples...")

    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_informative,
        n_redundant=5,
        n_classes=2,
        random_state=42,
        flip_y=0.1  # 10% label noise
    )

    # Create feature names
    feature_names = [f'feature_{i:02d}' for i in range(n_features)]

    # Create DataFrame
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y

    # Add metadata columns
    df['timestamp'] = pd.date_range(start='2024-01-01', periods=n_samples, freq='5min')
    df['sample_id'] = range(n_samples)

    return df


def generate_regression_dataset(n_samples=10000, n_features=15, noise=0.1):
    """Generate synthetic regression dataset."""
    logger.info(f"Generating regression dataset with {n_samples} samples...")

    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=10,
        noise=noise * 100,
        random_state=42
    )

    # Create feature names
    feature_names = [f'feature_{i:02d}' for i in range(n_features)]

    # Create DataFrame
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y

    # Add metadata
    df['timestamp'] = pd.date_range(start='2024-01-01', periods=n_samples, freq='10min')
    df['sample_id'] = range(n_samples)

    return df


def generate_drifted_dataset(base_df, drift_strength=0.3, drift_features=5):
    """Generate a dataset with artificial drift for testing drift detection."""
    logger.info(f"Generating drifted dataset with strength {drift_strength}...")

    df_drifted = base_df.copy()

    # Select random features to drift
    feature_cols = [col for col in df_drifted.columns if col.startswith('feature_')]
    drift_cols = np.random.choice(feature_cols, size=drift_features, replace=False)

    # Apply drift by shifting distribution
    for col in drift_cols:
        df_drifted[col] = df_drifted[col] + np.random.normal(
            drift_strength * df_drifted[col].std(),
            0.1 * df_drifted[col].std(),
            size=len(df_drifted)
        )

    # Update timestamps to be later
    df_drifted['timestamp'] = pd.date_range(
        start='2024-06-01',
        periods=len(df_drifted),
        freq='5min'
    )

    return df_drifted


def split_and_save_dataset(df, dataset_name, output_dir):
    """Split dataset into train/val/test and save as parquet."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Split: 70% train, 15% val, 15% test
    n = len(df)
    train_size = int(0.7 * n)
    val_size = int(0.15 * n)

    train_df = df.iloc[:train_size]
    val_df = df.iloc[train_size:train_size + val_size]
    test_df = df.iloc[train_size + val_size:]

    # Save as parquet
    train_path = output_dir / f'{dataset_name}_train.parquet'
    val_path = output_dir / f'{dataset_name}_val.parquet'
    test_path = output_dir / f'{dataset_name}_test.parquet'

    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)

    logger.info(f"Saved {dataset_name} datasets:")
    logger.info(f"  Train: {len(train_df)} samples → {train_path}")
    logger.info(f"  Val:   {len(val_df)} samples → {val_path}")
    logger.info(f"  Test:  {len(test_df)} samples → {test_path}")

    return train_df, val_df, test_df


def generate_all_datasets():
    """Generate all sample datasets for MLOps platform."""
    output_dir = Path(__file__).parent.parent / 'data' / 'samples'

    # 1. Classification dataset
    logger.info("=" * 60)
    logger.info("Generating Classification Dataset")
    logger.info("=" * 60)
    classification_df = generate_classification_dataset(n_samples=10000)
    split_and_save_dataset(classification_df, 'classification', output_dir)

    # 2. Regression dataset
    logger.info("\n" + "=" * 60)
    logger.info("Generating Regression Dataset")
    logger.info("=" * 60)
    regression_df = generate_regression_dataset(n_samples=10000)
    split_and_save_dataset(regression_df, 'regression', output_dir)

    # 3. Drifted classification dataset (for drift detection testing)
    logger.info("\n" + "=" * 60)
    logger.info("Generating Drifted Dataset")
    logger.info("=" * 60)
    drifted_df = generate_drifted_dataset(classification_df, drift_strength=0.5)
    drifted_path = output_dir / 'classification_drifted.parquet'
    drifted_df.to_parquet(drifted_path, index=False)
    logger.info(f"Saved drifted dataset: {len(drifted_df)} samples → {drifted_path}")

    # 4. Generate dataset metadata
    metadata = {
        'classification': {
            'n_samples': len(classification_df),
            'n_features': len([c for c in classification_df.columns if c.startswith('feature_')]),
            'task': 'binary_classification',
            'train_size': int(0.7 * len(classification_df)),
            'val_size': int(0.15 * len(classification_df)),
            'test_size': int(0.15 * len(classification_df))
        },
        'regression': {
            'n_samples': len(regression_df),
            'n_features': len([c for c in regression_df.columns if c.startswith('feature_')]),
            'task': 'regression',
            'train_size': int(0.7 * len(regression_df)),
            'val_size': int(0.15 * len(regression_df)),
            'test_size': int(0.15 * len(regression_df))
        },
        'classification_drifted': {
            'n_samples': len(drifted_df),
            'description': 'Classification dataset with artificial drift for testing',
            'drift_strength': 0.5,
            'drift_features': 5
        }
    }

    # Save metadata as JSON
    import json
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"\nSaved metadata: {metadata_path}")

    logger.info("\n" + "=" * 60)
    logger.info("Dataset Generation Complete!")
    logger.info("=" * 60)
    logger.info(f"Total datasets created: {len(metadata)}")
    logger.info(f"Output directory: {output_dir}")


if __name__ == '__main__':
    generate_all_datasets()
