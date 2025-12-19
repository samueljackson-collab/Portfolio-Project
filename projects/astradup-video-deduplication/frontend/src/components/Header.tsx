import React from 'react';
import { Film } from './Icons';

export const Header: React.FC = () => {
  return (
    <header className="w-full mb-8">
      <div className="flex items-center justify-center space-x-3 mb-2">
        <Film className="w-10 h-10 text-cyan-400" />
        <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
          AstraDup
        </h1>
      </div>
      <p className="text-center text-gray-400 text-lg">
        Intelligent Video Duplicate Detection & Management
      </p>
    </header>
  );
};
