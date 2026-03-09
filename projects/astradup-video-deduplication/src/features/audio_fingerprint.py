"""
Audio fingerprinting for duplicate detection
Uses Chromaprint for acoustic fingerprinting and MFCC for audio features
"""

import subprocess
import json
import numpy as np
import os
import tempfile
from typing import Tuple, List, Optional
from scipy.spatial.distance import jaccard
import logging

logger = logging.getLogger(__name__)


class AudioFingerprinter:
    """Generate and compare audio fingerprints"""

    def __init__(self, sample_rate: int = 11025):
        """
        Initialize audio fingerprinter

        Args:
            sample_rate: Audio sample rate (Chromaprint optimal: 11025)
        """
        self.sample_rate = sample_rate
        logger.info(f"Initialized AudioFingerprinter with sample_rate={sample_rate}")

    def extract_audio(
        self, video_path: str, output_path: Optional[str] = None, overwrite: bool = True
    ) -> str:
        """
        Extract audio track from video

        Args:
            video_path: Path to video file
            output_path: Output audio file path (optional)
            overwrite: Whether to overwrite existing file

        Returns:
            Path to extracted audio file

        Raises:
            RuntimeError: If FFmpeg extraction fails
        """
        if output_path is None:
            # Create temporary file
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(tempfile.gettempdir(), f"{base_name}_audio.wav")

        logger.debug(f"Extracting audio from {video_path} to {output_path}")

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",
            "-ar",
            str(self.sample_rate),
            "-ac",
            "1",  # Mono
        ]

        if overwrite:
            cmd.append("-y")  # Overwrite
        else:
            cmd.append("-n")  # No overwrite

        cmd.append(output_path)

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.decode("utf-8", errors="ignore")
                raise RuntimeError(f"FFmpeg failed: {error_msg}")

            logger.info(f"Audio extracted successfully: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"FFmpeg timeout for video: {video_path}")
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise

    def generate_fingerprint(self, audio_path: str) -> dict:
        """
        Generate Chromaprint fingerprint for audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with 'fingerprint' and 'duration'

        Raises:
            RuntimeError: If fpcalc (Chromaprint) fails
        """
        logger.debug(f"Generating fingerprint for: {audio_path}")

        cmd = ["fpcalc", "-json", audio_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                raise RuntimeError(f"fpcalc failed: {result.stderr}")

            data = json.loads(result.stdout)

            fingerprint_data = {
                "fingerprint": data.get("fingerprint", ""),
                "duration": data.get("duration", 0),
            }

            logger.debug(
                f"Fingerprint generated: duration={fingerprint_data['duration']}s"
            )

            return fingerprint_data

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"fpcalc timeout for audio: {audio_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse fpcalc output: {e}")
        except Exception as e:
            logger.error(f"Error generating fingerprint: {e}")
            raise

    def compare_fingerprints(
        self, fp1: str, fp2: str, method: str = "jaccard"
    ) -> float:
        """
        Compare two Chromaprint fingerprints

        Args:
            fp1, fp2: Fingerprints as base64 strings
            method: Comparison method ('jaccard' or 'hamming')

        Returns:
            Similarity score (0.0 - 1.0)
        """
        if not fp1 or not fp2:
            logger.warning("One or both fingerprints are empty")
            return 0.0

        try:
            # Decode fingerprints to bit vectors
            bits1 = self._decode_fingerprint(fp1)
            bits2 = self._decode_fingerprint(fp2)

            # Ensure same length by padding
            max_len = max(len(bits1), len(bits2))
            bits1 = np.pad(bits1, (0, max_len - len(bits1)), mode="constant")
            bits2 = np.pad(bits2, (0, max_len - len(bits2)), mode="constant")

            if method == "jaccard":
                # Jaccard similarity
                similarity = 1.0 - jaccard(bits1, bits2)
            elif method == "hamming":
                # Hamming similarity
                hamming_dist = np.sum(bits1 != bits2)
                similarity = 1.0 - (hamming_dist / len(bits1))
            else:
                raise ValueError(f"Unsupported comparison method: {method}")

            return float(similarity)

        except Exception as e:
            logger.error(f"Error comparing fingerprints: {e}")
            return 0.0

    def _decode_fingerprint(self, fingerprint: str) -> np.ndarray:
        """
        Decode base64 fingerprint to bit vector

        Args:
            fingerprint: Fingerprint as base64 string

        Returns:
            Numpy array of bits
        """
        import base64

        try:
            decoded = base64.b64decode(fingerprint)
            bits = np.unpackbits(np.frombuffer(decoded, dtype=np.uint8))
            return bits

        except Exception as e:
            logger.error(f"Error decoding fingerprint: {e}")
            # Return empty array on error
            return np.array([], dtype=np.uint8)

    def extract_mfcc(
        self, audio_path: str, n_mfcc: int = 13, use_librosa: bool = True
    ) -> np.ndarray:
        """
        Extract MFCC features from audio

        Args:
            audio_path: Path to audio file
            n_mfcc: Number of MFCC coefficients
            use_librosa: Whether to use librosa (if available)

        Returns:
            MFCC feature vector (normalized)
        """
        logger.debug(f"Extracting MFCC from: {audio_path}")

        try:
            if use_librosa:
                try:
                    import librosa

                    # Load audio
                    y, sr = librosa.load(audio_path, sr=self.sample_rate)

                    # Extract MFCC
                    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

                    # Aggregate over time using statistics
                    mfcc_mean = np.mean(mfcc, axis=1)
                    mfcc_std = np.std(mfcc, axis=1)

                    # Concatenate mean and std
                    features = np.concatenate([mfcc_mean, mfcc_std])

                    # Normalize
                    norm = np.linalg.norm(features)
                    if norm > 0:
                        features = features / norm

                    logger.debug(f"MFCC extracted: shape={features.shape}")

                    return features

                except ImportError:
                    logger.warning("librosa not available, using fallback method")
                    return self._extract_mfcc_fallback(audio_path, n_mfcc)

            else:
                return self._extract_mfcc_fallback(audio_path, n_mfcc)

        except Exception as e:
            logger.error(f"Error extracting MFCC: {e}")
            # Return zero vector on error
            return np.zeros(n_mfcc * 2)

    def _extract_mfcc_fallback(self, audio_path: str, n_mfcc: int) -> np.ndarray:
        """
        Fallback MFCC extraction using scipy

        Args:
            audio_path: Path to audio file
            n_mfcc: Number of MFCC coefficients

        Returns:
            MFCC feature vector
        """
        from scipy.io import wavfile
        from scipy.fftpack import dct

        logger.debug("Using fallback MFCC extraction")

        try:
            # Read WAV file
            sr, audio = wavfile.read(audio_path)

            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Simple MFCC approximation
            # This is a simplified version; for production use librosa
            frame_size = 2048
            hop_size = 512

            frames = []
            for i in range(0, len(audio) - frame_size, hop_size):
                frame = audio[i : i + frame_size]
                frames.append(frame)

            # Compute DCT on each frame (simplified MFCC)
            mfccs = []
            for frame in frames:
                mfcc_frame = dct(frame, norm="ortho")[:n_mfcc]
                mfccs.append(mfcc_frame)

            mfccs = np.array(mfccs)

            # Aggregate
            mfcc_mean = np.mean(mfccs, axis=0)
            mfcc_std = np.std(mfccs, axis=0)

            features = np.concatenate([mfcc_mean, mfcc_std])

            # Normalize
            norm = np.linalg.norm(features)
            if norm > 0:
                features = features / norm

            return features

        except Exception as e:
            logger.error(f"Fallback MFCC extraction failed: {e}")
            return np.zeros(n_mfcc * 2)


def main():
    """Example usage of AudioFingerprinter"""
    import argparse

    parser = argparse.ArgumentParser(description="Extract audio fingerprint from video")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--compare", help="Second video to compare")
    parser.add_argument(
        "--method",
        default="jaccard",
        choices=["jaccard", "hamming"],
        help="Comparison method",
    )
    parser.add_argument(
        "--mfcc", action="store_true", help="Also extract MFCC features"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize fingerprinter
    fingerprinter = AudioFingerprinter()

    # Extract audio
    print(f"\nProcessing video 1: {args.video}")
    audio1_path = fingerprinter.extract_audio(args.video)

    # Generate fingerprint
    fp1_data = fingerprinter.generate_fingerprint(audio1_path)
    print(f"Fingerprint 1 generated: duration={fp1_data['duration']}s")

    if args.mfcc:
        mfcc1 = fingerprinter.extract_mfcc(audio1_path)
        print(f"MFCC 1 extracted: shape={mfcc1.shape}")

    if args.compare:
        print(f"\nProcessing video 2: {args.compare}")
        audio2_path = fingerprinter.extract_audio(args.compare)

        fp2_data = fingerprinter.generate_fingerprint(audio2_path)
        print(f"Fingerprint 2 generated: duration={fp2_data['duration']}s")

        # Compare fingerprints
        similarity = fingerprinter.compare_fingerprints(
            fp1_data["fingerprint"], fp2_data["fingerprint"], method=args.method
        )

        print(f"\n{'='*60}")
        print(f"Audio Fingerprint Similarity: {similarity:.2%}")
        print(f"{'='*60}")

        if similarity >= 0.90:
            print("✓ VERY SIMILAR audio")
        elif similarity >= 0.70:
            print("~ SIMILAR audio")
        else:
            print("✗ DIFFERENT audio")

        if args.mfcc:
            mfcc2 = fingerprinter.extract_mfcc(audio2_path)
            mfcc_sim = np.dot(mfcc1, mfcc2)  # Already normalized
            print(f"\nMFCC Similarity: {mfcc_sim:.2%}")

    # Cleanup temp files
    if os.path.exists(audio1_path):
        os.remove(audio1_path)
    if args.compare and os.path.exists(audio2_path):
        os.remove(audio2_path)


if __name__ == "__main__":
    main()
