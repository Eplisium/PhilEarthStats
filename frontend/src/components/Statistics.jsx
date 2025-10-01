import React from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity, Layers } from 'lucide-react';

const Statistics = ({ statistics }) => {
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-5 w-5 text-purple-600" />
            <span className="text-sm text-gray-600">Total Events</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{statistics.total_earthquakes}</p>
          <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-red-600" />
            <span className="text-sm text-gray-600">Max Magnitude</span>
          </div>
          <p className="text-3xl font-bold text-red-600">
            {statistics.magnitude_stats.max.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Highest recorded</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-5 w-5 text-sky-500" />
            <span className="text-sm text-gray-600">Avg Magnitude</span>
          </div>
          <p className="text-3xl font-bold text-sky-500">
            {statistics.magnitude_stats.average.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Mean value</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Layers className="h-5 w-5 text-orange-600" />
            <span className="text-sm text-gray-600">Avg Depth</span>
          </div>
          <p className="text-3xl font-bold text-orange-600">
            {statistics.depth_stats.average.toFixed(0)} km
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
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={magnitudeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fontSize: 10 }}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" name="Count">
                {magnitudeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Depth Distribution */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Depth Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={depthData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {depthData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Magnitude Stats */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Magnitude Statistics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Maximum:</span>
              <span className="font-bold text-lg text-red-600">
                {statistics.magnitude_stats.max.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Average:</span>
              <span className="font-bold text-lg text-purple-600">
                {statistics.magnitude_stats.average.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Minimum:</span>
              <span className="font-bold text-lg text-sky-500">
                {statistics.magnitude_stats.min.toFixed(2)}
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
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Layers className="h-5 w-5" />
            Depth Statistics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Maximum:</span>
              <span className="font-bold text-lg text-red-600">
                {statistics.depth_stats.max.toFixed(1)} km
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Average:</span>
              <span className="font-bold text-lg text-purple-600">
                {statistics.depth_stats.average.toFixed(1)} km
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Minimum:</span>
              <span className="font-bold text-lg text-sky-500">
                {statistics.depth_stats.min.toFixed(1)} km
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

      {/* Info Box */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
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
