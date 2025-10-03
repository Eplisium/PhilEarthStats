import React, { useEffect } from 'react';
import { Brain, Loader, AlertCircle, TrendingUp, Activity, Trash2, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import useAIAnalysisStore from '../store/aiAnalysisStore';

const AIAnalysis = () => {
  const { 
    analysis, 
    loading, 
    error, 
    lastGenerated, 
    availableModels, 
    selectedModel, 
    loadingModels,
    progress,
    generateAnalysis, 
    clearAnalysis,
    fetchAvailableModels,
    setSelectedModel
  } = useAIAnalysisStore();

  // Fetch available models on component mount
  useEffect(() => {
    if (availableModels.length === 0) {
      fetchAvailableModels();
    }
  }, []);

  return (
    <div className="space-y-6">
      {/* Header with Generate Button */}
      <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg p-4 sm:p-6 border border-purple-300">
        <div className="flex flex-col lg:flex-row items-start justify-between gap-4">
          <div className="flex-1 w-full lg:w-auto">
            <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
              <Brain className="h-6 w-6 sm:h-8 sm:w-8 text-purple-600 flex-shrink-0" />
              <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">AI-Powered Seismic Analysis</h2>
            </div>
            <p className="text-sm sm:text-base text-gray-700 mb-3 sm:mb-4">
              Get comprehensive insights from an AI seismologist analyzing the last 90 days of earthquake data 
              for the Philippines region. The AI will assess patterns, risks, and provide actionable recommendations.
            </p>
            
            {/* Model Selection */}
            <div className="mb-3 sm:mb-4">
              <label className="block text-xs sm:text-sm font-semibold text-gray-700 mb-2">
                <Sparkles className="inline h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                AI Model Selection
              </label>
              <select
                value={selectedModel || ''}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={loading || loadingModels}
                className="w-full px-3 sm:px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50 disabled:cursor-not-allowed bg-white text-gray-900 text-sm sm:text-base"
              >
                {loadingModels ? (
                  <option>Loading models...</option>
                ) : (
                  availableModels.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name} - {model.description}
                    </option>
                  ))
                )}
              </select>
              <p className="text-xs text-gray-600 mt-1">
                Select the AI model to use for analysis. Different models may provide varying insights.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs sm:text-sm text-gray-600">
              <span className="flex items-center gap-1 bg-white px-2 sm:px-3 py-1 rounded-full border border-gray-200">
                <Activity className="h-3 w-3 sm:h-4 sm:w-4" />
                90-day comprehensive analysis
              </span>
              <span className="flex items-center gap-1 bg-white px-2 sm:px-3 py-1 rounded-full border border-gray-200">
                <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4" />
                Pattern detection
              </span>
              <span className="flex items-center gap-1 bg-white px-2 sm:px-3 py-1 rounded-full border border-gray-200">
                <AlertCircle className="h-3 w-3 sm:h-4 sm:w-4" />
                Risk assessment
              </span>
            </div>
          </div>
          <div className="flex flex-col gap-2 w-full lg:w-auto">
            <button
              onClick={generateAnalysis}
              disabled={loading}
              className="flex items-center justify-center gap-2 px-4 sm:px-6 py-2 sm:py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium shadow-md text-sm sm:text-base"
            >
              {loading ? (
                <>
                  <Loader className="h-5 w-5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Brain className="h-5 w-5" />
                  <span>{analysis ? 'Regenerate Analysis' : 'Generate AI Analysis'}</span>
                </>
              )}
            </button>
            {analysis && !loading && (
              <button
                onClick={clearAnalysis}
                className="flex items-center justify-center gap-2 px-6 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium text-sm"
              >
                <Trash2 className="h-4 w-4" />
                <span>Clear Analysis</span>
              </button>
            )}
            {lastGenerated && !loading && (
              <p className="text-xs text-gray-600 text-right">
                Last generated: {new Date(lastGenerated).toLocaleString()}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              {error.includes('API key') && (
                <p className="text-red-600 text-xs mt-2">
                  To use this feature, you need to set up your OpenRouter API key in the backend .env file.
                  Get your API key from <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="underline font-semibold">openrouter.ai/keys</a>
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Loading State with Progress */}
      {loading && (
        <div className="bg-white rounded-lg border border-gray-200 p-8 sm:p-12">
          <div className="flex flex-col items-center justify-center space-y-6">
            <Loader className="h-12 w-12 text-purple-600 animate-spin" />
            <div className="text-center w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-900">Analyzing Earthquake Data</h3>
              <p className="text-gray-600 mt-2">Processing 90 days of seismic data from the Philippines...</p>
              
              {/* Progress Bar */}
              {progress.percentage > 0 && (
                <div className="mt-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-purple-700">{progress.message}</span>
                    <span className="text-sm font-semibold text-purple-600">{progress.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${progress.percentage}%` }}
                    />
                  </div>
                  <div className="mt-3 space-y-1 text-xs text-gray-500">
                    <div className={progress.percentage >= 10 ? 'text-purple-600 font-semibold' : ''}>
                      ✓ Fetching earthquake data
                    </div>
                    <div className={progress.percentage >= 25 ? 'text-purple-600 font-semibold' : ''}>
                      {progress.percentage >= 25 ? '✓' : '○'} Processing regional statistics
                    </div>
                    <div className={progress.percentage >= 40 ? 'text-purple-600 font-semibold' : ''}>
                      {progress.percentage >= 40 ? '✓' : '○'} Detecting seismic clusters
                    </div>
                    <div className={progress.percentage >= 55 ? 'text-purple-600 font-semibold' : ''}>
                      {progress.percentage >= 55 ? '✓' : '○'} Analyzing aftershock sequences
                    </div>
                    <div className={progress.percentage >= 70 ? 'text-purple-600 font-semibold' : ''}>
                      {progress.percentage >= 70 ? '✓' : '○'} Calculating risk scores
                    </div>
                    <div className={progress.percentage >= 85 ? 'text-purple-600 font-semibold' : ''}>
                      {progress.percentage >= 85 ? '✓' : '○'} Running AI analysis
                    </div>
                  </div>
                </div>
              )}
              
              {progress.percentage === 0 && (
                <p className="text-sm text-gray-500 mt-4">Initializing analysis...</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {!loading && analysis && (
        <div className="space-y-4 sm:space-y-6">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Total Earthquakes</h4>
              <p className="text-2xl sm:text-3xl font-bold text-purple-600">{analysis.statistics.total_count}</p>
              <p className="text-xs text-gray-500 mt-1">Last {analysis.statistics.period_days || 90} days</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Max Magnitude</h4>
              <p className="text-2xl sm:text-3xl font-bold text-orange-600">M {analysis.statistics.max_magnitude.toFixed(1)}</p>
              <p className="text-xs text-gray-500 mt-1">Average: M {analysis.statistics.avg_magnitude.toFixed(1)}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Significant Events</h4>
              <p className="text-2xl sm:text-3xl font-bold text-red-600">{analysis.statistics.significant_count}</p>
              <p className="text-xs text-gray-500 mt-1">Magnitude ≥ 4.5</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Total Energy</h4>
              <p className="text-xl sm:text-2xl font-bold text-blue-600">
                {analysis.statistics.total_energy_joules 
                  ? (analysis.statistics.total_energy_joules >= 1e15 
                    ? `${(analysis.statistics.total_energy_joules / 1e15).toFixed(1)}×10¹⁵` 
                    : analysis.statistics.total_energy_joules >= 1e12
                    ? `${(analysis.statistics.total_energy_joules / 1e12).toFixed(1)}×10¹²`
                    : `${(analysis.statistics.total_energy_joules / 1e9).toFixed(1)}×10⁹`)
                  : 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">joules released</p>
            </div>
          </div>

          {/* Regional Breakdown - NEW */}
          {analysis.regional_breakdown && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">🗺️</span>
                Regional Breakdown
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Luzon */}
                <div className="border-l-4 border-blue-500 pl-4 bg-blue-50 rounded-r-lg p-4">
                  <h4 className="font-bold text-blue-900 mb-3 text-lg">Luzon</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Events:</span>
                      <span className="font-semibold text-gray-900">
                        {analysis.regional_breakdown.Luzon.count} ({analysis.regional_breakdown.Luzon.percentage}%)
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Magnitude:</span>
                      <span className="font-semibold text-gray-900">M {analysis.regional_breakdown.Luzon.avg_magnitude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Magnitude:</span>
                      <span className="font-semibold text-orange-600">M {analysis.regional_breakdown.Luzon.max_magnitude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Significant:</span>
                      <span className="font-semibold text-red-600">{analysis.regional_breakdown.Luzon.significant_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Depth:</span>
                      <span className="font-semibold text-gray-900">{analysis.regional_breakdown.Luzon.avg_depth} km</span>
                    </div>
                  </div>
                </div>

                {/* Visayas */}
                <div className="border-l-4 border-green-500 pl-4 bg-green-50 rounded-r-lg p-4">
                  <h4 className="font-bold text-green-900 mb-3 text-lg">Visayas</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Events:</span>
                      <span className="font-semibold text-gray-900">
                        {analysis.regional_breakdown.Visayas.count} ({analysis.regional_breakdown.Visayas.percentage}%)
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Magnitude:</span>
                      <span className="font-semibold text-gray-900">M {analysis.regional_breakdown.Visayas.avg_magnitude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Magnitude:</span>
                      <span className="font-semibold text-orange-600">M {analysis.regional_breakdown.Visayas.max_magnitude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Significant:</span>
                      <span className="font-semibold text-red-600">{analysis.regional_breakdown.Visayas.significant_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Depth:</span>
                      <span className="font-semibold text-gray-900">{analysis.regional_breakdown.Visayas.avg_depth} km</span>
                    </div>
                  </div>
                </div>

                {/* Mindanao */}
                <div className="border-l-4 border-purple-500 pl-4 bg-purple-50 rounded-r-lg p-4">
                  <h4 className="font-bold text-purple-900 mb-3 text-lg">Mindanao</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Events:</span>
                      <span className="font-semibold text-gray-900">
                        {analysis.regional_breakdown.Mindanao.count} ({analysis.regional_breakdown.Mindanao.percentage}%)
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Magnitude:</span>
                      <span className="font-semibold text-gray-900">M {analysis.regional_breakdown.Mindanao.avg_magnitude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Magnitude:</span>
                      <span className="font-semibold text-orange-600">M {analysis.regional_breakdown.Mindanao.max_magnitude}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Significant:</span>
                      <span className="font-semibold text-red-600">{analysis.regional_breakdown.Mindanao.significant_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Depth:</span>
                      <span className="font-semibold text-gray-900">{analysis.regional_breakdown.Mindanao.avg_depth} km</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Historical Comparison - NEW */}
          {analysis.historical_comparison && Object.keys(analysis.historical_comparison).length > 0 && (
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200 p-4 sm:p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">📊</span>
                Historical Comparison
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Previous Period */}
                {analysis.historical_comparison.vs_previous_period && (
                  <div className="bg-white rounded-lg p-4 border border-amber-200">
                    <h4 className="font-semibold text-gray-800 mb-3">vs Previous 90-Day Period</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Event Count Change:</span>
                        <span className={`font-bold ${
                          analysis.historical_comparison.vs_previous_period.count_change_percent > 0 
                            ? 'text-red-600' 
                            : analysis.historical_comparison.vs_previous_period.count_change_percent < 0
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }`}>
                          {analysis.historical_comparison.vs_previous_period.count_change_percent > 0 ? '+' : ''}
                          {analysis.historical_comparison.vs_previous_period.count_change_percent}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Previous Count:</span>
                        <span className="font-semibold text-gray-900">
                          {analysis.historical_comparison.vs_previous_period.previous_count}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Magnitude Change:</span>
                        <span className={`font-bold ${
                          analysis.historical_comparison.vs_previous_period.magnitude_change > 0 
                            ? 'text-red-600' 
                            : analysis.historical_comparison.vs_previous_period.magnitude_change < 0
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }`}>
                          {analysis.historical_comparison.vs_previous_period.magnitude_change > 0 ? '+' : ''}
                          {analysis.historical_comparison.vs_previous_period.magnitude_change}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Last Year */}
                {analysis.historical_comparison.vs_last_year && (
                  <div className="bg-white rounded-lg p-4 border border-amber-200">
                    <h4 className="font-semibold text-gray-800 mb-3">vs Same Period Last Year</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Event Count Change:</span>
                        <span className={`font-bold ${
                          analysis.historical_comparison.vs_last_year.count_change_percent > 0 
                            ? 'text-red-600' 
                            : analysis.historical_comparison.vs_last_year.count_change_percent < 0
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }`}>
                          {analysis.historical_comparison.vs_last_year.count_change_percent > 0 ? '+' : ''}
                          {analysis.historical_comparison.vs_last_year.count_change_percent}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Last Year Count:</span>
                        <span className="font-semibold text-gray-900">
                          {analysis.historical_comparison.vs_last_year.last_year_count}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Magnitude Change:</span>
                        <span className={`font-bold ${
                          analysis.historical_comparison.vs_last_year.magnitude_change > 0 
                            ? 'text-red-600' 
                            : analysis.historical_comparison.vs_last_year.magnitude_change < 0
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }`}>
                          {analysis.historical_comparison.vs_last_year.magnitude_change > 0 ? '+' : ''}
                          {analysis.historical_comparison.vs_last_year.magnitude_change}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Enhanced Depth Analysis - NEW */}
          {analysis.statistics.very_shallow_count !== undefined && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">⬇️</span>
                Enhanced Depth Distribution
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="text-3xl font-bold text-red-600">{analysis.statistics.very_shallow_count}</div>
                  <div className="text-xs text-gray-600 mt-1">Very Shallow</div>
                  <div className="text-xs text-gray-500">{'< 10 km'}</div>
                  <div className="text-xs text-red-600 mt-1 font-semibold">High damage risk</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="text-3xl font-bold text-orange-600">{analysis.statistics.shallow_count}</div>
                  <div className="text-xs text-gray-600 mt-1">Shallow</div>
                  <div className="text-xs text-gray-500">10-70 km</div>
                  <div className="text-xs text-orange-600 mt-1 font-semibold">Moderate risk</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="text-3xl font-bold text-yellow-600">{analysis.statistics.intermediate_count}</div>
                  <div className="text-xs text-gray-600 mt-1">Intermediate</div>
                  <div className="text-xs text-gray-500">70-300 km</div>
                  <div className="text-xs text-yellow-600 mt-1 font-semibold">Lower impact</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-3xl font-bold text-green-600">{analysis.statistics.deep_count}</div>
                  <div className="text-xs text-gray-600 mt-1">Deep</div>
                  <div className="text-xs text-gray-500">≥ 300 km</div>
                  <div className="text-xs text-green-600 mt-1 font-semibold">Minimal impact</div>
                </div>
              </div>
            </div>
          )}

          {/* PHASE 2: Risk Scores */}
          {analysis.risk_scores && (
            <div className="bg-gradient-to-r from-yellow-50 to-red-50 rounded-lg border border-yellow-200 p-4 sm:p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span className="text-xl">⚠️</span>
                Regional Risk Assessment
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(analysis.risk_scores).map(([region, risk]) => (
                  <div key={region} className={`p-4 rounded-lg border-2 ${
                    risk.color === 'red' ? 'bg-red-50 border-red-400' :
                    risk.color === 'orange' ? 'bg-orange-50 border-orange-400' :
                    risk.color === 'yellow' ? 'bg-yellow-50 border-yellow-400' :
                    'bg-green-50 border-green-400'
                  }`}>
                    <h4 className="font-bold text-gray-900 mb-2">{region}</h4>
                    <div className="flex items-baseline gap-2 mb-3">
                      <span className={`text-4xl font-bold ${
                        risk.color === 'red' ? 'text-red-600' :
                        risk.color === 'orange' ? 'text-orange-600' :
                        risk.color === 'yellow' ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>{risk.score}</span>
                      <span className="text-sm text-gray-600">/100</span>
                    </div>
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-3 ${
                      risk.color === 'red' ? 'bg-red-200 text-red-900' :
                      risk.color === 'orange' ? 'bg-orange-200 text-orange-900' :
                      risk.color === 'yellow' ? 'bg-yellow-200 text-yellow-900' :
                      'bg-green-200 text-green-900'
                    }`}>
                      {risk.level} Risk
                    </div>
                    <div className="text-xs space-y-1 text-gray-700">
                      <div>Activity: {risk.factors.activity}</div>
                      <div>Magnitude: {risk.factors.magnitude}</div>
                      <div>Significant: {risk.factors.significant_events}</div>
                      <div>Shallow: {risk.factors.shallow_depth}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PHASE 2: Clusters & Sequences */}
          {(analysis.clusters || analysis.sequences) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Clusters */}
              {analysis.clusters && analysis.clusters.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-xl">🎯</span>
                    Seismic Clusters Detected
                  </h3>
                  <div className="text-2xl font-bold text-purple-600 mb-3">{analysis.clusters.length} clusters</div>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {analysis.clusters.slice(0, 5).map((cluster, i) => (
                      <div key={i} className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                        <div className="font-semibold text-gray-900">Cluster {i + 1} - {cluster.region}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          <div>{cluster.count} events</div>
                          <div>Max: M{cluster.max_magnitude.toFixed(1)}, Avg: M{cluster.avg_magnitude.toFixed(1)}</div>
                          <div className="text-xs text-gray-500">Center: {cluster.center_lat.toFixed(2)}°N, {cluster.center_lon.toFixed(2)}°E</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sequences */}
              {analysis.sequences && analysis.sequences.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-xl">🔗</span>
                    Aftershock Sequences
                  </h3>
                  <div className="text-2xl font-bold text-indigo-600 mb-3">{analysis.sequences.length} sequences</div>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {analysis.sequences.map((seq, i) => (
                      <div key={i} className="p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                        <div className="font-semibold text-gray-900">
                          M{seq.mainshock_magnitude.toFixed(1)} Mainshock
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          <div>{seq.aftershock_count} aftershocks detected</div>
                          <div>Largest: M{seq.largest_aftershock_magnitude.toFixed(1)}</div>
                          <div className="text-xs text-gray-500">{seq.mainshock_location}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* PHASE 2: Trends & B-value */}
          {(analysis.trends || analysis.b_value !== undefined) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Trends */}
              {analysis.trends && (
                <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-xl">📈</span>
                    Temporal Trends
                  </h3>
                  <div className={`inline-block px-4 py-2 rounded-full text-lg font-bold mb-4 ${
                    analysis.trends.overall_trend === 'Increasing' ? 'bg-red-100 text-red-700' :
                    analysis.trends.overall_trend === 'Decreasing' ? 'bg-green-100 text-green-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {analysis.trends.overall_trend}
                  </div>
                  <div className="space-y-2">
                    {analysis.trends.segments.map((seg, i) => (
                      <div key={i} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm font-medium text-gray-700">{seg.period}</span>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-gray-900">{seg.count} events</div>
                          <div className="text-xs text-gray-500">M{seg.avg_magnitude.toFixed(1)} avg</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* B-value & Volcano Correlation */}
              <div className="space-y-4">
                {/* B-value */}
                {analysis.b_value !== undefined && analysis.b_value !== null && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <span className="text-xl">📊</span>
                      Gutenberg-Richter b-value
                    </h3>
                    <div className="text-center">
                      <div className="text-5xl font-bold text-indigo-600 mb-2">{analysis.b_value}</div>
                      <div className="text-sm text-gray-600">
                        {analysis.b_value > 1.0 ? 'Higher than normal - more small quakes' :
                         analysis.b_value < 0.8 ? 'Lower than normal - potential stress buildup' :
                         'Normal distribution (~1.0)'}
                      </div>
                    </div>
                  </div>
                )}

                {/* Volcano Correlation Summary */}
                {analysis.volcano_correlation && Object.keys(analysis.volcano_correlation).length > 0 && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <span className="text-xl">🌋</span>
                      Volcano Activity
                    </h3>
                    <div className="text-sm space-y-2">
                      {Object.entries(analysis.volcano_correlation).slice(0, 3).map(([volcano, data]) => (
                        <div key={volcano} className="p-2 bg-orange-50 rounded border border-orange-200">
                          <div className="font-semibold text-gray-900">{volcano}</div>
                          <div className="text-xs text-gray-600">
                            {data.earthquake_count} events nearby (Max: M{data.max_magnitude.toFixed(1)})
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* AI Analysis */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
            <div className="bg-gradient-to-r from-purple-600 to-sky-400 text-white px-6 py-4 rounded-t-lg">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Brain className="h-6 w-6" />
                AI Seismologist Analysis
              </h3>
              <p className="text-purple-100 text-sm mt-1">
                Generated using: {availableModels.find(m => m.id === analysis.metadata.model)?.name || analysis.metadata.model}
              </p>
            </div>
            <div className="p-6">
              <div className="prose prose-blue max-w-none ai-analysis-content">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm, remarkBreaks]}
                  components={{
                    // Headings with improved styling
                    h1: ({node, ...props}) => (
                      <h1 className="text-3xl font-bold text-gray-900 mt-8 mb-4 pb-2 border-b-2 border-purple-200" {...props} />
                    ),
                    h2: ({node, ...props}) => (
                      <h2 className="text-2xl font-bold text-gray-800 mt-6 mb-3 pb-1 border-b border-gray-200" {...props} />
                    ),
                    h3: ({node, ...props}) => (
                      <h3 className="text-xl font-semibold text-gray-800 mt-5 mb-2" {...props} />
                    ),
                    h4: ({node, ...props}) => (
                      <h4 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props} />
                    ),
                    h5: ({node, ...props}) => (
                      <h5 className="text-base font-semibold text-gray-700 mt-3 mb-2" {...props} />
                    ),
                    h6: ({node, ...props}) => (
                      <h6 className="text-sm font-semibold text-gray-700 mt-3 mb-2" {...props} />
                    ),
                    
                    // Paragraphs with proper spacing
                    p: ({node, ...props}) => (
                      <p className="text-gray-700 mb-4 leading-relaxed text-base" {...props} />
                    ),
                    
                    // Lists with better spacing and styling
                    ul: ({node, ...props}) => (
                      <ul className="list-disc list-outside ml-6 space-y-2 mb-4 text-gray-700" {...props} />
                    ),
                    ol: ({node, ...props}) => (
                      <ol className="list-decimal list-outside ml-6 space-y-2 mb-4 text-gray-700" {...props} />
                    ),
                    li: ({node, children, ...props}) => (
                      <li className="pl-2 leading-relaxed" {...props}>
                        <span className="inline-block">{children}</span>
                      </li>
                    ),
                    
                    // Text formatting
                    strong: ({node, ...props}) => (
                      <strong className="font-bold text-gray-900" {...props} />
                    ),
                    em: ({node, ...props}) => (
                      <em className="italic text-gray-800" {...props} />
                    ),
                    
                    // Code blocks and inline code
                    code: ({node, inline, className, children, ...props}) => {
                      const match = /language-(\w+)/.exec(className || '');
                      
                      // Check if this is truly inline code (single line, short text)
                      const codeText = String(children).trim();
                      const isReallyInline = inline !== false && !codeText.includes('\n') && codeText.length < 100;
                      
                      return isReallyInline ? (
                        <code className="bg-purple-50 text-purple-900 px-2 py-0.5 rounded text-sm font-semibold border border-purple-200" {...props}>
                          {children}
                        </code>
                      ) : (
                        <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg text-sm font-mono overflow-x-auto my-4" {...props}>
                          {children}
                        </code>
                      );
                    },
                    pre: ({node, children, ...props}) => {
                      // Check if the pre contains code that should be inline
                      const textContent = node?.children?.[0]?.children?.[0]?.value || '';
                      if (textContent && !textContent.includes('\n') && textContent.length < 100) {
                        // Render as inline code instead
                        return (
                          <code className="bg-purple-50 text-purple-900 px-2 py-0.5 rounded text-sm font-semibold border border-purple-200">
                            {textContent}
                          </code>
                        );
                      }
                      return <pre className="bg-gray-900 rounded-lg my-4 overflow-hidden" {...props}>{children}</pre>;
                    },
                    
                    // Blockquotes
                    blockquote: ({node, ...props}) => (
                      <blockquote className="border-l-4 border-purple-500 pl-4 py-2 my-4 bg-purple-50 text-gray-700 italic" {...props} />
                    ),
                    
                    // Links
                    a: ({node, ...props}) => (
                      <a className="text-purple-600 hover:text-purple-800 underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />
                    ),
                    
                    // Horizontal rules
                    hr: ({node, ...props}) => (
                      <hr className="my-6 border-t-2 border-gray-200" {...props} />
                    ),
                    
                    // Tables
                    table: ({node, ...props}) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full divide-y divide-gray-200 border border-gray-300" {...props} />
                      </div>
                    ),
                    thead: ({node, ...props}) => (
                      <thead className="bg-gray-50" {...props} />
                    ),
                    tbody: ({node, ...props}) => (
                      <tbody className="bg-white divide-y divide-gray-200" {...props} />
                    ),
                    tr: ({node, ...props}) => (
                      <tr {...props} />
                    ),
                    th: ({node, ...props}) => (
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider" {...props} />
                    ),
                    td: ({node, ...props}) => (
                      <td className="px-4 py-3 text-sm text-gray-700" {...props} />
                    ),
                  }}
                >
                  {analysis.analysis}
                </ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Notable Earthquakes */}
          {analysis.significant_earthquakes && analysis.significant_earthquakes.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Most Significant Earthquakes</h3>
              <div className="space-y-3">
                {analysis.significant_earthquakes.map((eq, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex-shrink-0">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-orange-100 text-orange-700 font-bold text-sm">
                        {index + 1}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-lg text-orange-600">M {eq.magnitude.toFixed(1)}</span>
                        <span className="text-gray-600">•</span>
                        <span className="font-semibold text-gray-900">{eq.place}</span>
                      </div>
                      <div className="text-sm text-gray-600 space-y-0.5">
                        <div>📅 {eq.time}</div>
                        <div>📍 Depth: {eq.depth.toFixed(1)} km</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-xs text-gray-600">
            <p>
              <strong>Analysis Generated:</strong> {new Date(analysis.metadata.generated).toLocaleString()} | 
              <strong className="ml-2">Data Points Analyzed:</strong> {analysis.metadata.data_points} earthquakes | 
              <strong className="ml-2">Period:</strong> {analysis.metadata.period}
            </p>
            <p className="mt-2 text-gray-500">
              ⚠️ This analysis is generated by AI and should be used as supplementary information. 
              Always refer to official sources like PHIVOLCS for authoritative earthquake information and warnings.
            </p>
          </div>
        </div>
      )}

      {/* Initial State */}
      {!loading && !analysis && !error && (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Brain className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Ready to Analyze
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Click the "Generate AI Analysis" button above to get a comprehensive 
            AI-powered assessment of recent seismic activity in the Philippines.
          </p>
        </div>
      )}
    </div>
  );
};

export default AIAnalysis;
