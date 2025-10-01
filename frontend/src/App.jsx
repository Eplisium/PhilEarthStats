import React, { useState, useEffect } from 'react';
import { Activity, MapPin, TrendingUp, AlertTriangle, RefreshCw, Mountain, Brain } from 'lucide-react';
import EarthquakeMap from './components/EarthquakeMap';
import EarthquakeList from './components/EarthquakeList';
import Statistics from './components/Statistics';
import VolcanoList from './components/VolcanoList';
import AIAnalysis from './components/AIAnalysis';
// Import your custom logo - place your logo.jpg in the src/assets folder
import logoImage from './assets/logo.jpg';

function App() {
  const [earthquakes, setEarthquakes] = useState([]);
  const [significantEarthquakes, setSignificantEarthquakes] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [volcanoes, setVolcanoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [activeTab, setActiveTab] = useState('map');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showAllEarthquakes, setShowAllEarthquakes] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch from the new /all endpoint to get all earthquakes including aftershocks
      const earthquakeEndpoint = showAllEarthquakes ? '/api/earthquakes/all' : '/api/earthquakes/recent';
      
      const [earthquakesRes, significantRes, statsRes, volcanoesRes] = await Promise.all([
        fetch(earthquakeEndpoint),
        fetch('/api/earthquakes/significant'),
        fetch('/api/earthquakes/statistics'),
        fetch('/api/volcanoes/active')
      ]);

      const earthquakesData = await earthquakesRes.json();
      const significantData = await significantRes.json();
      const statsData = await statsRes.json();
      const volcanoesData = await volcanoesRes.json();

      if (earthquakesData.success) {
        setEarthquakes(earthquakesData.earthquakes);
      }
      if (significantData.success) {
        setSignificantEarthquakes(significantData.earthquakes);
      }
      if (statsData.success) {
        setStatistics(statsData);
      }
      if (volcanoesData.success) {
        setVolcanoes(volcanoesData.volcanoes);
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [showAllEarthquakes]);

  // Real-time clock update every second
  useEffect(() => {
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(clockInterval);
  }, []);

  const getMagnitudeColor = (magnitude) => {
    if (magnitude >= 7) return 'text-red-600';
    if (magnitude >= 6) return 'text-orange-600';
    if (magnitude >= 5) return 'text-yellow-600';
    if (magnitude >= 4) return 'text-sky-500';
    return 'text-gray-600';
  };

  const getAlertLevelColor = (level) => {
    if (level >= 3) return 'bg-red-100 text-red-800 border-red-300';
    if (level >= 2) return 'bg-orange-100 text-orange-800 border-orange-300';
    if (level >= 1) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-green-100 text-green-800 border-green-300';
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* Custom Logo - Replace logo.jpg in src/assets folder */}
              <img 
                src={logoImage} 
                alt="PhilEarthStats Logo" 
                className="h-12 w-12 object-contain rounded-lg"
                onError={(e) => {
                  // Fallback to Activity icon if image fails to load
                  e.target.style.display = 'none';
                  e.target.nextElementSibling.style.display = 'block';
                }}
              />
              <Activity className="h-8 w-8 text-purple-600 hidden" />
              <div>
                <h1 
                  className="text-3xl font-bold text-gray-900 cursor-pointer hover:text-purple-600 transition-colors"
                  onClick={scrollToTop}
                  title="Click to scroll to top"
                >
                  PhilEarthStats
                </h1>
                <p className="text-sm text-gray-600">Real-time Philippines Seismic & Volcanic Monitor</p>
              </div>
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
            <div>
              {lastUpdate && (
                <span>Last updated: {lastUpdate.toLocaleString()}</span>
              )}
            </div>
            <div className="flex items-center gap-4">
              <span className="font-semibold text-purple-600">
                Local Time: {currentTime.toLocaleTimeString()}
              </span>
              <span className="text-gray-400">|</span>
              <span>
                {currentTime.toLocaleDateString(undefined, { 
                  weekday: 'short', 
                  year: 'numeric', 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter Toggle */}
        <div className="mb-6 bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Earthquake Data Filter</h3>
              <p className="text-sm text-gray-600 mt-1">
                {showAllEarthquakes 
                  ? 'Showing ALL earthquakes including tiny aftershocks (no magnitude filter)' 
                  : 'Showing earthquakes with magnitude ≥ 2.5'}
              </p>
            </div>
            <button
              onClick={() => setShowAllEarthquakes(!showAllEarthquakes)}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                showAllEarthquakes
                  ? 'bg-orange-600 text-white hover:bg-orange-700'
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              {showAllEarthquakes ? 'Show Filtered (M ≥ 2.5)' : 'Show All (Include Aftershocks)'}
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Recent Earthquakes</p>
                <p className="text-3xl font-bold text-gray-900">{earthquakes.length}</p>
                <p className="text-xs text-gray-500 mt-1">Last 7 days</p>
              </div>
              <Activity className="h-12 w-12 text-purple-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Significant Events</p>
                <p className="text-3xl font-bold text-orange-600">{significantEarthquakes.length}</p>
                <p className="text-xs text-gray-500 mt-1">M ≥ 4.5 (30 days)</p>
              </div>
              <AlertTriangle className="h-12 w-12 text-orange-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Volcanoes</p>
                <p className="text-3xl font-bold text-red-600">{volcanoes.filter(v => v.alert_level > 0).length}</p>
                <p className="text-xs text-gray-500 mt-1">Alert Level {'>'} 0</p>
              </div>
              <Mountain className="h-12 w-12 text-red-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Max Magnitude</p>
                <p className={`text-3xl font-bold ${statistics ? getMagnitudeColor(statistics.magnitude_stats.max) : 'text-gray-900'}`}>
                  {statistics ? statistics.magnitude_stats.max.toFixed(1) : '--'}
                </p>
                <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
              </div>
              <TrendingUp className="h-12 w-12 text-yellow-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('map')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'map'
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>Interactive Map</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('earthquakes')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'earthquakes'
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4" />
                  <span>Earthquake List</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('volcanoes')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'volcanoes'
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Mountain className="h-4 w-4" />
                  <span>Volcanoes</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('statistics')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'statistics'
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4" />
                  <span>Statistics</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('ai-analysis')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'ai-analysis'
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>AI Analysis</span>
                </div>
              </button>
            </nav>
          </div>

          <div className="p-6">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 text-purple-600 animate-spin" />
                <span className="ml-3 text-gray-600">Loading data...</span>
              </div>
            )}

            {!loading && activeTab === 'map' && (
              <EarthquakeMap 
                earthquakes={earthquakes} 
                volcanoes={volcanoes}
              />
            )}

            {!loading && activeTab === 'earthquakes' && (
              <EarthquakeList 
                earthquakes={earthquakes}
                significantEarthquakes={significantEarthquakes}
              />
            )}

            {!loading && activeTab === 'volcanoes' && (
              <VolcanoList volcanoes={volcanoes} />
            )}

            {!loading && activeTab === 'statistics' && statistics && (
              <Statistics statistics={statistics} />
            )}

            {activeTab === 'ai-analysis' && (
              <AIAnalysis />
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="space-y-2">
            <p className="text-sm text-gray-600">
              Data Sources: <span className="font-semibold">USGS Earthquake Catalog</span> & <span className="font-semibold">PHIVOLCS</span>
            </p>
            <p className="text-xs text-gray-500">
              Real-time earthquake data is provided by the United States Geological Survey (USGS).
              Volcano information is based on Philippine Institute of Volcanology and Seismology (PHIVOLCS) records.
            </p>
            <p className="text-xs text-gray-400 mt-2">
              For official warnings and alerts, please visit <a href="https://www.phivolcs.dost.gov.ph" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline">PHIVOLCS official website</a>
            </p>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                <strong>PHIVOLCS Social Media:</strong> 
                <a href="https://www.facebook.com/phivolcs.dost" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline ml-2">Facebook</a> | 
                <a href="https://twitter.com/phivolcs_dost" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline ml-2">Twitter</a>
              </p>
              <p className="text-xs text-gray-400 mt-2">
                All times are displayed in your local timezone. Server time is synchronized with UTC and Philippine Time (UTC+8).
              </p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;
