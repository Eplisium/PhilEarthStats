from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from functools import lru_cache
import time
import pytz
import os
import math
from collections import defaultdict
from dotenv import load_dotenv
from database import db, DatabaseService, EarthquakeEvent, YearStatistics
from ai_config import get_available_models, get_model_config, validate_model, DEFAULT_MODEL, FALLBACK_MODELS
from ai_prompts import build_analysis_prompt, get_system_prompt, get_prompt_config, PROMPT_VERSION
from insights_engine import InsightsEngine

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
# Real-time GeoJSON feeds (recommended by USGS, updated every 1-5 minutes)
USGS_FEED_HOUR = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
USGS_FEED_DAY = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
USGS_FEED_WEEK = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"
USGS_FEED_SIGNIFICANT = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
PHIVOLCS_API = "https://earthquake.phivolcs.dost.gov.ph/"

# Philippines bounds
PHILIPPINES_BOUNDS = {
    'minlatitude': 4.5,
    'maxlatitude': 21.5,
    'minlongitude': 116.0,
    'maxlongitude': 127.0
}

# Cache timeout (5 minutes for balanced performance)
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

def is_in_philippines(lat, lon):
    """Check if coordinates are within Philippines bounds"""
    return (PHILIPPINES_BOUNDS['minlatitude'] <= lat <= PHILIPPINES_BOUNDS['maxlatitude'] and
            PHILIPPINES_BOUNDS['minlongitude'] <= lon <= PHILIPPINES_BOUNDS['maxlongitude'])

def process_earthquake_feature(feature):
    """Process a GeoJSON feature into earthquake dict"""
    props = feature['properties']
    coords = feature['geometry']['coordinates']
    return {
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
    }

@app.route('/api/earthquakes/all', methods=['GET'])
def get_all_earthquakes():
    """Get ALL earthquakes in the Philippines including aftershocks (no minimum magnitude)"""
    try:
        # Check if force refresh is requested (bypass cache)
        force_refresh = request.args.get('force', 'false').lower() == 'true'
        
        def fetch_all_earthquakes():
            # Use USGS real-time feeds (updated every 1-5 minutes)
            # Combine hour + day + week feeds for comprehensive 7-day coverage
            all_earthquakes = {}
            
            for feed_url in [USGS_FEED_HOUR, USGS_FEED_DAY, USGS_FEED_WEEK]:
                try:
                    response = requests.get(feed_url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Filter to Philippines region and process
                    for feature in data['features']:
                        coords = feature['geometry']['coordinates']
                        lat, lon = coords[1], coords[0]
                        
                        # Only include earthquakes in Philippines
                        if is_in_philippines(lat, lon):
                            eq_id = feature['id']
                            # Use dict to avoid duplicates across feeds
                            if eq_id not in all_earthquakes:
                                all_earthquakes[eq_id] = process_earthquake_feature(feature)
                except Exception as e:
                    print(f"Warning: Failed to fetch from {feed_url}: {str(e)}")
                    continue
            
            earthquakes = list(all_earthquakes.values())
            # Sort by time (most recent first)
            earthquakes.sort(key=lambda x: x['time'], reverse=True)
            
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
                    'source': 'USGS Real-time GeoJSON Feeds (Updated Every 1-5 Minutes)',
                    'feed_update_frequency': '1-5 minutes'
                }
            }
        
        # Bypass cache if force refresh is requested
        if force_refresh:
            result = fetch_all_earthquakes()
            cache_data['all_earthquakes'] = result
            last_fetch_time['all_earthquakes'] = time.time()
        else:
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
        # Check if force refresh is requested (bypass cache)
        force_refresh = request.args.get('force', 'false').lower() == 'true'
        
        def fetch_earthquakes():
            # Use USGS real-time feeds (updated every 1-5 minutes)
            all_earthquakes = {}
            
            for feed_url in [USGS_FEED_HOUR, USGS_FEED_DAY, USGS_FEED_WEEK]:
                try:
                    response = requests.get(feed_url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Filter to Philippines region and magnitude >= 2.5
                    for feature in data['features']:
                        coords = feature['geometry']['coordinates']
                        lat, lon = coords[1], coords[0]
                        mag = feature['properties'].get('mag')
                        
                        # Only include earthquakes in Philippines with mag >= 2.5
                        if is_in_philippines(lat, lon) and mag is not None and mag >= 2.5:
                            eq_id = feature['id']
                            if eq_id not in all_earthquakes:
                                all_earthquakes[eq_id] = process_earthquake_feature(feature)
                except Exception as e:
                    print(f"Warning: Failed to fetch from {feed_url}: {str(e)}")
                    continue
            
            earthquakes = list(all_earthquakes.values())
            earthquakes.sort(key=lambda x: x['time'], reverse=True)
            
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
                    'source': 'USGS Real-time GeoJSON Feeds (Updated Every 1-5 Minutes)',
                    'feed_update_frequency': '1-5 minutes'
                }
            }
        
        # Bypass cache if force refresh is requested
        if force_refresh:
            result = fetch_earthquakes()
            cache_data['recent_earthquakes'] = result
            last_fetch_time['recent_earthquakes'] = time.time()
        else:
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
        # Check if force refresh is requested (bypass cache)
        force_refresh = request.args.get('force', 'false').lower() == 'true'
        
        def fetch_significant():
            # Use USGS real-time significant feed (updated every 5 minutes)
            try:
                response = requests.get(USGS_FEED_SIGNIFICANT, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Filter to Philippines region and magnitude >= 4.5
                earthquakes = []
                for feature in data['features']:
                    coords = feature['geometry']['coordinates']
                    lat, lon = coords[1], coords[0]
                    mag = feature['properties'].get('mag')
                    
                    # Only include earthquakes in Philippines with mag >= 4.5
                    if is_in_philippines(lat, lon) and mag is not None and mag >= 4.5:
                        props = feature['properties']
                        earthquakes.append({
                            'id': feature['id'],
                            'magnitude': mag,
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
                
                # Sort by magnitude (highest first)
                earthquakes.sort(key=lambda x: x['magnitude'], reverse=True)
                
                return {
                    'success': True,
                    'count': len(earthquakes),
                    'earthquakes': earthquakes,
                    'metadata': {
                        'generated': int(time.time() * 1000),
                        'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                        'title': 'Significant Philippines Earthquakes (30 days, M ≥ 4.5)',
                        'source': 'USGS Real-time GeoJSON Feeds (Updated Every 5 Minutes)',
                        'feed_update_frequency': '5 minutes'
                    }
                }
            except Exception as e:
                print(f"Warning: Failed to fetch significant earthquakes: {str(e)}")
                return {
                    'success': True,
                    'count': 0,
                    'earthquakes': [],
                    'metadata': {
                        'generated': int(time.time() * 1000),
                        'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                        'title': 'Significant Philippines Earthquakes (30 days, M ≥ 4.5)',
                        'source': 'USGS Real-time GeoJSON Feeds',
                        'error': str(e)
                    }
                }
        
        # Bypass cache if force refresh is requested
        if force_refresh:
            result = fetch_significant()
            cache_data['significant_earthquakes'] = result
            last_fetch_time['significant_earthquakes'] = time.time()
        else:
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
        # Check if force refresh is requested (bypass cache)
        force_refresh = request.args.get('force', 'false').lower() == 'true'
        
        def fetch_statistics():
            # Use USGS real-time feeds for 30-day statistics
            all_earthquakes = {}
            
            # Use month feed for comprehensive 30-day data
            try:
                response = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson", timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Filter to Philippines region
                for feature in data['features']:
                    coords = feature['geometry']['coordinates']
                    lat, lon = coords[1], coords[0]
                    
                    if is_in_philippines(lat, lon):
                        eq_id = feature['id']
                        if eq_id not in all_earthquakes:
                            all_earthquakes[eq_id] = process_earthquake_feature(feature)
            except Exception as e:
                print(f"Warning: Failed to fetch monthly feed for statistics: {str(e)}")
            
            earthquakes = list(all_earthquakes.values())
            
            # Calculate statistics
            magnitudes = [eq['magnitude'] for eq in earthquakes if eq.get('magnitude') is not None]
            depths = [eq['depth'] for eq in earthquakes if eq.get('depth') is not None]
            
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
                'total_earthquakes': len(earthquakes),
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
                    'source': 'USGS Real-time GeoJSON Feeds',
                    'feed_update_frequency': '5 minutes'
                }
            }
        
        # Bypass cache if force refresh is requested
        if force_refresh:
            result = fetch_statistics()
            cache_data['earthquake_statistics'] = result
            last_fetch_time['earthquake_statistics'] = time.time()
        else:
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
            '/api/ai/models': 'Get available AI models for analysis',
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

@app.route('/api/ai/models', methods=['GET'])
def get_ai_models():
    """Get available AI models for earthquake analysis"""
    try:
        models = get_available_models()
        return jsonify({
            'success': True,
            'models': models,
            'default_model': DEFAULT_MODEL,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch AI models: {str(e)}'
        }), 500

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
        
        # Get selected model from request body
        request_data = request.get_json() or {}
        selected_model = request_data.get('model', DEFAULT_MODEL)
        
        # Validate selected model
        if not validate_model(selected_model):
            selected_model = DEFAULT_MODEL
        
        # Helper function to calculate seismic energy
        def calculate_seismic_energy(magnitude):
            """Calculate seismic energy in joules using magnitude"""
            if magnitude is None:
                return 0
            # Energy (joules) = 10^(1.5 * M + 4.8)
            return 10 ** (1.5 * magnitude + 4.8)
        
        # Helper function to classify region
        def classify_region(latitude, longitude):
            """Classify earthquake by Philippine region"""
            if latitude >= 14.0:
                return 'Luzon'
            elif latitude >= 9.5:
                return 'Visayas'
            else:
                return 'Mindanao'
        
        # Helper function to detect earthquake clusters (simplified DBSCAN-like approach)
        def detect_clusters(earthquakes, eps=0.5, min_samples=3):
            """Detect spatial clusters of earthquakes"""
            clusters = []
            visited = set()
            
            for i, eq in enumerate(earthquakes):
                if i in visited or eq['magnitude'] is None:
                    continue
                
                # Find neighbors within eps degrees
                neighbors = []
                for j, other_eq in enumerate(earthquakes):
                    if j == i or other_eq['magnitude'] is None:
                        continue
                    
                    # Calculate distance (simplified Euclidean)
                    dist = math.sqrt(
                        (eq['latitude'] - other_eq['latitude'])**2 + 
                        (eq['longitude'] - other_eq['longitude'])**2
                    )
                    
                    if dist <= eps:
                        neighbors.append(j)
                
                # If enough neighbors, it's a cluster
                if len(neighbors) >= min_samples:
                    cluster = {
                        'center_lat': sum(earthquakes[j]['latitude'] for j in neighbors) / len(neighbors),
                        'center_lon': sum(earthquakes[j]['longitude'] for j in neighbors) / len(neighbors),
                        'count': len(neighbors),
                        'max_magnitude': max(earthquakes[j]['magnitude'] for j in neighbors if earthquakes[j]['magnitude']),
                        'avg_magnitude': sum(earthquakes[j]['magnitude'] for j in neighbors if earthquakes[j]['magnitude']) / len([earthquakes[j] for j in neighbors if earthquakes[j]['magnitude']]),
                        'region': eq['region'],
                        'earthquakes': neighbors
                    }
                    clusters.append(cluster)
                    visited.update(neighbors)
            
            return clusters
        
        # Helper function to detect mainshock-aftershock sequences
        def detect_sequences(earthquakes, time_window_days=30, distance_threshold=1.0):
            """Detect mainshock-aftershock sequences"""
            sequences = []
            sorted_eqs = sorted(earthquakes, key=lambda x: x['magnitude'] or 0, reverse=True)
            processed = set()
            
            for mainshock in sorted_eqs[:10]:  # Check top 10 largest events
                if mainshock['magnitude'] is None or mainshock['magnitude'] < 4.0:
                    continue
                
                mainshock_idx = earthquakes.index(mainshock)
                if mainshock_idx in processed:
                    continue
                
                # Find potential aftershocks
                aftershocks = []
                mainshock_time = datetime.strptime(mainshock['time'], '%Y-%m-%d %H:%M:%S UTC')
                
                for i, eq in enumerate(earthquakes):
                    if i == mainshock_idx or eq['magnitude'] is None or i in processed:
                        continue
                    
                    eq_time = datetime.strptime(eq['time'], '%Y-%m-%d %H:%M:%S UTC')
                    time_diff = abs((eq_time - mainshock_time).days)
                    
                    # Calculate distance
                    dist = math.sqrt(
                        (mainshock['latitude'] - eq['latitude'])**2 + 
                        (mainshock['longitude'] - eq['longitude'])**2
                    )
                    
                    # Aftershock criteria: within time window, nearby, smaller magnitude
                    if (time_diff <= time_window_days and 
                        dist <= distance_threshold and 
                        eq['magnitude'] < mainshock['magnitude']):
                        aftershocks.append(eq)
                
                if len(aftershocks) >= 3:
                    sequences.append({
                        'mainshock': mainshock,
                        'aftershock_count': len(aftershocks),
                        'largest_aftershock': max(aftershocks, key=lambda x: x['magnitude'] or 0),
                        'duration_days': time_window_days,
                        'location': mainshock['place']
                    })
                    processed.add(mainshock_idx)
            
            return sequences
        
        # Helper function to calculate regional risk scores
        def calculate_risk_scores(regional_stats, regional_data):
            """Calculate risk scores (0-100) for each region"""
            risk_scores = {}
            
            for region, stats in regional_stats.items():
                # Factors for risk calculation
                activity_score = min(stats['count'] / 10, 30)  # Max 30 points
                magnitude_score = min(stats['avg_magnitude'] * 5, 25)  # Max 25 points
                significant_score = min(stats['significant_count'] * 10, 25)  # Max 25 points
                shallow_ratio = (stats['very_shallow'] + stats['shallow']) / max(stats['count'], 1)
                depth_score = shallow_ratio * 20  # Max 20 points
                
                total_score = activity_score + magnitude_score + significant_score + depth_score
                
                # Determine risk level
                if total_score >= 70:
                    risk_level = 'High'
                    risk_color = 'red'
                elif total_score >= 50:
                    risk_level = 'Elevated'
                    risk_color = 'orange'
                elif total_score >= 30:
                    risk_level = 'Moderate'
                    risk_color = 'yellow'
                else:
                    risk_level = 'Low'
                    risk_color = 'green'
                
                risk_scores[region] = {
                    'score': round(total_score, 1),
                    'level': risk_level,
                    'color': risk_color,
                    'factors': {
                        'activity': round(activity_score, 1),
                        'magnitude': round(magnitude_score, 1),
                        'significant_events': round(significant_score, 1),
                        'shallow_depth': round(depth_score, 1)
                    }
                }
            
            return risk_scores
        
        # Helper function to analyze trends
        def analyze_trends(earthquakes, period_days=90):
            """Analyze temporal trends in seismic activity"""
            # Split into time segments
            segment_days = 30
            segments = []
            
            for i in range(0, period_days, segment_days):
                segment_start = datetime.utcnow() - timedelta(days=period_days-i)
                segment_end = segment_start + timedelta(days=segment_days)
                
                segment_eqs = [
                    eq for eq in earthquakes 
                    if segment_start <= datetime.strptime(eq['time'], '%Y-%m-%d %H:%M:%S UTC') < segment_end
                ]
                
                segment_mags = [eq['magnitude'] for eq in segment_eqs if eq['magnitude']]
                
                segments.append({
                    'period': f"Days {i+1}-{min(i+segment_days, period_days)}",
                    'count': len(segment_eqs),
                    'avg_magnitude': sum(segment_mags) / len(segment_mags) if segment_mags else 0,
                    'significant_count': sum(1 for m in segment_mags if m >= 4.5)
                })
            
            # Determine trend
            if len(segments) >= 2:
                recent_count = segments[-1]['count']
                older_count = segments[0]['count']
                
                if recent_count > older_count * 1.2:
                    trend = 'Increasing'
                elif recent_count < older_count * 0.8:
                    trend = 'Decreasing'
                else:
                    trend = 'Stable'
            else:
                trend = 'Insufficient data'
            
            return {
                'segments': segments,
                'overall_trend': trend
            }
        
        # Helper function to calculate Gutenberg-Richter b-value
        def calculate_b_value(magnitudes):
            """Calculate b-value from magnitude distribution"""
            if len(magnitudes) < 10:
                return None
            
            # Filter magnitudes >= 3.0 for better statistics
            filtered_mags = [m for m in magnitudes if m >= 3.0]
            
            if len(filtered_mags) < 10:
                return None
            
            # Simple b-value estimation: b ≈ log10(e) / (mean_magnitude - min_magnitude)
            mean_mag = sum(filtered_mags) / len(filtered_mags)
            min_mag = min(filtered_mags)
            
            if mean_mag - min_mag == 0:
                return None
            
            b_value = 1.0 / (mean_mag - min_mag) / math.log(10)
            
            return round(b_value, 2)
        
        # Helper function to correlate with volcanoes
        def correlate_with_volcanoes(earthquakes):
            """Find earthquakes near active volcanoes"""
            # Volcano locations (from the existing volcano data)
            volcanoes = [
                {'name': 'Mayon', 'lat': 13.2572, 'lon': 123.6856},
                {'name': 'Taal', 'lat': 14.0021, 'lon': 120.9937},
                {'name': 'Pinatubo', 'lat': 15.1300, 'lon': 120.3500},
                {'name': 'Bulusan', 'lat': 12.7700, 'lon': 124.0500},
                {'name': 'Kanlaon', 'lat': 10.4120, 'lon': 123.1320},
                {'name': 'Hibok-Hibok', 'lat': 9.2030, 'lon': 124.6730}
            ]
            
            volcano_correlation = {}
            threshold = 0.5  # degrees (~55 km)
            
            for volcano in volcanoes:
                nearby_eqs = []
                for eq in earthquakes:
                    dist = math.sqrt(
                        (eq['latitude'] - volcano['lat'])**2 + 
                        (eq['longitude'] - volcano['lon'])**2
                    )
                    if dist <= threshold:
                        nearby_eqs.append(eq)
                
                if nearby_eqs:
                    nearby_mags = [eq['magnitude'] for eq in nearby_eqs if eq['magnitude']]
                    volcano_correlation[volcano['name']] = {
                        'earthquake_count': len(nearby_eqs),
                        'max_magnitude': max(nearby_mags) if nearby_mags else 0,
                        'avg_magnitude': sum(nearby_mags) / len(nearby_mags) if nearby_mags else 0,
                        'significant_count': sum(1 for m in nearby_mags if m >= 4.0)
                    }
            
            return volcano_correlation
        
        # Get all earthquake data (90 days for better analysis)
        def fetch_all_data():
            # Use USGS real-time feeds for faster, up-to-date data
            # Combine month feed (30 days) with query API for full 90 days
            all_earthquakes = {}
            
            # First, get recent 30 days from real-time feed (fastest)
            try:
                response = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson", timeout=10)
                response.raise_for_status()
                month_data = response.json()
                
                # Filter to Philippines and add to collection
                for feature in month_data['features']:
                    coords = feature['geometry']['coordinates']
                    lat, lon = coords[1], coords[0]
                    
                    if is_in_philippines(lat, lon):
                        all_earthquakes[feature['id']] = feature
            except Exception as e:
                print(f"Warning: Failed to fetch month feed: {str(e)}")
            
            # Then get older data (30-90 days) from query API for historical context
            try:
                params = {
                    'format': 'geojson',
                    'starttime': (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d'),
                    'endtime': (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    **PHILIPPINES_BOUNDS,
                    'orderby': 'time'
                }
                
                response = requests.get(USGS_API, params=params, timeout=15)
                response.raise_for_status()
                older_data = response.json()
                
                # Add older earthquakes (avoid duplicates)
                for feature in older_data['features']:
                    eq_id = feature['id']
                    if eq_id not in all_earthquakes:
                        all_earthquakes[eq_id] = feature
            except Exception as e:
                print(f"Warning: Failed to fetch older data: {str(e)}")
            
            # Convert back to GeoJSON format
            return {
                'type': 'FeatureCollection',
                'features': list(all_earthquakes.values())
            }
        
        # Fetch historical data for comparison
        def fetch_historical_data(days_back):
            """Fetch historical data from specified period"""
            end_date = datetime.utcnow() - timedelta(days=days_back)
            start_date = end_date - timedelta(days=90)
            params = {
                'format': 'geojson',
                'starttime': start_date.strftime('%Y-%m-%d'),
                'endtime': end_date.strftime('%Y-%m-%d'),
                **PHILIPPINES_BOUNDS,
                'orderby': 'time'
            }
            
            try:
                response = requests.get(USGS_API, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except:
                return None
        
        data = fetch_all_data()
        
        # Process earthquake data with regional classification
        earthquakes = []
        regional_data = {'Luzon': [], 'Visayas': [], 'Mindanao': []}
        
        for feature in data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            latitude = coords[1]
            longitude = coords[0]
            magnitude = props.get('mag')
            depth = coords[2]
            
            region = classify_region(latitude, longitude)
            
            eq_data = {
                'magnitude': magnitude,
                'place': props.get('place'),
                'time': datetime.fromtimestamp(props.get('time') / 1000).strftime('%Y-%m-%d %H:%M:%S UTC'),
                'depth': depth,
                'latitude': latitude,
                'longitude': longitude,
                'significance': props.get('sig'),
                'felt': props.get('felt'),
                'tsunami': props.get('tsunami'),
                'region': region,
                'energy': calculate_seismic_energy(magnitude)
            }
            
            earthquakes.append(eq_data)
            regional_data[region].append(eq_data)
        
        # Calculate overall statistics
        magnitudes = [eq['magnitude'] for eq in earthquakes if eq['magnitude']]
        depths = [eq['depth'] for eq in earthquakes]
        energies = [eq['energy'] for eq in earthquakes]
        
        stats = {
            'total_count': len(earthquakes),
            'period_days': 90,
            'avg_magnitude': sum(magnitudes) / len(magnitudes) if magnitudes else 0,
            'max_magnitude': max(magnitudes) if magnitudes else 0,
            'min_magnitude': min(magnitudes) if magnitudes else 0,
            'avg_depth': sum(depths) / len(depths) if depths else 0,
            'max_depth': max(depths) if depths else 0,
            'total_energy_joules': sum(energies),
            'avg_daily_energy': sum(energies) / 90 if energies else 0,
            'very_shallow_count': sum(1 for d in depths if d < 10),
            'shallow_count': sum(1 for d in depths if 10 <= d < 70),
            'intermediate_count': sum(1 for d in depths if 70 <= d < 300),
            'deep_count': sum(1 for d in depths if d >= 300),
            'significant_count': sum(1 for m in magnitudes if m >= 4.5),
            'moderate_count': sum(1 for m in magnitudes if 3.0 <= m < 4.5),
            'minor_count': sum(1 for m in magnitudes if m < 3.0)
        }
        
        # Calculate regional statistics
        regional_stats = {}
        for region, region_eqs in regional_data.items():
            region_mags = [eq['magnitude'] for eq in region_eqs if eq['magnitude']]
            region_depths = [eq['depth'] for eq in region_eqs]
            region_energies = [eq['energy'] for eq in region_eqs]
            
            regional_stats[region] = {
                'count': len(region_eqs),
                'percentage': round(len(region_eqs) / len(earthquakes) * 100, 1) if earthquakes else 0,
                'avg_magnitude': round(sum(region_mags) / len(region_mags), 2) if region_mags else 0,
                'max_magnitude': round(max(region_mags), 1) if region_mags else 0,
                'avg_depth': round(sum(region_depths) / len(region_depths), 1) if region_depths else 0,
                'total_energy_joules': sum(region_energies),
                'significant_count': sum(1 for m in region_mags if m >= 4.5),
                'very_shallow': sum(1 for d in region_depths if d < 10),
                'shallow': sum(1 for d in region_depths if 10 <= d < 70),
                'intermediate': sum(1 for d in region_depths if 70 <= d < 300),
                'deep': sum(1 for d in region_depths if d >= 300)
            }
        
        # Fetch historical data for comparison
        previous_period_data = fetch_historical_data(90)  # Previous 90 days
        last_year_data = fetch_historical_data(365)  # Same period last year
        
        # Calculate historical comparison
        historical_comparison = {}
        
        if previous_period_data:
            prev_count = len(previous_period_data['features'])
            prev_mags = [f['properties'].get('mag') for f in previous_period_data['features'] if f['properties'].get('mag')]
            prev_avg_mag = sum(prev_mags) / len(prev_mags) if prev_mags else 0
            
            count_change = ((len(earthquakes) - prev_count) / prev_count * 100) if prev_count > 0 else 0
            mag_change = stats['avg_magnitude'] - prev_avg_mag
            
            historical_comparison['vs_previous_period'] = {
                'count_change_percent': round(count_change, 1),
                'magnitude_change': round(mag_change, 2),
                'previous_count': prev_count,
                'previous_avg_magnitude': round(prev_avg_mag, 2)
            }
        
        if last_year_data:
            ly_count = len(last_year_data['features'])
            ly_mags = [f['properties'].get('mag') for f in last_year_data['features'] if f['properties'].get('mag')]
            ly_avg_mag = sum(ly_mags) / len(ly_mags) if ly_mags else 0
            
            count_change = ((len(earthquakes) - ly_count) / ly_count * 100) if ly_count > 0 else 0
            mag_change = stats['avg_magnitude'] - ly_avg_mag
            
            historical_comparison['vs_last_year'] = {
                'count_change_percent': round(count_change, 1),
                'magnitude_change': round(mag_change, 2),
                'last_year_count': ly_count,
                'last_year_avg_magnitude': round(ly_avg_mag, 2)
            }
        
        # ===== PHASE 2: ADVANCED ANALYTICS =====
        
        # Detect clusters
        clusters = detect_clusters(earthquakes)
        
        # Detect mainshock-aftershock sequences
        sequences = detect_sequences(earthquakes)
        
        # Calculate risk scores
        risk_scores = calculate_risk_scores(regional_stats, regional_data)
        
        # Analyze trends
        trends = analyze_trends(earthquakes)
        
        # Calculate Gutenberg-Richter b-value
        b_value = calculate_b_value(magnitudes)
        
        # Correlate with volcanoes
        volcano_correlation = correlate_with_volcanoes(earthquakes)
        
        # Get most significant earthquakes with region info
        significant_earthquakes = sorted(
            [eq for eq in earthquakes if eq['magnitude'] and eq['magnitude'] >= 4.0],
            key=lambda x: x['magnitude'],
            reverse=True
        )[:10]
        
        # Format energy values for display
        def format_energy(joules):
            """Format energy in scientific notation"""
            if joules >= 1e15:
                return f"{joules/1e15:.2f} × 10¹⁵ joules"
            elif joules >= 1e12:
                return f"{joules/1e12:.2f} × 10¹² joules"
            elif joules >= 1e9:
                return f"{joules/1e9:.2f} × 10⁹ joules"
            else:
                return f"{joules:.2e} joules"
        
        # Create comprehensive prompt for LLM with Phase 1 enhancements
        prompt = f"""You are a seismologist analyzing earthquake data for the Philippines region. Provide a comprehensive analysis based on the following data:

**Analysis Period**: Last 90 days (extended timeframe for better trend detection)

**Overall Statistics**:
- Total earthquakes detected: {stats['total_count']}
- Average magnitude: {stats['avg_magnitude']:.2f}
- Maximum magnitude: {stats['max_magnitude']:.2f}
- Minimum magnitude: {stats['min_magnitude']:.2f}
- Average depth: {stats['avg_depth']:.2f} km
- Maximum depth: {stats['max_depth']:.2f} km
- **Total seismic energy released**: {format_energy(stats['total_energy_joules'])}
- **Average daily energy release**: {format_energy(stats['avg_daily_energy'])}

**Earthquake Distribution by Magnitude**:
- Significant (M ≥ 4.5): {stats['significant_count']}
- Moderate (3.0 ≤ M < 4.5): {stats['moderate_count']}
- Minor (M < 3.0): {stats['minor_count']}

**Enhanced Depth Distribution**:
- Very Shallow (< 10 km): {stats['very_shallow_count']} - High damage potential
- Shallow (10-70 km): {stats['shallow_count']} - Moderate damage potential
- Intermediate (70-300 km): {stats['intermediate_count']} - Lower surface impact
- Deep (≥ 300 km): {stats['deep_count']} - Minimal surface impact

**Regional Breakdown**:

**Luzon Region** (Northern Philippines):
- Event count: {regional_stats['Luzon']['count']} ({regional_stats['Luzon']['percentage']}% of total)
- Average magnitude: M {regional_stats['Luzon']['avg_magnitude']}
- Maximum magnitude: M {regional_stats['Luzon']['max_magnitude']}
- Average depth: {regional_stats['Luzon']['avg_depth']} km
- Significant events (M ≥ 4.5): {regional_stats['Luzon']['significant_count']}
- Total energy released: {format_energy(regional_stats['Luzon']['total_energy_joules'])}
- Depth profile: Very Shallow: {regional_stats['Luzon']['very_shallow']}, Shallow: {regional_stats['Luzon']['shallow']}, Intermediate: {regional_stats['Luzon']['intermediate']}, Deep: {regional_stats['Luzon']['deep']}

**Visayas Region** (Central Philippines):
- Event count: {regional_stats['Visayas']['count']} ({regional_stats['Visayas']['percentage']}% of total)
- Average magnitude: M {regional_stats['Visayas']['avg_magnitude']}
- Maximum magnitude: M {regional_stats['Visayas']['max_magnitude']}
- Average depth: {regional_stats['Visayas']['avg_depth']} km
- Significant events (M ≥ 4.5): {regional_stats['Visayas']['significant_count']}
- Total energy released: {format_energy(regional_stats['Visayas']['total_energy_joules'])}
- Depth profile: Very Shallow: {regional_stats['Visayas']['very_shallow']}, Shallow: {regional_stats['Visayas']['shallow']}, Intermediate: {regional_stats['Visayas']['intermediate']}, Deep: {regional_stats['Visayas']['deep']}

**Mindanao Region** (Southern Philippines):
- Event count: {regional_stats['Mindanao']['count']} ({regional_stats['Mindanao']['percentage']}% of total)
- Average magnitude: M {regional_stats['Mindanao']['avg_magnitude']}
- Maximum magnitude: M {regional_stats['Mindanao']['max_magnitude']}
- Average depth: {regional_stats['Mindanao']['avg_depth']} km
- Significant events (M ≥ 4.5): {regional_stats['Mindanao']['significant_count']}
- Total energy released: {format_energy(regional_stats['Mindanao']['total_energy_joules'])}
- Depth profile: Very Shallow: {regional_stats['Mindanao']['very_shallow']}, Shallow: {regional_stats['Mindanao']['shallow']}, Intermediate: {regional_stats['Mindanao']['intermediate']}, Deep: {regional_stats['Mindanao']['deep']}

**Historical Comparison**:"""

        # Add historical comparison data to prompt
        if 'vs_previous_period' in historical_comparison:
            prev = historical_comparison['vs_previous_period']
            prompt += f"""

*Compared to Previous 90-Day Period*:
- Earthquake count change: {prev['count_change_percent']:+.1f}% (was {prev['previous_count']} events)
- Average magnitude change: {prev['magnitude_change']:+.2f} (was M {prev['previous_avg_magnitude']})
- Trend: {'Increasing activity' if prev['count_change_percent'] > 10 else 'Decreasing activity' if prev['count_change_percent'] < -10 else 'Stable activity'}"""

        if 'vs_last_year' in historical_comparison:
            ly = historical_comparison['vs_last_year']
            prompt += f"""

*Compared to Same Period Last Year*:
- Earthquake count change: {ly['count_change_percent']:+.1f}% (was {ly['last_year_count']} events)
- Average magnitude change: {ly['magnitude_change']:+.2f} (was M {ly['last_year_avg_magnitude']})
- Year-over-year trend: {'Higher than last year' if ly['count_change_percent'] > 5 else 'Lower than last year' if ly['count_change_percent'] < -5 else 'Similar to last year'}"""

        prompt += f"""

**Top 10 Most Significant Earthquakes**:
{chr(10).join([f"{i+1}. M{eq['magnitude']:.1f} - {eq['region']} - {eq['place']} - {eq['time']} - Depth: {eq['depth']:.1f}km - Energy: {format_energy(eq['energy'])}" for i, eq in enumerate(significant_earthquakes)])}

**PHASE 2: ADVANCED ANALYTICS**

**Seismic Clustering Analysis**:
- **Total clusters detected**: {len(clusters)}
{chr(10).join([f"  - Cluster {i+1}: {cluster['count']} events in {cluster['region']}, Center: ({cluster['center_lat']:.2f}°N, {cluster['center_lon']:.2f}°E), Max Mag: M{cluster['max_magnitude']:.1f}, Avg: M{cluster['avg_magnitude']:.1f}" for i, cluster in enumerate(clusters[:5])]) if clusters else "  - No significant clusters detected"}

**Mainshock-Aftershock Sequences**:
- **Total sequences identified**: {len(sequences)}
{chr(10).join([f"  - Sequence {i+1}: M{seq['mainshock']['magnitude']:.1f} mainshock at {seq['location']}, {seq['aftershock_count']} aftershocks, Largest aftershock: M{seq['largest_aftershock']['magnitude']:.1f}" for i, seq in enumerate(sequences)]) if sequences else "  - No significant sequences detected"}

**Regional Risk Assessment** (Score 0-100):
- **Luzon**: Risk Score = {risk_scores['Luzon']['score']} ({risk_scores['Luzon']['level']})
  - Activity: {risk_scores['Luzon']['factors']['activity']}, Magnitude: {risk_scores['Luzon']['factors']['magnitude']}, Significant Events: {risk_scores['Luzon']['factors']['significant_events']}, Shallow Depth: {risk_scores['Luzon']['factors']['shallow_depth']}
- **Visayas**: Risk Score = {risk_scores['Visayas']['score']} ({risk_scores['Visayas']['level']})
  - Activity: {risk_scores['Visayas']['factors']['activity']}, Magnitude: {risk_scores['Visayas']['factors']['magnitude']}, Significant Events: {risk_scores['Visayas']['factors']['significant_events']}, Shallow Depth: {risk_scores['Visayas']['factors']['shallow_depth']}
- **Mindanao**: Risk Score = {risk_scores['Mindanao']['score']} ({risk_scores['Mindanao']['level']})
  - Activity: {risk_scores['Mindanao']['factors']['activity']}, Magnitude: {risk_scores['Mindanao']['factors']['magnitude']}, Significant Events: {risk_scores['Mindanao']['factors']['significant_events']}, Shallow Depth: {risk_scores['Mindanao']['factors']['shallow_depth']}

**Temporal Trends**:
- **Overall trend**: {trends['overall_trend']}
- Segment breakdown:
{chr(10).join([f"  - {seg['period']}: {seg['count']} events (Avg M{seg['avg_magnitude']:.1f}), {seg['significant_count']} significant" for seg in trends['segments']])}

**Gutenberg-Richter Analysis**:
- **b-value**: {b_value if b_value else 'Insufficient data (need M≥3.0 events)'}
  - Normal b-value ~ 1.0. Higher values indicate more small earthquakes relative to large ones; lower values may indicate stress accumulation.

**Volcano-Earthquake Correlation**:
{chr(10).join([f"  - **{volcano}**: {data['earthquake_count']} earthquakes nearby, Max: M{data['max_magnitude']:.1f}, Avg: M{data['avg_magnitude']:.1f}, Significant: {data['significant_count']}" for volcano, data in volcano_correlation.items()]) if volcano_correlation else "  - No significant seismic activity near monitored volcanoes"}

Based on this comprehensive 90-day dataset with PHASE 1 enhancements (regional analysis, historical comparison, seismic energy) and PHASE 2 advanced analytics (clustering, sequence detection, risk scoring, trend analysis, Gutenberg-Richter, volcano correlation), provide a detailed, structured analysis covering:

## Executive Summary
Provide a concise overview (3-4 sentences) with the most critical findings and overall risk level.

## Seismic Activity Overview
Assess whether current activity is normal, elevated, or concerning compared to historical baselines.

## Regional Analysis
Compare seismic patterns across Luzon, Visayas, and Mindanao. Discuss the risk scores and what they mean for each region.

## Advanced Pattern Recognition
Analyze the detected clusters and aftershock sequences. What do these patterns tell us about ongoing seismic processes?

## Temporal Trends
Examine the trend analysis segments. Are we seeing increasing, decreasing, or stable activity? What might this indicate?

## Depth and Energy Analysis
Discuss depth distributions and energy release patterns. Are shallow, high-damage-potential earthquakes a concern?

## Statistical Insights
Interpret the b-value (if available). What does it tell us about the stress state in the region?

## Volcano-Earthquake Relationships
Analyze seismic activity near volcanoes. Are there any concerning correlations that might indicate volcanic unrest?

## Risk Assessment by Region
Provide detailed risk assessments for Luzon, Visayas, and Mindanao based on all available data.

## Recommendations
Provide specific, actionable recommendations:
- For residents in each region
- For local authorities and emergency services
- For monitoring and preparedness efforts

Be specific, professional, data-driven, and structure your response with clear headings and sections.

**FORMATTING REQUIREMENTS - CRITICAL**:
- Use proper markdown formatting throughout your response
- Start main sections with ## (h2 headings)
- Use ### (h3 headings) for subsections
- Use **bold** for emphasis on key terms and important information
- Use bullet points (- ) for lists, NOT asterisks or other symbols
- Use numbered lists (1. 2. 3.) for sequential information
- Ensure blank lines between paragraphs and sections
- Use single backticks `like this` for inline technical terms, magnitude values (e.g., `M 5.2`), coordinates
- NEVER use code blocks (```) for magnitude values or short technical terms - only use single backticks `
- Code blocks (```) should ONLY be used for multi-line code or data, not for inline values
- Keep paragraphs concise (2-4 sentences max)
- Use > for important warnings or critical information as blockquotes
- Do NOT use unicode symbols like •, ×, ÷ - use markdown formatting instead
- Ensure all lists have proper spacing and indentation
- Start your response immediately with content, no meta-text like "Here is my analysis:"
- Write in a clear, professional tone suitable for public safety information

Your response will be rendered with ReactMarkdown, so proper markdown syntax is essential for readability."""
        
        # Get model configuration
        model_config = get_model_config(selected_model)
        
        # Call OpenRouter API using requests
        # Try selected model first, then fallback models
        models_to_try = [selected_model]
        # Add fallback models that aren't the selected model
        models_to_try.extend([m for m in FALLBACK_MODELS if m != selected_model])
        
        analysis = None
        last_error = None
        
        for model in models_to_try:
            try:
                openrouter_response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/Eplisium/PhilEarthStats",
                        "X-Title": "PhilEarthStats - Philippines Earthquake & Volcano Monitor"
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
                        "temperature": model_config.get('temperature', 0.7),
                        "max_tokens": model_config.get('max_tokens', 3000)
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
        
        # Prepare response data
        response_data = {
            'success': True,
            'analysis': analysis,
            'statistics': stats,
            'regional_breakdown': regional_stats,
            'historical_comparison': historical_comparison,
            'risk_scores': risk_scores,
            'clusters': [{
                'center_lat': c['center_lat'],
                'center_lon': c['center_lon'],
                'count': c['count'],
                'max_magnitude': c['max_magnitude'],
                'avg_magnitude': c['avg_magnitude'],
                'region': c['region']
            } for c in clusters],
            'sequences': [{
                'mainshock_magnitude': s['mainshock']['magnitude'],
                'mainshock_location': s['location'],
                'aftershock_count': s['aftershock_count'],
                'largest_aftershock_magnitude': s['largest_aftershock']['magnitude']
            } for s in sequences],
            'trends': trends,
            'b_value': b_value,
            'volcano_correlation': volcano_correlation,
            'significant_earthquakes': significant_earthquakes[:5],
            'metadata': {
                'model': used_model,
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'period': '90 days',
                'data_points': len(earthquakes),
                'phase': 'Phase 4 - Complete with Caching & History',
                'features': [
                    'Extended 90-day analysis',
                    'Regional breakdown (Luzon/Visayas/Mindanao)',
                    'Seismic energy calculations',
                    'Historical comparison',
                    'Enhanced depth analysis',
                    'Spatial clustering detection',
                    'Mainshock-aftershock sequence identification',
                    'Regional risk scoring (0-100)',
                    'Temporal trend analysis',
                    'Gutenberg-Richter b-value',
                    'Volcano-earthquake correlation',
                    'Structured AI output',
                    'Analysis history tracking',
                    'Performance optimizations'
                ]
            }
        }
        
        # Phase 4.4: Save analysis to history if session_id provided
        session_id = request_data.get('session_id')
        if session_id:
            try:
                DatabaseService.save_analysis_history(session_id, response_data)
            except Exception as e:
                print(f"Warning: Failed to save analysis history: {e}")
                # Don't fail the request if history saving fails
        
        return jsonify(response_data)
    
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

# ===== PHASE 4: AI ANALYSIS HISTORY ENDPOINTS =====

@app.route('/api/ai/history', methods=['GET'])
def get_ai_history():
    """Get AI analysis history for a session"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id parameter is required'
            }), 400
        
        limit = request.args.get('limit', 20, type=int)
        history = DatabaseService.get_analysis_history(session_id, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(history),
            'history': history,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch analysis history: {str(e)}'
        }), 500

@app.route('/api/ai/history/<int:analysis_id>', methods=['GET'])
def get_ai_history_by_id(analysis_id):
    """Get a specific AI analysis by ID"""
    try:
        analysis = DatabaseService.get_analysis_by_id(analysis_id)
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch analysis: {str(e)}'
        }), 500

@app.route('/api/ai/history/<int:analysis_id>', methods=['DELETE'])
def delete_ai_history(analysis_id):
    """Delete a specific AI analysis"""
    try:
        request_data = request.get_json() or {}
        session_id = request_data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id is required'
            }), 400
        
        success = DatabaseService.delete_analysis(analysis_id, session_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Analysis not found or unauthorized'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Analysis deleted successfully',
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete analysis: {str(e)}'
        }), 500

# ========== AI SEISMIC INSIGHTS ENGINE ENDPOINTS ==========

@app.route('/api/insights/config', methods=['GET'])
def get_insights_config():
    """Get AI Insights Engine configuration"""
    try:
        engine = InsightsEngine()
        status = engine.get_status()
        
        return jsonify({
            'success': True,
            'config': status,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get config: {str(e)}'
        }), 500

@app.route('/api/insights/config', methods=['POST'])
def update_insights_config():
    """Update AI Insights Engine configuration"""
    try:
        data = request.json
        
        enabled = data.get('enabled')
        frequency_hours = data.get('frequency_hours')
        ai_model = data.get('ai_model')
        min_confidence = data.get('min_confidence')
        
        success = DatabaseService.update_engine_config(
            enabled=enabled,
            frequency_hours=frequency_hours,
            ai_model=ai_model,
            min_confidence=min_confidence
        )
        
        if success:
            engine = InsightsEngine()
            status = engine.get_status()
            
            return jsonify({
                'success': True,
                'config': status,
                'message': 'Configuration updated successfully',
                'metadata': {
                    'generated': int(time.time() * 1000),
                    'server_time_utc': datetime.utcnow().isoformat() + 'Z'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update configuration'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update config: {str(e)}'
        }), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get active seismic insights with optional filtering"""
    try:
        insight_type = request.args.get('type')
        region = request.args.get('region')
        limit = int(request.args.get('limit', 50))
        
        insights = DatabaseService.get_active_insights(
            insight_type=insight_type,
            region=region,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'count': len(insights),
            'insights': insights,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'filters': {
                    'type': insight_type,
                    'region': region,
                    'limit': limit
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get insights: {str(e)}'
        }), 500

@app.route('/api/insights/recent', methods=['GET'])
def get_recent_insights():
    """Get recently created or updated insights"""
    try:
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 20))
        
        insights = DatabaseService.get_recent_insights(hours=hours, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(insights),
            'insights': insights,
            'time_window_hours': hours,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get recent insights: {str(e)}'
        }), 500

@app.route('/api/insights/<int:insight_id>', methods=['GET'])
def get_insight_details(insight_id):
    """Get detailed information about a specific insight"""
    try:
        insight = DatabaseService.get_insight_by_id(insight_id)
        
        if not insight:
            return jsonify({
                'success': False,
                'error': 'Insight not found'
            }), 404
        
        # Get history for this insight
        history = DatabaseService.get_insight_history(insight_id, limit=10)
        
        return jsonify({
            'success': True,
            'insight': insight,
            'history': history,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get insight details: {str(e)}'
        }), 500

@app.route('/api/insights/statistics', methods=['GET'])
def get_insights_statistics():
    """Get overall statistics about generated insights"""
    try:
        stats = DatabaseService.get_insights_statistics()
        
        if not stats:
            return jsonify({
                'success': False,
                'error': 'Failed to get statistics'
            }), 500
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get statistics: {str(e)}'
        }), 500

@app.route('/api/insights/run', methods=['POST'])
def trigger_insights_run():
    """Manually trigger an insights generation run"""
    try:
        engine = InsightsEngine()
        
        # Check if engine can run
        can_run, message = engine.should_run()
        
        # Allow manual override
        force = request.json.get('force', False) if request.json else False
        
        if not can_run and not force:
            return jsonify({
                'success': False,
                'error': message,
                'can_override': True
            }), 400
        
        # Fetch recent earthquakes to analyze
        # Use real-time feeds for faster, current data
        def fetch_earthquakes():
            all_earthquakes = {}
            
            # Use real-time feeds for 14-day data
            for feed_url in [USGS_FEED_HOUR, USGS_FEED_DAY, USGS_FEED_WEEK]:
                try:
                    response = requests.get(feed_url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Filter to Philippines region and magnitude >= 2.5
                    for feature in data['features']:
                        coords = feature['geometry']['coordinates']
                        lat, lon = coords[1], coords[0]
                        mag = feature['properties'].get('mag')
                        
                        # Only include earthquakes in Philippines with mag >= 2.5
                        if is_in_philippines(lat, lon) and mag is not None and mag >= 2.5:
                            eq_id = feature['id']
                            if eq_id not in all_earthquakes:
                                props = feature['properties']
                                all_earthquakes[eq_id] = {
                                    'id': eq_id,
                                    'magnitude': mag,
                                    'place': props.get('place'),
                                    'time': props.get('time'),
                                    'longitude': coords[0],
                                    'latitude': coords[1],
                                    'depth': coords[2]
                                }
                except Exception as e:
                    print(f"Warning: Failed to fetch from {feed_url}: {str(e)}")
                    continue
            
            earthquakes = list(all_earthquakes.values())
            
            return earthquakes
        
        earthquakes = fetch_earthquakes()
        
        # Run the analysis
        result = engine.run_analysis(earthquakes)
        
        return jsonify({
            'success': result.get('success', False),
            'insights_generated': result.get('insights_generated', 0),
            'duration_seconds': result.get('duration_seconds', 0),
            'earthquakes_analyzed': result.get('earthquakes_analyzed', 0),
            'error': result.get('error'),
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z',
                'manual_trigger': True,
                'data_source': 'USGS Real-time GeoJSON Feeds',
                'feed_update_frequency': '1-5 minutes'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to run insights generation: {str(e)}'
        }), 500

@app.route('/api/insights/<int:insight_id>', methods=['DELETE'])
def delete_insight(insight_id):
    """Invalidate/delete a specific insight"""
    try:
        reason = request.json.get('reason', 'Manually invalidated') if request.json else 'Manually invalidated'
        
        success = DatabaseService.invalidate_insight(insight_id, reason=reason)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Insight invalidated successfully',
                'metadata': {
                    'generated': int(time.time() * 1000),
                    'server_time_utc': datetime.utcnow().isoformat() + 'Z'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Insight not found or already invalidated'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete insight: {str(e)}'
        }), 500

@app.route('/api/insights/category/<category>', methods=['GET'])
def get_insights_by_category(category):
    """Get insights filtered by category"""
    try:
        limit = int(request.args.get('limit', 20))
        
        insights = DatabaseService.get_insights_by_category(category, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(insights),
            'category': category,
            'insights': insights,
            'metadata': {
                'generated': int(time.time() * 1000),
                'server_time_utc': datetime.utcnow().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get insights by category: {str(e)}'
        }), 500

# Serve static files (production)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Serve the React app static files"""
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    else:
        return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
