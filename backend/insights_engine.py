"""
AI Seismic Insights Engine
Intelligent background analysis system that continuously monitors earthquake patterns
and generates actionable insights stored in a persistent database.
"""

import time
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import math
from database import DatabaseService
from ai_config import get_model_config, DEFAULT_MODEL
import os
import json


class InsightsEngine:
    """Core engine for generating and managing seismic insights"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def should_run(self):
        """Check if the engine should run based on configuration"""
        config = DatabaseService.get_engine_config()
        if not config or not config.enabled:
            return False, "Engine is disabled"
        
        if not self.api_key:
            return False, "No API key configured"
        
        # Check if it's time to run
        if config.next_run_at and datetime.utcnow() < config.next_run_at:
            return False, f"Next run scheduled for {config.next_run_at}"
        
        return True, "Ready to run"
    
    def run_analysis(self, earthquakes_data):
        """
        Main analysis function - generates insights from earthquake data
        
        Args:
            earthquakes_data: List of recent earthquake events
        
        Returns:
            dict with insights generated and statistics
        """
        start_time = time.time()
        insights_generated = 0
        
        config = DatabaseService.get_engine_config()
        if not config:
            return {'success': False, 'error': 'No engine configuration'}
        
        try:
            # Analyze different aspects
            pattern_insights = self._detect_patterns(earthquakes_data, config)
            anomaly_insights = self._detect_anomalies(earthquakes_data, config)
            risk_insights = self._assess_risks(earthquakes_data, config)
            correlation_insights = self._find_correlations(earthquakes_data, config)
            
            # Store all generated insights
            all_insights = pattern_insights + anomaly_insights + risk_insights + correlation_insights
            
            for insight_data in all_insights:
                if insight_data.get('confidence_score', 0) >= config.min_confidence_threshold:
                    insight_id = DatabaseService.create_insight(insight_data)
                    if insight_id:
                        insights_generated += 1
            
            # Record the run
            DatabaseService.record_engine_run()
            
            # Log the trigger
            duration = time.time() - start_time
            earthquake_ids = [eq.get('id') for eq in earthquakes_data[:20]]  # First 20 IDs
            DatabaseService.create_insight_trigger(
                trigger_type='scheduled_analysis',
                description=f'Analyzed {len(earthquakes_data)} earthquakes',
                earthquake_ids=earthquake_ids,
                insights_generated=insights_generated,
                duration=duration
            )
            
            return {
                'success': True,
                'insights_generated': insights_generated,
                'duration_seconds': duration,
                'earthquakes_analyzed': len(earthquakes_data)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': time.time() - start_time
            }
    
    def _detect_patterns(self, earthquakes, config):
        """Detect earthquake patterns (clusters, swarms, migrations)"""
        insights = []
        
        # Group by region and analyze
        regional_data = self._group_by_region(earthquakes)
        
        for region, events in regional_data.items():
            if len(events) < 5:
                continue
            
            # Check for increasing activity
            recent_7d = [e for e in events if self._days_ago(e.get('time')) <= 7]
            previous_7d = [e for e in events if 7 < self._days_ago(e.get('time')) <= 14]
            
            if len(recent_7d) > len(previous_7d) * 1.5 and len(recent_7d) >= 10:
                # Significant increase detected
                avg_mag = sum(e.get('magnitude', 0) for e in recent_7d) / len(recent_7d)
                max_mag = max(e.get('magnitude', 0) for e in recent_7d)
                
                insights.append({
                    'insight_type': 'pattern',
                    'category': 'increasing_activity',
                    'title': f'Increased Seismic Activity in {region}',
                    'description': f'{region} has experienced {len(recent_7d)} earthquakes in the past 7 days, '
                                   f'up {((len(recent_7d) - len(previous_7d)) / len(previous_7d) * 100):.0f}% from the previous week. '
                                   f'Average magnitude: M{avg_mag:.1f}, Maximum: M{max_mag:.1f}. '
                                   f'This elevated activity warrants continued monitoring.',
                    'region': region,
                    'confidence_score': min(0.7 + (len(recent_7d) / 50), 0.95),
                    'severity_level': self._calculate_severity(max_mag, len(recent_7d)),
                    'earthquake_count': len(recent_7d),
                    'magnitude_range': f'M{min(e.get("magnitude", 0) for e in recent_7d):.1f} - M{max_mag:.1f}',
                    'time_window_days': 7,
                    'valid_until': datetime.utcnow() + timedelta(days=7),
                    'generated_by_model': config.ai_model,
                    'supporting_data': {
                        'recent_count': len(recent_7d),
                        'previous_count': len(previous_7d),
                        'earthquake_ids': [e.get('id') for e in recent_7d[:10]]
                    }
                })
            
            # Check for shallow earthquake clusters
            shallow_events = [e for e in recent_7d if e.get('depth', 999) < 10]
            if len(shallow_events) >= 5:
                insights.append({
                    'insight_type': 'pattern',
                    'category': 'shallow_clustering',
                    'title': f'Shallow Earthquake Cluster in {region}',
                    'description': f'{len(shallow_events)} shallow earthquakes (depth < 10km) detected in {region} within 7 days. '
                                   f'Shallow earthquakes have higher potential for surface damage. '
                                   f'Communities should review earthquake preparedness plans.',
                    'region': region,
                    'confidence_score': 0.75,
                    'severity_level': 'moderate',
                    'earthquake_count': len(shallow_events),
                    'depth_range': f'{min(e.get("depth", 0) for e in shallow_events):.1f}km - {max(e.get("depth", 0) for e in shallow_events):.1f}km',
                    'time_window_days': 7,
                    'valid_until': datetime.utcnow() + timedelta(days=5),
                    'generated_by_model': config.ai_model,
                    'supporting_data': {
                        'shallow_count': len(shallow_events),
                        'earthquake_ids': [e.get('id') for e in shallow_events]
                    }
                })
        
        return insights
    
    def _detect_anomalies(self, earthquakes, config):
        """Detect unusual patterns or anomalies"""
        insights = []
        
        # Check for unusual magnitude-depth relationships
        for eq in earthquakes:
            mag = eq.get('magnitude', 0)
            depth = eq.get('depth', 0)
            
            # Very shallow, strong earthquake (unusual and dangerous)
            if mag >= 5.0 and depth < 5:
                insights.append({
                    'insight_type': 'anomaly',
                    'category': 'unusual_shallow_strong',
                    'title': f'Unusually Shallow M{mag:.1f} Earthquake',
                    'description': f'A magnitude {mag:.1f} earthquake at only {depth:.1f}km depth occurred near {eq.get("place", "unknown location")}. '
                                   f'This shallow depth-to-magnitude ratio is uncommon and may result in stronger ground shaking than typical. '
                                   f'Aftershocks are likely.',
                    'region': self._determine_region(eq.get('latitude'), eq.get('longitude')),
                    'location': eq.get('place'),
                    'latitude': eq.get('latitude'),
                    'longitude': eq.get('longitude'),
                    'confidence_score': 0.85,
                    'severity_level': 'high' if mag >= 6.0 else 'moderate',
                    'earthquake_count': 1,
                    'magnitude_range': f'M{mag:.1f}',
                    'depth_range': f'{depth:.1f}km',
                    'time_window_days': 1,
                    'valid_until': datetime.utcnow() + timedelta(days=3),
                    'generated_by_model': config.ai_model,
                    'supporting_data': {
                        'earthquake_id': eq.get('id'),
                        'time': eq.get('time')
                    }
                })
        
        return insights
    
    def _assess_risks(self, earthquakes, config):
        """Assess regional risk levels"""
        insights = []
        
        regional_data = self._group_by_region(earthquakes)
        
        for region, events in regional_data.items():
            recent_events = [e for e in events if self._days_ago(e.get('time')) <= 14]
            
            if not recent_events:
                continue
            
            # Calculate risk score
            significant_count = len([e for e in recent_events if e.get('magnitude', 0) >= 4.5])
            shallow_count = len([e for e in recent_events if e.get('depth', 999) < 30])
            max_mag = max(e.get('magnitude', 0) for e in recent_events)
            
            risk_score = (
                (significant_count * 15) +
                (shallow_count * 5) +
                (max_mag * 10) +
                (len(recent_events) * 2)
            )
            
            risk_level = 'low'
            if risk_score >= 80:
                risk_level = 'critical'
            elif risk_score >= 50:
                risk_level = 'high'
            elif risk_score >= 25:
                risk_level = 'moderate'
            
            if risk_level in ['high', 'critical']:
                insights.append({
                    'insight_type': 'risk',
                    'category': 'regional_risk_assessment',
                    'title': f'{risk_level.title()} Seismic Risk in {region}',
                    'description': f'Based on recent seismic activity, {region} currently has {risk_level} seismic risk. '
                                   f'Factors: {significant_count} significant earthquakes (M≥4.5), '
                                   f'{shallow_count} shallow events (<30km), maximum magnitude M{max_mag:.1f}. '
                                   f'Risk score: {risk_score:.0f}/100.',
                    'region': region,
                    'confidence_score': 0.70,
                    'severity_level': risk_level,
                    'earthquake_count': len(recent_events),
                    'time_window_days': 14,
                    'valid_until': datetime.utcnow() + timedelta(days=7),
                    'generated_by_model': config.ai_model,
                    'supporting_data': {
                        'risk_score': risk_score,
                        'significant_count': significant_count,
                        'shallow_count': shallow_count,
                        'max_magnitude': max_mag
                    }
                })
        
        return insights
    
    def _find_correlations(self, earthquakes, config):
        """Find correlations between earthquakes and other factors"""
        insights = []
        
        # Check for temporal patterns (e.g., clustering in specific time periods)
        if len(earthquakes) >= 20:
            time_distribution = defaultdict(int)
            for eq in earthquakes:
                hour = datetime.fromtimestamp(eq.get('time', 0) / 1000).hour
                time_period = 'night' if hour < 6 or hour >= 20 else 'day'
                time_distribution[time_period] += 1
            
            # Note: This is just data observation, not causation
            if time_distribution:
                total = sum(time_distribution.values())
                night_pct = (time_distribution['night'] / total * 100) if total > 0 else 0
                
                # Only report if there's interesting distribution (not just random)
                if night_pct > 60 or night_pct < 40:
                    insights.append({
                        'insight_type': 'correlation',
                        'category': 'temporal_distribution',
                        'title': 'Temporal Distribution Pattern Observed',
                        'description': f'Recent earthquake activity shows {night_pct:.0f}% occurring during night hours (8PM-6AM). '
                                       f'This is an observational pattern and does not indicate predictive capability. '
                                       f'Earthquakes can occur at any time.',
                        'region': 'Philippines',
                        'confidence_score': 0.55,
                        'severity_level': 'low',
                        'earthquake_count': len(earthquakes),
                        'time_window_days': 14,
                        'valid_until': datetime.utcnow() + timedelta(days=7),
                        'generated_by_model': config.ai_model,
                        'supporting_data': {
                            'night_count': time_distribution['night'],
                            'day_count': time_distribution['day'],
                            'night_percentage': night_pct
                        }
                    })
        
        return insights
    
    # Helper methods
    
    def _group_by_region(self, earthquakes):
        """Group earthquakes by region (Luzon, Visayas, Mindanao)"""
        regional_data = defaultdict(list)
        
        for eq in earthquakes:
            region = self._determine_region(eq.get('latitude'), eq.get('longitude'))
            regional_data[region].append(eq)
        
        return regional_data
    
    def _determine_region(self, lat, lon):
        """Determine which region an earthquake belongs to"""
        if lat is None or lon is None:
            return 'Unknown'
        
        # Rough boundaries
        if lat >= 15:
            return 'Luzon'
        elif lat >= 10:
            return 'Visayas'
        else:
            return 'Mindanao'
    
    def _days_ago(self, timestamp_ms):
        """Calculate how many days ago an earthquake occurred"""
        if not timestamp_ms:
            return 999
        
        eq_time = datetime.fromtimestamp(timestamp_ms / 1000)
        delta = datetime.utcnow() - eq_time
        return delta.days + (delta.seconds / 86400)
    
    def _calculate_severity(self, max_magnitude, event_count):
        """Calculate severity level based on magnitude and frequency"""
        if max_magnitude >= 6.5 or event_count >= 50:
            return 'critical'
        elif max_magnitude >= 5.5 or event_count >= 30:
            return 'high'
        elif max_magnitude >= 4.5 or event_count >= 15:
            return 'moderate'
        else:
            return 'low'
    
    def trigger_manual_run(self, earthquakes_data):
        """Manually trigger an insight generation run"""
        config = DatabaseService.get_engine_config()
        
        if not config:
            return {'success': False, 'error': 'Engine not configured'}
        
        if not self.api_key:
            return {'success': False, 'error': 'No API key configured'}
        
        return self.run_analysis(earthquakes_data)
    
    def get_status(self):
        """Get current engine status"""
        config = DatabaseService.get_engine_config()
        
        if not config:
            return {
                'enabled': False,
                'configured': False,
                'message': 'Engine not initialized'
            }
        
        should_run, message = self.should_run()
        stats = DatabaseService.get_insights_statistics()
        
        return {
            'enabled': config.enabled,
            'configured': True,
            'api_key_present': bool(self.api_key),
            'should_run': should_run,
            'status_message': message,
            'last_run': config.last_run_at.isoformat() if config.last_run_at else None,
            'next_run': config.next_run_at.isoformat() if config.next_run_at else None,
            'total_runs': config.total_runs,
            'total_insights_generated': config.total_insights_generated,
            'current_active_insights': stats.get('active', 0) if stats else 0,
            'frequency_hours': config.analysis_frequency_hours,
            'ai_model': config.ai_model,
            'min_confidence': config.min_confidence_threshold
        }
