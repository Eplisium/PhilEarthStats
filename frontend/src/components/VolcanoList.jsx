import React, { useMemo, useState } from 'react';
import { Mountain, MapPin, TrendingUp, AlertTriangle, Activity, Users, Building2, Radio, ChevronDown, ChevronUp, Info, Waves, Target, Phone, Eye, Flame } from 'lucide-react';
import useCountUp from '../hooks/useCountUp';
import useDataStore from '../store/useDataStore';

const VolcanoList = () => {
  // Use Zustand store with optimized selector
  const volcanoes = useDataStore(state => state.volcanoes);
  const [expandedVolcano, setExpandedVolcano] = useState(null);
  
  // Memoize computed values
  const { onAlertCount, normalStatusCount, totalEruptions, totalAffectedPop, totalSeismicStations } = useMemo(() => {
    const onAlertCount = volcanoes.filter(v => v.alert_level > 0).length;
    const normalStatusCount = volcanoes.filter(v => v.alert_level === 0).length;
    const totalEruptions = volcanoes.reduce((sum, v) => sum + (v.eruption_history?.total_eruptions || 0), 0);
    const totalAffectedPop = volcanoes.reduce((sum, v) => sum + (v.hazards?.affected_population || 0), 0);
    const totalSeismicStations = volcanoes.reduce((sum, v) => sum + (v.monitoring?.seismic_stations || 0), 0);
    
    return { onAlertCount, normalStatusCount, totalEruptions, totalAffectedPop, totalSeismicStations };
  }, [volcanoes]);
  
  // Animated numbers for statistics
  const totalMonitored = useCountUp(volcanoes.length, 800, 0);
  const onAlert = useCountUp(onAlertCount, 800, 0);
  const normalStatus = useCountUp(normalStatusCount, 800, 0);
  const eruptionsCount = useCountUp(totalEruptions, 1000, 0);
  const affectedPopulation = useCountUp(totalAffectedPop, 1000, 0);
  const seismicStationsCount = useCountUp(totalSeismicStations, 800, 0);
  const getAlertLevelColor = (level) => {
    if (level >= 3) return 'bg-red-100 text-red-800 border-red-300';
    if (level >= 2) return 'bg-orange-100 text-orange-800 border-orange-300';
    if (level >= 1) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-green-100 text-green-800 border-green-300';
  };

  const getAlertLevelDescription = (level) => {
    switch (level) {
      case 0:
        return 'No alert - Normal condition';
      case 1:
        return 'Abnormal - Increased unrest';
      case 2:
        return 'Moderate - Increased tendency towards hazardous eruption';
      case 3:
        return 'High - Hazardous eruption possible within weeks';
      case 4:
        return 'Intense - Hazardous eruption in progress';
      case 5:
        return 'Critical - Hazardous eruption imminent or ongoing';
      default:
        return 'Unknown status';
    }
  };

  // Memoize sorted volcanoes to prevent unnecessary re-sorting
  const sortedVolcanoes = useMemo(() => {
    return [...volcanoes].sort((a, b) => {
      if (b.alert_level !== a.alert_level) {
        return b.alert_level - a.alert_level;
      }
      return a.name.localeCompare(b.name);
    });
  }, [volcanoes]);

  return (
    <div className="space-y-4">
      {/* Alert Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 sm:p-4">
        <div className="flex items-start gap-2 sm:gap-3">
          <AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5 text-purple-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm sm:text-base font-semibold text-purple-900 mb-1">Volcano Alert Levels</h3>
            <p className="text-xs sm:text-sm text-purple-800 mb-2">
              PHIVOLCS uses a 5-level alert system to indicate volcanic activity status:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 sm:gap-2 text-xs">
              <div><strong>Level 0:</strong> No alert (Normal)</div>
              <div><strong>Level 1:</strong> Abnormal (Increased unrest)</div>
              <div><strong>Level 2:</strong> Moderate unrest</div>
              <div><strong>Level 3:</strong> High unrest (Eruption possible)</div>
              <div className="sm:col-span-2"><strong>Level 4-5:</strong> Eruption imminent or in progress</div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Mountain className="h-4 w-4 sm:h-5 sm:w-5 text-gray-600" />
            <span className="text-xs sm:text-sm text-gray-600">Total Monitored</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-gray-900">{totalMonitored}</p>
          <p className="text-xs text-gray-500 mt-1">Active volcanoes</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5 text-orange-600" />
            <span className="text-xs sm:text-sm text-gray-600">On Alert</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-orange-600">
            {onAlert}
          </p>
          <p className="text-xs text-gray-500 mt-1">Alert Level &gt; 0</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg sm:col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-sky-500" />
            <span className="text-xs sm:text-sm text-gray-600">Normal Status</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-sky-500">
            {normalStatus}
          </p>
          <p className="text-xs text-gray-500 mt-1">Alert Level 0</p>
        </div>
      </div>

      {/* Additional Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Flame className="h-4 w-4 sm:h-5 sm:w-5 text-red-600" />
            <span className="text-xs sm:text-sm text-gray-600">Historical Eruptions</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-red-600">{eruptionsCount}</p>
          <p className="text-xs text-gray-500 mt-1">Total recorded</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600" />
            <span className="text-xs sm:text-sm text-gray-600">At-Risk Population</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-blue-600">{affectedPopulation.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">Within danger zones</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 transform transition-all duration-500 hover:scale-105 hover:shadow-lg sm:col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 mb-2">
            <Radio className="h-4 w-4 sm:h-5 sm:w-5 text-green-600" />
            <span className="text-xs sm:text-sm text-gray-600">Monitoring Network</span>
          </div>
          <p className="text-xl sm:text-2xl font-bold text-green-600">{seismicStationsCount}</p>
          <p className="text-xs text-gray-500 mt-1">Seismic stations</p>
        </div>
      </div>

      {/* Volcano Cards */}
      <div className="space-y-4">
        {sortedVolcanoes.map((volcano) => (
          <div
            key={volcano.id}
            className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-all duration-300"
          >
            {/* Main Card Header */}
            <div className="p-3 sm:p-5">
              <div className="flex flex-col sm:flex-row items-start sm:items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-2 sm:gap-3">
                  <Mountain className="h-6 w-6 sm:h-8 sm:w-8 text-gray-700 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900">{volcano.name}</h3>
                    <p className="text-xs sm:text-sm text-gray-600">{volcano.type}</p>
                  </div>
                </div>
                <span
                  className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-bold border self-start ${getAlertLevelColor(
                    volcano.alert_level
                  )}`}
                >
                  Level {volcano.alert_level}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-start gap-2 text-xs sm:text-sm">
                  <MapPin className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{volcano.location}</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm">
                  <div>
                    <span className="text-gray-600">Elevation:</span>{' '}
                    <span className="font-semibold text-gray-900">{volcano.elevation} m</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Last Eruption:</span>{' '}
                    <span className="font-semibold text-gray-900">{volcano.last_eruption}</span>
                  </div>
                </div>
                <div className="text-xs sm:text-sm">
                  <span className="text-gray-600">Coordinates:</span>{' '}
                  <span className="font-mono text-gray-900">
                    {volcano.latitude.toFixed(4)}°, {volcano.longitude.toFixed(4)}°
                  </span>
                </div>
              </div>

              <div className={`p-2 sm:p-3 rounded-lg border ${getAlertLevelColor(volcano.alert_level)}`}>
                <p className="text-xs sm:text-sm font-semibold mb-1">{volcano.status}</p>
                <p className="text-xs">{getAlertLevelDescription(volcano.alert_level)}</p>
              </div>

              <p className="text-xs sm:text-sm text-gray-600 mt-3 italic">{volcano.description}</p>

              {volcano.alert_level > 0 && (
                <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                  <p className="text-xs text-yellow-800">
                    ⚠️ This volcano is showing signs of unrest. Monitor official PHIVOLCS updates.
                  </p>
                </div>
              )}

              {/* Expand/Collapse Button */}
              <button
                onClick={() => setExpandedVolcano(expandedVolcano === volcano.id ? null : volcano.id)}
                className="mt-4 w-full flex items-center justify-center gap-2 px-3 sm:px-4 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-300 rounded-lg transition-colors"
              >
                <Info className="h-4 w-4" />
                <span className="text-xs sm:text-sm font-medium">
                  {expandedVolcano === volcano.id ? 'Hide' : 'Show'} Detailed Information
                </span>
                {expandedVolcano === volcano.id ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </button>
            </div>

            {/* Expanded Details Section */}
            {expandedVolcano === volcano.id && volcano.eruption_history && (
              <div className="border-t border-gray-200 bg-gray-50">
                <div className="p-5 space-y-6">
                  {/* Eruption History */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Flame className="h-5 w-5 text-orange-600" />
                      Eruption History
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-white p-3 rounded-lg border border-gray-200">
                        <p className="text-xs text-gray-600">Total Eruptions</p>
                        <p className="text-xl font-bold text-gray-900">{volcano.eruption_history.total_eruptions}</p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border border-gray-200">
                        <p className="text-xs text-gray-600">Avg. Years Between</p>
                        <p className="text-xl font-bold text-purple-600">{volcano.eruption_history.avg_years_between}</p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border border-gray-200 col-span-2">
                        <p className="text-xs text-gray-600">Activity Category</p>
                        <p className="text-lg font-bold text-orange-600">{volcano.eruption_history.frequency_category}</p>
                      </div>
                    </div>
                    <div className="mt-3 bg-white p-4 rounded-lg border border-gray-200">
                      <p className="text-xs font-semibold text-gray-700 mb-2">Most Recent Significant Eruption:</p>
                      <div className="space-y-1 text-sm">
                        <p><span className="text-gray-600">Date:</span> <span className="font-semibold">{volcano.eruption_history.most_recent_significant.date}</span></p>
                        <p><span className="text-gray-600">VEI:</span> <span className="font-semibold">{volcano.eruption_history.most_recent_significant.vei}</span></p>
                        <p><span className="text-gray-600">Description:</span> {volcano.eruption_history.most_recent_significant.description}</p>
                        <p><span className="text-gray-600">Casualties:</span> <span className="font-semibold">{volcano.eruption_history.most_recent_significant.casualties}</span></p>
                      </div>
                    </div>
                  </div>

                  {/* Hazard Information */}
                  {volcano.hazards && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Target className="h-5 w-5 text-red-600" />
                        Hazard Zones & Risks
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <p className="text-xs font-semibold text-gray-700 mb-2">Primary Hazards:</p>
                          <div className="flex flex-wrap gap-1">
                            {volcano.hazards.primary.map((hazard, idx) => (
                              <span key={idx} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded border border-red-200">
                                {hazard}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <p className="text-xs font-semibold text-gray-700 mb-2">Danger Zones:</p>
                          <div className="space-y-1 text-sm">
                            <p><span className="text-gray-600">PDZ Radius:</span> <span className="font-semibold">{volcano.hazards.pdz_radius} km</span></p>
                            <p><span className="text-gray-600">EDZ Radius:</span> <span className="font-semibold">{volcano.hazards.edz_radius} km</span></p>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 grid grid-cols-2 gap-4">
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <div className="flex items-center gap-2 mb-2">
                            <Users className="h-4 w-4 text-blue-600" />
                            <p className="text-xs font-semibold text-gray-700">Affected Population:</p>
                          </div>
                          <p className="text-2xl font-bold text-blue-600">{volcano.hazards.affected_population.toLocaleString()}</p>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <div className="flex items-center gap-2 mb-2">
                            <Building2 className="h-4 w-4 text-purple-600" />
                            <p className="text-xs font-semibold text-gray-700">Critical Infrastructure:</p>
                          </div>
                          <div className="space-y-1 text-xs">
                            {volcano.hazards.critical_infrastructure.map((item, idx) => (
                              <p key={idx} className="text-gray-700">{item}</p>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Monitoring Data */}
                  {volcano.monitoring && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Radio className="h-5 w-5 text-green-600" />
                        Real-time Monitoring
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="bg-white p-3 rounded-lg border border-gray-200">
                          <div className="flex items-center gap-2 mb-1">
                            <Activity className="h-4 w-4 text-gray-600" />
                            <p className="text-xs text-gray-600">Seismic Stations</p>
                          </div>
                          <p className="text-xl font-bold text-gray-900">{volcano.monitoring.seismic_stations}</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-gray-200">
                          <p className="text-xs text-gray-600">Earthquakes (24h)</p>
                          <p className="text-xl font-bold text-orange-600">{volcano.monitoring.recent_earthquakes_24h}</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-gray-200">
                          <p className="text-xs text-gray-600">Ground Deformation</p>
                          <p className="text-sm font-bold text-gray-900">{volcano.monitoring.ground_deformation}</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-gray-200">
                          <p className="text-xs text-gray-600">SO₂ Emission</p>
                          <p className="text-lg font-bold text-purple-600">{volcano.monitoring.so2_emission} t/day</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-gray-200 col-span-2">
                          <p className="text-xs text-gray-600">Last Observation</p>
                          <p className="text-xs font-mono text-gray-900">{new Date(volcano.monitoring.last_observation).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Practical Information */}
                  {volcano.practical_info && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Phone className="h-5 w-5 text-blue-600" />
                        Practical Information
                      </h4>
                      <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-2 text-sm">
                        <p><span className="text-gray-600">Observatory:</span> <span className="font-semibold">{volcano.practical_info.observatory}</span></p>
                        <p><span className="text-gray-600">Nearest City:</span> <span className="font-semibold">{volcano.practical_info.nearest_city}</span> ({volcano.practical_info.distance_to_city} km)</p>
                        <p><span className="text-gray-600">Evacuation Centers:</span> <span className="font-semibold">{volcano.practical_info.evacuation_centers}</span></p>
                        <p className="pt-2 border-t border-gray-200">
                          <span className="text-gray-600">Emergency Contact:</span> <span className="font-semibold text-blue-600">{volcano.practical_info.emergency_contact}</span>
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Additional Context */}
                  {volcano.additional_context && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Eye className="h-5 w-5 text-indigo-600" />
                        Additional Context
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <p className="text-xs font-semibold text-gray-700 mb-2">Geological Features:</p>
                          <div className="space-y-1 text-sm">
                            <p><span className="text-gray-600">Tectonic Setting:</span> {volcano.additional_context.tectonic_setting}</p>
                            <p><span className="text-gray-600">Crater Diameter:</span> <span className="font-semibold">{volcano.additional_context.crater_diameter} m</span></p>
                            <p><span className="text-gray-600">Morphology:</span> {volcano.classification?.morphology}</p>
                          </div>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                          <p className="text-xs font-semibold text-gray-700 mb-2">Cultural & Tourism:</p>
                          <div className="space-y-1 text-sm">
                            <p><span className="text-gray-600">Significance:</span> {volcano.additional_context.cultural_significance}</p>
                            <p><span className="text-gray-600">Tourism:</span> {volcano.additional_context.tourism_status}</p>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 bg-white p-4 rounded-lg border border-gray-200">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Notable Features:</p>
                        <div className="flex flex-wrap gap-1">
                          {volcano.additional_context.notable_features.map((feature, idx) => (
                            <span key={idx} className="px-2 py-1 bg-indigo-50 text-indigo-700 text-xs rounded border border-indigo-200">
                              {feature}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Note */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-700">
          <strong>Note:</strong> Volcano data is based on PHIVOLCS records. For the most current
          and official information, please visit{' '}
          <a
            href="https://www.phivolcs.dost.gov.ph"
            target="_blank"
            rel="noopener noreferrer"
            className="text-purple-600 hover:underline"
          >
            www.phivolcs.dost.gov.ph
          </a>
        </p>
      </div>
    </div>
  );
};

export default VolcanoList;
