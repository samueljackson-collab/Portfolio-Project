"""
AstraDup - AI Video De-duplication System
Setup configuration
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="astradup",
    version="1.0.0",
    author="Samuel Jackson",
    author_email="samuel.jackson@example.com",
    description="Intelligent Multi-Modal Video Similarity Detection System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samueljackson-collab/Portfolio-Project",
    project_urls={
        "Bug Tracker": "https://github.com/samueljackson-collab/Portfolio-Project/issues",
        "Documentation": "https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/astradup-video-deduplication/docs",
        "Source Code": "https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/astradup-video-deduplication",
    },
    packages=find_packages(where=".", exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.4.1",
            "isort>=5.12.0",
        ],
        "clip": [
            "git+https://github.com/openai/CLIP.git",
        ],
    },
    entry_points={
        "console_scripts": [
            "astradup-hash=src.features.perceptual_hash:main",
            "astradup-embed=src.features.deep_embeddings:main",
            "astradup-audio=src.features.audio_fingerprint:main",
            "astradup-similarity=src.engine.similarity_engine:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    keywords=[
        "video",
        "deduplication",
        "machine-learning",
        "computer-vision",
        "similarity-detection",
        "perceptual-hashing",
        "deep-learning",
        "pytorch",
        "opencv",
    ],
    zip_safe=False,
)
