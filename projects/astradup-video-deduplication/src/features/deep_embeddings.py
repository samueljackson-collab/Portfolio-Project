"""
Deep learning feature extraction using pre-trained models
ResNet-50 and CLIP for robust visual similarity detection
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DeepFeatureExtractor:
    """Extract deep learning features from video frames"""

    def __init__(
        self,
        model_name: str = 'resnet50',
        device: Optional[str] = None,
        use_clip: bool = False
    ):
        """
        Initialize feature extractor with pre-trained model

        Args:
            model_name: Model to use ('resnet50', 'vgg16')
            device: Device for inference ('cuda' or 'cpu')
            use_clip: Whether to use CLIP model (requires separate installation)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.use_clip = use_clip

        logger.info(f"Initializing DeepFeatureExtractor: model={model_name}, "
                   f"device={self.device}, clip={use_clip}")

        if use_clip:
            try:
                import clip
                self.model, self.preprocess = self._load_clip()
                logger.info("Loaded CLIP model successfully")
            except ImportError:
                logger.warning("CLIP not available, falling back to ResNet")
                self.use_clip = False
                self.model = self._load_resnet()
        elif model_name == 'resnet50':
            self.model = self._load_resnet()
        elif model_name == 'vgg16':
            self.model = self._load_vgg()
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        self.model.eval()
        self.model.to(self.device)

        # Disable gradients for inference
        for param in self.model.parameters():
            param.requires_grad = False

        logger.info(f"Model loaded successfully on device: {self.device}")

    def _load_resnet(self) -> nn.Module:
        """Load ResNet-50 with ImageNet weights, remove final FC layer"""
        logger.debug("Loading ResNet-50 model...")

        model = models.resnet50(pretrained=True)

        # Remove final classification layer to get embeddings
        model = nn.Sequential(*list(model.children())[:-1])

        return model

    def _load_vgg(self) -> nn.Module:
        """Load VGG-16 with ImageNet weights, remove final FC layer"""
        logger.debug("Loading VGG-16 model...")

        model = models.vgg16(pretrained=True)

        # Remove final classification layers
        model.classifier = nn.Sequential(*list(model.classifier.children())[:-3])

        return model

    def _load_clip(self) -> Tuple[nn.Module, transforms.Compose]:
        """Load CLIP ViT-B/32 model"""
        import clip

        logger.debug("Loading CLIP ViT-B/32 model...")

        model, preprocess = clip.load("ViT-B/32", device=self.device)

        return model, preprocess

    def _get_transform(self) -> transforms.Compose:
        """Get image preprocessing transform"""
        if self.use_clip:
            return self.preprocess

        return transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_frame_features(self, frame: np.ndarray) -> np.ndarray:
        """
        Extract feature vector from a single frame

        Args:
            frame: Frame as numpy array (BGR format from OpenCV)

        Returns:
            Feature vector as numpy array (normalized)
        """
        try:
            # Convert BGR to RGB and create PIL Image
            frame_rgb = Image.fromarray(frame[:, :, ::-1])

            # Preprocess
            transform = self._get_transform()
            image_tensor = transform(frame_rgb).unsqueeze(0).to(self.device)

            # Extract features
            with torch.no_grad():
                if self.use_clip:
                    features = self.model.encode_image(image_tensor)
                else:
                    features = self.model(image_tensor)

                # Flatten and convert to numpy
                features = features.squeeze().cpu().numpy()

                # L2 normalize
                norm = np.linalg.norm(features)
                if norm > 0:
                    features = features / norm

            return features

        except Exception as e:
            logger.error(f"Error extracting frame features: {e}")
            raise

    def extract_video_features(
        self,
        frames: List[np.ndarray],
        aggregation: str = 'mean'
    ) -> np.ndarray:
        """
        Extract features from multiple frames and aggregate

        Args:
            frames: List of video frames
            aggregation: Aggregation method ('mean', 'max', 'concat')

        Returns:
            Aggregated feature vector (normalized)
        """
        if not frames:
            raise ValueError("Empty frames list provided")

        logger.debug(f"Extracting features from {len(frames)} frames "
                    f"with {aggregation} aggregation")

        frame_features = []

        for i, frame in enumerate(frames):
            try:
                features = self.extract_frame_features(frame)
                frame_features.append(features)
            except Exception as e:
                logger.warning(f"Failed to extract features from frame {i}: {e}")
                continue

        if not frame_features:
            raise ValueError("Failed to extract features from any frame")

        frame_features = np.array(frame_features)

        # Aggregate features
        if aggregation == 'mean':
            video_features = np.mean(frame_features, axis=0)
        elif aggregation == 'max':
            video_features = np.max(frame_features, axis=0)
        elif aggregation == 'concat':
            # Flatten all features (warning: can be large)
            video_features = frame_features.flatten()
        else:
            raise ValueError(f"Unsupported aggregation method: {aggregation}")

        # Re-normalize after aggregation
        norm = np.linalg.norm(video_features)
        if norm > 0:
            video_features = video_features / norm

        logger.debug(f"Extracted video features: shape={video_features.shape}, "
                    f"norm={np.linalg.norm(video_features):.4f}")

        return video_features

    @staticmethod
    def cosine_similarity(features1: np.ndarray, features2: np.ndarray) -> float:
        """
        Compute cosine similarity between two feature vectors

        Args:
            features1, features2: Feature vectors (should be normalized)

        Returns:
            Cosine similarity score (0.0 - 1.0)
        """
        try:
            # Compute dot product (cosine similarity for normalized vectors)
            similarity = np.dot(features1, features2)

            # Clamp to valid range (handles numerical precision issues)
            similarity = np.clip(similarity, -1.0, 1.0)

            # Convert from [-1, 1] to [0, 1]
            similarity = (similarity + 1.0) / 2.0

            return float(similarity)

        except Exception as e:
            logger.error(f"Error computing cosine similarity: {e}")
            return 0.0

    @staticmethod
    def euclidean_distance(features1: np.ndarray, features2: np.ndarray) -> float:
        """
        Compute Euclidean distance between two feature vectors

        Args:
            features1, features2: Feature vectors

        Returns:
            Euclidean distance
        """
        try:
            distance = np.linalg.norm(features1 - features2)
            return float(distance)

        except Exception as e:
            logger.error(f"Error computing Euclidean distance: {e}")
            return float('inf')


def main():
    """Example usage of DeepFeatureExtractor"""
    import argparse
    import cv2

    parser = argparse.ArgumentParser(description='Extract deep features from video')
    parser.add_argument('video', help='Path to video file')
    parser.add_argument('--model', default='resnet50', choices=['resnet50', 'vgg16'],
                       help='Model to use (default: resnet50)')
    parser.add_argument('--clip', action='store_true', help='Use CLIP model')
    parser.add_argument('--fps', type=float, default=1.0,
                       help='Frames per second to sample (default: 1.0)')
    parser.add_argument('--device', default=None, help='Device (cuda/cpu)')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize extractor
    extractor = DeepFeatureExtractor(
        model_name=args.model,
        device=args.device,
        use_clip=args.clip
    )

    # Extract frames
    print(f"\nExtracting frames from: {args.video}")
    cap = cv2.VideoCapture(args.video)

    if not cap.isOpened():
        print(f"Error: Cannot open video {args.video}")
        return

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / args.fps)
    frames = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frames.append(frame)

        frame_count += 1

        if len(frames) >= 10:  # Limit for demo
            break

    cap.release()

    print(f"Extracted {len(frames)} frames")

    # Extract features
    print(f"\nExtracting deep features...")
    video_features = extractor.extract_video_features(frames)

    print(f"\n{'='*60}")
    print(f"Feature Extraction Complete")
    print(f"{'='*60}")
    print(f"Model: {args.model}" + (" + CLIP" if args.clip else ""))
    print(f"Device: {extractor.device}")
    print(f"Feature dimension: {len(video_features)}")
    print(f"Feature norm: {np.linalg.norm(video_features):.6f}")
    print(f"Feature stats:")
    print(f"  Mean: {np.mean(video_features):.6f}")
    print(f"  Std: {np.std(video_features):.6f}")
    print(f"  Min: {np.min(video_features):.6f}")
    print(f"  Max: {np.max(video_features):.6f}")


if __name__ == "__main__":
    main()
