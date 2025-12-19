import React from 'react';
import type { VideoAnalysis } from '../types';
import { ScoreBar } from '../components/ScoreBar';
import { Film, Star, Video } from '../components/Icons';

// --- MOCK DATA for demonstration ---
const mockVideo: VideoAnalysis = {
  metadata: {
    id: 'vid_abc123',
    fileName: 'the.dark.knight.2008.1080p.bluray.x264-anoxmous.mp4',
    fileSize: 8589934592, // 8 GB
    duration: 9120, // 2h 32m
    width: 1920,
    height: 1080,
    frameRate: 23.976,
    thumbnail: 'https://picsum.photos/seed/vid_abc123/600/400',
  },
  enrichedMetadata: {
    title: 'The Dark Knight',
    year: 2008,
    genres: ['Action', 'Crime', 'Drama'],
    actors: ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart', 'Michael Caine'],
    director: 'Christopher Nolan',
    plot: 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
    imdbRating: 9.0,
    source: 'IMDB',
  },
};

const mockDuplicates: Array<{ video: VideoAnalysis, similarity: number }> = [
  {
    video: {
      metadata: { ...mockVideo.metadata, id: 'dup_01', fileName: 'TDK.2008.720p.mkv', fileSize: 4294967296 },
      enrichedMetadata: mockVideo.enrichedMetadata,
    },
    similarity: 0.98,
  },
  {
    video: {
      metadata: { ...mockVideo.metadata, id: 'dup_02', fileName: 'Dark Knight Rises Again.mp4', fileSize: 8590000000, duration: 9125 },
      enrichedMetadata: mockVideo.enrichedMetadata,
    },
    similarity: 0.91,
  },
  {
    video: {
        metadata: { ...mockVideo.metadata, id: 'dup_03', fileName: 'Batman 2.avi', fileSize: 1395864371, width: 720, height: 480 },
        enrichedMetadata: mockVideo.enrichedMetadata,
      },
    similarity: 0.76,
  },
];
// --- END MOCK DATA ---

const formatBytes = (bytes: number, decimals = 2): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const formatDuration = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.round(seconds % 60);
    return [
      h > 0 ? `${h}h` : '',
      m > 0 ? `${m}m` : '',
      s > 0 ? `${s}s` : '',
    ].filter(Boolean).join(' ');
};

const DuplicateItem: React.FC<{ video: VideoAnalysis, similarity: number }> = ({ video, similarity }) => (
    <div className="bg-gray-800 p-4 rounded-lg flex items-center space-x-4 hover:bg-gray-700 transition-colors duration-200">
        <img src={video.metadata.thumbnail} alt={video.metadata.fileName} className="w-24 h-16 object-cover rounded" />
        <div className="flex-grow">
            <p className="font-semibold text-gray-200 truncate">{video.metadata.fileName}</p>
            <p className="text-xs text-gray-400">{formatBytes(video.metadata.fileSize)} | {video.metadata.width}x{video.metadata.height}</p>
        </div>
        <div className="w-1/3">
            <ScoreBar score={similarity} label="Similarity" />
        </div>
    </div>
);

const VideoDetail: React.FC = () => {
  // In a real app, this data would come from props or a data fetching hook
  const { metadata, enrichedMetadata } = mockVideo;

  if (!enrichedMetadata) {
    return <div>Loading...</div>; // Or some other placeholder
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-4 md:p-8">
      <div className="container mx-auto">
        {/* --- Header Section --- */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">{enrichedMetadata.title}
            <span className="text-gray-500 font-semibold ml-3">({enrichedMetadata.year})</span>
          </h1>
          <div className="flex items-center space-x-4 mt-2">
            <div className="flex items-center space-x-1 text-yellow-400">
                <Star className="w-5 h-5"/>
                <span className="font-bold text-lg">{enrichedMetadata.imdbRating.toFixed(1)}</span>
                <span className="text-gray-400 text-sm">/ 10</span>
            </div>
            <div className="flex items-center space-x-2">
                {enrichedMetadata.genres.map(genre => (
                    <span key={genre} className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-0.5 rounded-full">{genre}</span>
                ))}
            </div>
          </div>
        </div>

        {/* --- Main Content Grid --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Thumbnail and File Details */}
          <div className="lg:col-span-1 space-y-6">
            <img src={metadata.thumbnail} alt={`Poster for ${enrichedMetadata.title}`} className="w-full rounded-lg shadow-2xl" />

            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 space-y-3">
              <h3 className="text-lg font-semibold text-cyan-400 border-b border-gray-700 pb-2 mb-3">File Details</h3>
              <div className="flex items-start space-x-3 text-sm">
                <Film className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="font-semibold text-gray-400">Filename</p>
                  <p className="text-gray-200 break-all font-mono text-xs">{metadata.fileName}</p>
                </div>
              </div>
               <div className="flex items-start space-x-3 text-sm">
                <Video className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="font-semibold text-gray-400">Properties</p>
                  <p className="text-gray-300">{formatBytes(metadata.fileSize)} | {formatDuration(metadata.duration)} | {metadata.width}x{metadata.height}@{metadata.frameRate.toFixed(2)}fps</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Synopsis and Credits */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-cyan-400 mb-2">Synopsis</h3>
              <p className="text-gray-300 leading-relaxed">{enrichedMetadata.plot}</p>
            </div>
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-cyan-400 mb-4">Cast & Crew</h3>
              <div className="space-y-3 text-sm">
                <div className="flex">
                  <p className="w-24 font-semibold text-gray-400">Director</p>
                  <p className="text-gray-200">{enrichedMetadata.director}</p>
                </div>
                <div className="flex">
                  <p className="w-24 font-semibold text-gray-400">Starring</p>
                  <p className="text-gray-200 flex-1">{enrichedMetadata.actors.join(', ')}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* --- Duplicates Section --- */}
        <div className="mt-12">
            <h2 className="text-3xl font-bold mb-6 text-center">Potential Duplicates</h2>
            <div className="space-y-4 max-w-4xl mx-auto">
                {mockDuplicates.map(dup => (
                    <DuplicateItem key={dup.video.metadata.id} video={dup.video} similarity={dup.similarity} />
                ))}
            </div>
        </div>
      </div>
    </div>
  );
};

export default VideoDetail;
