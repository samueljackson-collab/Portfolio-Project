"""
Perceptual hashing for near-duplicate video detection
Implements average hashing (aHash) and difference hashing (dHash)
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import imagehash
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class PerceptualHasher:
    """Generate perceptual hashes for video frames"""

    def __init__(self, hash_size: int = 16):
        """
        Initialize perceptual hasher

        Args:
            hash_size: Size of hash (default 16 = 256-bit hash)
        """
        self.hash_size = hash_size
        logger.info(f"Initialized PerceptualHasher with hash_size={hash_size}")

    def extract_key_frames(
        self,
        video_path: str,
        fps: float = 1.0,
        max_frames: Optional[int] = None
    ) -> List[np.ndarray]:
        """
        Extract key frames from video at specified FPS

        Args:
            video_path: Path to video file
            fps: Frames per second to extract (default 1.0)
            max_frames: Maximum number of frames to extract (optional)

        Returns:
            List of frames as numpy arrays

        Raises:
            ValueError: If video cannot be opened
        """
        cap = cv2.VideoCapture(video_path)
        frames = []

        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        try:
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if video_fps == 0:
                logger.warning(f"Invalid FPS for video: {video_path}, defaulting to 30")
                video_fps = 30

            frame_interval = int(video_fps / fps)
            frame_count = 0
            extracted_count = 0

            logger.debug(f"Extracting frames from {video_path}: "
                        f"video_fps={video_fps}, interval={frame_interval}, "
                        f"total_frames={total_frames}")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    frames.append(frame)
                    extracted_count += 1

                    if max_frames and extracted_count >= max_frames:
                        break

                frame_count += 1

            logger.info(f"Extracted {len(frames)} frames from {video_path}")

        finally:
            cap.release()

        return frames

    def compute_phash(self, frame: np.ndarray) -> str:
        """
        Compute perceptual hash for a frame

        Args:
            frame: Video frame as numpy array (BGR format)

        Returns:
            Hex string representation of perceptual hash
        """
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)

            # Compute perceptual hash
            phash = imagehash.phash(pil_image, hash_size=self.hash_size)

            return str(phash)

        except Exception as e:
            logger.error(f"Error computing phash: {e}")
            raise

    def compute_video_signature(
        self,
        video_path: str,
        fps: float = 1.0,
        max_frames: Optional[int] = None
    ) -> List[str]:
        """
        Generate video signature as list of frame hashes

        Args:
            video_path: Path to video file
            fps: Frames per second to extract (default 1.0)
            max_frames: Maximum number of frames to extract (optional)

        Returns:
            List of perceptual hashes for key frames
        """
        logger.info(f"Computing video signature for: {video_path}")

        frames = self.extract_key_frames(video_path, fps, max_frames)

        if not frames:
            logger.warning(f"No frames extracted from {video_path}")
            return []

        hashes = []
        for i, frame in enumerate(frames):
            try:
                phash = self.compute_phash(frame)
                hashes.append(phash)
            except Exception as e:
                logger.warning(f"Failed to compute hash for frame {i}: {e}")
                continue

        logger.info(f"Computed {len(hashes)} hashes for {video_path}")
        return hashes

    def hamming_distance(self, hash1: str, hash2: str) -> int:
        """
        Calculate Hamming distance between two hashes

        Args:
            hash1, hash2: Perceptual hashes as hex strings

        Returns:
            Hamming distance (number of differing bits)
        """
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)

            # imagehash overloads - operator for Hamming distance
            return h1 - h2

        except Exception as e:
            logger.error(f"Error computing Hamming distance: {e}")
            return self.hash_size ** 2  # Return maximum distance on error

    def compare_videos(
        self,
        video1_hashes: List[str],
        video2_hashes: List[str],
        method: str = 'dtw'
    ) -> float:
        """
        Compare two videos using their perceptual hash signatures

        Args:
            video1_hashes: List of hashes for video 1
            video2_hashes: List of hashes for video 2
            method: Comparison method ('dtw' for Dynamic Time Warping or 'topk')

        Returns:
            Similarity score (0.0 - 1.0)
        """
        if not video1_hashes or not video2_hashes:
            logger.warning("One or both video hash lists are empty")
            return 0.0

        # Build similarity matrix
        similarity_matrix = np.zeros((len(video1_hashes), len(video2_hashes)))
        max_distance = self.hash_size ** 2  # Maximum possible Hamming distance

        for i, h1 in enumerate(video1_hashes):
            for j, h2 in enumerate(video2_hashes):
                distance = self.hamming_distance(h1, h2)
                similarity = 1.0 - (distance / max_distance)
                similarity_matrix[i][j] = similarity

        if method == 'dtw':
            # Use diagonal of similarity matrix (simple DTW approximation)
            # In production, use proper DTW implementation
            min_len = min(len(video1_hashes), len(video2_hashes))
            diagonal_sim = np.mean([similarity_matrix[i][i] for i in range(min_len)])
            return float(diagonal_sim)

        elif method == 'topk':
            # Average of top k similarities (robust to minor edits)
            top_k = min(10, similarity_matrix.size)
            top_similarities = np.sort(similarity_matrix.flatten())[-top_k:]
            return float(np.mean(top_similarities))

        else:
            # Default: overall average
            return float(np.mean(similarity_matrix))


def main():
    """Example usage of PerceptualHasher"""
    import argparse

    parser = argparse.ArgumentParser(description='Compare two videos using perceptual hashing')
    parser.add_argument('video1', help='Path to first video')
    parser.add_argument('video2', help='Path to second video')
    parser.add_argument('--hash-size', type=int, default=16, help='Hash size (default: 16)')
    parser.add_argument('--fps', type=float, default=1.0, help='Frames per second to sample (default: 1.0)')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize hasher
    hasher = PerceptualHasher(hash_size=args.hash_size)

    # Process videos
    print(f"\nExtracting features from video 1: {args.video1}")
    hashes1 = hasher.compute_video_signature(args.video1, fps=args.fps)

    print(f"Extracting features from video 2: {args.video2}")
    hashes2 = hasher.compute_video_signature(args.video2, fps=args.fps)

    # Compare
    similarity = hasher.compare_videos(hashes1, hashes2, method='topk')

    print(f"\n{'='*60}")
    print(f"Similarity Score: {similarity:.2%}")
    print(f"{'='*60}")

    if similarity >= 0.95:
        print("✓ EXACT DUPLICATE detected")
    elif similarity >= 0.85:
        print("⚠ NEAR DUPLICATE detected")
    elif similarity >= 0.70:
        print("~ SIMILAR CONTENT detected")
    else:
        print("✗ DIFFERENT CONTENT")

    print(f"\nDetails:")
    print(f"  Video 1: {len(hashes1)} frames analyzed")
    print(f"  Video 2: {len(hashes2)} frames analyzed")
    print(f"  Hash size: {args.hash_size}x{args.hash_size} = {args.hash_size**2} bits")


if __name__ == "__main__":
    main()
