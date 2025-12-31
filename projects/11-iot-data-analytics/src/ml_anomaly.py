#!/usr/bin/env python3
"""ML-based anomaly detection for IoT telemetry data."""
from __future__ import annotations

import json
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLAnomalyDetector:
    """
    ML-based anomaly detection for IoT sensor data.

    Uses Isolation Forest algorithm for unsupervised anomaly detection
    combined with statistical methods for validation.
    """

    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 100,
        model_path: Optional[Path] = None
    ):
        """
        Initialize anomaly detector.

        Args:
            contamination: Expected proportion of anomalies (0.0 to 0.5)
            n_estimators: Number of trees in Isolation Forest
            model_path: Path to save/load trained model
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.model_path = model_path or Path('models/anomaly_detector.pkl')

        # Initialize models
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.pca = None

        # Feature columns
        self.feature_columns = [
            'temperature',
            'humidity',
            'battery_level',
            'signal_strength'
        ]

        # Training history
        self.training_history = []

        logger.info(f"ML Anomaly Detector initialized (contamination={contamination})")

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from raw telemetry data.

        Args:
            df: DataFrame with raw telemetry

        Returns:
            DataFrame with extracted features
        """
        features = df[self.feature_columns].copy()

        # Add derived features
        features['temp_humidity_ratio'] = features['temperature'] / (features['humidity'] + 1)
        features['battery_temp_interaction'] = features['battery_level'] * features['temperature']

        # Add time-based features if timestamp available
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            features['hour'] = df['timestamp'].dt.hour
            features['day_of_week'] = df['timestamp'].dt.dayofweek

        return features

    def train(self, df: pd.DataFrame, use_pca: bool = False, n_components: int = 4):
        """
        Train anomaly detection model on historical data.

        Args:
            df: Training DataFrame with telemetry data
            use_pca: Whether to use PCA for dimensionality reduction
            n_components: Number of PCA components
        """
        logger.info(f"Training on {len(df)} samples...")

        # Extract features
        X = self.extract_features(df)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Optional PCA
        if use_pca:
            self.pca = PCA(n_components=n_components, random_state=42)
            X_scaled = self.pca.fit_transform(X_scaled)
            logger.info(f"PCA variance explained: {self.pca.explained_variance_ratio_.sum():.3f}")

        # Train Isolation Forest
        self.model.fit(X_scaled)

        # Record training info
        training_info = {
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(df),
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'features': list(X.columns),
            'use_pca': use_pca
        }
        self.training_history.append(training_info)

        logger.info("Training completed")

        # Save model
        if self.model_path:
            self.save_model()

    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies for new data.

        Args:
            df: DataFrame with telemetry data

        Returns:
            Tuple of (predictions, anomaly_scores)
            predictions: 1 for normal, -1 for anomaly
            anomaly_scores: Anomaly scores (lower = more anomalous)
        """
        # Extract features
        X = self.extract_features(df)

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Apply PCA if trained with it
        if self.pca:
            X_scaled = self.pca.transform(X_scaled)

        # Predict
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)

        return predictions, anomaly_scores

    def detect_anomalies(
        self,
        df: pd.DataFrame,
        combine_with_stats: bool = True
    ) -> pd.DataFrame:
        """
        Detect anomalies and return enriched DataFrame.

        Args:
            df: Input DataFrame
            combine_with_stats: Whether to combine ML with statistical methods

        Returns:
            DataFrame with anomaly flags and scores
        """
        result = df.copy()

        # ML-based detection
        predictions, scores = self.predict(df)

        result['is_anomaly_ml'] = (predictions == -1)
        result['anomaly_score'] = scores

        # Statistical detection (z-score method)
        if combine_with_stats:
            for col in self.feature_columns:
                if col in result.columns:
                    z_scores = np.abs((result[col] - result[col].mean()) / result[col].std())
                    result[f'{col}_z_score'] = z_scores
                    result[f'{col}_anomaly'] = z_scores > 3

            # Combined anomaly flag
            stat_anomaly = result[[f'{col}_anomaly' for col in self.feature_columns
                                  if col in result.columns]].any(axis=1)
            result['is_anomaly_combined'] = result['is_anomaly_ml'] | stat_anomaly

        return result

    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for detected anomalies.

        Args:
            df: DataFrame with telemetry and anomaly flags

        Returns:
            Dictionary with summary statistics
        """
        result = self.detect_anomalies(df)

        summary = {
            'total_records': len(result),
            'anomalies_ml': int(result['is_anomaly_ml'].sum()),
            'anomaly_rate_ml': float(result['is_anomaly_ml'].mean()),
            'avg_anomaly_score': float(result['anomaly_score'].mean()),
            'min_anomaly_score': float(result['anomaly_score'].min()),
            'max_anomaly_score': float(result['anomaly_score'].max())
        }

        if 'is_anomaly_combined' in result.columns:
            summary['anomalies_combined'] = int(result['is_anomaly_combined'].sum())
            summary['anomaly_rate_combined'] = float(result['is_anomaly_combined'].mean())

        # Anomalies by device
        if 'device_id' in result.columns:
            anomaly_by_device = result[result['is_anomaly_ml']].groupby('device_id').size()
            summary['top_anomalous_devices'] = anomaly_by_device.nlargest(5).to_dict()

        # Anomalies by feature
        anomaly_reasons = []
        for col in self.feature_columns:
            if f'{col}_anomaly' in result.columns:
                count = result[f'{col}_anomaly'].sum()
                if count > 0:
                    anomaly_reasons.append({'feature': col, 'count': int(count)})

        summary['anomaly_reasons'] = anomaly_reasons

        return summary

    def save_model(self):
        """Save trained model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'pca': self.pca,
            'feature_columns': self.feature_columns,
            'training_history': self.training_history,
            'contamination': self.contamination
        }

        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {self.model_path}")

    def load_model(self):
        """Load trained model from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.pca = model_data.get('pca')
        self.feature_columns = model_data['feature_columns']
        self.training_history = model_data.get('training_history', [])
        self.contamination = model_data['contamination']

        logger.info(f"Model loaded from {self.model_path}")


class RealTimeAnomalyDetector:
    """Real-time anomaly detection for streaming data."""

    def __init__(
        self,
        db_config: Dict,
        detector: MLAnomalyDetector,
        check_interval_seconds: int = 60
    ):
        """
        Initialize real-time detector.

        Args:
            db_config: Database configuration
            detector: Trained ML anomaly detector
            check_interval_seconds: How often to check for anomalies
        """
        self.db_config = db_config
        self.detector = detector
        self.check_interval = check_interval_seconds

        logger.info(f"Real-time detector initialized (interval={check_interval}s)")

    def check_recent_data(self, lookback_minutes: int = 5) -> Dict:
        """
        Check recent data for anomalies.

        Args:
            lookback_minutes: How far back to look for data

        Returns:
            Dictionary with anomaly detection results
        """
        import psycopg2

        # Connect to database
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Query recent data
        query = """
            SELECT
                device_id,
                timestamp,
                temperature,
                humidity,
                battery_level,
                signal_strength
            FROM iot_telemetry
            WHERE timestamp > NOW() - INTERVAL '%s minutes'
            ORDER BY timestamp DESC
        """

        cursor.execute(query, (lookback_minutes,))
        rows = cursor.fetchall()

        if not rows:
            logger.warning("No recent data found")
            return {'anomalies_found': False}

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=[
            'device_id', 'timestamp', 'temperature',
            'humidity', 'battery_level', 'signal_strength'
        ])

        # Detect anomalies
        result = self.detector.detect_anomalies(df)
        anomalies = result[result['is_anomaly_combined']]

        # Get summary
        summary = self.detector.get_anomaly_summary(df)

        # Close connection
        cursor.close()
        conn.close()

        if len(anomalies) > 0:
            logger.warning(f"Found {len(anomalies)} anomalies in recent data")

            # Store anomalies in database
            self._store_anomalies(anomalies)

        return {
            'anomalies_found': len(anomalies) > 0,
            'anomaly_count': len(anomalies),
            'checked_records': len(df),
            'summary': summary,
            'anomalies': anomalies.to_dict('records') if len(anomalies) < 20 else []
        }

    def _store_anomalies(self, anomalies_df: pd.DataFrame):
        """Store detected anomalies in database."""
        import psycopg2

        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Create anomalies table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iot_anomalies (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(50),
                detected_at TIMESTAMP DEFAULT NOW(),
                anomaly_timestamp TIMESTAMP,
                temperature FLOAT,
                humidity FLOAT,
                battery_level FLOAT,
                signal_strength FLOAT,
                anomaly_score FLOAT,
                anomaly_type VARCHAR(20)
            )
        """)

        # Insert anomalies
        for _, row in anomalies_df.iterrows():
            cursor.execute("""
                INSERT INTO iot_anomalies (
                    device_id, anomaly_timestamp, temperature, humidity,
                    battery_level, signal_strength, anomaly_score, anomaly_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['device_id'],
                row['timestamp'],
                row['temperature'],
                row['humidity'],
                row['battery_level'],
                row.get('signal_strength'),
                row['anomaly_score'],
                'combined'
            ))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Stored {len(anomalies_df)} anomalies in database")


def main():
    """Example usage of ML anomaly detector."""
    import argparse
    import psycopg2

    parser = argparse.ArgumentParser(description='ML Anomaly Detection')
    parser.add_argument('--action', choices=['train', 'detect', 'realtime'], required=True)
    parser.add_argument('--db-host', default='localhost')
    parser.add_argument('--db-port', type=int, default=5432)
    parser.add_argument('--db-name', default='iot_analytics')
    parser.add_argument('--db-user', default='postgres')
    parser.add_argument('--db-password', default='postgres')
    parser.add_argument('--contamination', type=float, default=0.1)
    parser.add_argument('--lookback-hours', type=int, default=24)

    args = parser.parse_args()

    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }

    # Initialize detector
    detector = MLAnomalyDetector(contamination=args.contamination)

    if args.action == 'train':
        # Load training data
        logger.info(f"Loading training data (last {args.lookback_hours} hours)...")

        conn = psycopg2.connect(**db_config)
        query = f"""
            SELECT device_id, timestamp, temperature, humidity,
                   battery_level, signal_strength
            FROM iot_telemetry
            WHERE timestamp > NOW() - INTERVAL '{args.lookback_hours} hours'
        """
        df = pd.read_sql(query, conn)
        conn.close()

        logger.info(f"Loaded {len(df)} records")

        # Train model
        detector.train(df, use_pca=True)

        logger.info("Training completed and model saved")

    elif args.action == 'detect':
        # Load model
        detector.load_model()

        # Load recent data
        logger.info("Loading recent data...")
        conn = psycopg2.connect(**db_config)
        query = """
            SELECT device_id, timestamp, temperature, humidity,
                   battery_level, signal_strength
            FROM iot_telemetry
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """
        df = pd.read_sql(query, conn)
        conn.close()

        # Detect anomalies
        summary = detector.get_anomaly_summary(df)

        logger.info("\n" + "=" * 60)
        logger.info("Anomaly Detection Summary")
        logger.info("=" * 60)
        logger.info(f"Total records: {summary['total_records']}")
        logger.info(f"Anomalies (ML): {summary['anomalies_ml']} ({summary['anomaly_rate_ml']:.2%})")
        if 'anomalies_combined' in summary:
            logger.info(f"Anomalies (Combined): {summary['anomalies_combined']} ({summary['anomaly_rate_combined']:.2%})")
        logger.info("=" * 60)

    elif args.action == 'realtime':
        # Load model
        detector.load_model()

        # Start real-time monitoring
        rt_detector = RealTimeAnomalyDetector(db_config, detector)

        logger.info("Starting real-time anomaly detection...")
        logger.info("Press Ctrl+C to stop")

        import time
        try:
            while True:
                result = rt_detector.check_recent_data(lookback_minutes=5)
                if result['anomalies_found']:
                    logger.warning(f"Anomalies detected: {result['anomaly_count']}")

                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Stopped")


if __name__ == '__main__':
    main()
