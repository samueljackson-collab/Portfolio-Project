export interface VideoMetadata {
  id: string;
  fileName: string;
  fileSize: number;
  duration: number;
  width: number;
  height: number;
  frameRate: number;
  thumbnail: string;
}

export interface EnrichedMetadata {
  title: string;
  year: number;
  genres: string[];
  actors: string[];
  director: string;
  plot: string;
  imdbRating: number;
  source: string;
}

export interface VideoAnalysis {
  metadata: VideoMetadata;
  enrichedMetadata?: EnrichedMetadata | null;
}

export interface SimilarityScore {
  visual: number;
  audio: number;
  metadata: number;
  combined: number;
}

export type StatusType = 'Exact Duplicate' | 'Near Duplicate' | 'Similar Content' | 'Different Content';

export interface ComparisonReport {
  video1: VideoAnalysis;
  video2: VideoAnalysis;
  similarity: SimilarityScore;
  status: StatusType;
}
