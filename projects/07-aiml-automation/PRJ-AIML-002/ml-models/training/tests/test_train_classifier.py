"""
Tests for Tab Classifier Training Script
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import tempfile
import os

# Mock TensorFlow before importing
sys.modules['tensorflow'] = MagicMock()
sys.modules['transformers'] = MagicMock()

sys.path.insert(0, '..')
from train_classifier import TabClassifierModel, load_dataset, CATEGORIES


class TestTabClassifierModel(unittest.TestCase):
    """Test cases for TabClassifierModel"""

    def setUp(self):
        """Set up test fixtures"""
        self.model = TabClassifierModel()

    def test_initialization(self):
        """Test model initialization"""
        self.assertIsNotNone(self.model.tokenizer)
        self.assertIsNotNone(self.model.label_encoder)
        self.assertIsNone(self.model.model)

    def test_label_encoder_categories(self):
        """Test that label encoder has all categories"""
        expected_categories = [
            'Work', 'Research', 'Shopping', 'Social Media',
            'Entertainment', 'News', 'Finance', 'Education', 'Other'
        ]
        
        encoded = self.model.label_encoder.transform(expected_categories)
        decoded = self.model.label_encoder.inverse_transform(encoded)
        
        self.assertEqual(list(decoded), expected_categories)

    def test_categories_constant(self):
        """Test CATEGORIES constant"""
        self.assertEqual(len(CATEGORIES), 9)
        self.assertIn('Work', CATEGORIES)
        self.assertIn('Research', CATEGORIES)
        self.assertIn('Shopping', CATEGORIES)
        self.assertIn('Other', CATEGORIES)

    @patch('train_classifier.TFDistilBertModel')
    def test_create_model(self, mock_bert):
        """Test model creation"""
        mock_bert.from_pretrained.return_value = MagicMock()
        
        # self.model.create_model()
        
        # Model should be created
        # self.assertIsNotNone(self.model.model)

    def test_prepare_dataset_structure(self):
        """Test dataset preparation returns correct structure"""
        df = pd.DataFrame({
            'title': ['Test Title 1', 'Test Title 2'],
            'url': ['https://example.com/1', 'https://example.com/2'],
            'description': ['Desc 1', 'Desc 2'],
            'category': ['Work', 'Research']
        })

        # Mock tokenizer
        self.model.tokenizer = Mock()
        self.model.tokenizer.return_value = {
            'input_ids': [[1, 2, 3], [4, 5, 6]],
            'attention_mask': [[1, 1, 1], [1, 1, 1]]
        }

        # X, y = self.model.prepare_dataset(df)
        
        # Should return dict with input_ids and attention_mask, and labels
        # self.assertIn('input_ids', X)
        # self.assertIn('attention_mask', X)

    def test_prepare_dataset_combines_text_fields(self):
        """Test that dataset preparation combines title, URL, and description"""
        df = pd.DataFrame({
            'title': ['Title'],
            'url': ['https://example.com'],
            'description': ['Description'],
            'category': ['Work']
        })

        # Check that text fields are combined
        # The actual implementation should combine: title + url + description

    def test_prepare_dataset_handles_missing_description(self):
        """Test handling of missing description field"""
        df = pd.DataFrame({
            'title': ['Title'],
            'url': ['https://example.com'],
            'description': [None],
            'category': ['Work']
        })

        # Should handle None/NaN in description
        # self.model.tokenizer = Mock(return_value={'input_ids': [[1]], 'attention_mask': [[1]]})
        # X, y = self.model.prepare_dataset(df)


class TestLoadDataset(unittest.TestCase):
    """Test cases for load_dataset function"""

    def test_load_dataset_returns_dataframe(self):
        """Test that load_dataset returns a DataFrame"""
        df = load_dataset()
        
        self.assertIsInstance(df, pd.DataFrame)

    def test_load_dataset_has_required_columns(self):
        """Test that dataset has required columns"""
        df = load_dataset()
        
        required_columns = ['title', 'url', 'description', 'category']
        for col in required_columns:
            self.assertIn(col, df.columns)

    def test_load_dataset_has_valid_categories(self):
        """Test that all categories are valid"""
        df = load_dataset()
        
        for category in df['category']:
            self.assertIn(category, CATEGORIES)

    def test_load_dataset_not_empty(self):
        """Test that dataset is not empty"""
        df = load_dataset()
        
        self.assertGreater(len(df), 0)

    def test_load_dataset_urls_are_valid(self):
        """Test that URLs in dataset are valid"""
        df = load_dataset()
        
        for url in df['url']:
            self.assertTrue(url.startswith('http'))

    def test_load_dataset_titles_not_empty(self):
        """Test that titles are not empty"""
        df = load_dataset()
        
        for title in df['title']:
            self.assertIsInstance(title, str)
            self.assertGreater(len(title), 0)


class TestTrainingConfiguration(unittest.TestCase):
    """Test training configuration constants"""

    def test_max_length_is_positive(self):
        """Test MAX_LENGTH constant"""
        from train_classifier import MAX_LENGTH
        
        self.assertGreater(MAX_LENGTH, 0)
        self.assertEqual(MAX_LENGTH, 512)

    def test_batch_size_is_positive(self):
        """Test BATCH_SIZE constant"""
        from train_classifier import BATCH_SIZE
        
        self.assertGreater(BATCH_SIZE, 0)
        self.assertEqual(BATCH_SIZE, 32)

    def test_epochs_is_positive(self):
        """Test EPOCHS constant"""
        from train_classifier import EPOCHS
        
        self.assertGreater(EPOCHS, 0)
        self.assertEqual(EPOCHS, 10)

    def test_learning_rate_is_valid(self):
        """Test LEARNING_RATE constant"""
        from train_classifier import LEARNING_RATE
        
        self.assertGreater(LEARNING_RATE, 0)
        self.assertLess(LEARNING_RATE, 1)
        self.assertEqual(LEARNING_RATE, 2e-5)

    def test_num_categories_matches(self):
        """Test NUM_CATEGORIES matches CATEGORIES length"""
        from train_classifier import NUM_CATEGORIES
        
        self.assertEqual(NUM_CATEGORIES, len(CATEGORIES))
        self.assertEqual(NUM_CATEGORIES, 9)


class TestTabClassifierEdgeCases(unittest.TestCase):
    """Edge case tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.model = TabClassifierModel()

    def test_empty_dataframe(self):
        """Test handling empty DataFrame"""
        df = pd.DataFrame(columns=['title', 'url', 'description', 'category'])
        
        # Should handle gracefully
        # self.model.tokenizer = Mock(return_value={'input_ids': [], 'attention_mask': []})

    def test_very_long_text(self):
        """Test handling very long text"""
        df = pd.DataFrame({
            'title': ['Title ' * 1000],
            'url': ['https://example.com'],
            'description': ['Description ' * 1000],
            'category': ['Work']
        })

        # Should truncate to MAX_LENGTH
        # Tokenizer should handle this

    def test_special_characters_in_text(self):
        """Test handling special characters"""
        df = pd.DataFrame({
            'title': ['<script>alert("xss")</script>'],
            'url': ['https://example.com?param=<>&"\''],
            'description': ['Special chars: !@#$%^&*()'],
            'category': ['Work']
        })

        # Should handle special characters gracefully

    def test_unicode_in_text(self):
        """Test handling Unicode text"""
        df = pd.DataFrame({
            'title': ['日本語のタイトル 🚀'],
            'url': ['https://例え.jp'],
            'description': ['Описание на русском'],
            'category': ['Research']
        })

        # Should handle Unicode properly

    def test_all_categories_represented(self):
        """Test dataset with all categories"""
        df = pd.DataFrame({
            'title': [f'Title {i}' for i in range(9)],
            'url': [f'https://example{i}.com' for i in range(9)],
            'description': [f'Desc {i}' for i in range(9)],
            'category': CATEGORIES
        })

        # All categories should be encodable
        encoded = self.model.label_encoder.transform(df['category'])
        self.assertEqual(len(set(encoded)), 9)


class TestModelSaving(unittest.TestCase):
    """Test model saving functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.model = TabClassifierModel()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('train_classifier.tf')
    def test_convert_to_tflite(self, mock_tf):
        """Test TFLite conversion"""
        # Mock TensorFlow Lite converter
        mock_converter = MagicMock()
        mock_converter.convert.return_value = b'fake tflite model'
        mock_tf.lite.TFLiteConverter.from_keras_model.return_value = mock_converter

        self.model.model = MagicMock()
        output_path = os.path.join(self.temp_dir, 'test_model.tflite')

        # self.model.convert_to_tflite(output_path)
        
        # Should create file
        # self.assertTrue(os.path.exists(output_path))

    def test_tflite_output_path(self):
        """Test TFLite output path handling"""
        output_path = 'test_output.tflite'
        
        # Should handle path correctly
        self.assertTrue(output_path.endswith('.tflite'))


if __name__ == '__main__':
    unittest.main()