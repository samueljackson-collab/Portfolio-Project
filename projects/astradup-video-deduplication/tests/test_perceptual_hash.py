"""
Unit tests for perceptual hashing module
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import cv2

from src.features.perceptual_hash import PerceptualHasher


class TestPerceptualHasher:
    """Test suite for PerceptualHasher class"""

    @pytest.fixture
    def hasher(self):
        """Create a PerceptualHasher instance for testing"""
        return PerceptualHasher(hash_size=16)

    @pytest.fixture
    def sample_frame(self):
        """Create a sample video frame"""
        # Create a simple 100x100 RGB frame
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    def test_initialization(self):
        """Test PerceptualHasher initialization"""
        hasher = PerceptualHasher(hash_size=8)
        assert hasher.hash_size == 8

        hasher = PerceptualHasher()
        assert hasher.hash_size == 16

    def test_compute_phash_identical_frames(self, hasher, sample_frame):
        """Test that identical frames produce identical hashes"""
        hash1 = hasher.compute_phash(sample_frame)
        hash2 = hasher.compute_phash(sample_frame)

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) > 0

    def test_compute_phash_similar_frames(self, hasher):
        """Test that similar frames produce similar hashes"""
        # Create two similar frames
        frame1 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        frame2 = np.clip(
            frame1.astype(int) + np.random.randint(-10, 10, frame1.shape),
            0, 255
        ).astype(np.uint8)

        hash1 = hasher.compute_phash(frame1)
        hash2 = hasher.compute_phash(frame2)

        # Hashes should be different but similar
        assert hash1 != hash2

        # Hamming distance should be small
        distance = hasher.hamming_distance(hash1, hash2)
        assert distance < 30  # Small threshold for similar images

    def test_hamming_distance_identical(self, hasher):
        """Test Hamming distance for identical hashes"""
        hash1 = "a" * 64  # Example hash
        distance = hasher.hamming_distance(hash1, hash1)
        assert distance == 0

    def test_hamming_distance_different(self, hasher):
        """Test Hamming distance for different hashes"""
        hash1 = "a" * 64
        hash2 = "f" * 64

        distance = hasher.hamming_distance(hash1, hash2)
        assert distance > 0

    def test_compare_videos_empty_lists(self, hasher):
        """Test video comparison with empty hash lists"""
        similarity = hasher.compare_videos([], [])
        assert similarity == 0.0

        similarity = hasher.compare_videos(["abc"], [])
        assert similarity == 0.0

        similarity = hasher.compare_videos([], ["abc"])
        assert similarity == 0.0

    def test_compare_videos_identical_lists(self, hasher):
        """Test video comparison with identical hash lists"""
        hashes = ["abc123", "def456", "ghi789"]
        similarity = hasher.compare_videos(hashes, hashes)

        # Should be very high similarity (close to 1.0)
        assert similarity > 0.95

    def test_compare_videos_different_lengths(self, hasher):
        """Test video comparison with different length hash lists"""
        hashes1 = ["abc"] * 5
        hashes2 = ["abc"] * 10

        similarity = hasher.compare_videos(hashes1, hashes2)

        # Should still work and return a valid similarity score
        assert 0.0 <= similarity <= 1.0

    @patch('cv2.VideoCapture')
    def test_extract_key_frames_success(self, mock_cv2, hasher):
        """Test successful key frame extraction"""
        # Mock video capture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = [30.0, 300]  # FPS=30, 300 total frames

        # Mock frames
        test_frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mock_cap.read.side_effect = [
            (True, test_frame) for _ in range(10)
        ] + [(False, None)]

        mock_cv2.return_value = mock_cap

        # Extract frames at 1 FPS
        frames = hasher.extract_key_frames("test_video.mp4", fps=1.0)

        assert len(frames) > 0
        assert all(isinstance(f, np.ndarray) for f in frames)

    @patch('cv2.VideoCapture')
    def test_extract_key_frames_cannot_open(self, mock_cv2, hasher):
        """Test key frame extraction when video cannot be opened"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cv2.return_value = mock_cap

        with pytest.raises(ValueError, match="Cannot open video"):
            hasher.extract_key_frames("nonexistent_video.mp4")

    def test_compare_videos_methods(self, hasher):
        """Test different comparison methods"""
        hashes1 = ["abc123"] * 5
        hashes2 = ["abc123"] * 5

        # Test DTW method
        sim_dtw = hasher.compare_videos(hashes1, hashes2, method='dtw')
        assert 0.0 <= sim_dtw <= 1.0

        # Test topk method
        sim_topk = hasher.compare_videos(hashes1, hashes2, method='topk')
        assert 0.0 <= sim_topk <= 1.0

        # Test default method
        sim_default = hasher.compare_videos(hashes1, hashes2)
        assert 0.0 <= sim_default <= 1.0


class TestPerceptualHasherIntegration:
    """Integration tests for PerceptualHasher"""

    @pytest.fixture
    def hasher(self):
        return PerceptualHasher(hash_size=16)

    def test_end_to_end_workflow(self, hasher):
        """Test complete workflow from frames to similarity"""
        # Create two sets of similar frames
        frames1 = [
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            for _ in range(5)
        ]
        frames2 = frames1.copy()  # Identical frames

        # Compute hashes
        hashes1 = [hasher.compute_phash(f) for f in frames1]
        hashes2 = [hasher.compute_phash(f) for f in frames2]

        # Compare
        similarity = hasher.compare_videos(hashes1, hashes2)

        # Should be very similar
        assert similarity > 0.95

    def test_different_content_detection(self, hasher):
        """Test detection of different content"""
        # Create two sets of very different frames
        frames1 = [
            np.zeros((100, 100, 3), dtype=np.uint8)  # Black frames
            for _ in range(5)
        ]
        frames2 = [
            np.ones((100, 100, 3), dtype=np.uint8) * 255  # White frames
            for _ in range(5)
        ]

        # Compute hashes
        hashes1 = [hasher.compute_phash(f) for f in frames1]
        hashes2 = [hasher.compute_phash(f) for f in frames2]

        # Compare
        similarity = hasher.compare_videos(hashes1, hashes2)

        # Should be very different
        assert similarity < 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
