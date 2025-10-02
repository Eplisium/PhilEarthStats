import React, { useState } from 'react';

const CustomTooltip = ({ children, text, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false);

  const getPositionClasses = () => {
    const positions = {
      top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
      bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
      left: 'right-full top-1/2 -translate-y-1/2 mr-2',
      right: 'left-full top-1/2 -translate-y-1/2 ml-2'
    };
    return positions[position] || positions.top;
  };

  const getArrowClasses = () => {
    const arrows = {
      top: 'top-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-gray-900',
      bottom: 'bottom-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-gray-900',
      left: 'left-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-gray-900',
      right: 'right-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-gray-900'
    };
    return arrows[position] || arrows.top;
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && text && (
        <div className={`absolute z-50 ${getPositionClasses()} animate-in fade-in duration-200`}>
          <div className="bg-gray-900 text-white text-xs font-medium px-3 py-2 rounded-lg shadow-lg whitespace-nowrap">
            {text}
            <div className={`absolute w-0 h-0 border-4 ${getArrowClasses()}`}></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomTooltip;
