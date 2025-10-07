import React, { memo } from 'react';
import { Clock as ClockIcon, Globe } from 'lucide-react';
import useDataStore from '../store/useDataStore';

// Separate component for clock display - prevents App from re-rendering every second
const Clock = memo(() => {
  // Only subscribe to currentTime in this component
  const currentTime = useDataStore(state => state.currentTime);
  
  return (
    <div className="flex flex-wrap items-center gap-2 sm:gap-3">
      {/* Philippine Time (PHT) */}
      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-md border border-blue-200">
        <Globe className="h-3.5 w-3.5 text-blue-600" />
        <span className="font-semibold text-blue-700 text-xs">
          PHT: {currentTime.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true,
            timeZone: 'Asia/Manila'
          })}
        </span>
      </div>
      
      {/* Local Time */}
      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-purple-50 to-pink-50 rounded-md border border-purple-200">
        <ClockIcon className="h-3.5 w-3.5 text-purple-600" />
        <span className="font-semibold text-purple-700 text-xs">
          Local: {currentTime.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
          })}
        </span>
      </div>
      
      {/* UTC Time */}
      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-gray-50 to-slate-50 rounded-md border border-gray-200">
        <ClockIcon className="h-3.5 w-3.5 text-gray-600" />
        <span className="font-semibold text-gray-700 text-xs">
          UTC: {currentTime.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
            timeZone: 'UTC'
          })}
        </span>
      </div>
    </div>
  );
});

Clock.displayName = 'Clock';

export default Clock;
