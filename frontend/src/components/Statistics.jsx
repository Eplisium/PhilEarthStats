import React, { useState, useEffect } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity, Layers } from 'lucide-react';
import useCountUp from '../hooks/useCountUp';
import useTabStore from '../store/tabStore';
import EarthquakeCalendar from './EarthquakeCalendar';

const Statistics = ({ statistics }) => {
  const [chartKey, setChartKey] = useState(0);
  const [showCharts, setShowCharts] = useState(false);
  const [animateCards, setAnimateCards] = useState(false);
  const { activeTab, tabChangeCount } = useTabStore();

  // Trigger chart re-animation when Statistics tab becomes active
  useEffect(() => {
    // Only animate if we're on the statistics tab
    if (activeTab === 'statistics') {
      setShowCharts(false);
      setAnimateCards(false);
      
      // Stagger animations: cards first, then charts
      const cardTimer = setTimeout(() => {
        setAnimateCards(true);
      }, 100);
      
      const chartTimer = setTimeout(() => {
        setChartKey(prev => prev + 1);
        setShowCharts(true);
      }, 800);
      
      return () => {
        clearTimeout(cardTimer);
        clearTimeout(chartTimer);
      };
    }
  }, [activeTab, tabChangeCount]);

  // Animated numbers
  const totalEvents = useCountUp(statistics.total_earthquakes, 1000, 0);
  const maxMagnitude = useCountUp(statistics.magnitude_stats.max, 1000, 1);
  const avgMagnitude = useCountUp(statistics.magnitude_stats.average, 1000, 1);
  const avgDepth = useCountUp(statistics.depth_stats.average, 1000, 0);
  const detailMaxMag = useCountUp(statistics.magnitude_stats.max, 1000, 2);
  const detailAvgMag = useCountUp(statistics.magnitude_stats.average, 1000, 2);
  const detailMinMag = useCountUp(statistics.magnitude_stats.min, 1000, 2);
  const detailMaxDepth = useCountUp(statistics.depth_stats.max, 1000, 1);
  const detailAvgDepth = useCountUp(statistics.depth_stats.average, 1000, 1);
  const detailMinDepth = useCountUp(statistics.depth_stats.min, 1000, 1);
  const COLORS = {
    micro: '#6b7280',
    minor: '#059669',
    light: '#7c3aed',
    moderate: '#ca8a04',
    strong: '#ea580c',
    major: '#dc2626',
    great: '#7c2d12'
  };

  const DEPTH_COLORS = {
    shallow: '#fbbf24',
    intermediate: '#f97316',
    deep: '#dc2626'
  };

  const magnitudeData = [
    { name: 'Micro (<3.0)', value: statistics.magnitude_stats.distribution.micro, color: COLORS.micro },
    { name: 'Minor (3.0-3.9)', value: statistics.magnitude_stats.distribution.minor, color: COLORS.minor },
    { name: 'Light (4.0-4.9)', value: statistics.magnitude_stats.distribution.light, color: COLORS.light },
    { name: 'Moderate (5.0-5.9)', value: statistics.magnitude_stats.distribution.moderate, color: COLORS.moderate },
    { name: 'Strong (6.0-6.9)', value: statistics.magnitude_stats.distribution.strong, color: COLORS.strong },
    { name: 'Major (7.0-7.9)', value: statistics.magnitude_stats.distribution.major, color: COLORS.major },
    { name: 'Great (≥8.0)', value: statistics.magnitude_stats.distribution.great, color: COLORS.great }
  ].filter(item => item.value > 0);

  const depthData = [
    { name: 'Shallow (<70 km)', value: statistics.depth_stats.distribution.shallow, color: DEPTH_COLORS.shallow },
    { name: 'Intermediate (70-300 km)', value: statistics.depth_stats.distribution.intermediate, color: DEPTH_COLORS.intermediate },
    { name: 'Deep (≥300 km)', value: statistics.depth_stats.distribution.deep, color: DEPTH_COLORS.deep }
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 transition-all duration-700 ${
        animateCards ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        <div className="bg-white border border-gray-200 rounded-lg p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-5 w-5 text-purple-600" />
            <span className="text-sm text-gray-600">Total Events</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{totalEvents}</p>
          <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-red-600" />
            <span className="text-sm text-gray-600">Max Magnitude</span>
          </div>
          <p className="text-3xl font-bold text-red-600">
            {maxMagnitude.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Highest recorded</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-5 w-5 text-sky-500" />
            <span className="text-sm text-gray-600">Avg Magnitude</span>
          </div>
          <p className="text-3xl font-bold text-sky-500">
            {avgMagnitude.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Mean value</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Layers className="h-5 w-5 text-orange-600" />
            <span className="text-sm text-gray-600">Avg Depth</span>
          </div>
          <p className="text-3xl font-bold text-orange-600">
            {avgDepth.toFixed(0)} km
          </p>
          <p className="text-xs text-gray-500 mt-1">Mean depth</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Magnitude Distribution */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Magnitude Distribution
          </h3>
          {showCharts ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={magnitudeData} key={`bar-${chartKey}`} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <defs>
                  {magnitudeData.map((entry, index) => (
                    <linearGradient key={`gradient-${index}`} id={`barGradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={entry.color} stopOpacity={0.9} />
                      <stop offset="95%" stopColor={entry.color} stopOpacity={0.7} />
                    </linearGradient>
                  ))}
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" strokeOpacity={0.5} />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  tick={{ fontSize: 10, fill: '#6b7280' }}
                  stroke="#9ca3af"
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  stroke="#9ca3af"
                />
                <Tooltip 
                  cursor={{ fill: 'rgba(147, 51, 234, 0.1)' }}
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.98)', 
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
                    padding: '12px'
                  }}
                  labelStyle={{ fontWeight: 600, color: '#111827', marginBottom: '4px' }}
                  itemStyle={{ color: '#6b7280', padding: '4px 0' }}
                />
                <Bar 
                  dataKey="value" 
                  name="Count"
                  isAnimationActive={true}
                  isUpdateAnimationActive={true}
                  animationBegin={0}
                  animationDuration={1500}
                  animationEasing="ease-in-out"
                  radius={[8, 8, 0, 0]}
                  maxBarSize={80}
                >
                  {magnitudeData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={`url(#barGradient-${index})`}
                      stroke={entry.color}
                      strokeWidth={2}
                      className="transition-all duration-300 hover:opacity-80"
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center">
              <div className="animate-pulse space-y-4 w-full px-8">
                <div className="flex gap-4 items-end justify-around h-48">
                  <div className="bg-gray-200 rounded-t-lg w-16 h-24 animate-pulse" style={{ animationDelay: '0ms' }}></div>
                  <div className="bg-gray-200 rounded-t-lg w-16 h-32 animate-pulse" style={{ animationDelay: '100ms' }}></div>
                  <div className="bg-gray-200 rounded-t-lg w-16 h-40 animate-pulse" style={{ animationDelay: '200ms' }}></div>
                  <div className="bg-gray-200 rounded-t-lg w-16 h-28 animate-pulse" style={{ animationDelay: '300ms' }}></div>
                  <div className="bg-gray-200 rounded-t-lg w-16 h-20 animate-pulse" style={{ animationDelay: '400ms' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Depth Distribution */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Depth Distribution
          </h3>
          {showCharts ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart key={`pie-${chartKey}`}>
                <defs>
                  {depthData.map((entry, index) => (
                    <linearGradient key={`pieGradient-${index}`} id={`pieGradient-${index}`} x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor={entry.color} stopOpacity={1} />
                      <stop offset="100%" stopColor={entry.color} stopOpacity={0.8} />
                    </linearGradient>
                  ))}
                </defs>
                <Pie
                  data={depthData}
                  cx="50%"
                  cy="50%"
                  labelLine={{
                    stroke: '#9ca3af',
                    strokeWidth: 1.5
                  }}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  innerRadius={0}
                  fill="#8884d8"
                  dataKey="value"
                  isAnimationActive={true}
                  isUpdateAnimationActive={true}
                  animationBegin={200}
                  animationDuration={1800}
                  animationEasing="ease-in-out"
                  paddingAngle={3}
                >
                  {depthData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={`url(#pieGradient-${index})`}
                      stroke="#ffffff"
                      strokeWidth={3}
                      className="transition-all duration-300"
                      style={{
                        filter: 'drop-shadow(0px 2px 4px rgba(0,0,0,0.2))',
                        transition: 'all 0.3s ease'
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.98)', 
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
                    padding: '12px'
                  }}
                  labelStyle={{ fontWeight: 600, color: '#111827', marginBottom: '4px' }}
                  itemStyle={{ color: '#6b7280', padding: '4px 0' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600" style={{ animationDuration: '1s' }}></div>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 transition-all duration-700 delay-300 ${
        animateCards ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        {/* Magnitude Stats */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 transform transition-all duration-500 hover:scale-[1.02] hover:shadow-xl">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Magnitude Statistics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b transition-all duration-300 hover:bg-gray-50 hover:px-2 rounded">
              <span className="text-gray-600">Maximum:</span>
              <span className="font-bold text-lg text-red-600">
                {detailMaxMag.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b transition-all duration-300 hover:bg-gray-50 hover:px-2 rounded">
              <span className="text-gray-600">Average:</span>
              <span className="font-bold text-lg text-purple-600">
                {detailAvgMag.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b transition-all duration-300 hover:bg-gray-50 hover:px-2 rounded">
              <span className="text-gray-600">Minimum:</span>
              <span className="font-bold text-lg text-sky-500">
                {detailMinMag.toFixed(2)}
              </span>
            </div>
          </div>

          <div className="mt-4 p-3 bg-gray-50 rounded">
            <p className="text-sm font-semibold text-gray-700 mb-2">Classification Breakdown:</p>
            <div className="space-y-1 text-xs">
              {Object.entries(statistics.magnitude_stats.distribution).map(([key, value]) => {
                if (value === 0) return null;
                return (
                  <div key={key} className="flex justify-between">
                    <span className="capitalize">{key}:</span>
                    <span className="font-semibold">{value} events</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Depth Stats */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 transform transition-all duration-500 hover:scale-[1.02] hover:shadow-xl">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Layers className="h-5 w-5" />
            Depth Statistics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b transition-all duration-300 hover:bg-gray-50 hover:px-2 rounded">
              <span className="text-gray-600">Maximum:</span>
              <span className="font-bold text-lg text-red-600">
                {detailMaxDepth.toFixed(1)} km
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b transition-all duration-300 hover:bg-gray-50 hover:px-2 rounded">
              <span className="text-gray-600">Average:</span>
              <span className="font-bold text-lg text-purple-600">
                {detailAvgDepth.toFixed(1)} km
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b transition-all duration-300 hover:bg-gray-50 hover:px-2 rounded">
              <span className="text-gray-600">Minimum:</span>
              <span className="font-bold text-lg text-sky-500">
                {detailMinDepth.toFixed(1)} km
              </span>
            </div>
          </div>

          <div className="mt-4 p-3 bg-gray-50 rounded">
            <p className="text-sm font-semibold text-gray-700 mb-2">Depth Classification:</p>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Shallow (&lt;70 km):</span>
                <span className="font-semibold">
                  {statistics.depth_stats.distribution.shallow} events
                </span>
              </div>
              <div className="flex justify-between">
                <span>Intermediate (70-300 km):</span>
                <span className="font-semibold">
                  {statistics.depth_stats.distribution.intermediate} events
                </span>
              </div>
              <div className="flex justify-between">
                <span>Deep (≥300 km):</span>
                <span className="font-semibold">
                  {statistics.depth_stats.distribution.deep} events
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Tracking & Calendar */}
      <div className={`transition-all duration-700 delay-700 ${
        animateCards ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        <EarthquakeCalendar />
      </div>

      {/* Info Box */}
      <div className={`bg-purple-50 border border-purple-200 rounded-lg p-4 transition-all duration-700 delay-900 ${
        animateCards ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        <p className="text-sm text-purple-800">
          <strong>Analysis Period:</strong> {statistics.period} | 
          <strong className="ml-2">Data Source:</strong> {statistics.metadata.source} | 
          <strong className="ml-2">Total Events:</strong> {statistics.total_earthquakes}
        </p>
      </div>
    </div>
  );
};

export default Statistics;
