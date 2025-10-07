import React, { useMemo, useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';
import { format } from 'date-fns';
import { 
  Layers, 
  Maximize, 
  RotateCcw, 
  Crosshair, 
  ZoomIn,
  Eye,
  EyeOff,
  Mountain,
  Activity
} from 'lucide-react';
import useDataStore from '../store/useDataStore';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Component to handle map controls
const MapControls = ({ 
  onZoomToExtent, 
  onResetView, 
  onLocateUser, 
  isLocating,
  onToggleFullscreen,
  isFullscreen 
}) => {
  return (
    <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
      <button
        onClick={onToggleFullscreen}
        className="bg-white p-2 rounded-lg shadow-lg hover:bg-gray-100 transition-colors"
        title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
      >
        <Maximize className="h-5 w-5 text-gray-700" />
      </button>
      <button
        onClick={onZoomToExtent}
        className="bg-white p-2 rounded-lg shadow-lg hover:bg-gray-100 transition-colors"
        title="Zoom to All Data"
      >
        <ZoomIn className="h-5 w-5 text-gray-700" />
      </button>
      <button
        onClick={onResetView}
        className="bg-white p-2 rounded-lg shadow-lg hover:bg-gray-100 transition-colors"
        title="Reset View"
      >
        <RotateCcw className="h-5 w-5 text-gray-700" />
      </button>
      <button
        onClick={onLocateUser}
        disabled={isLocating}
        className={`bg-white p-2 rounded-lg shadow-lg hover:bg-gray-100 transition-colors ${isLocating ? 'animate-pulse' : ''}`}
        title="Find My Location"
      >
        <Crosshair className={`h-5 w-5 ${isLocating ? 'text-blue-600' : 'text-gray-700'}`} />
      </button>
    </div>
  );
};

// Component to handle map view changes
const MapViewController = ({ center, zoom, flyTo }) => {
  const map = useMap();
  
  useEffect(() => {
    if (flyTo && center) {
      map.flyTo(center, zoom || 10, {
        duration: 1.5,
        easeLinearity: 0.25
      });
    }
  }, [center, zoom, flyTo, map]);
  
  return null;
};

const EarthquakeMap = ({ selectedEarthquake = null }) => {
  // Use Zustand store with optimized selectors
  const earthquakes = useDataStore(state => state.earthquakes);
  const volcanoes = useDataStore(state => state.volcanoes);
  const philippinesCenter = [12.8797, 121.7740];
  
  // Local state for map controls
  const [showEarthquakes, setShowEarthquakes] = useState(true);
  const [showVolcanoes, setShowVolcanoes] = useState(true);
  const [magnitudeFilter, setMagnitudeFilter] = useState(0);
  const [basemap, setBasemap] = useState('street');
  const [isLocating, setIsLocating] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [mapCenter, setMapCenter] = useState(philippinesCenter);
  const [mapZoom, setMapZoom] = useState(6);
  const [shouldFlyTo, setShouldFlyTo] = useState(false);
  
  const mapRef = useRef(null);
  const containerRef = useRef(null);

  // Handle selected earthquake from list
  useEffect(() => {
    if (selectedEarthquake) {
      setMapCenter([selectedEarthquake.latitude, selectedEarthquake.longitude]);
      setMapZoom(10);
      setShouldFlyTo(true);
      setTimeout(() => setShouldFlyTo(false), 100);
    }
  }, [selectedEarthquake]);

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

  // Filter earthquakes by magnitude
  const filteredEarthquakes = useMemo(() => {
    return earthquakes.filter(eq => eq.magnitude >= magnitudeFilter);
  }, [earthquakes, magnitudeFilter]);

  // Basemap tiles
  const basemapTiles = {
    street: {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    satellite: {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attribution: '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    },
    dark: {
      url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    },
    terrain: {
      url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
    }
  };

  // Zoom to show all data
  const handleZoomToExtent = () => {
    if (mapRef.current) {
      const bounds = [];
      
      if (showEarthquakes) {
        filteredEarthquakes.forEach(eq => {
          bounds.push([eq.latitude, eq.longitude]);
        });
      }
      
      if (showVolcanoes) {
        volcanoes.forEach(v => {
          bounds.push([v.latitude, v.longitude]);
        });
      }
      
      if (bounds.length > 0) {
        mapRef.current.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
      }
    }
  };

  // Reset to default view
  const handleResetView = () => {
    setMapCenter(philippinesCenter);
    setMapZoom(6);
    setShouldFlyTo(true);
    setTimeout(() => setShouldFlyTo(false), 100);
  };

  // Locate user
  const handleLocateUser = () => {
    setIsLocating(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setMapCenter([latitude, longitude]);
          setMapZoom(12);
          setShouldFlyTo(true);
          setTimeout(() => setShouldFlyTo(false), 100);
          setIsLocating(false);
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your location. Please enable location services.');
          setIsLocating(false);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
      setIsLocating(false);
    }
  };

  // Toggle fullscreen
  const handleToggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls Panel */}
      <div className="bg-white rounded-lg shadow-md p-4 space-y-4">
        {/* Layer Toggles */}
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-gray-600" />
            <span className="text-sm font-semibold text-gray-700">Layers:</span>
          </div>
          <button
            onClick={() => setShowEarthquakes(!showEarthquakes)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              showEarthquakes
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {showEarthquakes ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
            <Activity className="h-4 w-4" />
            Earthquakes
          </button>
          <button
            onClick={() => setShowVolcanoes(!showVolcanoes)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              showVolcanoes
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {showVolcanoes ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
            <Mountain className="h-4 w-4" />
            Volcanoes
          </button>
        </div>

        {/* Magnitude Filter */}
        {showEarthquakes && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-gray-700">
                Magnitude Filter: ≥ {magnitudeFilter.toFixed(1)}
              </label>
              <span className="text-xs text-gray-500">
                {filteredEarthquakes.length} of {earthquakes.length} shown
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="8"
              step="0.5"
              value={magnitudeFilter}
              onChange={(e) => setMagnitudeFilter(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>All (0.0+)</span>
              <span>Minor (3.0+)</span>
              <span>Moderate (5.0+)</span>
              <span>Major (7.0+)</span>
            </div>
          </div>
        )}

        {/* Basemap Selector */}
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-sm font-semibold text-gray-700">Map Style:</span>
          {Object.keys(basemapTiles).map((key) => (
            <button
              key={key}
              onClick={() => setBasemap(key)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize ${
                basemap === key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {key}
            </button>
          ))}
        </div>
      </div>

      {/* Map Container */}
      <div 
        ref={containerRef}
        className={`rounded-lg overflow-hidden ${
          isFullscreen 
            ? 'fixed inset-0 z-[9999] rounded-none' 
            : 'h-[400px] sm:h-[500px] lg:h-[600px]'
        }`}
      >
        <MapContainer
          center={philippinesCenter}
          zoom={6}
          style={{ height: '100%', width: '100%' }}
          ref={mapRef}
        >
          <MapViewController center={mapCenter} zoom={mapZoom} flyTo={shouldFlyTo} />
          
          <TileLayer
            attribution={basemapTiles[basemap].attribution}
            url={basemapTiles[basemap].url}
          />

          <MapControls
            onZoomToExtent={handleZoomToExtent}
            onResetView={handleResetView}
            onLocateUser={handleLocateUser}
            isLocating={isLocating}
            onToggleFullscreen={handleToggleFullscreen}
            isFullscreen={isFullscreen}
          />

          {/* Earthquake markers with clustering */}
          {showEarthquakes && (
            <MarkerClusterGroup
              chunkedLoading
              maxClusterRadius={50}
              spiderfyOnMaxZoom={true}
              showCoverageOnHover={false}
              zoomToBoundsOnClick={true}
              iconCreateFunction={(cluster) => {
                const count = cluster.getChildCount();
                let size = 'small';
                let color = 'bg-blue-500';
                
                if (count > 50) {
                  size = 'large';
                  color = 'bg-red-500';
                } else if (count > 20) {
                  size = 'medium';
                  color = 'bg-orange-500';
                }
                
                const sizeClass = size === 'large' ? 'h-12 w-12' : size === 'medium' ? 'h-10 w-10' : 'h-8 w-8';
                
                return L.divIcon({
                  html: `<div class="${sizeClass} ${color} rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg border-2 border-white">${count}</div>`,
                  className: 'custom-cluster-icon',
                  iconSize: L.point(40, 40, true)
                });
              }}
            >
              {filteredEarthquakes.map((earthquake) => (
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
            </MarkerClusterGroup>
          )}

          {/* Volcano markers */}
          {showVolcanoes && volcanoes.map((volcano) => (
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
      </div>

      {/* Legend */}
      <div className="mt-3 sm:mt-4 bg-white p-3 sm:p-4 rounded-lg border-2 border-gray-300 shadow-sm">
        <h4 className="text-sm sm:text-base font-semibold mb-2">Legend</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <div>
            <p className="text-xs sm:text-sm font-semibold mb-2 sm:mb-3 text-gray-700">Earthquake Magnitude:</p>
            <div className="space-y-1 sm:space-y-2 text-xs">
              <div className="flex items-center">
                <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full mr-2 border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#dc2626' }}></div>
                <span className="font-medium">M ≥ 7.0 (Major)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full mr-2 border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#ea580c' }}></div>
                <span>M 6.0-6.9 (Strong)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full mr-2 border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#eab308' }}></div>
                <span>M 5.0-5.9 (Moderate)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full mr-2 border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#3b82f6' }}></div>
                <span>M 4.0-4.9 (Light)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 sm:w-4 sm:h-4 rounded-full mr-2 border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#10b981' }}></div>
                <span>M 3.0-3.9 (Minor)</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-xs sm:text-sm font-semibold mb-2 sm:mb-3 text-gray-700">Markers:</p>
            <div className="space-y-1 text-xs">
              <div className="flex items-center">
                <div className="w-5 h-5 sm:w-6 sm:h-6 mr-2 flex-shrink-0">🔴</div>
                <span>Earthquake Epicenter</span>
              </div>
              <div className="flex items-center">
                <div className="w-5 h-5 sm:w-6 sm:h-6 mr-2 flex-shrink-0">🌋</div>
                <span>Active Volcano</span>
              </div>
              <div className="flex items-center">
                <div className="w-5 h-5 sm:w-6 sm:h-6 bg-blue-500 rounded-full text-white font-bold flex items-center justify-center mr-2 flex-shrink-0 text-xs">5</div>
                <span>Clustered Events</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EarthquakeMap;
