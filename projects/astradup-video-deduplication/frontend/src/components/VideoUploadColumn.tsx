import React, { useRef } from 'react';
import { Upload, XCircle, PlayCircle } from './Icons';

interface VideoUploadColumnProps {
  videoFile: File | null;
  setVideoFile: (file: File | null) => void;
  videoNumber: number;
}

export const VideoUploadColumn: React.FC<VideoUploadColumnProps> = ({
  videoFile,
  setVideoFile,
  videoNumber,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoPreviewRef = useRef<HTMLVideoElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      setVideoFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('video/')) {
      setVideoFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleRemove = () => {
    setVideoFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="md:col-span-5">
      <h2 className="text-2xl font-bold text-white mb-4 text-center">
        Video {videoNumber}
      </h2>
      <div
        className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center bg-gray-800/30 hover:bg-gray-800/50 transition-colors cursor-pointer"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => !videoFile && fileInputRef.current?.click()}
      >
        {!videoFile ? (
          <div className="space-y-4">
            <Upload className="w-16 h-16 mx-auto text-gray-500" />
            <div>
              <p className="text-gray-300 font-semibold mb-1">
                Drop video file here
              </p>
              <p className="text-gray-500 text-sm">or click to browse</p>
            </div>
            <p className="text-xs text-gray-600">
              Supported formats: MP4, AVI, MKV, MOV
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative group">
              {videoFile.type.startsWith('video/') && (
                <video
                  ref={videoPreviewRef}
                  className="w-full h-48 object-cover rounded-lg bg-black"
                  controls
                  src={URL.createObjectURL(videoFile)}
                />
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemove();
                }}
                className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white p-2 rounded-full transition-colors"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="text-left bg-gray-900/50 p-4 rounded-lg">
              <div className="flex items-start space-x-3">
                <PlayCircle className="w-6 h-6 text-cyan-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-gray-200 font-medium truncate" title={videoFile.name}>
                    {videoFile.name}
                  </p>
                  <p className="text-gray-400 text-sm mt-1">
                    {formatFileSize(videoFile.size)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
    </div>
  );
};
