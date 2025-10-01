import React from 'react';
import { Mountain, MapPin, TrendingUp, AlertTriangle } from 'lucide-react';

const VolcanoList = ({ volcanoes }) => {
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

  // Sort by alert level (highest first) and then by name
  const sortedVolcanoes = [...volcanoes].sort((a, b) => {
    if (b.alert_level !== a.alert_level) {
      return b.alert_level - a.alert_level;
    }
    return a.name.localeCompare(b.name);
  });

  return (
    <div className="space-y-4">
      {/* Alert Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-purple-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-purple-900 mb-1">Volcano Alert Levels</h3>
            <p className="text-sm text-purple-800 mb-2">
              PHIVOLCS uses a 5-level alert system to indicate volcanic activity status:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
              <div><strong>Level 0:</strong> No alert (Normal)</div>
              <div><strong>Level 1:</strong> Abnormal (Increased unrest)</div>
              <div><strong>Level 2:</strong> Moderate unrest</div>
              <div><strong>Level 3:</strong> High unrest (Eruption possible)</div>
              <div><strong>Level 4-5:</strong> Eruption imminent or in progress</div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Mountain className="h-5 w-5 text-gray-600" />
            <span className="text-sm text-gray-600">Total Monitored</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{volcanoes.length}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-orange-600" />
            <span className="text-sm text-gray-600">On Alert</span>
          </div>
          <p className="text-2xl font-bold text-orange-600">
            {volcanoes.filter(v => v.alert_level > 0).length}
          </p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-sky-500" />
            <span className="text-sm text-gray-600">Normal Status</span>
          </div>
          <p className="text-2xl font-bold text-sky-500">
            {volcanoes.filter(v => v.alert_level === 0).length}
          </p>
        </div>
      </div>

      {/* Volcano Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sortedVolcanoes.map((volcano) => (
          <div
            key={volcano.id}
            className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <Mountain className="h-8 w-8 text-gray-700" />
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{volcano.name}</h3>
                  <p className="text-sm text-gray-600">{volcano.type}</p>
                </div>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-sm font-bold border ${getAlertLevelColor(
                  volcano.alert_level
                )}`}
              >
                Level {volcano.alert_level}
              </span>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex items-start gap-2 text-sm">
                <MapPin className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{volcano.location}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-600">Elevation:</span>{' '}
                  <span className="font-semibold text-gray-900">{volcano.elevation} m</span>
                </div>
                <div>
                  <span className="text-gray-600">Last Eruption:</span>{' '}
                  <span className="font-semibold text-gray-900">{volcano.last_eruption}</span>
                </div>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Coordinates:</span>{' '}
                <span className="font-mono text-gray-900">
                  {volcano.latitude.toFixed(4)}°, {volcano.longitude.toFixed(4)}°
                </span>
              </div>
            </div>

            <div className={`p-3 rounded-lg border ${getAlertLevelColor(volcano.alert_level)}`}>
              <p className="text-sm font-semibold mb-1">{volcano.status}</p>
              <p className="text-xs">{getAlertLevelDescription(volcano.alert_level)}</p>
            </div>

            <p className="text-sm text-gray-600 mt-3 italic">{volcano.description}</p>

            {volcano.alert_level > 0 && (
              <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-xs text-yellow-800">
                  ⚠️ This volcano is showing signs of unrest. Monitor official PHIVOLCS updates.
                </p>
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
