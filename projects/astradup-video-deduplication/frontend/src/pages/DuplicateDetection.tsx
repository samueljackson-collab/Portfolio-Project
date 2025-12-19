import React, { useState, useCallback } from 'react';
import { Header } from '../components/Header';
import { VideoUploadColumn } from '../components/VideoUploadColumn';
import { ComparisonResult } from '../components/ComparisonResult';
import { Spinner } from '../components/Spinner';
import { Button } from '../components/Button';
import { ArrowRight, Zap } from '../components/Icons';
import type { VideoAnalysis, ComparisonReport, StatusType } from '../types';
import { mockVideoAnalysis, mockMetadataFetch } from '../services/mockAnalysisService';

const DuplicateDetection: React.FC = () => {
  const [video1, setVideo1] = useState<File | null>(null);
  const [video2, setVideo2] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ComparisonReport | null>(null);

  const handleCompare = useCallback(async () => {
    if (!video1 || !video2) {
      setError('Please select two videos to compare.');
      return;
    }
    setError(null);
    setIsLoading(true);
    setReport(null);

    try {
      // Simulate parallel processing
      const [analysis1, analysis2] = await Promise.all([
        mockVideoAnalysis(video1),
        mockVideoAnalysis(video2),
      ]);

      const [enrichedMeta1, enrichedMeta2] = await Promise.all([
        mockMetadataFetch(analysis1.metadata.fileName),
        mockMetadataFetch(analysis2.metadata.fileName),
      ]);

      const videoData1: VideoAnalysis = { ...analysis1, enrichedMetadata: enrichedMeta1 };
      const videoData2: VideoAnalysis = { ...analysis2, enrichedMetadata: enrichedMeta2 };

      const visualWeight = 0.65;
      const audioWeight = 0.25;
      const metadataWeight = 0.10;

      const visualSim = Math.random() * 0.4 + 0.6; // Bias towards more similar
      const audioSim = Math.random() * 0.4 + 0.6;

      const durationDiff = Math.abs(videoData1.metadata.duration - videoData2.metadata.duration);
      const metadataSim = Math.max(0, 1 - durationDiff / 60);

      const combinedScore = (visualSim * visualWeight) + (audioSim * audioWeight) + (metadataSim * metadataWeight);

      let status: StatusType;
      if (combinedScore >= 0.95) status = 'Exact Duplicate';
      else if (combinedScore >= 0.85) status = 'Near Duplicate';
      else if (combinedScore >= 0.70) status = 'Similar Content';
      else status = 'Different Content';

      setReport({
        video1: videoData1,
        video2: videoData2,
        similarity: {
          visual: visualSim,
          audio: audioSim,
          metadata: metadataSim,
          combined: combinedScore,
        },
        status: status,
      });

    } catch (e) {
      setError('An error occurred during analysis.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [video1, video2]);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col p-4 md:p-8">
      <Header />
      <main className="flex-grow container mx-auto flex flex-col items-center justify-center space-y-8 py-8">
        <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-11 gap-8 items-start">
          <VideoUploadColumn videoFile={video1} setVideoFile={setVideo1} videoNumber={1} />
          <div className="flex flex-col items-center justify-center h-full md:col-span-1 pt-0 md:pt-32">
            <div className="hidden md:block w-px h-24 bg-gray-700"></div>
            <ArrowRight className="w-8 h-8 text-gray-500 my-4 transform md:rotate-0 rotate-90" />
            <div className="hidden md:block w-px h-24 bg-gray-700"></div>
          </div>
          <VideoUploadColumn videoFile={video2} setVideoFile={setVideo2} videoNumber={2} />
        </div>

        <div className="w-full max-w-md text-center">
          <Button
            onClick={handleCompare}
            disabled={!video1 || !video2 || isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Spinner /> Analyzing...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5 mr-2" />
                Compare Videos
              </>
            )}
          </Button>
          {error && <p className="text-red-400 mt-4">{error}</p>}
        </div>

        {isLoading && (
          <div className="text-center p-8 bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl">
              <Spinner className="w-12 h-12 mx-auto" />
              <p className="mt-4 text-lg font-semibold text-cyan-400 animate-pulse">Running Multi-Modal Analysis...</p>
              <p className="text-gray-400 mt-2">Extracting visual fingerprints, audio signatures, and enriching metadata...</p>
          </div>
        )}

        {report && !isLoading && (
          <div className="w-full max-w-7xl">
            <ComparisonResult report={report} />
          </div>
        )}
      </main>
    </div>
  );
};

export default DuplicateDetection;
