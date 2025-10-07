import React, { useState, useEffect, useMemo } from 'react';
import { 
  Brain, Settings, Play, Pause, RefreshCw, AlertTriangle, 
  TrendingUp, Activity, Target, Layers, Clock, CheckCircle,
  XCircle, AlertCircle, Info, ChevronDown, ChevronUp, Zap,
  BarChart3, Eye, EyeOff, Filter
} from 'lucide-react';

const AIInsights = () => {
  const [config, setConfig] = useState(null);
  const [insights, setInsights] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [recentInsights, setRecentInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [filterRegion, setFilterRegion] = useState('all');
  const [showConfig, setShowConfig] = useState(false);
  
  // Temporary config editing state
  const [editConfig, setEditConfig] = useState({
    enabled: false,
    frequency_hours: 6,
    min_confidence: 0.6
  });

  // Fetch config and insights on mount
  useEffect(() => {
    fetchConfig();
    fetchInsights();
    fetchStatistics();
    fetchRecentInsights();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      if (!running) {
        fetchInsights();
        fetchRecentInsights();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/insights/config');
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
        setEditConfig({
          enabled: data.config.enabled,
          frequency_hours: data.config.frequency_hours,
          min_confidence: data.config.min_confidence
        });
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      const params = new URLSearchParams();
      if (filterType !== 'all') params.append('type', filterType);
      if (filterRegion !== 'all') params.append('region', filterRegion);
      
      const response = await fetch(`http://localhost:5000/api/insights?${params}`);
      const data = await response.json();
      if (data.success) {
        setInsights(data.insights);
      }
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/insights/statistics');
      const data = await response.json();
      if (data.success) {
        setStatistics(data.statistics);
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const fetchRecentInsights = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/insights/recent?hours=24');
      const data = await response.json();
      if (data.success) {
        setRecentInsights(data.insights);
      }
    } catch (error) {
      console.error('Failed to fetch recent insights:', error);
    }
  };

  const toggleEngine = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/insights/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !config.enabled })
      });
      
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
        setEditConfig(prev => ({ ...prev, enabled: data.config.enabled }));
      }
    } catch (error) {
      console.error('Failed to toggle engine:', error);
    }
  };

  const updateConfiguration = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/insights/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editConfig)
      });
      
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
        setShowConfig(false);
      }
    } catch (error) {
      console.error('Failed to update config:', error);
    }
  };

  const runManualAnalysis = async () => {
    setRunning(true);
    try {
      const response = await fetch('http://localhost:5000/api/insights/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force: true })
      });
      
      const data = await response.json();
      if (data.success) {
        // Refresh insights after successful run
        await fetchInsights();
        await fetchStatistics();
        await fetchRecentInsights();
        await fetchConfig();
      }
    } catch (error) {
      console.error('Failed to run analysis:', error);
    } finally {
      setRunning(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-300';
      case 'high': return 'text-orange-600 bg-orange-100 border-orange-300';
      case 'moderate': return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      case 'low': return 'text-blue-600 bg-blue-100 border-blue-300';
      default: return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'risk': return <AlertTriangle className="w-5 h-5" />;
      case 'pattern': return <TrendingUp className="w-5 h-5" />;
      case 'anomaly': return <Zap className="w-5 h-5" />;
      case 'correlation': return <Layers className="w-5 h-5" />;
      case 'prediction': return <Target className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  const filteredInsights = useMemo(() => {
    return insights;
  }, [insights]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Engine Status */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">AI Seismic Insights Engine</h2>
              <p className="text-purple-100 text-sm">Intelligent background pattern detection & analysis</p>
            </div>
          </div>
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <Settings className="w-6 h-6" />
          </button>
        </div>

        {/* Engine Status Bar */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${config?.enabled ? 'bg-green-500' : 'bg-red-500'}`}>
              {config?.enabled ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
            </div>
            <div>
              <p className="text-xs text-purple-100">Status</p>
              <p className="font-semibold">{config?.enabled ? 'Active' : 'Inactive'}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Clock className="w-8 h-8 text-purple-200" />
            <div>
              <p className="text-xs text-purple-100">Total Runs</p>
              <p className="font-semibold">{config?.total_runs || 0}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-purple-200" />
            <div>
              <p className="text-xs text-purple-100">Active Insights</p>
              <p className="font-semibold">{statistics?.active || 0}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-purple-200" />
            <div>
              <p className="text-xs text-purple-100">Generated</p>
              <p className="font-semibold">{config?.total_insights_generated || 0}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleEngine}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-all ${
                config?.enabled 
                  ? 'bg-red-500 hover:bg-red-600' 
                  : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              {config?.enabled ? <><Pause className="w-4 h-4 inline mr-1" /> Disable</> : <><Play className="w-4 h-4 inline mr-1" /> Enable</>}
            </button>
            <button
              onClick={runManualAnalysis}
              disabled={running}
              className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${running ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Configuration Panel */}
        {showConfig && (
          <div className="mt-4 bg-white/10 backdrop-blur-sm rounded-lg p-4 space-y-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Configuration
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-purple-100 mb-2">Analysis Frequency (hours)</label>
                <input
                  type="number"
                  min="1"
                  max="24"
                  value={editConfig.frequency_hours}
                  onChange={(e) => setEditConfig({ ...editConfig, frequency_hours: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 bg-white/20 rounded-lg text-white placeholder-purple-200"
                />
              </div>
              
              <div>
                <label className="block text-sm text-purple-100 mb-2">Min Confidence Threshold</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={editConfig.min_confidence}
                  onChange={(e) => setEditConfig({ ...editConfig, min_confidence: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 bg-white/20 rounded-lg text-white placeholder-purple-200"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={updateConfiguration}
                className="px-4 py-2 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
              >
                Save Configuration
              </button>
              <button
                onClick={() => setShowConfig(false)}
                className="px-4 py-2 bg-white/20 rounded-lg font-semibold hover:bg-white/30 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(statistics.by_type || {}).map(([type, count]) => (
            <div key={type} className="bg-white rounded-lg p-4 shadow-md border-l-4 border-purple-500">
              <div className="flex items-center gap-2 mb-2">
                {getTypeIcon(type)}
                <span className="text-sm font-semibold text-gray-700 capitalize">{type}</span>
              </div>
              <p className="text-2xl font-bold text-purple-600">{count}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg p-4 shadow-md">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="font-semibold text-gray-700">Filters:</span>
          </div>
          
          <select
            value={filterType}
            onChange={(e) => { setFilterType(e.target.value); }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="risk">Risk</option>
            <option value="pattern">Pattern</option>
            <option value="anomaly">Anomaly</option>
            <option value="correlation">Correlation</option>
            <option value="prediction">Prediction</option>
          </select>

          <select
            value={filterRegion}
            onChange={(e) => { setFilterRegion(e.target.value); }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="all">All Regions</option>
            <option value="Luzon">Luzon</option>
            <option value="Visayas">Visayas</option>
            <option value="Mindanao">Mindanao</option>
          </select>

          <button
            onClick={() => { setFilterType('all'); setFilterRegion('all'); }}
            className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Recent Updates */}
      {recentInsights.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 flex items-center gap-2 mb-3">
            <Clock className="w-5 h-5" />
            Recent Updates (Last 24 Hours)
          </h3>
          <div className="space-y-2">
            {recentInsights.slice(0, 3).map((insight) => (
              <div key={insight.id} className="text-sm text-blue-800 flex items-start gap-2">
                <div className="mt-0.5">{getTypeIcon(insight.insight_type)}</div>
                <div>
                  <span className="font-semibold">{insight.title}</span>
                  <span className="text-blue-600 ml-2">({Math.round(insight.age_hours)}h ago)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Insights List */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Activity className="w-6 h-6 text-purple-600" />
          Active Insights ({filteredInsights.length})
        </h3>

        {filteredInsights.length === 0 ? (
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <Info className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No active insights found. Try running the analysis or adjusting filters.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredInsights.map((insight) => (
              <div
                key={insight.id}
                className={`bg-white rounded-lg p-5 shadow-md border-l-4 cursor-pointer transition-all hover:shadow-lg ${
                  getSeverityColor(insight.severity_level).split(' ')[2]
                }`}
                onClick={() => setSelectedInsight(selectedInsight === insight.id ? null : insight.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className={`p-2 rounded-lg ${getSeverityColor(insight.severity_level)}`}>
                        {getTypeIcon(insight.insight_type)}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-bold text-gray-800 text-lg">{insight.title}</h4>
                        <div className="flex items-center gap-3 mt-1">
                          <span className={`text-xs px-2 py-1 rounded-full font-semibold ${getSeverityColor(insight.severity_level)}`}>
                            {insight.severity_level?.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">{insight.region}</span>
                          <span className="text-xs text-gray-500">v{insight.version}</span>
                          <span className="text-xs text-gray-500">
                            {insight.confidence_score ? `${(insight.confidence_score * 100).toFixed(0)}% confidence` : ''}
                          </span>
                        </div>
                      </div>
                    </div>

                    <p className="text-gray-700 leading-relaxed">{insight.description}</p>

                    {selectedInsight === insight.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          {insight.earthquake_count && (
                            <div className="bg-gray-50 rounded p-2">
                              <p className="text-xs text-gray-500">Earthquakes</p>
                              <p className="font-semibold text-gray-800">{insight.earthquake_count}</p>
                            </div>
                          )}
                          {insight.magnitude_range && (
                            <div className="bg-gray-50 rounded p-2">
                              <p className="text-xs text-gray-500">Magnitude Range</p>
                              <p className="font-semibold text-gray-800">{insight.magnitude_range}</p>
                            </div>
                          )}
                          {insight.depth_range && (
                            <div className="bg-gray-50 rounded p-2">
                              <p className="text-xs text-gray-500">Depth Range</p>
                              <p className="font-semibold text-gray-800">{insight.depth_range}</p>
                            </div>
                          )}
                          {insight.time_window_days && (
                            <div className="bg-gray-50 rounded p-2">
                              <p className="text-xs text-gray-500">Time Window</p>
                              <p className="font-semibold text-gray-800">{insight.time_window_days} days</p>
                            </div>
                          )}
                        </div>

                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>Generated by {insight.generated_by_model}</span>
                          <span>Created {Math.round(insight.age_hours)}h ago</span>
                        </div>
                      </div>
                    )}
                  </div>

                  <button className="text-gray-400 hover:text-gray-600 ml-4">
                    {selectedInsight === insight.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Footer */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-purple-900">
            <p className="font-semibold mb-1">About AI Insights Engine</p>
            <p className="text-purple-800">
              The AI Insights Engine continuously monitors earthquake patterns and automatically generates actionable insights. 
              When enabled, it analyzes data every {config?.frequency_hours || 6} hours to detect patterns, anomalies, and risks. 
              All insights are stored with confidence scores and evolve as new data arrives.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
