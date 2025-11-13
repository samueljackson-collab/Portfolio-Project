"""
Multi-modal similarity engine combining visual, audio, and metadata signals
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SimilarityResult:
    """Container for similarity computation results"""
    video_id_1: str
    video_id_2: str
    visual_similarity: float
    audio_similarity: float
    metadata_similarity: float
    combined_similarity: float
    is_duplicate: bool
    confidence: float

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    def __str__(self) -> str:
        status = "DUPLICATE" if self.is_duplicate else "SIMILAR"
        return (f"[{status}] {self.video_id_1} <-> {self.video_id_2}: "
                f"{self.combined_similarity:.2%} "
                f"(V:{self.visual_similarity:.2%}, "
                f"A:{self.audio_similarity:.2%}, "
                f"M:{self.metadata_similarity:.2%}, "
                f"Conf:{self.confidence:.2%})")


class SimilarityEngine:
    """Compute multi-modal video similarity"""

    # Weights for different modalities
    VISUAL_WEIGHT = 0.65
    AUDIO_WEIGHT = 0.25
    METADATA_WEIGHT = 0.10

    # Thresholds
    DUPLICATE_THRESHOLD = 0.95
    NEAR_DUPLICATE_THRESHOLD = 0.85
    SIMILAR_THRESHOLD = 0.70

    def __init__(
        self,
        visual_weight: float = VISUAL_WEIGHT,
        audio_weight: float = AUDIO_WEIGHT,
        metadata_weight: float = METADATA_WEIGHT
    ):
        """
        Initialize similarity engine

        Args:
            visual_weight: Weight for visual similarity (default: 0.65)
            audio_weight: Weight for audio similarity (default: 0.25)
            metadata_weight: Weight for metadata similarity (default: 0.10)
        """
        # Normalize weights
        total_weight = visual_weight + audio_weight + metadata_weight
        self.visual_weight = visual_weight / total_weight
        self.audio_weight = audio_weight / total_weight
        self.metadata_weight = metadata_weight / total_weight

        logger.info(f"Initialized SimilarityEngine with weights: "
                   f"visual={self.visual_weight:.2f}, "
                   f"audio={self.audio_weight:.2f}, "
                   f"metadata={self.metadata_weight:.2f}")

    def compute_visual_similarity(
        self,
        features1: Dict,
        features2: Dict,
        phash_weight: float = 0.4,
        embedding_weight: float = 0.6
    ) -> float:
        """
        Compute visual similarity using multiple methods

        Combines:
        - Perceptual hash similarity (fast, good for exact/near-duplicates)
        - Deep embedding similarity (robust, good for edited videos)

        Args:
            features1, features2: Feature dictionaries with 'phashes' and 'embeddings'
            phash_weight: Weight for perceptual hash similarity
            embedding_weight: Weight for embedding similarity

        Returns:
            Visual similarity score (0.0 - 1.0)
        """
        similarities = []

        # Perceptual hash similarity
        if 'phashes' in features1 and 'phashes' in features2:
            phash_sim = self._compare_phashes(
                features1['phashes'],
                features2['phashes']
            )
            similarities.append(('phash', phash_sim, phash_weight))
            logger.debug(f"Perceptual hash similarity: {phash_sim:.4f}")

        # Deep embedding similarity
        if 'embeddings' in features1 and 'embeddings' in features2:
            embedding_sim = self._compare_embeddings(
                features1['embeddings'],
                features2['embeddings']
            )
            similarities.append(('embedding', embedding_sim, embedding_weight))
            logger.debug(f"Embedding similarity: {embedding_sim:.4f}")

        if not similarities:
            logger.warning("No visual features available for comparison")
            return 0.5  # Neutral score

        # Weighted combination
        total_weight = sum(weight for _, _, weight in similarities)
        visual_sim = sum(sim * weight for _, sim, weight in similarities) / total_weight

        return float(visual_sim)

    def compute_audio_similarity(
        self,
        features1: Dict,
        features2: Dict,
        fingerprint_weight: float = 0.7,
        mfcc_weight: float = 0.3
    ) -> float:
        """
        Compute audio similarity using multiple methods

        Combines:
        - Chromaprint fingerprint matching
        - MFCC feature similarity

        Args:
            features1, features2: Feature dictionaries
            fingerprint_weight: Weight for fingerprint similarity
            mfcc_weight: Weight for MFCC similarity

        Returns:
            Audio similarity score (0.0 - 1.0)
        """
        # Handle videos without audio
        has_audio1 = features1.get('has_audio', True)
        has_audio2 = features2.get('has_audio', True)

        if not has_audio1 or not has_audio2:
            logger.debug("One or both videos have no audio")
            return 0.5  # Neutral score

        similarities = []

        # Fingerprint similarity
        if 'audio_fingerprint' in features1 and 'audio_fingerprint' in features2:
            fp_sim = self._compare_fingerprints(
                features1['audio_fingerprint'],
                features2['audio_fingerprint']
            )
            similarities.append(('fingerprint', fp_sim, fingerprint_weight))
            logger.debug(f"Audio fingerprint similarity: {fp_sim:.4f}")

        # MFCC similarity
        if 'mfcc_features' in features1 and 'mfcc_features' in features2:
            mfcc_sim = self._compare_mfcc(
                features1['mfcc_features'],
                features2['mfcc_features']
            )
            similarities.append(('mfcc', mfcc_sim, mfcc_weight))
            logger.debug(f"MFCC similarity: {mfcc_sim:.4f}")

        if not similarities:
            logger.warning("No audio features available for comparison")
            return 0.5  # Neutral score

        # Weighted combination
        total_weight = sum(weight for _, _, weight in similarities)
        audio_sim = sum(sim * weight for _, sim, weight in similarities) / total_weight

        return float(audio_sim)

    def compute_metadata_similarity(
        self,
        metadata1: Dict,
        metadata2: Dict
    ) -> float:
        """
        Compute metadata similarity

        Compares:
        - Duration (±5 seconds tolerance)
        - Resolution and aspect ratio
        - File size (±20% tolerance)
        - Frame rate

        Args:
            metadata1, metadata2: Metadata dictionaries

        Returns:
            Metadata similarity score (0.0 - 1.0)
        """
        similarities = []

        # Duration similarity (±5 seconds tolerance)
        duration1 = metadata1.get('duration', 0)
        duration2 = metadata2.get('duration', 0)

        if duration1 > 0 and duration2 > 0:
            duration_diff = abs(duration1 - duration2)
            duration_sim = max(0.0, 1.0 - (duration_diff / 5.0))  # 5 sec tolerance
            similarities.append(duration_sim)
            logger.debug(f"Duration similarity: {duration_sim:.4f} "
                        f"({duration1:.1f}s vs {duration2:.1f}s)")

        # Resolution similarity
        res1 = (metadata1.get('width', 0), metadata1.get('height', 0))
        res2 = (metadata2.get('width', 0), metadata2.get('height', 0))

        if res1[0] > 0 and res2[0] > 0:
            if res1 == res2:
                res_sim = 1.0
            else:
                # Same aspect ratio but different resolution
                aspect1 = res1[0] / res1[1] if res1[1] > 0 else 0
                aspect2 = res2[0] / res2[1] if res2[1] > 0 else 0
                aspect_diff = abs(aspect1 - aspect2)
                res_sim = 0.8 if aspect_diff < 0.1 else 0.5

            similarities.append(res_sim)
            logger.debug(f"Resolution similarity: {res_sim:.4f} "
                        f"({res1} vs {res2})")

        # File size similarity (±20% tolerance)
        size1 = metadata1.get('file_size', 0)
        size2 = metadata2.get('file_size', 0)

        if size1 > 0 and size2 > 0:
            size_ratio = min(size1, size2) / max(size1, size2)
            # Linear scale from 0.8 to 1.0 -> similarity 0 to 1
            size_sim = max(0.0, (size_ratio - 0.8) / 0.2)
            similarities.append(size_sim)
            logger.debug(f"File size similarity: {size_sim:.4f} "
                        f"({size1} vs {size2} bytes)")

        # Frame rate similarity
        fps1 = metadata1.get('fps', 0)
        fps2 = metadata2.get('fps', 0)

        if fps1 > 0 and fps2 > 0:
            fps_diff = abs(fps1 - fps2)
            fps_sim = 1.0 if fps_diff < 1.0 else 0.7
            similarities.append(fps_sim)
            logger.debug(f"FPS similarity: {fps_sim:.4f} ({fps1} vs {fps2})")

        # Average of all metadata similarities
        if similarities:
            metadata_sim = np.mean(similarities)
        else:
            logger.warning("No metadata available for comparison")
            metadata_sim = 0.5  # Neutral score

        return float(metadata_sim)

    def compute_combined_similarity(
        self,
        visual_sim: float,
        audio_sim: float,
        metadata_sim: float
    ) -> Tuple[float, float]:
        """
        Compute weighted combined similarity and confidence

        Args:
            visual_sim: Visual similarity score
            audio_sim: Audio similarity score
            metadata_sim: Metadata similarity score

        Returns:
            Tuple of (combined_similarity, confidence)
        """
        # Weighted combination
        combined = (
            self.visual_weight * visual_sim +
            self.audio_weight * audio_sim +
            self.metadata_weight * metadata_sim
        )

        # Confidence based on agreement between modalities
        # Higher confidence when all modalities agree
        modality_scores = [visual_sim, audio_sim, metadata_sim]
        modality_variance = np.var(modality_scores)

        # Normalize variance to confidence score
        # Low variance (high agreement) -> high confidence
        # High variance (low agreement) -> low confidence
        confidence = 1.0 - min(modality_variance, 0.5) / 0.5  # Range: [0.5, 1.0]

        logger.debug(f"Combined similarity: {combined:.4f}, confidence: {confidence:.4f}")

        return float(combined), float(confidence)

    def compare_videos(
        self,
        video1_features: Dict,
        video2_features: Dict,
        video1_metadata: Dict,
        video2_metadata: Dict,
        video1_id: str = "video1",
        video2_id: str = "video2"
    ) -> SimilarityResult:
        """
        Compare two videos using all available features

        Args:
            video1_features: Features for video 1
            video2_features: Features for video 2
            video1_metadata: Metadata for video 1
            video2_metadata: Metadata for video 2
            video1_id: ID for video 1
            video2_id: ID for video 2

        Returns:
            SimilarityResult object
        """
        logger.info(f"Comparing videos: {video1_id} vs {video2_id}")

        # Compute similarities
        visual_sim = self.compute_visual_similarity(video1_features, video2_features)
        audio_sim = self.compute_audio_similarity(video1_features, video2_features)
        metadata_sim = self.compute_metadata_similarity(video1_metadata, video2_metadata)

        # Combine similarities
        combined_sim, confidence = self.compute_combined_similarity(
            visual_sim, audio_sim, metadata_sim
        )

        # Determine if duplicate
        is_duplicate = combined_sim >= self.DUPLICATE_THRESHOLD

        result = SimilarityResult(
            video_id_1=video1_id,
            video_id_2=video2_id,
            visual_similarity=visual_sim,
            audio_similarity=audio_sim,
            metadata_similarity=metadata_sim,
            combined_similarity=combined_sim,
            is_duplicate=is_duplicate,
            confidence=confidence
        )

        logger.info(f"Comparison result: {result}")

        return result

    def _compare_phashes(self, phashes1: List[str], phashes2: List[str]) -> float:
        """
        Compare lists of perceptual hashes

        Args:
            phashes1, phashes2: Lists of perceptual hashes

        Returns:
            Similarity score (0.0 - 1.0)
        """
        try:
            from src.features.perceptual_hash import PerceptualHasher

            hasher = PerceptualHasher()
            return hasher.compare_videos(phashes1, phashes2)

        except Exception as e:
            logger.error(f"Error comparing phashes: {e}")
            return 0.0

    def _compare_embeddings(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray
    ) -> float:
        """
        Compare deep learning embeddings

        Args:
            embeddings1, embeddings2: Feature embeddings

        Returns:
            Similarity score (0.0 - 1.0)
        """
        try:
            from src.features.deep_embeddings import DeepFeatureExtractor

            return DeepFeatureExtractor.cosine_similarity(embeddings1, embeddings2)

        except Exception as e:
            logger.error(f"Error comparing embeddings: {e}")
            return 0.0

    def _compare_fingerprints(self, fp1: str, fp2: str) -> float:
        """
        Compare audio fingerprints

        Args:
            fp1, fp2: Audio fingerprints

        Returns:
            Similarity score (0.0 - 1.0)
        """
        try:
            from src.features.audio_fingerprint import AudioFingerprinter

            fingerprinter = AudioFingerprinter()
            return fingerprinter.compare_fingerprints(fp1, fp2)

        except Exception as e:
            logger.error(f"Error comparing fingerprints: {e}")
            return 0.0

    def _compare_mfcc(self, mfcc1: np.ndarray, mfcc2: np.ndarray) -> float:
        """
        Compare MFCC features

        Args:
            mfcc1, mfcc2: MFCC feature vectors (normalized)

        Returns:
            Similarity score (0.0 - 1.0)
        """
        try:
            # Cosine similarity (dot product for normalized vectors)
            similarity = float(np.dot(mfcc1, mfcc2))
            # Convert from [-1, 1] to [0, 1]
            return (similarity + 1.0) / 2.0

        except Exception as e:
            logger.error(f"Error comparing MFCC: {e}")
            return 0.0


def main():
    """Example usage of SimilarityEngine"""
    import argparse

    parser = argparse.ArgumentParser(description='Compare two videos for similarity')
    parser.add_argument('video1', help='Path to first video')
    parser.add_argument('video2', help='Path to second video')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize engine
    engine = SimilarityEngine()

    print(f"\nProcessing videos:")
    print(f"  Video 1: {args.video1}")
    print(f"  Video 2: {args.video2}")

    # For demo purposes, create dummy features
    # In production, extract actual features
    video1_features = {
        'phashes': ['abc123', 'def456'],
        'embeddings': np.random.randn(2048),
        'has_audio': True,
        'audio_fingerprint': 'fp1',
        'mfcc_features': np.random.randn(26)
    }

    video2_features = {
        'phashes': ['abc124', 'def457'],
        'embeddings': np.random.randn(2048),
        'has_audio': True,
        'audio_fingerprint': 'fp2',
        'mfcc_features': np.random.randn(26)
    }

    video1_metadata = {
        'duration': 120.5,
        'width': 1920,
        'height': 1080,
        'file_size': 50000000,
        'fps': 30.0
    }

    video2_metadata = {
        'duration': 121.0,
        'width': 1920,
        'height': 1080,
        'file_size': 51000000,
        'fps': 30.0
    }

    # Compare videos
    result = engine.compare_videos(
        video1_features, video2_features,
        video1_metadata, video2_metadata,
        args.video1, args.video2
    )

    # Display results
    print(f"\n{'='*60}")
    print(f"Similarity Analysis Results")
    print(f"{'='*60}")
    print(f"Visual Similarity:    {result.visual_similarity:.2%}")
    print(f"Audio Similarity:     {result.audio_similarity:.2%}")
    print(f"Metadata Similarity:  {result.metadata_similarity:.2%}")
    print(f"{'='*60}")
    print(f"Combined Similarity:  {result.combined_similarity:.2%}")
    print(f"Confidence:           {result.confidence:.2%}")
    print(f"{'='*60}")
    print(f"Status: {'DUPLICATE' if result.is_duplicate else 'NOT DUPLICATE'}")


if __name__ == "__main__":
    main()
