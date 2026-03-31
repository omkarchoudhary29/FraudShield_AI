import React from 'react';
import { getFraudProbabilityGradient, getRiskColor } from '../utils/helpers';

const RiskMeter = ({ probability, riskLevel, size = 'md' }) => {
  const percentage = Math.round(probability * 100);
  
  const sizes = {
    sm: { container: 'w-32 h-32', text: 'text-2xl', label: 'text-xs' },
    md: { container: 'w-40 h-40', text: 'text-3xl', label: 'text-sm' },
    lg: { container: 'w-48 h-48', text: 'text-4xl', label: 'text-base' },
  };

  const gradient = getFraudProbabilityGradient(probability);
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className={`relative ${sizes[size].container}`}>
        <svg className="transform -rotate-90 w-full h-full">
          {/* Background circle */}
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            stroke="url(#gradient)"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" className={gradient.split(' ')[0].replace('from-', 'text-')} stopColor="currentColor" />
              <stop offset="100%" className={gradient.split(' ')[1].replace('to-', 'text-')} stopColor="currentColor" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${sizes[size].text}`}>{percentage}%</span>
          <span className={`text-gray-500 ${sizes[size].label}`}>Risk Score</span>
        </div>
      </div>
      <div className={`px-4 py-2 rounded-full ${getRiskColor(riskLevel)} font-semibold`}>
        {riskLevel}
      </div>
    </div>
  );
};

export default RiskMeter;
