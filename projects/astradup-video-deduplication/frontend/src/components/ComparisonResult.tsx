import React from 'react';
import type { ComparisonReport } from '../types';
import { ScoreBar } from './ScoreBar';
import { CheckCircle, XCircle } from './Icons';

interface ComparisonResultProps {
  report: ComparisonReport;
}

export const ComparisonResult: React.FC<ComparisonResultProps> = ({ report }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'Exact Duplicate':
        return 'text-red-400 border-red-500';
      case 'Near Duplicate':
        return 'text-orange-400 border-orange-500';
      case 'Similar Content':
        return 'text-yellow-400 border-yellow-500';
      default:
        return 'text-green-400 border-green-500';
    }
  };

  const getStatusIcon = (status: string) => {
    return status === 'Different Content' ? (
      <CheckCircle className="w-8 h-8" />
    ) : (
      <XCircle className="w-8 h-8" />
    );
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.round(seconds % 60);
    return [h > 0 ? `${h}h` : '', m > 0 ? `${m}m` : '', s > 0 ? `${s}s` : '']
      .filter(Boolean)
      .join(' ');
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-2xl p-8 border border-gray-700">
      <div className={`text-center mb-8 pb-6 border-b-2 ${getStatusColor(report.status)}`}>
        <div className="flex items-center justify-center space-x-3 mb-3">
          {getStatusIcon(report.status)}
          <h2 className="text-3xl font-bold">{report.status}</h2>
        </div>
        <p className="text-gray-400">
          Overall Similarity: {Math.round(report.similarity.combined * 100)}%
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="space-y-2">
          <ScoreBar score={report.similarity.visual} label="Visual Similarity" />
        </div>
        <div className="space-y-2">
          <ScoreBar score={report.similarity.audio} label="Audio Similarity" />
        </div>
        <div className="space-y-2">
          <ScoreBar score={report.similarity.metadata} label="Metadata Similarity" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[report.video1, report.video2].map((video, idx) => (
          <div key={idx} className="bg-gray-900/50 rounded-lg p-6 space-y-4">
            <h3 className="text-xl font-semibold text-cyan-400 border-b border-gray-700 pb-2">
              Video {idx + 1}
            </h3>
            <img
              src={video.metadata.thumbnail}
              alt={video.metadata.fileName}
              className="w-full h-40 object-cover rounded-lg"
            />
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-400">Filename:</span>
                <p className="text-gray-200 font-mono text-xs break-all">
                  {video.metadata.fileName}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Size:</span>
                <span className="text-gray-200 ml-2">
                  {formatBytes(video.metadata.fileSize)}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Duration:</span>
                <span className="text-gray-200 ml-2">
                  {formatDuration(video.metadata.duration)}
                </span>
              </div>
              <div>
                <span className="text-gray-400">Resolution:</span>
                <span className="text-gray-200 ml-2">
                  {video.metadata.width}x{video.metadata.height} @ {video.metadata.frameRate.toFixed(2)}fps
                </span>
              </div>
              {video.enrichedMetadata && (
                <>
                  <div className="pt-2 border-t border-gray-700">
                    <span className="text-gray-400">Title:</span>
                    <p className="text-gray-200">
                      {video.enrichedMetadata.title} ({video.enrichedMetadata.year})
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-400">IMDB:</span>
                    <span className="text-yellow-400 ml-2 font-semibold">
                      {video.enrichedMetadata.imdbRating}/10
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
