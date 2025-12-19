import React from 'react';
import { Link } from 'react-router-dom';
import { Film, Pencil, PlayCircle } from '../components/Icons';
import { Button } from '../components/Button';

const Dashboard: React.FC = () => {
  const features = [
    {
      icon: <Film className="w-12 h-12 text-cyan-400" />,
      title: 'Duplicate Detection',
      description: 'Compare two videos using multi-modal analysis to detect duplicates with high accuracy.',
      link: '/detect',
      buttonText: 'Start Detection',
    },
    {
      icon: <Pencil className="w-12 h-12 text-purple-400" />,
      title: 'File Renaming',
      description: 'Automatically rename video files using enriched metadata from IMDB and other sources.',
      link: '/rename',
      buttonText: 'Rename Files',
    },
    {
      icon: <PlayCircle className="w-12 h-12 text-green-400" />,
      title: 'Video Details',
      description: 'View detailed information about videos including metadata, duplicates, and enriched data.',
      link: '/video/demo',
      buttonText: 'View Demo',
    },
  ];

  const stats = [
    { label: 'Videos Analyzed', value: '1,234', color: 'text-cyan-400' },
    { label: 'Duplicates Found', value: '456', color: 'text-red-400' },
    { label: 'Storage Saved', value: '2.3 TB', color: 'text-green-400' },
    { label: 'Files Renamed', value: '789', color: 'text-purple-400' },
  ];

  return (
    <div className="space-y-12">
      <div className="text-center">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-4">
          Welcome to AstraDup
        </h1>
        <p className="text-xl text-gray-400 max-w-3xl mx-auto">
          Intelligent video duplicate detection and management powered by advanced AI and multi-modal analysis
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 text-center">
            <p className="text-gray-400 text-sm mb-2">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature, idx) => (
          <div
            key={idx}
            className="bg-gray-800/50 border border-gray-700 rounded-lg p-8 hover:bg-gray-800 transition-all duration-200 hover:border-cyan-500 group"
          >
            <div className="mb-6 group-hover:scale-110 transition-transform duration-200">
              {feature.icon}
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">{feature.title}</h3>
            <p className="text-gray-400 mb-6 min-h-[3rem]">{feature.description}</p>
            <Link to={feature.link}>
              <Button className="w-full">{feature.buttonText}</Button>
            </Link>
          </div>
        ))}
      </div>

      <div className="bg-gradient-to-r from-cyan-900/20 to-blue-900/20 border border-cyan-700/30 rounded-lg p-8">
        <h2 className="text-3xl font-bold text-white mb-4">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div className="space-y-2">
            <div className="w-10 h-10 bg-cyan-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
              1
            </div>
            <h4 className="text-lg font-semibold text-cyan-400">Upload Videos</h4>
            <p className="text-gray-400 text-sm">
              Select two videos to compare or batch upload for renaming and analysis
            </p>
          </div>
          <div className="space-y-2">
            <div className="w-10 h-10 bg-cyan-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
              2
            </div>
            <h4 className="text-lg font-semibold text-cyan-400">AI Analysis</h4>
            <p className="text-gray-400 text-sm">
              Multi-modal AI analyzes visual, audio, and metadata to detect similarities
            </p>
          </div>
          <div className="space-y-2">
            <div className="w-10 h-10 bg-cyan-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
              3
            </div>
            <h4 className="text-lg font-semibold text-cyan-400">Get Results</h4>
            <p className="text-gray-400 text-sm">
              Receive detailed reports with similarity scores and recommended actions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
