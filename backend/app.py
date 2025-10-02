from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from functools import lru_cache
import time
import pytz
import os
from dotenv import load_dotenv
from database import db, DatabaseService, EarthquakeEvent, YearStatistics

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///earthquakes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
DatabaseService.initialize_database(app)

# API Endpoints
USGS_API = "https://earthquake.usgs.gov/fdsnws/event/1/query"
USGS_GEOJSON_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
PHIVOLCS_API = "https://earthquake.phivolcs.dost.gov.ph/"

# Philippines bounds
PHILIPPINES_BOUNDS = {
    'minlatitude': 4.5,
    'maxlatitude': 21.5,
    'minlongitude': 116.0,
    'maxlongitude': 127.0
}

# Cache timeout (5 minutes)
CACHE_TIMEOUT = 300
last_fetch_time = {}
cache_data = {}

def is_cache_valid(cache_key):
    """Check if cache is still valid"""
    if cache_key not in last_fetch_time:
        return False
    return (time.time() - last_fetch_time[cache_key]) < CACHE_TIMEOUT

def get_cached_or_fetch(cache_key, fetch_function):
    """Get data from cache or fetch if expired"""
    if is_cache_valid(cache_key) and cache_key in cache_data:
        return cache_data[cache_key]
    
    data = fetch_function()
    cache_data[cache_key] = data
    last_fetch_time[cache_key] = time.time()
    return data

@app.route('/api/earthquakes/all', methods=['GET'])
def get_all_earthquakes():
    """Get ALL earthquakes in the Philippines including aftershocks (no minimum magnitude)"""
    try:
        def fetch_all_earthquakes():
            # Get ALL earthquakes from the last 7 days in Philippines region
            params = {
                'format': 'geojson',
                'starttime': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'endtime': datetime.utcnow().strftime('%Y-%m-%d'),
                **PHILIPPINES_BOUNDS,
                'orderby': 'time',
                'minmagnitude': 0  # Include all magnitudes, even tiny aftershocks
            }
            
            response = requests.get(USGS_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process and enrich the data
            earthquakes = []
            for feature in data['features']:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                earthquakes.append({
                    'id': feature['id'],
                    'magnitude': props.get('mag'),
                    'place': props.get('place'),
                    'time': props.get('time'),
                    'updated': props.get('updated'),
                    'timezone': props.get('tz'),
                    'url': props.get('url'),
                    'detail': props.get('detail'),
                    'felt': props.get('felt'),
                    'alert': props.get('alert'),
                    'status': props.get('status'),
                    'tsunami': props.get('tsunami'),
                    'significance': props.get('sig'),
                    'type': props.get('type'),
                    'title': props.get('title'),
                    'longitude': coords[0],
                    'latitude': coords[1],
                    'depth': coords[2]
                })
            
            # Store earthquakes in database for historical tracking
            DatabaseService.store_multiple_earthquakes(earthquakes)
            
            return {
                'success': True,
                'count': len(earthquakes),
                'earthquakes': earthquakes,
                'metadata': {
                    'generated': int(time.time() * 1000),
                    'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                    'title': 'All Philippines Earthquakes Including Aftershocks (7 days)',
                    'source': 'USGS Earthquake Catalog'
                }
            }
        
        result = get_cached_or_fetch('all_earthquakes', fetch_all_earthquakes)
        return jsonify(result)
    
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch earthquake data: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@app.route('/api/earthquakes/recent', methods=['GET'])
def get_recent_earthquakes():
    """Get recent earthquakes in the Philippines from USGS (magnitude >= 2.5)"""
    try:
        def fetch_earthquakes():
            # Get earthquakes from the last 7 days in Philippines region
            params = {
                'format': 'geojson',
                'starttime': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'endtime': datetime.utcnow().strftime('%Y-%m-%d'),
                **PHILIPPINES_BOUNDS,
                'orderby': 'time',
                'minmagnitude': 2.5  # Filter out very small tremors for this endpoint
            }
            
            response = requests.get(USGS_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process and enrich the data
            earthquakes = []
            for feature in data['features']:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                earthquakes.append({
                    'id': feature['id'],
                    'magnitude': props.get('mag'),
                    'place': props.get('place'),
                    'time': props.get('time'),
                    'updated': props.get('updated'),
                    'timezone': props.get('tz'),
                    'url': props.get('url'),
                    'detail': props.get('detail'),
                    'felt': props.get('felt'),
                    'alert': props.get('alert'),
                    'status': props.get('status'),
                    'tsunami': props.get('tsunami'),
                    'significance': props.get('sig'),
                    'type': props.get('type'),
                    'title': props.get('title'),
                    'longitude': coords[0],
                    'latitude': coords[1],
                    'depth': coords[2]
                })
            
            # Store earthquakes in database for historical tracking
            DatabaseService.store_multiple_earthquakes(earthquakes)
            
            return {
                'success': True,
                'count': len(earthquakes),
                'earthquakes': earthquakes,
                'metadata': {
                    'generated': int(time.time() * 1000),
                    'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                    'title': 'Recent Philippines Earthquakes (7 days, M ≥ 2.5)',
                    'source': 'USGS Earthquake Catalog'
                }
            }
        
        result = get_cached_or_fetch('recent_earthquakes', fetch_earthquakes)
        return jsonify(result)
    
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch earthquake data: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500

@app.route('/api/earthquakes/significant', methods=['GET'])
def get_significant_earthquakes():
    """Get significant earthquakes (magnitude >= 4.5) in the Philippines"""
    try:
        def fetch_significant():
            params = {
                'format': 'geojson',
                'starttime': (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'endtime': datetime.utcnow().strftime('%Y-%m-%d'),
                'minmagnitude': 4.5,
                **PHILIPPINES_BOUNDS,
                'orderby': 'magnitude'
            }
            
            response = requests.get(USGS_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            earthquakes = []
            for feature in data['features']:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                earthquakes.append({
                    'id': feature['id'],
                    'magnitude': props.get('mag'),
                    'place': props.get('place'),
                    'time': props.get('time'),
                    'url': props.get('url'),
                    'alert': props.get('alert'),
                    'tsunami': props.get('tsunami'),
                    'significance': props.get('sig'),
                    'title': props.get('title'),
                    'longitude': coords[0],
                    'latitude': coords[1],
                    'depth': coords[2]
                })
            
            return {
                'success': True,
                'count': len(earthquakes),
                'earthquakes': earthquakes,
                'metadata': {
                    'generated': int(time.time() * 1000),
                    'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                    'title': 'Significant Philippines Earthquakes (30 days, M ≥ 4.5)',
                    'source': 'USGS Earthquake Catalog'
                }
            }
        
        result = get_cached_or_fetch('significant_earthquakes', fetch_significant)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch significant earthquakes: {str(e)}'
        }), 500

@app.route('/api/earthquakes/statistics', methods=['GET'])
def get_earthquake_statistics():
    """Get earthquake statistics for the Philippines"""
    try:
        def fetch_statistics():
            # Get all earthquakes from the last 30 days
            params = {
                'format': 'geojson',
                'starttime': (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'endtime': datetime.utcnow().strftime('%Y-%m-%d'),
                **PHILIPPINES_BOUNDS
            }
            
            response = requests.get(USGS_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Calculate statistics
            magnitudes = [f['properties']['mag'] for f in data['features'] if f['properties'].get('mag')]
            depths = [f['geometry']['coordinates'][2] for f in data['features']]
            
            # Count by magnitude ranges
            magnitude_ranges = {
                'micro': sum(1 for m in magnitudes if m < 3.0),
                'minor': sum(1 for m in magnitudes if 3.0 <= m < 4.0),
                'light': sum(1 for m in magnitudes if 4.0 <= m < 5.0),
                'moderate': sum(1 for m in magnitudes if 5.0 <= m < 6.0),
                'strong': sum(1 for m in magnitudes if 6.0 <= m < 7.0),
                'major': sum(1 for m in magnitudes if 7.0 <= m < 8.0),
                'great': sum(1 for m in magnitudes if m >= 8.0)
            }
            
            # Depth distribution
            depth_ranges = {
                'shallow': sum(1 for d in depths if d < 70),
                'intermediate': sum(1 for d in depths if 70 <= d < 300),
                'deep': sum(1 for d in depths if d >= 300)
            }
            
            return {
                'success': True,
                'period': '30 days',
                'total_earthquakes': len(data['features']),
                'magnitude_stats': {
                    'max': max(magnitudes) if magnitudes else 0,
                    'min': min(magnitudes) if magnitudes else 0,
                    'average': sum(magnitudes) / len(magnitudes) if magnitudes else 0,
                    'distribution': magnitude_ranges
                },
                'depth_stats': {
                    'max': max(depths) if depths else 0,
                    'min': min(depths) if depths else 0,
                    'average': sum(depths) / len(depths) if depths else 0,
                    'distribution': depth_ranges
                },
                'metadata': {
                    'generated': int(time.time() * 1000),
                    'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                    'source': 'USGS Earthquake Catalog'
                }
            }
        
        result = get_cached_or_fetch('earthquake_statistics', fetch_statistics)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch statistics: {str(e)}'
        }), 500

@app.route('/api/volcanoes/active', methods=['GET'])
def get_active_volcanoes():
    """Get comprehensive information about active volcanoes in the Philippines"""
    # Note: This data is relatively static and based on PHIVOLCS records
    # In a production system, this should be fetched from an official API
    active_volcanoes = [
        {
            'id': 1,
            'name': 'Mayon',
            'location': 'Albay, Bicol Region',
            'latitude': 13.2572,
            'longitude': 123.6856,
            'elevation': 2463,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '2018',
            'alert_level': 0,
            'description': 'Most active volcano in the Philippines, known for its perfect cone shape',
            'eruption_history': {
                'total_eruptions': 51,
                'most_recent_significant': {
                    'date': '2018-01-13',
                    'vei': 2,
                    'description': 'Phreatic eruption with lava fountaining',
                    'casualties': 0
                },
                'avg_years_between': 8,
                'frequency_category': 'Very Active'
            },
            'hazards': {
                'primary': ['Lava flows', 'Pyroclastic flows', 'Lahars', 'Ashfall', 'Rockfalls'],
                'pdz_radius': 6.0,
                'edz_radius': 8.0,
                'affected_population': 50000,
                'critical_infrastructure': ['Schools: 45', 'Hospitals: 3', 'Evacuation centers: 25']
            },
            'monitoring': {
                'seismic_stations': 8,
                'recent_earthquakes_24h': 3,
                'ground_deformation': 'Stable',
                'so2_emission': 250,
                'last_observation': datetime.utcnow().isoformat() + 'Z'
            },
            'classification': {
                'activity': 'Active',
                'eruption_category': 'Historical Record',
                'morphology': 'Young, well-preserved cone'
            },
            'practical_info': {
                'observatory': 'Lignon Hill Observatory',
                'nearest_city': 'Legazpi City',
                'distance_to_city': 15,
                'evacuation_centers': 25,
                'emergency_contact': 'PHIVOLCS Lignon Hill: (052) 820-1981'
            },
            'additional_context': {
                'tectonic_setting': 'Philippine Trench subduction zone',
                'crater_diameter': 200,
                'notable_features': ['Perfect cone shape', 'Frequent lava flows'],
                'cultural_significance': 'Named after Daragang Magayon (Beautiful Maiden)',
                'tourism_status': 'Major tourist attraction'
            }
        },
        {
            'id': 2,
            'name': 'Taal',
            'location': 'Batangas, CALABARZON',
            'latitude': 14.0021,
            'longitude': 120.9937,
            'elevation': 311,
            'type': 'Complex volcano',
            'status': 'Alert Level 1 (Abnormal)',
            'last_eruption': '2022',
            'alert_level': 1,
            'description': 'One of the most active volcanoes, located on an island within a lake',
            'eruption_history': {
                'total_eruptions': 34,
                'most_recent_significant': {
                    'date': '2020-01-12',
                    'vei': 4,
                    'description': 'Phreatomagmatic eruption with ash column',
                    'casualties': 39
                },
                'avg_years_between': 15,
                'frequency_category': 'Very Active'
            },
            'hazards': {
                'primary': ['Base surges', 'Ashfall', 'Volcanic tsunamis', 'Ballistic projectiles'],
                'pdz_radius': 7.0,
                'edz_radius': 14.0,
                'affected_population': 450000,
                'critical_infrastructure': ['Schools: 120', 'Hospitals: 8', 'Evacuation centers: 85']
            },
            'monitoring': {
                'seismic_stations': 10,
                'recent_earthquakes_24h': 12,
                'ground_deformation': 'Slight inflation',
                'so2_emission': 1200,
                'last_observation': datetime.utcnow().isoformat() + 'Z'
            },
            'classification': {
                'activity': 'Active',
                'eruption_category': 'Historical Record',
                'morphology': 'Complex caldera system'
            },
            'practical_info': {
                'observatory': 'Taal Volcano Observatory',
                'nearest_city': 'Tagaytay City',
                'distance_to_city': 25,
                'evacuation_centers': 85,
                'emergency_contact': 'PHIVOLCS Tagaytay: (046) 413-1145'
            },
            'additional_context': {
                'tectonic_setting': 'Manila Trench subduction zone',
                'crater_diameter': 2500,
                'notable_features': ['Crater lake', 'Island within a lake within an island'],
                'cultural_significance': 'One of the Decade Volcanoes',
                'tourism_status': 'Major tourist destination'
            }
        },
        {
            'id': 3,
            'name': 'Pinatubo',
            'location': 'Zambales/Pampanga/Tarlac',
            'latitude': 15.1300,
            'longitude': 120.3500,
            'elevation': 1486,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '1993',
            'alert_level': 0,
            'description': 'Famous for its catastrophic 1991 eruption, one of the largest of the 20th century',
            'eruption_history': {
                'total_eruptions': 6,
                'most_recent_significant': {
                    'date': '1991-06-15',
                    'vei': 6,
                    'description': 'Cataclysmic Plinian eruption with global climate impact',
                    'casualties': 847
                },
                'avg_years_between': 500,
                'frequency_category': 'Moderately Active'
            },
            'hazards': {
                'primary': ['Lahars', 'Pyroclastic flows', 'Ashfall', 'Volcanic gases'],
                'pdz_radius': 10.0,
                'edz_radius': 20.0,
                'affected_population': 200000,
                'critical_infrastructure': ['Schools: 75', 'Hospitals: 5', 'Evacuation centers: 50']
            },
            'monitoring': {
                'seismic_stations': 6,
                'recent_earthquakes_24h': 1,
                'ground_deformation': 'Stable',
                'so2_emission': 180,
                'last_observation': datetime.utcnow().isoformat() + 'Z'
            },
            'classification': {
                'activity': 'Active',
                'eruption_category': 'Historical Record',
                'morphology': 'Caldera with crater lake'
            },
            'practical_info': {
                'observatory': 'Clark Observatory',
                'nearest_city': 'Angeles City',
                'distance_to_city': 28,
                'evacuation_centers': 50,
                'emergency_contact': 'PHIVOLCS Clark: (045) 599-1031'
            },
            'additional_context': {
                'tectonic_setting': 'Manila Trench subduction zone',
                'crater_diameter': 2500,
                'notable_features': ['Crater lake formed post-1991', 'Massive lahar deposits'],
                'cultural_significance': 'Second-largest volcanic eruption of 20th century',
                'tourism_status': 'Eco-tourism and trekking destination'
            }
        },
        {
            'id': 4,
            'name': 'Bulusan',
            'location': 'Sorsogon, Bicol Region',
            'latitude': 12.7700,
            'longitude': 124.0500,
            'elevation': 1565,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '2017',
            'alert_level': 0,
            'description': 'Active volcano in southeastern Luzon with frequent phreatic eruptions',
            'eruption_history': {
                'total_eruptions': 17,
                'most_recent_significant': {
                    'date': '2016-06-10',
                    'vei': 2,
                    'description': 'Phreatic eruption with ash plume',
                    'casualties': 0
                },
                'avg_years_between': 12,
                'frequency_category': 'Active'
            },
            'hazards': {
                'primary': ['Phreatic eruptions', 'Ashfall', 'Lahars', 'Pyroclastic flows'],
                'pdz_radius': 4.0,
                'edz_radius': 6.0,
                'affected_population': 25000,
                'critical_infrastructure': ['Schools: 30', 'Hospitals: 2', 'Evacuation centers: 18']
            },
            'monitoring': {
                'seismic_stations': 5,
                'recent_earthquakes_24h': 4,
                'ground_deformation': 'Stable',
                'so2_emission': 320,
                'last_observation': datetime.utcnow().isoformat() + 'Z'
            },
            'classification': {
                'activity': 'Active',
                'eruption_category': 'Historical Record',
                'morphology': 'Young stratovolcano'
            },
            'practical_info': {
                'observatory': 'Bulusan Volcano Observatory',
                'nearest_city': 'Sorsogon City',
                'distance_to_city': 20,
                'evacuation_centers': 18,
                'emergency_contact': 'PHIVOLCS Bulusan: (056) 211-1134'
            },
            'additional_context': {
                'tectonic_setting': 'Philippine Trench subduction zone',
                'crater_diameter': 300,
                'notable_features': ['Four craters', 'Crater lakes', 'Hot springs'],
                'cultural_significance': 'Local pilgrimage site',
                'tourism_status': 'Eco-tourism destination'
            }
        },
        {
            'id': 5,
            'name': 'Kanlaon',
            'location': 'Negros Oriental/Occidental',
            'latitude': 10.4120,
            'longitude': 123.1320,
            'elevation': 2465,
            'type': 'Stratovolcano',
            'status': 'Alert Level 1 (Abnormal)',
            'last_eruption': '2020',
            'alert_level': 1,
            'description': 'Most active volcano in central Philippines with frequent activity',
            'eruption_history': {
                'total_eruptions': 30,
                'most_recent_significant': {
                    'date': '2017-06-18',
                    'vei': 2,
                    'description': 'Phreatic eruption with ash emission',
                    'casualties': 0
                },
                'avg_years_between': 10,
                'frequency_category': 'Very Active'
            },
            'hazards': {
                'primary': ['Pyroclastic flows', 'Ashfall', 'Lava flows', 'Lahars'],
                'pdz_radius': 4.0,
                'edz_radius': 6.0,
                'affected_population': 35000,
                'critical_infrastructure': ['Schools: 40', 'Hospitals: 3', 'Evacuation centers: 22']
            },
            'monitoring': {
                'seismic_stations': 7,
                'recent_earthquakes_24h': 8,
                'ground_deformation': 'Slight inflation',
                'so2_emission': 890,
                'last_observation': datetime.utcnow().isoformat() + 'Z'
            },
            'classification': {
                'activity': 'Active',
                'eruption_category': 'Historical Record',
                'morphology': 'Young stratovolcano'
            },
            'practical_info': {
                'observatory': 'Kanlaon Observatory',
                'nearest_city': 'Bacolod City',
                'distance_to_city': 30,
                'evacuation_centers': 22,
                'emergency_contact': 'PHIVOLCS Kanlaon: (034) 476-5248'
            },
            'additional_context': {
                'tectonic_setting': 'Negros Trench subduction zone',
                'crater_diameter': 400,
                'notable_features': ['Active crater', 'Fumaroles', 'Sulfur deposits'],
                'cultural_significance': 'Named after Kan, deity of pre-colonial Negrenses',
                'tourism_status': 'Popular hiking destination'
            }
        },
        {
            'id': 6,
            'name': 'Hibok-Hibok',
            'location': 'Camiguin, Northern Mindanao',
            'latitude': 9.2030,
            'longitude': 124.6730,
            'elevation': 1332,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '1953',
            'alert_level': 0,
            'description': 'Lava dome complex with a history of explosive eruptions',
            'eruption_history': {
                'total_eruptions': 5,
                'most_recent_significant': {
                    'date': '1951-12-04',
                    'vei': 3,
                    'description': 'Explosive eruption with pyroclastic flows',
                    'casualties': 500
                },
                'avg_years_between': 100,
                'frequency_category': 'Moderately Active'
            },
            'hazards': {
                'primary': ['Pyroclastic flows', 'Dome collapse', 'Ashfall', 'Lahars'],
                'pdz_radius': 4.0,
                'edz_radius': 7.0,
                'affected_population': 18000,
                'critical_infrastructure': ['Schools: 20', 'Hospitals: 2', 'Evacuation centers: 12']
            },
            'monitoring': {
                'seismic_stations': 4,
                'recent_earthquakes_24h': 2,
                'ground_deformation': 'Stable',
                'so2_emission': 95,
                'last_observation': datetime.utcnow().isoformat() + 'Z'
            },
            'classification': {
                'activity': 'Active',
                'eruption_category': 'Historical Record',
                'morphology': 'Lava dome complex'
            },
            'practical_info': {
                'observatory': 'Camiguin Volcano Observatory',
                'nearest_city': 'Mambajao',
                'distance_to_city': 8,
                'evacuation_centers': 12,
                'emergency_contact': 'PHIVOLCS Camiguin: (088) 387-9042'
            },
            'additional_context': {
                'tectonic_setting': 'Philippine Trench subduction zone',
                'crater_diameter': 320,
                'notable_features': ['Five lava domes', 'Hot springs', 'Fumaroles'],
                'cultural_significance': 'Part of Camiguin volcanic field',
                'tourism_status': 'Island tourist destination with hot springs'
            }
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(active_volcanoes),
        'volcanoes': active_volcanoes,
        'metadata': {
            'generated': int(time.time() * 1000),
            'server_time_utc': datetime.utcnow().isoformat() + 'Z',
            'title': 'Active Volcanoes in the Philippines - Comprehensive Data',
            'source': 'PHIVOLCS Records',
            'note': 'Alert levels and status should be verified with official PHIVOLCS sources',
            'data_fields': [
                'Basic Info', 'Eruption History', 'Hazard Zones', 'Monitoring Data',
                'Classification', 'Practical Information', 'Additional Context'
            ]
        }
    })

@app.route('/api/volcanoes/statistics', methods=['GET'])
def get_volcano_statistics():
    """Get comprehensive statistics about all monitored volcanoes"""
    # Get volcano data from the active volcanoes endpoint logic
    volcanoes_data = get_active_volcanoes().get_json()
    
    if not volcanoes_data or not volcanoes_data.get('success'):
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve volcano data'
        }), 500
    
    volcanoes = volcanoes_data['volcanoes']
    
    # Calculate comprehensive statistics
    total_volcanoes = len(volcanoes)
    alert_distribution = {
        'level_0': sum(1 for v in volcanoes if v['alert_level'] == 0),
        'level_1': sum(1 for v in volcanoes if v['alert_level'] == 1),
        'level_2': sum(1 for v in volcanoes if v['alert_level'] == 2),
        'level_3': sum(1 for v in volcanoes if v['alert_level'] >= 3),
    }
    
    total_eruptions = sum(v.get('eruption_history', {}).get('total_eruptions', 0) for v in volcanoes)
    avg_eruptions = total_eruptions / total_volcanoes if total_volcanoes > 0 else 0
    
    activity_categories = {}
    for v in volcanoes:
        category = v.get('eruption_history', {}).get('frequency_category', 'Unknown')
        activity_categories[category] = activity_categories.get(category, 0) + 1
    
    total_affected_population = sum(v.get('hazards', {}).get('affected_population', 0) for v in volcanoes)
    
    total_seismic_stations = sum(v.get('monitoring', {}).get('seismic_stations', 0) for v in volcanoes)
    total_earthquakes_24h = sum(v.get('monitoring', {}).get('recent_earthquakes_24h', 0) for v in volcanoes)
    
    avg_so2 = sum(v.get('monitoring', {}).get('so2_emission', 0) for v in volcanoes) / total_volcanoes if total_volcanoes > 0 else 0
    
    most_active = max(volcanoes, key=lambda v: v.get('eruption_history', {}).get('total_eruptions', 0))
    highest_alert = max(volcanoes, key=lambda v: v['alert_level'])
    
    return jsonify({
        'success': True,
        'total_volcanoes': total_volcanoes,
        'alert_distribution': alert_distribution,
        'on_alert': sum(1 for v in volcanoes if v['alert_level'] > 0),
        'eruption_statistics': {
            'total_historical_eruptions': total_eruptions,
            'average_per_volcano': round(avg_eruptions, 1),
            'activity_categories': activity_categories
        },
        'population_impact': {
            'total_affected': total_affected_population,
            'average_per_volcano': round(total_affected_population / total_volcanoes) if total_volcanoes > 0 else 0
        },
        'monitoring_capacity': {
            'total_seismic_stations': total_seismic_stations,
            'total_earthquakes_24h': total_earthquakes_24h,
            'average_so2_emission': round(avg_so2, 1)
        },
        'highlights': {
            'most_active': {
                'name': most_active['name'],
                'eruptions': most_active.get('eruption_history', {}).get('total_eruptions', 0)
            },
            'highest_alert': {
                'name': highest_alert['name'],
                'alert_level': highest_alert['alert_level'],
                'status': highest_alert['status']
            }
        },
        'metadata': {
            'generated': int(time.time() * 1000),
            'server_time_utc': datetime.utcnow().isoformat() + 'Z',
            'source': 'PHIVOLCS Records'
        }
    })

@app.route('/api/phivolcs/latest', methods=['GET'])
def get_phivolcs_latest():
    """Get latest earthquake bulletins from PHIVOLCS"""
    # Note: PHIVOLCS doesn't have a public API. This would require web scraping
    # or accessing their social media feeds. For now, we'll provide a placeholder
    # that includes instructions for future implementation.
    return jsonify({
        'success': True,
        'message': 'PHIVOLCS integration pending',
        'note': 'PHIVOLCS does not provide a public API. To access their earthquake bulletins, consider: 1) Web scraping their official website, 2) Using Facebook Graph API to access their public posts, 3) Monitoring their RSS feed if available',
        'official_sources': [
            'https://earthquake.phivolcs.dost.gov.ph/',
            'https://www.facebook.com/phivolcs.dost',
            'https://twitter.com/phivolcs_dost'
        ],
        'metadata': {
            'generated': int(time.time() * 1000),
            'server_time_utc': datetime.utcnow().isoformat() + 'Z'
        }
    })

@app.route('/api/time', methods=['GET'])
def get_server_time():
    """Get server time information"""
    now_utc = datetime.utcnow()
    # Get Philippine time (UTC+8)
    phil_tz = pytz.timezone('Asia/Manila')
    now_phil = datetime.now(phil_tz)
    
    return jsonify({
        'success': True,
        'utc': now_utc.isoformat() + 'Z',
        'philippine_time': now_phil.isoformat(),
        'timestamp': int(time.time() * 1000),
        'timezone': 'Asia/Manila (UTC+8)'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time() * 1000),
        'server_time_utc': datetime.utcnow().isoformat() + 'Z',
        'service': 'PhilEarthStats API'
    })

@app.route('/api/info', methods=['GET'])
def get_info():
    """Get API information"""
    return jsonify({
        'name': 'PhilEarthStats API',
        'version': '1.0.0',
        'description': 'Real-time Philippines earthquake and volcano monitoring system',
        'endpoints': {
            '/api/earthquakes/all': 'Get ALL earthquakes including aftershocks (7 days, no magnitude filter)',
            '/api/earthquakes/recent': 'Get recent earthquakes (7 days, M ≥ 2.5)',
            '/api/earthquakes/significant': 'Get significant earthquakes (M ≥ 4.5, 30 days)',
            '/api/earthquakes/statistics': 'Get earthquake statistics (30 days)',
            '/api/volcanoes/active': 'Get comprehensive active volcanoes information with all monitoring data',
            '/api/volcanoes/statistics': 'Get aggregated statistics about all monitored volcanoes',
            '/api/phivolcs/latest': 'Get PHIVOLCS earthquake bulletins (pending implementation)',
            '/api/time': 'Get server time information',
            '/api/health': 'Health check',
            '/api/info': 'API information',
            '/api/ai/analyze': 'Get AI-powered analysis of earthquake data (POST)',
            '/api/history/worst-years': 'Get worst earthquake years ranked by severity',
            '/api/history/year/<year>': 'Get earthquake data for a specific year',
            '/api/calendar': 'Get calendar view of earthquakes by date',
            '/api/history/date-range': 'Get earthquakes within a date range',
            '/api/history/sync': 'Sync historical data from USGS (POST)'
        },
        'data_sources': [
            'USGS Earthquake Catalog (earthquake.usgs.gov)',
            'PHIVOLCS - Philippine Institute of Volcanology and Seismology'
        ],
        'cache_timeout': f'{CACHE_TIMEOUT} seconds'
    })

@app.route('/api/ai/analyze', methods=['POST'])
def analyze_with_ai():
    """Use OpenRouter LLM to analyze earthquake data and provide insights"""
    try:
        # Get OpenRouter API key from environment
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key or api_key == 'your_openrouter_api_key_here':
            return jsonify({
                'success': False,
                'error': 'OpenRouter API key not configured. Please set OPENROUTER_API_KEY in your .env file.'
            }), 400
        
        # Get all earthquake data
        def fetch_all_data():
            # Fetch earthquakes from last 30 days for comprehensive analysis
            params = {
                'format': 'geojson',
                'starttime': (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'endtime': datetime.utcnow().strftime('%Y-%m-%d'),
                **PHILIPPINES_BOUNDS,
                'orderby': 'time'
            }
            
            response = requests.get(USGS_API, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        
        data = fetch_all_data()
        
        # Process earthquake data
        earthquakes = []
        for feature in data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            earthquakes.append({
                'magnitude': props.get('mag'),
                'place': props.get('place'),
                'time': datetime.fromtimestamp(props.get('time') / 1000).strftime('%Y-%m-%d %H:%M:%S UTC'),
                'depth': coords[2],
                'latitude': coords[1],
                'longitude': coords[0],
                'significance': props.get('sig'),
                'felt': props.get('felt'),
                'tsunami': props.get('tsunami')
            })
        
        # Calculate statistics
        magnitudes = [eq['magnitude'] for eq in earthquakes if eq['magnitude']]
        depths = [eq['depth'] for eq in earthquakes]
        
        stats = {
            'total_count': len(earthquakes),
            'avg_magnitude': sum(magnitudes) / len(magnitudes) if magnitudes else 0,
            'max_magnitude': max(magnitudes) if magnitudes else 0,
            'min_magnitude': min(magnitudes) if magnitudes else 0,
            'avg_depth': sum(depths) / len(depths) if depths else 0,
            'max_depth': max(depths) if depths else 0,
            'shallow_count': sum(1 for d in depths if d < 70),
            'intermediate_count': sum(1 for d in depths if 70 <= d < 300),
            'deep_count': sum(1 for d in depths if d >= 300),
            'significant_count': sum(1 for m in magnitudes if m >= 4.5),
            'moderate_count': sum(1 for m in magnitudes if 3.0 <= m < 4.5),
            'minor_count': sum(1 for m in magnitudes if m < 3.0)
        }
        
        # Get most significant earthquakes
        significant_earthquakes = sorted(
            [eq for eq in earthquakes if eq['magnitude'] and eq['magnitude'] >= 4.0],
            key=lambda x: x['magnitude'],
            reverse=True
        )[:10]
        
        # Create comprehensive prompt for LLM
        prompt = f"""You are a seismologist analyzing earthquake data for the Philippines region. Provide a comprehensive analysis based on the following data:

**Period**: Last 30 days

**Overall Statistics**:
- Total earthquakes detected: {stats['total_count']}
- Average magnitude: {stats['avg_magnitude']:.2f}
- Maximum magnitude: {stats['max_magnitude']:.2f}
- Minimum magnitude: {stats['min_magnitude']:.2f}
- Average depth: {stats['avg_depth']:.2f} km
- Maximum depth: {stats['max_depth']:.2f} km

**Earthquake Distribution**:
- Significant (M ≥ 4.5): {stats['significant_count']}
- Moderate (3.0 ≤ M < 4.5): {stats['moderate_count']}
- Minor (M < 3.0): {stats['minor_count']}

**Depth Distribution**:
- Shallow (< 70 km): {stats['shallow_count']}
- Intermediate (70-300 km): {stats['intermediate_count']}
- Deep (≥ 300 km): {stats['deep_count']}

**Top 10 Significant Earthquakes**:
{chr(10).join([f"{i+1}. M{eq['magnitude']:.1f} - {eq['place']} - {eq['time']} - Depth: {eq['depth']:.1f}km" for i, eq in enumerate(significant_earthquakes)])}

Provide a detailed analysis covering:
1. Overall seismic activity assessment (is it normal, elevated, concerning?)
2. Patterns and trends observed (clustering, depth patterns, magnitude distribution)
3. Geographic distribution and hot spots
4. Risk assessment and potential concerns
5. Actionable recommendations for residents and authorities
6. Any notable events or sequences (aftershocks, swarms, etc.)

Be specific, professional, and provide context. Format your response with clear sections and use markdown formatting."""
        
        # Call OpenRouter API using requests
        # Try multiple models in case one is unavailable
        models_to_try = [
            "x-ai/grok-4-fast",  # Most reliable
            "openai/gpt-4o",  # Good alternative
            "google/gemini-pro-1.5",  # Another fallback
        ]
        
        analysis = None
        last_error = None
        
        for model in models_to_try:
            try:
                openrouter_response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert seismologist with deep knowledge of earthquake patterns, tectonic activity, and disaster preparedness in the Philippines region. Provide thorough, accurate, and actionable analysis."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 3000
                    },
                    timeout=60
                )
                
                openrouter_response.raise_for_status()
                completion_data = openrouter_response.json()
                
                # Check if there's an error in the response
                if 'error' in completion_data:
                    last_error = completion_data['error'].get('message', 'Unknown error')
                    continue
                
                analysis = completion_data['choices'][0]['message']['content']
                used_model = model
                break  # Success, exit the loop
                
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                continue  # Try next model
        
        if analysis is None:
            return jsonify({
                'success': False,
                'error': f'All AI models are currently unavailable. Last error: {last_error}'
            }), 503
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'statistics': stats,
            'significant_earthquakes': significant_earthquakes[:5],
            'metadata': {
                'model': used_model,
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'period': '30 days',
                'data_points': len(earthquakes)
            }
        })
    
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch earthquake data: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate AI analysis: {str(e)}'
        }), 500

@app.route('/api/history/worst-years', methods=['GET'])
def get_worst_years():
    """Get the worst earthquake years in Philippine history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        worst_years = DatabaseService.get_worst_years(limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(worst_years),
            'worst_years': worst_years,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'description': 'Worst earthquake years ranked by severity score',
                'source': 'PhilEarthStats Historical Database'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch worst years: {str(e)}'
        }), 500

@app.route('/api/history/year/<int:year>', methods=['GET'])
def get_year_data(year):
    """Get earthquake data for a specific year"""
    try:
        # Get year statistics
        year_stat = YearStatistics.query.get(year)
        
        # Get all events for that year
        events = DatabaseService.get_events_by_year(year)
        
        return jsonify({
            'success': True,
            'year': year,
            'statistics': year_stat.to_dict() if year_stat else None,
            'event_count': len(events),
            'events': events[:100],  # Limit to 100 most significant
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'source': 'PhilEarthStats Historical Database'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch year data: {str(e)}'
        }), 500

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """Get earthquake calendar data"""
    try:
        year = request.args.get('year', datetime.utcnow().year, type=int)
        month = request.args.get('month', type=int)
        
        calendar_data = DatabaseService.get_calendar_data(year=year, month=month)
        
        return jsonify({
            'success': True,
            'year': year,
            'month': month,
            'calendar_data': calendar_data,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'source': 'PhilEarthStats Historical Database'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch calendar data: {str(e)}'
        }), 500

@app.route('/api/history/date-range', methods=['GET'])
def get_date_range():
    """Get earthquake events within a date range"""
    try:
        start = request.args.get('start', (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end = request.args.get('end', datetime.utcnow().strftime('%Y-%m-%d'))
        
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        
        events = DatabaseService.get_events_by_date_range(start_date, end_date)
        
        return jsonify({
            'success': True,
            'start_date': start,
            'end_date': end,
            'event_count': len(events),
            'events': events,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'source': 'PhilEarthStats Historical Database'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch date range data: {str(e)}'
        }), 500

@app.route('/api/history/sync', methods=['POST'])
def sync_historical_data():
    """Sync historical data from USGS for a specific time period"""
    try:
        # Get parameters from request
        data = request.get_json() or {}
        start_date = data.get('start_date', (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.utcnow().strftime('%Y-%m-%d'))
        
        # Fetch from USGS
        params = {
            'format': 'geojson',
            'starttime': start_date,
            'endtime': end_date,
            **PHILIPPINES_BOUNDS,
            'orderby': 'time'
        }
        
        response = requests.get(USGS_API, params=params, timeout=30)
        response.raise_for_status()
        usgs_data = response.json()
        
        # Process and store
        earthquakes = []
        for feature in usgs_data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            earthquakes.append({
                'id': feature['id'],
                'magnitude': props.get('mag'),
                'place': props.get('place'),
                'time': props.get('time'),
                'latitude': coords[1],
                'longitude': coords[0],
                'depth': coords[2],
                'significance': props.get('sig'),
                'felt': props.get('felt'),
                'alert': props.get('alert'),
                'tsunami': props.get('tsunami', 0),
                'type': props.get('type', 'earthquake'),
                'status': props.get('status', 'automatic')
            })
        
        stored_count = DatabaseService.store_multiple_earthquakes(earthquakes)
        
        return jsonify({
            'success': True,
            'synced_count': stored_count,
            'total_fetched': len(earthquakes),
            'start_date': start_date,
            'end_date': end_date,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to sync historical data: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
