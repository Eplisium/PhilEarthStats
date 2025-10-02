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
              Get comprehensive insights from an AI seismologist analyzing the last 30 days of earthquake data 
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
                30-day comprehensive analysis
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

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg border border-gray-200 p-12">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Loader className="h-12 w-12 text-purple-600 animate-spin" />
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">Analyzing Earthquake Data</h3>
              <p className="text-gray-600 mt-2">The AI is processing 30 days of seismic data...</p>
              <p className="text-sm text-gray-500 mt-1">This may take 10-30 seconds</p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {!loading && analysis && (
        <div className="space-y-4 sm:space-y-6">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Total Earthquakes</h4>
              <p className="text-2xl sm:text-3xl font-bold text-purple-600">{analysis.statistics.total_count}</p>
              <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Max Magnitude</h4>
              <p className="text-2xl sm:text-3xl font-bold text-orange-600">M {analysis.statistics.max_magnitude.toFixed(1)}</p>
              <p className="text-xs text-gray-500 mt-1">Average: M {analysis.statistics.avg_magnitude.toFixed(1)}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4 sm:col-span-2 lg:col-span-1">
              <h4 className="text-xs sm:text-sm font-semibold text-gray-600 mb-2">Significant Events</h4>
              <p className="text-2xl sm:text-3xl font-bold text-red-600">{analysis.statistics.significant_count}</p>
              <p className="text-xs text-gray-500 mt-1">Magnitude ≥ 4.5</p>
            </div>
          </div>

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
