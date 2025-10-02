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
    """Get information about active volcanoes in the Philippines"""
    # Note: This data is relatively static and based on PHIVOLCS records
    # In a production system, this should be fetched from an official API
    active_volcanoes = [
        {
            'id': 1,
            'name': 'Mayon',
            'location': 'Albay',
            'latitude': 13.2572,
            'longitude': 123.6856,
            'elevation': 2463,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '2018',
            'alert_level': 0,
            'description': 'Most active volcano in the Philippines, known for its perfect cone shape'
        },
        {
            'id': 2,
            'name': 'Taal',
            'location': 'Batangas',
            'latitude': 14.0021,
            'longitude': 120.9937,
            'elevation': 311,
            'type': 'Complex volcano',
            'status': 'Alert Level 1 (Abnormal)',
            'last_eruption': '2022',
            'alert_level': 1,
            'description': 'One of the most active volcanoes, located on an island within a lake'
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
            'description': 'Famous for its catastrophic 1991 eruption, one of the largest of the 20th century'
        },
        {
            'id': 4,
            'name': 'Bulusan',
            'location': 'Sorsogon',
            'latitude': 12.7700,
            'longitude': 124.0500,
            'elevation': 1565,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '2017',
            'alert_level': 0,
            'description': 'Active volcano in southeastern Luzon'
        },
        {
            'id': 5,
            'name': 'Kanlaon',
            'location': 'Negros Island',
            'latitude': 10.4120,
            'longitude': 123.1320,
            'elevation': 2465,
            'type': 'Stratovolcano',
            'status': 'Alert Level 1 (Abnormal)',
            'last_eruption': '2020',
            'alert_level': 1,
            'description': 'Most active volcano in central Philippines'
        },
        {
            'id': 6,
            'name': 'Hibok-Hibok',
            'location': 'Camiguin',
            'latitude': 9.2030,
            'longitude': 124.6730,
            'elevation': 1332,
            'type': 'Stratovolcano',
            'status': 'Alert Level 0 (Normal)',
            'last_eruption': '1953',
            'alert_level': 0,
            'description': 'Dome volcano in Mindanao'
        }
    ]
    
    return jsonify({
        'success': True,
        'count': len(active_volcanoes),
        'volcanoes': active_volcanoes,
        'metadata': {
            'generated': int(time.time() * 1000),
            'server_time_utc': datetime.utcnow().isoformat() + 'Z',
            'title': 'Active Volcanoes in the Philippines',
            'source': 'PHIVOLCS Records',
            'note': 'Alert levels and status should be verified with official PHIVOLCS sources'
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
            '/api/volcanoes/active': 'Get active volcanoes information',
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
