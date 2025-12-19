import React from 'react';

interface ScoreBarProps {
  score: number;
  label?: string;
}

export const ScoreBar: React.FC<ScoreBarProps> = ({ score, label }) => {
  const percentage = Math.round(score * 100);

  const getColor = (score: number): string => {
    if (score >= 0.95) return 'bg-red-500';
    if (score >= 0.85) return 'bg-orange-500';
    if (score >= 0.70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{label}</span>
          <span className="font-semibold">{percentage}%</span>
        </div>
      )}
      <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full ${getColor(score)} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
