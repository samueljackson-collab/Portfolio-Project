# AstraDup Architecture Documentation

## System Overview

AstraDup is a distributed, multi-modal video de-duplication system that combines computer vision, audio processing, and metadata analysis to achieve high-accuracy duplicate detection at scale.

## Architecture Components

### 1. Feature Extraction Layer

#### Perceptual Hashing (`src/features/perceptual_hash.py`)
- **Purpose**: Fast near-duplicate detection using perceptual hashes
- **Algorithm**: pHash (difference hashing)
- **Key Features**:
  - Extracts key frames at 1 FPS
  - Generates 256-bit hashes per frame
  - Uses Hamming distance for comparison
  - Robust to re-encoding and resolution changes

#### Deep Learning Embeddings (`src/features/deep_embeddings.py`)
- **Purpose**: Semantic visual similarity using deep neural networks
- **Models**: ResNet-50, VGG-16, CLIP (optional)
- **Key Features**:
  - 2048-dimensional feature vectors
  - Pre-trained on ImageNet
  - Cosine similarity for comparison
  - GPU-accelerated batch processing

#### Audio Fingerprinting (`src/features/audio_fingerprint.py`)
- **Purpose**: Audio-based duplicate detection
- **Technologies**: Chromaprint, MFCC
- **Key Features**:
  - Acoustic fingerprint generation
  - MFCC feature extraction (13 coefficients)
  - Jaccard similarity for fingerprint comparison
  - Handles videos without audio gracefully

### 2. Similarity Engine (`src/engine/similarity_engine.py`)

#### Multi-Modal Fusion
Combines three modalities with weighted scoring:
- **Visual**: 65% weight
- **Audio**: 25% weight
- **Metadata**: 10% weight

#### Confidence Scoring
- Variance-based confidence computation
- High confidence when modalities agree
- Triggers human review for low-confidence cases

#### Thresholds
- Duplicate: ≥95% similarity
- Near-duplicate: ≥85% similarity
- Similar: ≥70% similarity

### 3. Processing Pipeline (`dags/video_deduplication_pipeline.py`)

#### Apache Airflow DAG
1. **Scan**: Discover new videos in S3
2. **Preprocess**: Transcode, extract frames and audio
3. **Feature Extraction**:
   - Visual features (parallel)
   - Audio features (parallel)
4. **Similarity Computation**: Query vector DB, compute scores
5. **Report Generation**: Summarize results
6. **Database Update**: Persist metadata and results

#### Parallelization
- Celery distributed task queue
- 50 worker nodes
- GPU acceleration for deep learning

### 4. Storage Layer

#### PostgreSQL
- Video metadata
- Processing status
- Duplicate relationships

#### Redis
- Task queue (Celery broker)
- Feature cache (L1)
- Real-time data

#### S3
- Raw videos
- Extracted frames
- Audio tracks
- Feature vectors (L2 cache)

#### Pinecone Vector Database
- Deep learning embeddings
- Fast similarity search using HNSW
- Sub-second query times for millions of vectors

## Data Flow

```
┌─────────────┐
│  S3 Upload  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Airflow DAG Triggered      │
│  (Every hour or on-demand)  │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Celery Worker Pool         │
│  (Parallel Processing)      │
└──────┬──────────────────────┘
       │
       ├──────────────┬──────────────┬───────────────┐
       │              │              │               │
       ▼              ▼              ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Transcode│  │  Extract │  │  Extract │  │   Extract    │
│  Video   │  │  Frames  │  │  Audio   │  │   Metadata   │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘
     │             │             │                │
     └─────────────┴─────────────┴────────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │  Feature Extraction          │
           │  ┌────────┬────────┬───────┐ │
           │  │ pHash  │ResNet  │Chroma │ │
           │  │        │ /CLIP  │print  │ │
           │  └───┬────┴───┬────┴───┬───┘ │
           └──────┼────────┼────────┼─────┘
                  │        │        │
                  ▼        ▼        ▼
           ┌─────────────────────────────┐
           │  Store Features             │
           │  ├─ S3 (embeddings)         │
           │  ├─ PostgreSQL (metadata)   │
           │  └─ Pinecone (vectors)      │
           └────────────┬────────────────┘
                        │
                        ▼
           ┌─────────────────────────────┐
           │  Similarity Engine          │
           │  ├─ Query Pinecone          │
           │  ├─ Compute scores          │
           │  └─ Store results           │
           └────────────┬────────────────┘
                        │
                        ▼
           ┌─────────────────────────────┐
           │  Results & Actions          │
           │  ├─ Update database         │
           │  ├─ Generate report         │
           │  ├─ Trigger cleanup         │
           │  └─ Send notifications      │
           └─────────────────────────────┘
```

## Scaling Strategy

### Horizontal Scaling
- Add more Celery workers for increased throughput
- Shard Pinecone index for larger video libraries
- Read replicas for PostgreSQL

### Vertical Scaling
- GPU instances for feature extraction
- High-memory instances for large batch processing
- SSD storage for faster I/O

### Performance Optimizations
1. **Caching**: Two-level cache (Redis + S3)
2. **Batch Processing**: Process 100 videos per batch
3. **Sampling**: 1 FPS frame extraction (97% reduction)
4. **Vector Search**: HNSW approximate nearest neighbor
5. **Parallel Processing**: Multi-worker distributed queue

## Monitoring & Observability

### Metrics (Prometheus)
- Processing throughput (videos/hour)
- Feature extraction time
- Similarity computation time
- Duplicate detection rate
- False positive/negative rates
- Queue depth
- Worker utilization

### Dashboards (Grafana)
- Real-time processing status
- Performance metrics
- Error rates and alerts
- Storage utilization
- Cost tracking

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation
- Error tracking and alerting

## Security Considerations

### Data Protection
- Encryption at rest (S3, PostgreSQL)
- Encryption in transit (TLS/SSL)
- IAM role-based access control

### Secrets Management
- Environment variables for configuration
- AWS Secrets Manager for credentials
- No hardcoded secrets

### Network Security
- VPC isolation
- Security groups
- Private subnets for workers

## Disaster Recovery

### Backup Strategy
- Daily PostgreSQL backups
- S3 versioning for video storage
- Pinecone index snapshots

### Recovery Procedures
- Automated backup restoration
- Replay from S3 event logs
- Graceful degradation (fallback to reduced accuracy)

## Future Enhancements

1. **Temporal Analysis**: Detect partial duplicates (clips from full videos)
2. **Cross-Modal Retrieval**: Text-to-video search using CLIP
3. **Active Learning**: Improve models from human feedback
4. **Real-Time Streaming**: Process live video streams
5. **Edge Deployment**: Lightweight models for mobile/edge devices

---

**Last Updated**: 2025-11-11
**Version**: 1.0.0
**Author**: AstraDup Team
