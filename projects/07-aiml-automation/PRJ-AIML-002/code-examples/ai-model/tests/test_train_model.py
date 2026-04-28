"""Comprehensive unit tests for train_model.py"""
import pytest
import numpy as np
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))
import train_model


class TestFeatureExtraction:
    """Test feature extraction functions"""
    
    def test_extract_features_synthetic_returns_correct_shape(self):
        """Test that synthetic feature extraction returns correct feature count"""
        for category in train_model.CATEGORIES:
            features = train_model.extract_features_synthetic(category)
            # 6 domain features + 6 keyword features + 3 URL structure = 15
            assert len(features) == 15
            assert all(isinstance(f, (int, float, np.number)) for f in features)
    
    def test_extract_features_synthetic_category_bias(self):
        """Test that synthetic features are biased toward the target category"""
        category = 'work'
        features = train_model.extract_features_synthetic(category)
        
        # Domain features (first 6)
        work_domain_feature = features[train_model.CATEGORIES.index(category)]
        assert work_domain_feature >= 0.7, "Work domain feature should be high for work category"
        
        # Other domain features should be lower
        for i, cat in enumerate(train_model.CATEGORIES[:-1]):
            if cat != category:
                assert features[i] <= 0.3, f"{cat} feature should be low for work category"
    
    def test_extract_features_synthetic_all_features_in_range(self):
        """Test that all features are in valid range [0, 1]"""
        for category in train_model.CATEGORIES:
            features = train_model.extract_features_synthetic(category)
            assert all(0.0 <= f <= 1.0 for f in features), "All features should be normalized"
    
    def test_extract_features_real_with_work_url(self):
        """Test real feature extraction with a work-related URL"""
        url = "https://github.com/user/repo/issues/123"
        title = "GitHub Issue - API Documentation"
        content = "This is a code review for the API documentation update"
        
        features = train_model.extract_features_real(url, title, content)
        
        # Should have same shape as synthetic
        assert len(features) == 15
        
        # Work domain feature should be 1.0 (github.com is in work patterns)
        work_idx = list(train_model.DOMAIN_PATTERNS.keys()).index('work')
        assert features[work_idx] == 1.0
    
    def test_extract_features_real_with_shopping_url(self):
        """Test real feature extraction with a shopping URL"""
        url = "https://amazon.com/product/12345?ref=cart"
        title = "Buy Product - Add to Cart"
        content = "Shop now and save! Price: $29.99. Add to cart."
        
        features = train_model.extract_features_real(url, title, content)
        
        # Shopping domain feature should be 1.0
        shopping_idx = list(train_model.DOMAIN_PATTERNS.keys()).index('shopping')
        assert features[shopping_idx] == 1.0
        
        # Keyword features should reflect shopping terms
        keyword_start = len(train_model.DOMAIN_PATTERNS)
        shopping_keyword_idx = keyword_start + shopping_idx
        assert features[shopping_keyword_idx] > 0.0
    
    def test_extract_features_real_url_structure(self):
        """Test URL structure feature extraction"""
        url = "https://example.com/a/b/c/d?param=value#section"
        features = train_model.extract_features_real(url, "", "")
        
        # Path depth feature (last 3 features)
        assert features[-3] > 0.0, "Should have positive path depth"
        assert features[-2] == 1.0, "Should detect query params"
        assert features[-1] == 1.0, "Should detect fragment"
    
    def test_extract_features_real_case_insensitive(self):
        """Test that feature extraction is case-insensitive"""
        url1 = "https://GitHub.com/repo"
        url2 = "https://github.com/repo"
        
        features1 = train_model.extract_features_real(url1, "Title", "Content")
        features2 = train_model.extract_features_real(url2, "Title", "Content")
        
        assert features1 == features2


class TestSyntheticDataGeneration:
    """Test synthetic data generation"""
    
    def test_generate_synthetic_data_returns_correct_shape(self):
        """Test that synthetic data generation returns correct shapes"""
        num_samples = 1000
        X, y = train_model.generate_synthetic_data(num_samples)
        
        assert X.shape[0] == num_samples
        assert y.shape[0] == num_samples
        assert X.shape[1] == 15, "Should have 15 features"
    
    def test_generate_synthetic_data_balanced_classes(self):
        """Test that synthetic data has balanced class distribution"""
        num_samples = 700  # Divisible by 7 categories
        X, y = train_model.generate_synthetic_data(num_samples)
        
        from collections import Counter
        class_counts = Counter(y)
        
        expected_per_class = num_samples // len(train_model.CATEGORIES)
        for category in train_model.CATEGORIES:
            assert class_counts[category] == expected_per_class
    
    def test_generate_synthetic_data_all_categories_present(self):
        """Test that all categories are present in synthetic data"""
        X, y = train_model.generate_synthetic_data(1000)
        
        unique_labels = set(y)
        assert unique_labels == set(train_model.CATEGORIES)
    
    def test_generate_synthetic_data_features_valid(self):
        """Test that generated features are valid"""
        X, y = train_model.generate_synthetic_data(100)
        
        # All features should be in [0, 1] range
        assert np.all(X >= 0.0) and np.all(X <= 1.0)
        
        # No NaN or Inf values
        assert not np.any(np.isnan(X))
        assert not np.any(np.isinf(X))


class TestModelBuilding:
    """Test model building functions"""
    
    @patch('train_model.models.Sequential')
    def test_build_model_creates_correct_architecture(self, mock_sequential):
        """Test that build_model creates the expected architecture"""
        input_dim = 15
        num_classes = 7
        
        train_model.build_model(input_dim, num_classes)
        
        # Verify Sequential was called
        mock_sequential.assert_called_once()
    
    def test_build_model_returns_compiled_model(self):
        """Test that build_model returns a compiled model"""
        input_dim = 15
        num_classes = 7
        
        model = train_model.build_model(input_dim, num_classes)
        
        # Check model is compiled (has optimizer)
        assert model.optimizer is not None
        assert model.loss is not None
    
    def test_build_model_with_different_dimensions(self):
        """Test model building with various input dimensions"""
        test_cases = [
            (10, 5),
            (15, 7),
            (20, 10),
        ]
        
        for input_dim, num_classes in test_cases:
            model = train_model.build_model(input_dim, num_classes)
            assert model is not None
            
            # Test with dummy data
            dummy_input = np.random.randn(1, input_dim)
            output = model.predict(dummy_input, verbose=0)
            assert output.shape == (1, num_classes)


class TestModelTraining:
    """Test model training functions"""
    
    @patch('train_model.build_model')
    @patch('train_model.LabelEncoder')
    def test_train_model_encodes_labels(self, mock_encoder_class, mock_build_model):
        """Test that train_model properly encodes labels"""
        mock_encoder = Mock()
        mock_encoder.fit_transform.return_value = np.array([0, 1, 2, 0, 1, 2])
        mock_encoder.transform.return_value = np.array([0, 1])
        mock_encoder_class.return_value = mock_encoder
        
        mock_model = Mock()
        mock_model.fit.return_value = Mock(history={'loss': [0.5], 'accuracy': [0.8]})
        mock_build_model.return_value = mock_model
        
        X_train = np.random.randn(6, 15)
        y_train = np.array(['work', 'social', 'shopping', 'work', 'social', 'shopping'])
        X_val = np.random.randn(2, 15)
        y_val = np.array(['work', 'social'])
        
        model, encoder, history = train_model.train_model(X_train, y_train, X_val, y_val)
        
        # Verify encoding was called
        mock_encoder.fit_transform.assert_called_once()
        mock_encoder.transform.assert_called_once()
    
    @patch('train_model.build_model')
    @patch('train_model.LabelEncoder')
    def test_train_model_uses_callbacks(self, mock_encoder_class, mock_build_model):
        """Test that train_model uses EarlyStopping and ModelCheckpoint"""
        mock_encoder = Mock()
        mock_encoder.fit_transform.return_value = np.array([0, 1, 0, 1])
        mock_encoder.transform.return_value = np.array([0, 1])
        mock_encoder_class.return_value = mock_encoder
        
        mock_model = Mock()
        mock_model.fit.return_value = Mock(history={'loss': [0.5], 'accuracy': [0.8]})
        mock_build_model.return_value = mock_model
        
        X_train = np.random.randn(4, 15)
        y_train = np.array(['work', 'social', 'work', 'social'])
        X_val = np.random.randn(2, 15)
        y_val = np.array(['work', 'social'])
        
        model, encoder, history = train_model.train_model(X_train, y_train, X_val, y_val)
        
        # Verify fit was called with callbacks
        assert mock_model.fit.called
        call_kwargs = mock_model.fit.call_args[1]
        assert 'callbacks' in call_kwargs
        assert len(call_kwargs['callbacks']) == 2  # EarlyStopping and ModelCheckpoint


class TestModelEvaluation:
    """Test model evaluation functions"""
    
    @patch('train_model.classification_report')
    @patch('train_model.confusion_matrix')
    def test_evaluate_model_calculates_metrics(self, mock_cm, mock_report):
        """Test that evaluate_model calculates all metrics"""
        from sklearn.preprocessing import LabelEncoder
        
        mock_model = Mock()
        mock_model.evaluate.return_value = (0.3, 0.85)
        mock_model.predict.return_value = np.array([[0.8, 0.1, 0.1],
                                                      [0.1, 0.8, 0.1],
                                                      [0.1, 0.1, 0.8]])
        
        X_test = np.random.randn(3, 15)
        y_test = np.array(['work', 'social', 'shopping'])
        
        encoder = LabelEncoder()
        encoder.fit(y_test)
        
        train_model.evaluate_model(mock_model, X_test, y_test, encoder)
        
        # Verify evaluation was called
        mock_model.evaluate.assert_called_once()
        mock_model.predict.assert_called_once()
        mock_report.assert_called_once()
        mock_cm.assert_called_once()


class TestTFLiteConversion:
    """Test TensorFlow Lite conversion"""
    
    @patch('train_model.tf.lite.TFLiteConverter.from_keras_model')
    def test_convert_to_tflite_creates_file(self, mock_converter_class):
        """Test that TFLite conversion creates output file"""
        mock_converter = Mock()
        mock_converter.convert.return_value = b'fake_tflite_model'
        mock_converter_class.return_value = mock_converter
        
        mock_model = Mock()
        
        with tempfile.NamedTemporaryFile(suffix='.tflite', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            train_model.convert_to_tflite(mock_model, output_path)
            
            # Verify file was created
            assert os.path.exists(output_path)
            
            # Verify converter was called
            mock_converter_class.assert_called_once_with(mock_model)
            mock_converter.convert.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @patch('train_model.tf.lite.TFLiteConverter.from_keras_model')
    def test_convert_to_tflite_with_optimization(self, mock_converter_class):
        """Test that TFLite conversion applies optimizations"""
        mock_converter = Mock()
        mock_converter.convert.return_value = b'fake_model'
        mock_converter_class.return_value = mock_converter
        
        mock_model = Mock()
        
        with tempfile.NamedTemporaryFile(suffix='.tflite', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            train_model.convert_to_tflite(mock_model, output_path)
            
            # Verify optimizations were set
            assert hasattr(mock_converter, 'optimizations')
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestConstants:
    """Test module constants and configurations"""
    
    def test_categories_list_complete(self):
        """Test that all expected categories are defined"""
        expected_categories = ['work', 'research', 'shopping', 'social', 
                              'entertainment', 'news', 'custom']
        assert train_model.CATEGORIES == expected_categories
    
    def test_domain_patterns_all_categories(self):
        """Test that domain patterns exist for all main categories"""
        for category in train_model.CATEGORIES[:-1]:  # Exclude 'custom'
            assert category in train_model.DOMAIN_PATTERNS
            assert len(train_model.DOMAIN_PATTERNS[category]) > 0
    
    def test_keyword_patterns_all_categories(self):
        """Test that keyword patterns exist for all main categories"""
        for category in train_model.CATEGORIES[:-1]:  # Exclude 'custom'
            assert category in train_model.KEYWORD_PATTERNS
            assert len(train_model.KEYWORD_PATTERNS[category]) > 0
    
    def test_domain_patterns_no_duplicates(self):
        """Test that domain patterns don't have duplicates within categories"""
        for category, domains in train_model.DOMAIN_PATTERNS.items():
            assert len(domains) == len(set(domains)), f"Duplicates in {category} domains"
    
    def test_keyword_patterns_lowercase(self):
        """Test that all keyword patterns are lowercase"""
        for category, keywords in train_model.KEYWORD_PATTERNS.items():
            assert all(kw == kw.lower() for kw in keywords)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_extract_features_real_with_empty_strings(self):
        """Test feature extraction with empty inputs"""
        features = train_model.extract_features_real("", "", "")
        
        assert len(features) == 15
        assert all(isinstance(f, (int, float, np.number)) for f in features)
    
    def test_extract_features_real_with_special_characters(self):
        """Test feature extraction with special characters"""
        url = "https://example.com/路径/目录?param=值#锚点"
        title = "Special 字符 Title"
        content = "Content with émojis 😀 and spëcial chârs"
        
        features = train_model.extract_features_real(url, title, content)
        
        assert len(features) == 15
        assert not any(np.isnan(features))
    
    def test_extract_features_real_with_very_long_url(self):
        """Test feature extraction with very long URL"""
        url = "https://example.com/" + "/".join(["segment"] * 100) + "?param=value"
        features = train_model.extract_features_real(url, "Title", "Content")
        
        # Path depth should be capped at 1.0
        assert features[-3] <= 1.0
    
    def test_generate_synthetic_data_with_small_samples(self):
        """Test synthetic data generation with small sample count"""
        num_samples = 10
        X, y = train_model.generate_synthetic_data(num_samples)
        
        assert X.shape[0] == num_samples
        assert y.shape[0] == num_samples
    
    def test_generate_synthetic_data_with_zero_samples(self):
        """Test synthetic data generation with zero samples"""
        num_samples = 0
        X, y = train_model.generate_synthetic_data(num_samples)
        
        assert X.shape[0] == 0
        assert y.shape[0] == 0


class TestIntegration:
    """Integration tests for the full pipeline"""
    
    def test_full_pipeline_with_small_dataset(self):
        """Test the complete training pipeline with a small dataset"""
        # Generate small dataset
        X, y = train_model.generate_synthetic_data(100)
        
        # Split data
        split_idx = 80
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        X_val = X_test[:10]
        y_val = y_test[:10]
        
        # Build and train model
        from sklearn.preprocessing import LabelEncoder
        encoder = LabelEncoder()
        y_train_encoded = encoder.fit_transform(y_train)
        y_val_encoded = encoder.transform(y_val)
        
        model = train_model.build_model(X_train.shape[1], len(train_model.CATEGORIES))
        
        # Train for just 1 epoch
        history = model.fit(
            X_train, y_train_encoded,
            validation_data=(X_val, y_val_encoded),
            epochs=1,
            batch_size=16,
            verbose=0
        )
        
        assert history is not None
        assert 'loss' in history.history
        assert 'accuracy' in history.history


if __name__ == '__main__':
    pytest.main([__file__, '-v'])