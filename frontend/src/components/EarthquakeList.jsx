import React, { useMemo, memo } from 'react';
import { format } from 'date-fns';
import { ExternalLink, AlertTriangle, MapPin, Map } from 'lucide-react';
import useDataStore from '../store/useDataStore';
import useEarthquakeListStore from '../store/useEarthquakeListStore';
import useMapStore from '../store/useMapStore';
import useTabStore from '../store/tabStore';

const EarthquakeList = () => {
  // Use Zustand stores with optimized selectors
  const earthquakes = useDataStore(state => state.earthquakes);
  const significantEarthquakes = useDataStore(state => state.significantEarthquakes);
  const showSignificant = useEarthquakeListStore(state => state.showSignificant);
  const setShowSignificant = useEarthquakeListStore(state => state.setShowSignificant);
  const sortBy = useEarthquakeListStore(state => state.sortBy);
  const setSortBy = useEarthquakeListStore(state => state.setSortBy);
  
  // Map and tab stores for navigation
  const setSelectedEarthquake = useMapStore(state => state.setSelectedEarthquake);
  const setActiveTab = useTabStore(state => state.setActiveTab);
  
  // Handle view on map
  const handleViewOnMap = (earthquake) => {
    setSelectedEarthquake(earthquake);
    setActiveTab('map');
    // Scroll to top to show the map
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getMagnitudeColor = (magnitude) => {
    if (magnitude >= 7) return 'bg-red-100 text-red-800 border-red-300';
    if (magnitude >= 6) return 'bg-orange-100 text-orange-800 border-orange-300';
    if (magnitude >= 5) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    if (magnitude >= 4) return 'bg-sky-100 text-sky-800 border-sky-300';
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  // Memoize sorted data to prevent unnecessary recalculations
  const sortedData = useMemo(() => {
    const displayData = showSignificant ? significantEarthquakes : earthquakes;
    const sorted = [...displayData];
    
    if (sortBy === 'time') {
      return sorted.sort((a, b) => b.time - a.time);
    } else if (sortBy === 'magnitude') {
      return sorted.sort((a, b) => b.magnitude - a.magnitude);
    } else if (sortBy === 'depth') {
      return sorted.sort((a, b) => a.depth - b.depth);
    }
    return sorted;
  }, [earthquakes, significantEarthquakes, showSignificant, sortBy]);

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-center justify-between">
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <button
            onClick={() => setShowSignificant(false)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors text-sm sm:text-base ${
              !showSignificant
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Earthquakes ({earthquakes.length})
          </button>
          <button
            onClick={() => setShowSignificant(true)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors text-sm sm:text-base ${
              showSignificant
                ? 'bg-orange-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Significant (M ≥ 4.5) ({significantEarthquakes.length})
          </button>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
          <label className="text-xs sm:text-sm font-medium text-gray-700">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm sm:text-base"
          >
            <option value="time">Time (Newest First)</option>
            <option value="magnitude">Magnitude (Highest First)</option>
            <option value="depth">Depth (Shallowest First)</option>
          </select>
        </div>
      </div>

      {/* Earthquake List */}
      <div className="space-y-3">
        {sortedData.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No earthquakes to display</p>
          </div>
        ) : (
          sortedData.map((earthquake) => (
            <div
              key={earthquake.id}
              className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <span
                      className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-bold border ${getMagnitudeColor(
                        earthquake.magnitude
                      )}`}
                    >
                      M {earthquake.magnitude.toFixed(1)}
                    </span>
                    {earthquake.tsunami && (
                      <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
                        <AlertTriangle className="h-3 w-3" />
                        <span className="hidden sm:inline">TSUNAMI</span>
                        <span className="sm:hidden">🌊</span>
                      </span>
                    )}
                    {earthquake.alert && (
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        earthquake.alert === 'red' ? 'bg-red-100 text-red-700' :
                        earthquake.alert === 'orange' ? 'bg-orange-100 text-orange-700' :
                        earthquake.alert === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {earthquake.alert.toUpperCase()} ALERT
                      </span>
                    )}
                  </div>

                  <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
                    {earthquake.title || earthquake.place}
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <span className="truncate">{earthquake.place}</span>
                    </div>
                    <div>
                      <strong>Time:</strong> {format(new Date(earthquake.time), 'PPpp')} (Local)
                    </div>
                    <div>
                      <strong>Coordinates:</strong> {earthquake.latitude.toFixed(3)}°, {earthquake.longitude.toFixed(3)}°
                    </div>
                    <div>
                      <strong>Depth:</strong> {earthquake.depth.toFixed(1)} km
                    </div>
                    {earthquake.felt && (
                      <div>
                        <strong>Felt Reports:</strong> {earthquake.felt}
                      </div>
                    )}
                    {earthquake.significance && (
                      <div>
                        <strong>Significance:</strong> {earthquake.significance}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mt-3">
                    <button
                      onClick={() => handleViewOnMap(earthquake)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-purple-100 text-purple-700 hover:bg-purple-200 rounded-lg text-xs sm:text-sm font-medium transition-colors"
                    >
                      <Map className="h-3 w-3" />
                      View on Map
                    </button>
                    {earthquake.url && (
                      <a
                        href={earthquake.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg text-xs sm:text-sm font-medium transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                        USGS Details
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default memo(EarthquakeList);
