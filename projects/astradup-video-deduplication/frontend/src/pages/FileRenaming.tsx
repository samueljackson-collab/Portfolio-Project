import React, { useState, useMemo } from 'react';
import type { VideoAnalysis } from '../types';
import { Button } from '../components/Button';
import { ArrowRight, Pencil } from '../components/Icons';

// --- MOCK DATA ---
const MOCK_VIDEOS: VideoAnalysis[] = [
  {
    metadata: { id: 'vid_1', fileName: 'dk.2008.x264.720p.mkv', fileSize: 4294967296, duration: 9120, width: 1280, height: 720, frameRate: 23.976, thumbnail: '' },
    enrichedMetadata: { title: 'The Dark Knight', year: 2008, genres: ['Action', 'Crime', 'Drama'], actors: [], director: '', plot: '', imdbRating: 9.0, source: 'IMDB' }
  },
  {
    metadata: { id: 'vid_2', fileName: 'inception_2010_brrip.mp4', fileSize: 8590000000, duration: 8880, width: 1920, height: 1080, frameRate: 24, thumbnail: '' },
    enrichedMetadata: { title: 'Inception', year: 2010, genres: ['Action', 'Sci-Fi'], actors: [], director: '', plot: '', imdbRating: 8.8, source: 'TMDb' }
  },
  {
    metadata: { id: 'vid_3', fileName: 'some-random-movie.avi', fileSize: 1395864371, duration: 7200, width: 720, height: 480, frameRate: 29.97, thumbnail: '' },
    enrichedMetadata: null // Video without enriched data
  },
  {
    metadata: { id: 'vid_4', fileName: 'pulp.fiction.1994.mp4', fileSize: 2147483648, duration: 9240, width: 1920, height: 816, frameRate: 24, thumbnail: '' },
    enrichedMetadata: { title: 'Pulp Fiction', year: 1994, genres: ['Crime', 'Drama'], actors: [], director: '', plot: '', imdbRating: 8.9, source: 'IMDB' }
  },
];

const MOCK_TEMPLATES = [
    { id: 't1', name: 'Title (Year)', format: '{Title} ({Year})' },
    { id: 't2', name: 'Title.Year.Resolution', format: '{Title}.{Year}.{Resolution}p' },
    { id: 't3', name: 'Title [IMDB Rating]', format: '{Title} [{IMDB_Rating}]' },
    { id: 't4', name: 'Title - Director', format: '{Title} - {Director}' },
];
// --- END MOCK DATA ---

const FileRenaming: React.FC = () => {
    const [selectedTemplateId, setSelectedTemplateId] = useState<string>(MOCK_TEMPLATES[0].id);
    const [selectedVideoIds, setSelectedVideoIds] = useState<Set<string>>(() => new Set(MOCK_VIDEOS.filter(v => v.enrichedMetadata).map(v => v.metadata.id)));

    const selectedTemplate = MOCK_TEMPLATES.find(t => t.id === selectedTemplateId);

    const generatePreview = (video: VideoAnalysis, template: string): string | null => {
        if (!video.enrichedMetadata) return null;

        const extension = video.metadata.fileName.split('.').pop() || 'mp4';

        let newName = template
            .replace('{Title}', video.enrichedMetadata.title)
            .replace('{Year}', String(video.enrichedMetadata.year))
            .replace('{Resolution}', String(video.metadata.height))
            .replace('{IMDB_Rating}', String(video.enrichedMetadata.imdbRating))
            .replace('{Director}', video.enrichedMetadata.director)
            // Sanitize filename
            .replace(/[<>:"/\\|?*]/g, '_');

        return `${newName}.${extension}`;
    };

    const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.checked) {
            setSelectedVideoIds(new Set(MOCK_VIDEOS.filter(v => v.enrichedMetadata).map(v => v.metadata.id)));
        } else {
            setSelectedVideoIds(new Set());
        }
    };

    const handleSelectVideo = (videoId: string) => {
        setSelectedVideoIds(prev => {
            const newSet = new Set(prev);
            if (newSet.has(videoId)) {
                newSet.delete(videoId);
            } else {
                newSet.add(videoId);
            }
            return newSet;
        });
    };

    const handleApplyRenaming = () => {
        alert(`Simulating renaming for ${selectedVideoIds.size} files using template: "${selectedTemplate?.name}"`);
    }

    const videosWithPreview = useMemo(() => {
        return MOCK_VIDEOS.map(video => ({
            ...video,
            preview: selectedTemplate ? generatePreview(video, selectedTemplate.format) : null,
        }));
    }, [selectedTemplateId]);

    const allSelectable = MOCK_VIDEOS.filter(v => v.enrichedMetadata).length;

  return (
    <div className="container mx-auto">
      <div className="mb-8">
          <h1 className="text-4xl font-extrabold text-white tracking-tight">Intelligent File Renaming</h1>
          <p className="mt-1 text-lg text-gray-400">Batch rename your video files using enriched metadata.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left Column: Controls */}
        <div className="lg:col-span-1 space-y-6 sticky top-6">
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-cyan-400 mb-4">1. Select Renaming Template</h3>
                <select
                    value={selectedTemplateId}
                    onChange={(e) => setSelectedTemplateId(e.target.value)}
                    className="w-full bg-gray-700 border border-gray-600 text-white rounded-md p-2 focus:ring-cyan-500 focus:border-cyan-500"
                >
                    {MOCK_TEMPLATES.map(template => (
                        <option key={template.id} value={template.id}>{template.name}</option>
                    ))}
                </select>
                <p className="text-xs text-gray-400 mt-2">Format: <span className="font-mono bg-gray-900 p-1 rounded">{selectedTemplate?.format}</span></p>
            </div>
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
                 <h3 className="text-lg font-semibold text-cyan-400 mb-4">2. Apply Changes</h3>
                 <p className="text-sm text-gray-400 mb-4">{selectedVideoIds.size} of {allSelectable} files selected for renaming.</p>
                 <Button onClick={handleApplyRenaming} disabled={selectedVideoIds.size === 0} className="w-full">
                     <Pencil className="w-5 h-5 mr-2" />
                     Rename Selected Files
                 </Button>
            </div>
        </div>

        {/* Right Column: Preview List */}
        <div className="lg:col-span-2">
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg">
                <div className="p-4 border-b border-gray-700 flex items-center">
                    <input
                        type="checkbox"
                        className="h-4 w-4 rounded bg-gray-700 border-gray-600 text-cyan-600 focus:ring-cyan-500"
                        checked={selectedVideoIds.size === allSelectable && allSelectable > 0}
                        onChange={handleSelectAll}
                    />
                    <h3 className="text-lg font-semibold text-gray-200 ml-4">Preview Renaming</h3>
                </div>
                <div className="divide-y divide-gray-700">
                    {videosWithPreview.map(video => (
                        <div key={video.metadata.id} className={`p-4 flex items-center space-x-4 ${!video.enrichedMetadata ? 'opacity-50' : ''}`}>
                            <input
                                type="checkbox"
                                className="h-4 w-4 rounded bg-gray-700 border-gray-600 text-cyan-600 focus:ring-cyan-500"
                                disabled={!video.enrichedMetadata}
                                checked={selectedVideoIds.has(video.metadata.id)}
                                onChange={() => handleSelectVideo(video.metadata.id)}
                            />
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-400 truncate" title={video.metadata.fileName}>{video.metadata.fileName}</p>
                            </div>
                            <ArrowRight className="w-5 h-5 text-gray-500 mx-4" />
                            <div className="flex-1 min-w-0">
                                {video.preview ? (
                                    <p className="text-sm font-medium text-cyan-400 truncate" title={video.preview}>{video.preview}</p>
                                ) : (
                                    <p className="text-sm text-gray-500 italic">No enriched data</p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default FileRenaming;
