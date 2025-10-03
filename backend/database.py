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
