import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import { format } from 'date-fns';
import useDataStore from '../store/useDataStore';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const EarthquakeMap = () => {
  // Use Zustand store with optimized selectors
  const earthquakes = useDataStore(state => state.earthquakes);
  const volcanoes = useDataStore(state => state.volcanoes);
  const philippinesCenter = [12.8797, 121.7740];

  const getMagnitudeColor = (magnitude) => {
    if (magnitude >= 7) return '#dc2626'; // Red for major
    if (magnitude >= 6) return '#ea580c'; // Orange for strong
    if (magnitude >= 5) return '#eab308'; // Yellow for moderate
    if (magnitude >= 4) return '#3b82f6'; // Blue for light
    if (magnitude >= 3) return '#10b981'; // Green for minor
    return '#6b7280'; // Gray for micro
  };

  const getMagnitudeRadius = (magnitude) => {
    return Math.pow(10, magnitude) * 100;
  };

  // Create custom volcano icon
  const volcanoIcon = new L.Icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="red" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10 2 8 8H3l7 12 4-20z"></path>
        <path d="m14 14 4-8 3 4"></path>
      </svg>
    `),
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });

  return (
    <div className="h-[600px] rounded-lg overflow-hidden">
      <MapContainer
        center={philippinesCenter}
        zoom={6}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Earthquake markers */}
        {earthquakes.map((earthquake) => (
          <React.Fragment key={earthquake.id}>
            <Circle
              center={[earthquake.latitude, earthquake.longitude]}
              radius={getMagnitudeRadius(earthquake.magnitude)}
              pathOptions={{
                color: getMagnitudeColor(earthquake.magnitude),
                fillColor: getMagnitudeColor(earthquake.magnitude),
                fillOpacity: 0.15,
                weight: 2.5,
                opacity: 0.8
              }}
            />
            <Marker
              position={[earthquake.latitude, earthquake.longitude]}
            >
              <Popup>
                <div className="p-2 min-w-[200px]">
                  <h3 className="font-bold text-lg mb-2">
                    M {earthquake.magnitude.toFixed(1)} Earthquake
                  </h3>
                  <div className="space-y-1 text-sm">
                    <p><strong>Location:</strong> {earthquake.place}</p>
                    <p><strong>Time:</strong> {format(new Date(earthquake.time), 'PPpp')}</p>
                    <p><strong>Depth:</strong> {earthquake.depth.toFixed(1)} km</p>
                    <p><strong>Coordinates:</strong> {earthquake.latitude.toFixed(3)}°, {earthquake.longitude.toFixed(3)}°</p>
                    {earthquake.significance && (
                      <p><strong>Significance:</strong> {earthquake.significance}</p>
                    )}
                    {earthquake.tsunami && (
                      <p className="text-red-600 font-semibold">⚠️ Tsunami Warning</p>
                    )}
                    {earthquake.url && (
                      <a
                        href={earthquake.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 font-medium block mt-2"
                      >
                        More Details →
                      </a>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        ))}

        {/* Volcano markers */}
        {volcanoes.map((volcano) => (
          <Marker
            key={volcano.id}
            position={[volcano.latitude, volcano.longitude]}
            icon={volcanoIcon}
          >
            <Popup>
              <div className="p-2 min-w-[200px]">
                <h3 className="font-bold text-lg mb-2">{volcano.name}</h3>
                <div className="space-y-1 text-sm">
                  <p><strong>Location:</strong> {volcano.location}</p>
                  <p><strong>Type:</strong> {volcano.type}</p>
                  <p><strong>Elevation:</strong> {volcano.elevation} m</p>
                  <p><strong>Status:</strong> {volcano.status}</p>
                  <p>
                    <strong>Alert Level:</strong>{' '}
                    <span className={`font-semibold ${volcano.alert_level > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                      {volcano.alert_level}
                    </span>
                  </p>
                  <p><strong>Last Eruption:</strong> {volcano.last_eruption}</p>
                  <p className="text-gray-600 mt-2 italic">{volcano.description}</p>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="mt-4 bg-white p-4 rounded-lg border-2 border-gray-300 shadow-sm">
        <h4 className="font-semibold mb-2">Legend</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-semibold mb-3 text-gray-700">Earthquake Magnitude:</p>
            <div className="space-y-2 text-xs">
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full mr-2 border border-gray-300" style={{ backgroundColor: '#dc2626' }}></div>
                <span className="font-medium">M ≥ 7.0 (Major)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full mr-2 border border-gray-300" style={{ backgroundColor: '#ea580c' }}></div>
                <span>M 6.0-6.9 (Strong)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full mr-2 border border-gray-300" style={{ backgroundColor: '#eab308' }}></div>
                <span>M 5.0-5.9 (Moderate)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full mr-2 border border-gray-300" style={{ backgroundColor: '#3b82f6' }}></div>
                <span>M 4.0-4.9 (Light)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full mr-2 border border-gray-300" style={{ backgroundColor: '#10b981' }}></div>
                <span>M 3.0-3.9 (Minor)</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-sm font-semibold mb-3 text-gray-700">Markers:</p>
            <div className="space-y-1 text-xs">
              <div className="flex items-center">
                <div className="w-6 h-6 mr-2">🔴</div>
                <span>Earthquake Epicenter</span>
              </div>
              <div className="flex items-center">
                <div className="w-6 h-6 mr-2">🌋</div>
                <span>Active Volcano</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EarthquakeMap;
