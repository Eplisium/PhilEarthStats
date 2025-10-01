# Changelog

All notable changes to PhilEarthStats will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-01

### Added
- **Backend API**
  - Flask REST API with CORS support
  - Real-time earthquake data from USGS Earthquake Catalog
  - Philippines volcano information based on PHIVOLCS data
  - Earthquake statistics and analysis endpoints
  - 5-minute caching system for API responses
  - Health check and API info endpoints

- **Frontend Application**
  - Modern React 18 application with Vite
  - Interactive map with Leaflet showing earthquakes and volcanoes
  - Real-time earthquake list with sorting and filtering
  - Volcano monitoring dashboard with alert levels
  - Statistical analysis with charts and graphs
  - Auto-refresh every 5 minutes
  - Responsive design for mobile and desktop
  - Beautiful UI with TailwindCSS

- **Features**
  - Geographic filtering for Philippines region (4.5°-21.5° N, 116°-127° E)
  - Magnitude-based color coding and visualization
  - Depth distribution analysis
  - Tsunami warning indicators
  - PHIVOLCS alert level system for volcanoes
  - Direct links to USGS event pages

- **Documentation**
  - Comprehensive README with installation instructions
  - Quick setup guide for developers
  - Complete API documentation
  - Contributing guidelines
  - MIT License

- **Developer Tools**
  - Windows batch scripts for easy startup
  - Git ignore configuration
  - Environment variable examples
  - Project structure and organization

### Data Sources
- USGS Earthquake Catalog API (earthquake.usgs.gov)
- PHIVOLCS volcano monitoring data

### Technical Stack
- **Backend**: Python 3.8+, Flask, Flask-CORS, Requests
- **Frontend**: React 18, Vite, TailwindCSS, Leaflet, Recharts, Lucide React
- **Data Format**: GeoJSON for earthquakes, JSON for API responses

---

## Future Releases

### [1.1.0] - Planned
- [ ] Email notification system for significant earthquakes
- [ ] User preferences and settings
- [ ] Historical data analysis
- [ ] Export data functionality (CSV, JSON)
- [ ] Dark mode support

### [1.2.0] - Planned
- [ ] Mobile app version (React Native)
- [ ] Push notifications
- [ ] Multi-language support (Filipino, English)
- [ ] Advanced filtering options
- [ ] Earthquake prediction models (educational)

### [2.0.0] - Future
- [ ] User authentication and personalized dashboards
- [ ] Community reporting features
- [ ] Integration with more data sources
- [ ] Machine learning for pattern analysis
- [ ] 3D visualization of seismic data

---

## Notes

- All dates are in ISO 8601 format
- Version numbers follow Semantic Versioning
- Breaking changes will be clearly marked
- Security updates will be released as needed
