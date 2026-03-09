"""
Unit tests for similarity engine
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.engine.similarity_engine import SimilarityEngine, SimilarityResult


class TestSimilarityResult:
    """Test suite for SimilarityResult dataclass"""

    def test_similarity_result_creation(self):
        """Test creating a SimilarityResult"""
        result = SimilarityResult(
            video_id_1="vid1",
            video_id_2="vid2",
            visual_similarity=0.95,
            audio_similarity=0.90,
            metadata_similarity=0.85,
            combined_similarity=0.92,
            is_duplicate=True,
            confidence=0.88,
        )

        assert result.video_id_1 == "vid1"
        assert result.video_id_2 == "vid2"
        assert result.visual_similarity == 0.95
        assert result.is_duplicate is True

    def test_similarity_result_to_dict(self):
        """Test converting SimilarityResult to dictionary"""
        result = SimilarityResult(
            video_id_1="vid1",
            video_id_2="vid2",
            visual_similarity=0.95,
            audio_similarity=0.90,
            metadata_similarity=0.85,
            combined_similarity=0.92,
            is_duplicate=True,
            confidence=0.88,
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["video_id_1"] == "vid1"
        assert result_dict["combined_similarity"] == 0.92

    def test_similarity_result_str(self):
        """Test string representation of SimilarityResult"""
        result = SimilarityResult(
            video_id_1="vid1",
            video_id_2="vid2",
            visual_similarity=0.95,
            audio_similarity=0.90,
            metadata_similarity=0.85,
            combined_similarity=0.92,
            is_duplicate=True,
            confidence=0.88,
        )

        result_str = str(result)

        assert "vid1" in result_str
        assert "vid2" in result_str
        assert "DUPLICATE" in result_str


class TestSimilarityEngine:
    """Test suite for SimilarityEngine class"""

    @pytest.fixture
    def engine(self):
        """Create a SimilarityEngine instance for testing"""
        return SimilarityEngine()

    def test_initialization_default_weights(self):
        """Test SimilarityEngine initialization with default weights"""
        engine = SimilarityEngine()

        assert engine.visual_weight == pytest.approx(0.65)
        assert engine.audio_weight == pytest.approx(0.25)
        assert engine.metadata_weight == pytest.approx(0.10)

    def test_initialization_custom_weights(self):
        """Test SimilarityEngine initialization with custom weights"""
        engine = SimilarityEngine(
            visual_weight=0.5, audio_weight=0.3, metadata_weight=0.2
        )

        # Weights should be normalized
        total = engine.visual_weight + engine.audio_weight + engine.metadata_weight
        assert total == pytest.approx(1.0)

        assert engine.visual_weight == pytest.approx(0.5)
        assert engine.audio_weight == pytest.approx(0.3)
        assert engine.metadata_weight == pytest.approx(0.2)

    def test_compute_metadata_similarity_identical(self, engine):
        """Test metadata similarity with identical metadata"""
        metadata1 = {
            "duration": 120.0,
            "width": 1920,
            "height": 1080,
            "file_size": 50000000,
            "fps": 30.0,
        }
        metadata2 = metadata1.copy()

        similarity = engine.compute_metadata_similarity(metadata1, metadata2)

        # Should be very high (1.0)
        assert similarity == pytest.approx(1.0)

    def test_compute_metadata_similarity_different(self, engine):
        """Test metadata similarity with different metadata"""
        metadata1 = {
            "duration": 120.0,
            "width": 1920,
            "height": 1080,
            "file_size": 50000000,
            "fps": 30.0,
        }
        metadata2 = {
            "duration": 60.0,  # Different duration
            "width": 1280,  # Different resolution
            "height": 720,
            "file_size": 25000000,  # Different size
            "fps": 24.0,  # Different FPS
        }

        similarity = engine.compute_metadata_similarity(metadata1, metadata2)

        # Should be lower
        assert similarity < 0.8

    def test_compute_metadata_similarity_missing_data(self, engine):
        """Test metadata similarity with missing data"""
        metadata1 = {}
        metadata2 = {}

        similarity = engine.compute_metadata_similarity(metadata1, metadata2)

        # Should return neutral score
        assert similarity == pytest.approx(0.5)

    def test_compute_visual_similarity_with_phashes(self, engine):
        """Test visual similarity computation with perceptual hashes"""
        features1 = {
            "phashes": ["abc123", "def456"],
            "embeddings": np.random.randn(2048),
        }
        features2 = {
            "phashes": ["abc123", "def456"],
            "embeddings": np.random.randn(2048),
        }

        with patch.object(engine, "_compare_phashes", return_value=0.95):
            with patch.object(engine, "_compare_embeddings", return_value=0.90):
                similarity = engine.compute_visual_similarity(features1, features2)

                # Should be weighted combination
                expected = 0.4 * 0.95 + 0.6 * 0.90
                assert similarity == pytest.approx(expected, rel=0.01)

    def test_compute_visual_similarity_missing_features(self, engine):
        """Test visual similarity with missing features"""
        features1 = {}
        features2 = {}

        similarity = engine.compute_visual_similarity(features1, features2)

        # Should return neutral score
        assert similarity == 0.5

    def test_compute_audio_similarity_with_audio(self, engine):
        """Test audio similarity computation with audio features"""
        features1 = {
            "has_audio": True,
            "audio_fingerprint": "fp1",
            "mfcc_features": np.random.randn(26),
        }
        features2 = {
            "has_audio": True,
            "audio_fingerprint": "fp2",
            "mfcc_features": np.random.randn(26),
        }

        with patch.object(engine, "_compare_fingerprints", return_value=0.85):
            with patch.object(engine, "_compare_mfcc", return_value=0.80):
                similarity = engine.compute_audio_similarity(features1, features2)

                # Should be weighted combination
                expected = 0.7 * 0.85 + 0.3 * 0.80
                assert similarity == pytest.approx(expected, rel=0.01)

    def test_compute_audio_similarity_no_audio(self, engine):
        """Test audio similarity when videos have no audio"""
        features1 = {"has_audio": False}
        features2 = {"has_audio": False}

        similarity = engine.compute_audio_similarity(features1, features2)

        # Should return neutral score
        assert similarity == 0.5

    def test_compute_combined_similarity(self, engine):
        """Test combined similarity computation"""
        visual_sim = 0.95
        audio_sim = 0.90
        metadata_sim = 0.85

        combined, confidence = engine.compute_combined_similarity(
            visual_sim, audio_sim, metadata_sim
        )

        # Check weighted combination
        expected = (
            engine.visual_weight * visual_sim
            + engine.audio_weight * audio_sim
            + engine.metadata_weight * metadata_sim
        )
        assert combined == pytest.approx(expected, rel=0.01)

        # Confidence should be high when all scores agree
        assert 0.5 <= confidence <= 1.0

    def test_compute_combined_similarity_low_agreement(self, engine):
        """Test combined similarity with low modality agreement"""
        visual_sim = 0.95  # High
        audio_sim = 0.20  # Low
        metadata_sim = 0.60  # Medium

        combined, confidence = engine.compute_combined_similarity(
            visual_sim, audio_sim, metadata_sim
        )

        # Confidence should be lower due to disagreement
        assert confidence < 0.8

    def test_compare_videos_duplicate(self, engine):
        """Test full video comparison resulting in duplicate"""
        video1_features = {
            "phashes": ["abc"] * 5,
            "embeddings": np.random.randn(2048),
            "has_audio": True,
            "audio_fingerprint": "fp1",
            "mfcc_features": np.random.randn(26),
        }

        video2_features = video1_features.copy()

        video1_metadata = {
            "duration": 120.0,
            "width": 1920,
            "height": 1080,
            "file_size": 50000000,
            "fps": 30.0,
        }

        video2_metadata = video1_metadata.copy()

        # Mock the comparison methods to return high similarity
        with patch.object(engine, "_compare_phashes", return_value=0.98):
            with patch.object(engine, "_compare_embeddings", return_value=0.97):
                with patch.object(engine, "_compare_fingerprints", return_value=0.96):
                    with patch.object(engine, "_compare_mfcc", return_value=0.95):
                        result = engine.compare_videos(
                            video1_features,
                            video2_features,
                            video1_metadata,
                            video2_metadata,
                            "vid1",
                            "vid2",
                        )

                        assert isinstance(result, SimilarityResult)
                        assert result.is_duplicate is True
                        assert result.combined_similarity >= engine.DUPLICATE_THRESHOLD

    def test_compare_videos_not_duplicate(self, engine):
        """Test full video comparison resulting in non-duplicate"""
        video1_features = {
            "phashes": ["abc"] * 5,
            "embeddings": np.random.randn(2048),
            "has_audio": True,
            "audio_fingerprint": "fp1",
            "mfcc_features": np.random.randn(26),
        }

        video2_features = {
            "phashes": ["xyz"] * 5,
            "embeddings": np.random.randn(2048),
            "has_audio": True,
            "audio_fingerprint": "fp2",
            "mfcc_features": np.random.randn(26),
        }

        video1_metadata = {
            "duration": 120.0,
            "width": 1920,
            "height": 1080,
        }

        video2_metadata = {
            "duration": 60.0,  # Different
            "width": 1280,  # Different
            "height": 720,
        }

        # Mock the comparison methods to return low similarity
        with patch.object(engine, "_compare_phashes", return_value=0.40):
            with patch.object(engine, "_compare_embeddings", return_value=0.45):
                with patch.object(engine, "_compare_fingerprints", return_value=0.35):
                    with patch.object(engine, "_compare_mfcc", return_value=0.38):
                        result = engine.compare_videos(
                            video1_features,
                            video2_features,
                            video1_metadata,
                            video2_metadata,
                            "vid1",
                            "vid2",
                        )

                        assert isinstance(result, SimilarityResult)
                        assert result.is_duplicate is False
                        assert result.combined_similarity < engine.DUPLICATE_THRESHOLD


class TestSimilarityEngineThresholds:
    """Test similarity thresholds"""

    def test_duplicate_threshold(self):
        """Test duplicate threshold"""
        engine = SimilarityEngine()
        assert engine.DUPLICATE_THRESHOLD == 0.95

    def test_near_duplicate_threshold(self):
        """Test near duplicate threshold"""
        engine = SimilarityEngine()
        assert engine.NEAR_DUPLICATE_THRESHOLD == 0.85

    def test_similar_threshold(self):
        """Test similar content threshold"""
        engine = SimilarityEngine()
        assert engine.SIMILAR_THRESHOLD == 0.70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
