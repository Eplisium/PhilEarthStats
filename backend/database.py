from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
import json

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

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def initialize_database(app):
        """Initialize the database with the Flask app"""
        db.init_app(app)
        with app.app_context():
            db.create_all()
            # Initialize with historical data if database is empty
            if YearStatistics.query.count() == 0:
                DatabaseService.seed_historical_data()
    
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
        
        for year_data in historical_years:
            year_stat = YearStatistics(**year_data)
            db.session.add(year_stat)
        
        try:
            db.session.commit()
            print(f"✓ Seeded {len(historical_years)} historical years into database")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error seeding historical data: {e}")
    
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
