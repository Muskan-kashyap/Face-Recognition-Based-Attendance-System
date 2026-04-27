import React from 'react';

export const DashboardSkeleton = () => {
  return (
    <div className="p-6 space-y-4 animate-pulse">
      <div className="h-8 w-1/3 bg-gray-800 rounded"></div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="h-32 bg-gray-800 rounded-xl"></div>
        <div className="h-32 bg-gray-800 rounded-xl"></div>
        <div className="h-32 bg-gray-800 rounded-xl"></div>
      </div>

      <div className="h-64 bg-gray-800 rounded-xl"></div>
    </div>
  );
};
