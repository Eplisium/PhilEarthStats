from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
import json
import hashlib

db = SQLAlchemy()

class EarthquakeEvent(db.Model):
    """Store historical earthquake events"""
    __tablename__ = 'earthquake_events'
    
    id = db.Column(db.String(100), primary_key=True)
    magnitude = db.Column(db.Float, nullable=False)
    place = db.Column(db.String(255))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False, index=True)
    significance = db.Column(db.Integer)
    felt = db.Column(db.Integer)
    alert = db.Column(db.String(20))
    tsunami = db.Column(db.Integer)
    event_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'magnitude': self.magnitude,
            'place': self.place,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'depth': self.depth,
            'time': int(self.time.timestamp() * 1000),
            'time_formatted': self.time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'significance': self.significance,
            'felt': self.felt,
            'alert': self.alert,
            'tsunami': self.tsunami,
            'type': self.event_type,
            'status': self.status
        }

class YearStatistics(db.Model):
    """Store yearly earthquake statistics for worst years tracking"""
    __tablename__ = 'year_statistics'
    
    year = db.Column(db.Integer, primary_key=True)
    total_events = db.Column(db.Integer, default=0)
    max_magnitude = db.Column(db.Float, default=0.0)
    avg_magnitude = db.Column(db.Float, default=0.0)
    total_significance = db.Column(db.Integer, default=0)
    significant_events = db.Column(db.Integer, default=0)  # M >= 4.5
    major_events = db.Column(db.Integer, default=0)  # M >= 6.0
    deaths_estimated = db.Column(db.Integer, default=0)  # Can be updated manually
    damage_level = db.Column(db.String(20))  # Low, Moderate, High, Severe
    notable_events = db.Column(db.Text)  # JSON string of notable events
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'year': self.year,
            'total_events': self.total_events,
            'max_magnitude': self.max_magnitude,
            'avg_magnitude': self.avg_magnitude,
            'total_significance': self.total_significance,
            'significant_events': self.significant_events,
            'major_events': self.major_events,
            'deaths_estimated': self.deaths_estimated,
            'damage_level': self.damage_level,
            'notable_events': json.loads(self.notable_events) if self.notable_events else [],
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class AnalysisCache(db.Model):
    """Cache expensive computation results (Phase 4.1)"""
    __tablename__ = 'analysis_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    cache_type = db.Column(db.String(50), nullable=False)  # clusters, risk_scores, trends, etc.
    data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    
    def to_dict(self):
        return {
            'cache_key': self.cache_key,
            'cache_type': self.cache_type,
            'data': json.loads(self.data),
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }

class AnalysisHistory(db.Model):
    """Store AI analysis history for comparison (Phase 4.4)"""
    __tablename__ = 'analysis_history'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)  # For grouping user's analyses
    model_used = db.Column(db.String(100), nullable=False)
    period_days = db.Column(db.Integer, default=90)
    total_count = db.Column(db.Integer)
    max_magnitude = db.Column(db.Float)
    avg_magnitude = db.Column(db.Float)
    significant_count = db.Column(db.Integer)
    total_energy = db.Column(db.Float)
    
    # Store key metrics as JSON for flexibility
    regional_stats = db.Column(db.Text)  # JSON: Luzon, Visayas, Mindanao stats
    risk_scores = db.Column(db.Text)  # JSON: Risk scores by region
    historical_comparison = db.Column(db.Text)  # JSON: Comparison data
    clusters_count = db.Column(db.Integer, default=0)
    sequences_count = db.Column(db.Integer, default=0)
    b_value = db.Column(db.Float)
    trend = db.Column(db.String(50))  # Increasing, Decreasing, Stable
    
    # Store the full analysis text
    analysis_text = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self, include_full_text=False):
        result = {
            'id': self.id,
            'session_id': self.session_id,
            'model_used': self.model_used,
            'period_days': self.period_days,
            'statistics': {
                'total_count': self.total_count,
                'max_magnitude': self.max_magnitude,
                'avg_magnitude': self.avg_magnitude,
                'significant_count': self.significant_count,
                'total_energy': self.total_energy
            },
            'regional_stats': json.loads(self.regional_stats) if self.regional_stats else None,
            'risk_scores': json.loads(self.risk_scores) if self.risk_scores else None,
            'historical_comparison': json.loads(self.historical_comparison) if self.historical_comparison else None,
            'clusters_count': self.clusters_count,
            'sequences_count': self.sequences_count,
            'b_value': self.b_value,
            'trend': self.trend,
            'created_at': self.created_at.isoformat(),
            'created_at_timestamp': int(self.created_at.timestamp() * 1000)
        }
        
        if include_full_text:
            result['analysis_text'] = self.analysis_text
        
        return result

# ========== AI SEISMIC INSIGHTS ENGINE MODELS ==========

class EngineConfig(db.Model):
    """Store AI Insights Engine configuration and state"""
    __tablename__ = 'engine_config'
    
    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    analysis_frequency_hours = db.Column(db.Integer, default=6)  # Run every 6 hours by default
    last_run_at = db.Column(db.DateTime, index=True)
    next_run_at = db.Column(db.DateTime, index=True)
    total_runs = db.Column(db.Integer, default=0)
    total_insights_generated = db.Column(db.Integer, default=0)
    ai_model = db.Column(db.String(100))  # Which AI model to use
    min_confidence_threshold = db.Column(db.Float, default=0.6)  # Minimum confidence to store insight
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'enabled': self.enabled,
            'analysis_frequency_hours': self.analysis_frequency_hours,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'total_runs': self.total_runs,
            'total_insights_generated': self.total_insights_generated,
            'ai_model': self.ai_model,
            'min_confidence_threshold': self.min_confidence_threshold,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SeismicInsight(db.Model):
    """Store AI-generated seismic insights"""
    __tablename__ = 'seismic_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    insight_type = db.Column(db.String(50), nullable=False, index=True)  # risk, pattern, anomaly, correlation, prediction
    category = db.Column(db.String(50))  # shallow_activity, cluster_formation, regional_risk, etc.
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Geographic scope
    region = db.Column(db.String(100))  # Luzon, Visayas, Mindanao, or specific location
    location = db.Column(db.String(255))  # More specific location
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Insight metadata
    confidence_score = db.Column(db.Float, default=0.5)  # 0.0 to 1.0
    severity_level = db.Column(db.String(20))  # low, moderate, high, critical
    status = db.Column(db.String(20), default='active')  # active, updated, invalidated, evolved
    
    # Data supporting the insight
    supporting_data = db.Column(db.Text)  # JSON: earthquake IDs, statistics, etc.
    earthquake_count = db.Column(db.Integer, default=0)
    magnitude_range = db.Column(db.String(50))  # e.g., "M3.5 - M5.2"
    depth_range = db.Column(db.String(50))  # e.g., "5km - 15km"
    time_window_days = db.Column(db.Integer)  # Number of days analyzed
    
    # Lifecycle tracking
    version = db.Column(db.Integer, default=1)
    parent_insight_id = db.Column(db.Integer, db.ForeignKey('seismic_insights.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    valid_until = db.Column(db.DateTime)  # When this insight should be re-evaluated
    
    # AI metadata
    generated_by_model = db.Column(db.String(100))
    generation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'insight_type': self.insight_type,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'region': self.region,
            'location': self.location,
            'coordinates': {
                'latitude': self.latitude,
                'longitude': self.longitude
            } if self.latitude and self.longitude else None,
            'confidence_score': self.confidence_score,
            'severity_level': self.severity_level,
            'status': self.status,
            'supporting_data': json.loads(self.supporting_data) if self.supporting_data else {},
            'earthquake_count': self.earthquake_count,
            'magnitude_range': self.magnitude_range,
            'depth_range': self.depth_range,
            'time_window_days': self.time_window_days,
            'version': self.version,
            'parent_insight_id': self.parent_insight_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'generated_by_model': self.generated_by_model,
            'age_hours': (datetime.utcnow() - self.created_at).total_seconds() / 3600
        }

class InsightHistory(db.Model):
    """Track how insights evolve over time"""
    __tablename__ = 'insight_history'
    
    id = db.Column(db.Integer, primary_key=True)
    insight_id = db.Column(db.Integer, db.ForeignKey('seismic_insights.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # created, updated, confidence_changed, invalidated, evolved
    previous_state = db.Column(db.Text)  # JSON snapshot of previous state
    new_state = db.Column(db.Text)  # JSON snapshot of new state
    reason = db.Column(db.Text)  # Why the change occurred
    triggered_by_event_id = db.Column(db.String(100))  # Which earthquake triggered the update
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'insight_id': self.insight_id,
            'action': self.action,
            'previous_state': json.loads(self.previous_state) if self.previous_state else None,
            'new_state': json.loads(self.new_state) if self.new_state else None,
            'reason': self.reason,
            'triggered_by_event_id': self.triggered_by_event_id,
            'timestamp': self.timestamp.isoformat()
        }

class InsightTrigger(db.Model):
    """Log what events/patterns triggered insight generation"""
    __tablename__ = 'insight_triggers'
    
    id = db.Column(db.Integer, primary_key=True)
    trigger_type = db.Column(db.String(50), nullable=False)  # new_earthquake, pattern_detected, threshold_exceeded
    trigger_description = db.Column(db.Text)
    earthquake_ids = db.Column(db.Text)  # JSON array of related earthquake IDs
    insights_generated = db.Column(db.Integer, default=0)
    analysis_duration_seconds = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trigger_type': self.trigger_type,
            'trigger_description': self.trigger_description,
            'earthquake_ids': json.loads(self.earthquake_ids) if self.earthquake_ids else [],
            'insights_generated': self.insights_generated,
            'analysis_duration_seconds': self.analysis_duration_seconds,
            'timestamp': self.timestamp.isoformat()
        }

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def initialize_database(app):
        """Initialize the database with the Flask app"""
        db.init_app(app)
        with app.app_context():
            try:
                # Create tables if they don't exist (Flask-SQLAlchemy checks first by default)
                db.create_all()
            except Exception as e:
                # Tables likely already exist from another worker, this is fine
                pass
            
            # Seed historical data with proper race condition handling
            try:
                # Check if database is empty and seed if needed
                if YearStatistics.query.count() == 0:
                    DatabaseService.seed_historical_data()
                    db.session.commit()
                    print(f"✓ Historical data seeded successfully")
                else:
                    print(f"✓ Historical data already present in database")
            except Exception as e:
                db.session.rollback()
                # Another worker likely seeded already or seeding in progress
                # Check if data is now present
                try:
                    count = YearStatistics.query.count()
                    if count > 0:
                        print(f"✓ Historical data already present ({count} years)")
                    else:
                        print(f"⚠ Warning during seeding: {e}")
                except:
                    print(f"✓ Database initialization complete")
            
            # Clean up expired cache entries
            try:
                DatabaseService.cleanup_expired_cache()
            except:
                pass
    
    @staticmethod
    def seed_historical_data():
        """Seed database with notable historical earthquake years in Philippines"""
        historical_years = [
            {
                'year': 1976,
                'total_events': 87,
                'max_magnitude': 7.9,
                'avg_magnitude': 4.2,
                'total_significance': 8942,
                'significant_events': 12,
                'major_events': 1,
                'deaths_estimated': 8000,
                'damage_level': 'Severe',
                'notable_events': json.dumps([
                    {
                        'date': '1976-08-16',
                        'magnitude': 7.9,
                        'location': 'Moro Gulf',
                        'deaths': 8000,
                        'description': 'Moro Gulf Earthquake - Generated tsunami'
                    }
                ])
            },
            {
                'year': 1990,
                'total_events': 156,
                'max_magnitude': 7.8,
                'avg_magnitude': 4.5,
                'total_significance': 12453,
                'significant_events': 23,
                'major_events': 1,
                'deaths_estimated': 2412,
                'damage_level': 'Severe',
                'notable_events': json.dumps([
                    {
                        'date': '1990-07-16',
                        'magnitude': 7.8,
                        'location': 'Luzon',
                        'deaths': 2412,
                        'description': 'Luzon Earthquake - Destroyed buildings in Baguio'
                    }
                ])
            },
            {
                'year': 2012,
                'total_events': 234,
                'max_magnitude': 7.6,
                'avg_magnitude': 4.1,
                'total_significance': 9876,
                'significant_events': 34,
                'major_events': 1,
                'deaths_estimated': 52,
                'damage_level': 'High',
                'notable_events': json.dumps([
                    {
                        'date': '2012-08-31',
                        'magnitude': 7.6,
                        'location': 'Samar',
                        'deaths': 52,
                        'description': 'Generated small tsunami waves'
                    }
                ])
            },
            {
                'year': 2013,
                'total_events': 312,
                'max_magnitude': 7.2,
                'avg_magnitude': 4.3,
                'total_significance': 11234,
                'significant_events': 45,
                'major_events': 1,
                'deaths_estimated': 222,
                'damage_level': 'High',
                'notable_events': json.dumps([
                    {
                        'date': '2013-10-15',
                        'magnitude': 7.2,
                        'location': 'Bohol',
                        'deaths': 222,
                        'description': 'Bohol Earthquake - Damaged historic churches'
                    }
                ])
            },
            {
                'year': 2019,
                'total_events': 289,
                'max_magnitude': 6.9,
                'avg_magnitude': 4.0,
                'total_significance': 8234,
                'significant_events': 38,
                'major_events': 3,
                'deaths_estimated': 21,
                'damage_level': 'Moderate',
                'notable_events': json.dumps([
                    {
                        'date': '2019-10-16',
                        'magnitude': 6.3,
                        'location': 'Cotabato',
                        'deaths': 5,
                        'description': 'Part of October 2019 earthquake sequence'
                    },
                    {
                        'date': '2019-10-29',
                        'magnitude': 6.5,
                        'location': 'Cotabato',
                        'deaths': 10,
                        'description': 'Part of October 2019 earthquake sequence'
                    },
                    {
                        'date': '2019-12-15',
                        'magnitude': 6.9,
                        'location': 'Davao del Sur',
                        'deaths': 6,
                        'description': 'Caused landslides and damage'
                    }
                ])
            },
            {
                'year': datetime.utcnow().year,
                'total_events': 0,
                'max_magnitude': 0.0,
                'avg_magnitude': 0.0,
                'total_significance': 0,
                'significant_events': 0,
                'major_events': 0,
                'deaths_estimated': 0,
                'damage_level': 'Low',
                'notable_events': json.dumps([])
            }
        ]
        
        # Add all historical years in one transaction
        # This function is only called when count is 0, so safe to insert all
        for year_data in historical_years:
            year_stat = YearStatistics(**year_data)
            db.session.add(year_stat)
        
        # Commit is handled by parent function
    
    @staticmethod
    def store_earthquake(earthquake_data):
        """Store or update an earthquake event"""
        try:
            event = EarthquakeEvent.query.get(earthquake_data['id'])
            
            if not event:
                event = EarthquakeEvent(
                    id=earthquake_data['id'],
                    magnitude=earthquake_data.get('magnitude', 0),
                    place=earthquake_data.get('place', 'Unknown'),
                    latitude=earthquake_data.get('latitude', 0),
                    longitude=earthquake_data.get('longitude', 0),
                    depth=earthquake_data.get('depth', 0),
                    time=datetime.fromtimestamp(earthquake_data.get('time', 0) / 1000),
                    significance=earthquake_data.get('significance'),
                    felt=earthquake_data.get('felt'),
                    alert=earthquake_data.get('alert'),
                    tsunami=earthquake_data.get('tsunami', 0),
                    event_type=earthquake_data.get('type', 'earthquake'),
                    status=earthquake_data.get('status', 'automatic')
                )
                db.session.add(event)
            else:
                # Update existing event
                event.magnitude = earthquake_data.get('magnitude', event.magnitude)
                event.status = earthquake_data.get('status', event.status)
            
            db.session.commit()
            
            # Update year statistics
            DatabaseService.update_year_statistics(event.time.year)
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error storing earthquake: {e}")
            return False
    
    @staticmethod
    def store_multiple_earthquakes(earthquakes_list):
        """Store multiple earthquake events efficiently"""
        stored_count = 0
        for eq_data in earthquakes_list:
            if DatabaseService.store_earthquake(eq_data):
                stored_count += 1
        return stored_count
    
    @staticmethod
    def update_year_statistics(year):
        """Update statistics for a specific year"""
        try:
            # Get all earthquakes for this year
            events = EarthquakeEvent.query.filter(
                extract('year', EarthquakeEvent.time) == year
            ).all()
            
            if not events:
                return
            
            magnitudes = [e.magnitude for e in events if e.magnitude]
            
            # Get or create year statistics
            year_stat = YearStatistics.query.get(year)
            if not year_stat:
                year_stat = YearStatistics(year=year)
                db.session.add(year_stat)
            
            # Update statistics
            year_stat.total_events = len(events)
            year_stat.max_magnitude = max(magnitudes) if magnitudes else 0
            year_stat.avg_magnitude = sum(magnitudes) / len(magnitudes) if magnitudes else 0
            year_stat.total_significance = sum(e.significance or 0 for e in events)
            year_stat.significant_events = sum(1 for e in events if e.magnitude and e.magnitude >= 4.5)
            year_stat.major_events = sum(1 for e in events if e.magnitude and e.magnitude >= 6.0)
            
            # Determine damage level based on major events and max magnitude
            if year_stat.major_events >= 3 or year_stat.max_magnitude >= 7.5:
                year_stat.damage_level = 'Severe'
            elif year_stat.major_events >= 1 or year_stat.max_magnitude >= 6.5:
                year_stat.damage_level = 'High'
            elif year_stat.significant_events >= 20:
                year_stat.damage_level = 'Moderate'
            else:
                year_stat.damage_level = 'Low'
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating year statistics: {e}")
    
    @staticmethod
    def get_worst_years(limit=10):
        """Get the worst earthquake years ranked by severity"""
        try:
            # Create severity score: major events * 1000 + max_magnitude * 100 + significant_events
            years = YearStatistics.query.all()
            
            years_with_score = []
            for year in years:
                severity_score = (
                    (year.major_events * 1000) +
                    (year.max_magnitude * 100) +
                    (year.significant_events * 5) +
                    (year.deaths_estimated * 0.1)  # Factor in deaths if available
                )
                years_with_score.append({
                    **year.to_dict(),
                    'severity_score': round(severity_score, 2)
                })
            
            # Sort by severity score
            years_with_score.sort(key=lambda x: x['severity_score'], reverse=True)
            
            return years_with_score[:limit]
        except Exception as e:
            print(f"Error getting worst years: {e}")
            return []
    
    @staticmethod
    def get_events_by_year(year):
        """Get all earthquake events for a specific year"""
        try:
            events = EarthquakeEvent.query.filter(
                extract('year', EarthquakeEvent.time) == year
            ).order_by(EarthquakeEvent.magnitude.desc()).all()
            
            return [event.to_dict() for event in events]
        except Exception as e:
            print(f"Error getting events by year: {e}")
            return []
    
    @staticmethod
    def get_events_by_date_range(start_date, end_date):
        """Get earthquake events within a date range"""
        try:
            events = EarthquakeEvent.query.filter(
                and_(
                    EarthquakeEvent.time >= start_date,
                    EarthquakeEvent.time <= end_date
                )
            ).order_by(EarthquakeEvent.time.desc()).all()
            
            return [event.to_dict() for event in events]
        except Exception as e:
            print(f"Error getting events by date range: {e}")
            return []
    
    @staticmethod
    def get_calendar_data(year=None, month=None):
        """Get earthquake data organized by calendar dates"""
        try:
            if year is None:
                year = datetime.utcnow().year
            
            query = EarthquakeEvent.query.filter(
                extract('year', EarthquakeEvent.time) == year
            )
            
            if month is not None:
                query = query.filter(extract('month', EarthquakeEvent.time) == month)
            
            events = query.all()
            
            # Organize by date
            calendar_data = {}
            for event in events:
                date_key = event.time.strftime('%Y-%m-%d')
                if date_key not in calendar_data:
                    calendar_data[date_key] = {
                        'date': date_key,
                        'events': [],
                        'max_magnitude': 0,
                        'event_count': 0
                    }
                
                calendar_data[date_key]['events'].append(event.to_dict())
                calendar_data[date_key]['event_count'] += 1
                calendar_data[date_key]['max_magnitude'] = max(
                    calendar_data[date_key]['max_magnitude'],
                    event.magnitude
                )
            
            return list(calendar_data.values())
        except Exception as e:
            print(f"Error getting calendar data: {e}")
            return []
    
    # ========== PHASE 4: CACHING & HISTORY ==========
    
    @staticmethod
    def generate_cache_key(cache_type, params):
        """Generate a unique cache key based on type and parameters"""
        # Create a deterministic string from params
        param_str = json.dumps(params, sort_keys=True)
        # Hash it for a shorter key
        hash_obj = hashlib.md5(param_str.encode())
        return f"{cache_type}_{hash_obj.hexdigest()}"
    
    @staticmethod
    def get_cached_data(cache_key):
        """Retrieve cached data if not expired"""
        try:
            cache_entry = AnalysisCache.query.filter_by(cache_key=cache_key).first()
            
            if cache_entry and cache_entry.expires_at > datetime.utcnow():
                return json.loads(cache_entry.data)
            
            # Clean up expired entry if found
            if cache_entry:
                db.session.delete(cache_entry)
                db.session.commit()
            
            return None
        except Exception as e:
            print(f"Error getting cached data: {e}")
            return None
    
    @staticmethod
    def set_cached_data(cache_key, cache_type, data, ttl_hours=1):
        """Store data in cache with expiration"""
        try:
            # Delete existing entry if present
            existing = AnalysisCache.query.filter_by(cache_key=cache_key).first()
            if existing:
                db.session.delete(existing)
            
            # Create new cache entry
            cache_entry = AnalysisCache(
                cache_key=cache_key,
                cache_type=cache_type,
                data=json.dumps(data),
                expires_at=datetime.utcnow() + timedelta(hours=ttl_hours)
            )
            
            db.session.add(cache_entry)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error setting cached data: {e}")
            return False
    
    @staticmethod
    def cleanup_expired_cache():
        """Remove expired cache entries"""
        try:
            deleted = AnalysisCache.query.filter(
                AnalysisCache.expires_at < datetime.utcnow()
            ).delete()
            db.session.commit()
            if deleted > 0:
                print(f"✓ Cleaned up {deleted} expired cache entries")
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up cache: {e}")
    
    @staticmethod
    def invalidate_cache_by_type(cache_type):
        """Invalidate all cache entries of a specific type"""
        try:
            deleted = AnalysisCache.query.filter_by(cache_type=cache_type).delete()
            db.session.commit()
            return deleted
        except Exception as e:
            db.session.rollback()
            print(f"Error invalidating cache: {e}")
            return 0
    
    @staticmethod
    def save_analysis_history(session_id, analysis_data):
        """Save analysis to history (Phase 4.4)"""
        try:
            history_entry = AnalysisHistory(
                session_id=session_id,
                model_used=analysis_data.get('metadata', {}).get('model', 'unknown'),
                period_days=analysis_data.get('statistics', {}).get('period_days', 90),
                total_count=analysis_data.get('statistics', {}).get('total_count'),
                max_magnitude=analysis_data.get('statistics', {}).get('max_magnitude'),
                avg_magnitude=analysis_data.get('statistics', {}).get('avg_magnitude'),
                significant_count=analysis_data.get('statistics', {}).get('significant_count'),
                total_energy=analysis_data.get('statistics', {}).get('total_energy_joules'),
                regional_stats=json.dumps(analysis_data.get('regional_breakdown')),
                risk_scores=json.dumps(analysis_data.get('risk_scores')),
                historical_comparison=json.dumps(analysis_data.get('historical_comparison')),
                clusters_count=len(analysis_data.get('clusters', [])),
                sequences_count=len(analysis_data.get('sequences', [])),
                b_value=analysis_data.get('b_value'),
                trend=analysis_data.get('trends', {}).get('overall_trend'),
                analysis_text=analysis_data.get('analysis')
            )
            
            db.session.add(history_entry)
            db.session.commit()
            
            # Keep only last 20 analyses per session
            DatabaseService.cleanup_old_history(session_id, keep_count=20)
            
            return history_entry.id
        except Exception as e:
            db.session.rollback()
            print(f"Error saving analysis history: {e}")
            return None
    
    @staticmethod
    def get_analysis_history(session_id, limit=20):
        """Get analysis history for a session"""
        try:
            histories = AnalysisHistory.query.filter_by(session_id=session_id)\
                .order_by(AnalysisHistory.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [h.to_dict(include_full_text=False) for h in histories]
        except Exception as e:
            print(f"Error getting analysis history: {e}")
            return []
    
    @staticmethod
    def get_analysis_by_id(analysis_id):
        """Get a specific analysis by ID"""
        try:
            history = AnalysisHistory.query.get(analysis_id)
            return history.to_dict(include_full_text=True) if history else None
        except Exception as e:
            print(f"Error getting analysis by ID: {e}")
            return None
    
    @staticmethod
    def cleanup_old_history(session_id, keep_count=20):
        """Keep only the most recent N analyses per session"""
        try:
            # Get all histories for this session ordered by date
            all_histories = AnalysisHistory.query.filter_by(session_id=session_id)\
                .order_by(AnalysisHistory.created_at.desc())\
                .all()
            
            # Delete old ones beyond keep_count
            if len(all_histories) > keep_count:
                to_delete = all_histories[keep_count:]
                for history in to_delete:
                    db.session.delete(history)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up old history: {e}")
    
    @staticmethod
    def delete_analysis(analysis_id, session_id):
        """Delete a specific analysis (with session validation)"""
        try:
            history = AnalysisHistory.query.filter_by(
                id=analysis_id,
                session_id=session_id
            ).first()
            
            if history:
                db.session.delete(history)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting analysis: {e}")
            return False
    
    # ========== AI SEISMIC INSIGHTS ENGINE SERVICES ==========
    
    @staticmethod
    def get_engine_config():
        """Get or create engine configuration"""
        try:
            config = EngineConfig.query.first()
            if not config:
                # Create default configuration
                config = EngineConfig(
                    enabled=False,
                    analysis_frequency_hours=6,
                    ai_model='x-ai/grok-4-fast',
                    min_confidence_threshold=0.6
                )
                db.session.add(config)
                db.session.commit()
            return config
        except Exception as e:
            print(f"Error getting engine config: {e}")
            return None
    
    @staticmethod
    def update_engine_config(enabled=None, frequency_hours=None, ai_model=None, min_confidence=None):
        """Update engine configuration"""
        try:
            config = DatabaseService.get_engine_config()
            if not config:
                return False
            
            if enabled is not None:
                config.enabled = enabled
                # Schedule next run if enabling
                if enabled and not config.next_run_at:
                    config.next_run_at = datetime.utcnow() + timedelta(hours=config.analysis_frequency_hours)
            
            if frequency_hours is not None:
                config.analysis_frequency_hours = frequency_hours
                # Reschedule next run
                if config.enabled:
                    config.next_run_at = datetime.utcnow() + timedelta(hours=frequency_hours)
            
            if ai_model is not None:
                config.ai_model = ai_model
            
            if min_confidence is not None:
                config.min_confidence_threshold = min_confidence
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating engine config: {e}")
            return False
    
    @staticmethod
    def record_engine_run():
        """Record that the engine completed a run"""
        try:
            config = DatabaseService.get_engine_config()
            if config:
                config.last_run_at = datetime.utcnow()
                config.total_runs += 1
                config.next_run_at = datetime.utcnow() + timedelta(hours=config.analysis_frequency_hours)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error recording engine run: {e}")
            return False
    
    @staticmethod
    def create_insight(insight_data):
        """Create a new seismic insight"""
        try:
            insight = SeismicInsight(
                insight_type=insight_data.get('insight_type'),
                category=insight_data.get('category'),
                title=insight_data.get('title'),
                description=insight_data.get('description'),
                region=insight_data.get('region'),
                location=insight_data.get('location'),
                latitude=insight_data.get('latitude'),
                longitude=insight_data.get('longitude'),
                confidence_score=insight_data.get('confidence_score', 0.5),
                severity_level=insight_data.get('severity_level', 'moderate'),
                status='active',
                supporting_data=json.dumps(insight_data.get('supporting_data', {})),
                earthquake_count=insight_data.get('earthquake_count', 0),
                magnitude_range=insight_data.get('magnitude_range'),
                depth_range=insight_data.get('depth_range'),
                time_window_days=insight_data.get('time_window_days'),
                valid_until=insight_data.get('valid_until'),
                generated_by_model=insight_data.get('generated_by_model'),
                version=1
            )
            
            db.session.add(insight)
            db.session.commit()
            
            # Record creation in history
            DatabaseService.record_insight_history(
                insight.id,
                'created',
                None,
                insight.to_dict(),
                f"Insight created by {insight_data.get('generated_by_model', 'AI')}"
            )
            
            # Update engine stats
            config = DatabaseService.get_engine_config()
            if config:
                config.total_insights_generated += 1
                db.session.commit()
            
            return insight.id
        except Exception as e:
            db.session.rollback()
            print(f"Error creating insight: {e}")
            return None
    
    @staticmethod
    def update_insight(insight_id, updates, reason=None, triggered_by_event=None):
        """Update an existing insight"""
        try:
            insight = SeismicInsight.query.get(insight_id)
            if not insight:
                return False
            
            # Capture previous state
            previous_state = insight.to_dict()
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(insight, key):
                    if key == 'supporting_data':
                        setattr(insight, key, json.dumps(value))
                    else:
                        setattr(insight, key, value)
            
            insight.version += 1
            insight.status = 'updated'
            
            db.session.commit()
            
            # Record in history
            DatabaseService.record_insight_history(
                insight_id,
                'updated',
                previous_state,
                insight.to_dict(),
                reason or "Insight updated based on new data",
                triggered_by_event
            )
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating insight: {e}")
            return False
    
    @staticmethod
    def invalidate_insight(insight_id, reason=None):
        """Mark an insight as invalidated"""
        try:
            insight = SeismicInsight.query.get(insight_id)
            if not insight:
                return False
            
            previous_state = insight.to_dict()
            insight.status = 'invalidated'
            
            db.session.commit()
            
            DatabaseService.record_insight_history(
                insight_id,
                'invalidated',
                previous_state,
                insight.to_dict(),
                reason or "Pattern no longer detected in recent data"
            )
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error invalidating insight: {e}")
            return False
    
    @staticmethod
    def get_active_insights(insight_type=None, region=None, limit=50):
        """Get active insights with optional filtering"""
        try:
            query = SeismicInsight.query.filter_by(status='active')
            
            if insight_type:
                query = query.filter_by(insight_type=insight_type)
            
            if region:
                query = query.filter_by(region=region)
            
            insights = query.order_by(SeismicInsight.created_at.desc()).limit(limit).all()
            return [insight.to_dict() for insight in insights]
        except Exception as e:
            print(f"Error getting active insights: {e}")
            return []
    
    @staticmethod
    def get_recent_insights(hours=24, limit=20):
        """Get insights created or updated in the last N hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            insights = SeismicInsight.query.filter(
                SeismicInsight.updated_at >= cutoff_time
            ).order_by(SeismicInsight.updated_at.desc()).limit(limit).all()
            
            return [insight.to_dict() for insight in insights]
        except Exception as e:
            print(f"Error getting recent insights: {e}")
            return []
    
    @staticmethod
    def get_insight_by_id(insight_id):
        """Get a specific insight by ID"""
        try:
            insight = SeismicInsight.query.get(insight_id)
            return insight.to_dict() if insight else None
        except Exception as e:
            print(f"Error getting insight by ID: {e}")
            return None
    
    @staticmethod
    def get_insight_history(insight_id, limit=20):
        """Get history for a specific insight"""
        try:
            history = InsightHistory.query.filter_by(insight_id=insight_id)\
                .order_by(InsightHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting insight history: {e}")
            return []
    
    @staticmethod
    def record_insight_history(insight_id, action, previous_state, new_state, reason, triggered_by_event=None):
        """Record an insight history entry"""
        try:
            history = InsightHistory(
                insight_id=insight_id,
                action=action,
                previous_state=json.dumps(previous_state) if previous_state else None,
                new_state=json.dumps(new_state) if new_state else None,
                reason=reason,
                triggered_by_event_id=triggered_by_event
            )
            
            db.session.add(history)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error recording insight history: {e}")
            return False
    
    @staticmethod
    def create_insight_trigger(trigger_type, description, earthquake_ids, insights_generated, duration):
        """Log an insight generation trigger"""
        try:
            trigger = InsightTrigger(
                trigger_type=trigger_type,
                trigger_description=description,
                earthquake_ids=json.dumps(earthquake_ids) if earthquake_ids else None,
                insights_generated=insights_generated,
                analysis_duration_seconds=duration
            )
            
            db.session.add(trigger)
            db.session.commit()
            return trigger.id
        except Exception as e:
            db.session.rollback()
            print(f"Error creating insight trigger: {e}")
            return None
    
    @staticmethod
    def get_insights_by_category(category, limit=20):
        """Get insights by category"""
        try:
            insights = SeismicInsight.query.filter_by(
                category=category,
                status='active'
            ).order_by(SeismicInsight.confidence_score.desc()).limit(limit).all()
            
            return [insight.to_dict() for insight in insights]
        except Exception as e:
            print(f"Error getting insights by category: {e}")
            return []
    
    @staticmethod
    def get_insights_statistics():
        """Get overall statistics about insights"""
        try:
            total = SeismicInsight.query.count()
            active = SeismicInsight.query.filter_by(status='active').count()
            updated = SeismicInsight.query.filter_by(status='updated').count()
            invalidated = SeismicInsight.query.filter_by(status='invalidated').count()
            
            # Count by type
            by_type = {}
            for insight_type in ['risk', 'pattern', 'anomaly', 'correlation', 'prediction']:
                count = SeismicInsight.query.filter_by(
                    insight_type=insight_type,
                    status='active'
                ).count()
                by_type[insight_type] = count
            
            # Count by severity
            by_severity = {}
            for severity in ['low', 'moderate', 'high', 'critical']:
                count = SeismicInsight.query.filter_by(
                    severity_level=severity,
                    status='active'
                ).count()
                by_severity[severity] = count
            
            return {
                'total': total,
                'active': active,
                'updated': updated,
                'invalidated': invalidated,
                'by_type': by_type,
                'by_severity': by_severity
            }
        except Exception as e:
            print(f"Error getting insights statistics: {e}")
            return None
    
    @staticmethod
    def cleanup_old_insights(keep_days=30):
        """Clean up old invalidated insights"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
            deleted = SeismicInsight.query.filter(
                and_(
                    SeismicInsight.status == 'invalidated',
                    SeismicInsight.updated_at < cutoff_date
                )
            ).delete()
            
            db.session.commit()
            return deleted
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up old insights: {e}")
            return 0
