# PhilEarthStats - Project Overview

## 🎯 Purpose

PhilEarthStats is a real-time monitoring system for earthquakes and volcanic activity in the Philippines. It aggregates data from official sources (USGS and PHIVOLCS) and presents it in an intuitive, interactive web interface.

## 📊 Key Features

### 1. Real-Time Earthquake Monitoring
- Live data from USGS Earthquake Catalog
- Updates every 5 minutes
- 7-day and 30-day views
- Filtering by magnitude (significant events M ≥ 4.5)

### 2. Interactive Map Visualization
- Geographic display of all earthquakes
- Color-coded by magnitude
- Circle radius representing intensity
- Active volcano markers
- Clickable markers with detailed information

### 3. Volcano Monitoring
- 6+ active Philippine volcanoes tracked
- PHIVOLCS alert level system (0-5)
- Detailed volcano information:
  - Location, elevation, type
  - Last eruption dates
  - Current status and alerts
  - Historical context

### 4. Statistical Analysis
- Magnitude distribution charts
- Depth distribution analysis
- Time-series trends
- Maximum, minimum, and average calculations
- Visual data representation with graphs

### 5. User-Friendly Interface
- Modern, responsive design
- Works on desktop and mobile
- Tab-based navigation
- Auto-refresh capability
- Manual refresh button
- Direct links to official sources

## 🏗️ Architecture

### Backend (Python/Flask)
```
backend/
├── app.py              # Main Flask application
└── requirements.txt    # Python dependencies
```

**Responsibilities:**
- Fetch data from USGS API
- Cache responses (5 minutes)
- Filter for Philippines region
- Process and aggregate statistics
- Serve REST API endpoints

**Key Technologies:**
- Flask: Web framework
- Flask-CORS: Cross-origin support
- Requests: HTTP client

### Frontend (React/Vite)
```
frontend/
├── src/
│   ├── App.jsx                    # Main application
│   ├── components/
│   │   ├── EarthquakeMap.jsx      # Interactive Leaflet map
│   │   ├── EarthquakeList.jsx     # Sortable earthquake list
│   │   ├── VolcanoList.jsx        # Volcano information cards
│   │   └── Statistics.jsx         # Charts and analysis
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Global styles
├── package.json
├── vite.config.js
└── tailwind.config.js
```

**Key Technologies:**
- React 18: UI library
- Vite: Build tool
- TailwindCSS: Styling
- Leaflet: Mapping
- Recharts: Data visualization
- Lucide React: Icons

## 🔄 Data Flow

1. **User opens application** → Frontend loads
2. **Frontend requests data** → Calls backend API
3. **Backend checks cache** → Valid? Return cached data
4. **Cache expired?** → Fetch from USGS API
5. **Process data** → Filter for Philippines, calculate stats
6. **Cache & return** → Store for 5 minutes, send to frontend
7. **Frontend displays** → Render map, lists, charts
8. **Auto-refresh** → Every 5 minutes, repeat process

## 🌍 Data Sources

### USGS Earthquake Catalog
- **URL**: https://earthquake.usgs.gov/
- **API**: RESTful JSON/GeoJSON
- **Coverage**: Global, real-time
- **Accuracy**: Scientific-grade seismological data
- **Update Frequency**: Minutes after event

### PHIVOLCS (Static Data)
- **URL**: https://www.phivolcs.dost.gov.ph/
- **Coverage**: Philippine volcanoes and seismic activity
- **Authority**: Official Philippine government agency
- **Note**: Volcano data is embedded; alert levels should be verified

## 🗺️ Geographic Coverage

**Philippines Bounding Box:**
- Latitude: 4.5° to 21.5° N
- Longitude: 116.0° to 127.0° E

This encompasses all Philippine territory including:
- Luzon
- Visayas
- Mindanao
- Surrounding waters

## 📈 Earthquake Classification

### By Magnitude (Richter Scale)
- **Micro**: < 3.0 (Often not felt)
- **Minor**: 3.0 - 3.9 (Felt but rarely causes damage)
- **Light**: 4.0 - 4.9 (Noticeable shaking)
- **Moderate**: 5.0 - 5.9 (Can cause damage)
- **Strong**: 6.0 - 6.9 (Significant damage possible)
- **Major**: 7.0 - 7.9 (Serious damage over large areas)
- **Great**: ≥ 8.0 (Devastating damage)

### By Depth
- **Shallow**: < 70 km (Most damaging)
- **Intermediate**: 70 - 300 km
- **Deep**: ≥ 300 km (Rarely felt at surface)

## 🚨 Volcano Alert Levels (PHIVOLCS)

- **Level 0**: Normal - No alert
- **Level 1**: Abnormal - Low-level unrest
- **Level 2**: Moderate - Increased unrest
- **Level 3**: High - Magma near surface
- **Level 4**: Intense - Hazardous eruption imminent
- **Level 5**: Critical - Hazardous eruption in progress

## 🔒 Security & Privacy

- **No user data collection**: Application doesn't store personal information
- **Public data only**: All data is from public scientific sources
- **No authentication required**: Free and open access
- **CORS enabled**: Frontend-backend communication secured
- **API rate limiting**: Respectful to data sources via caching

## ⚡ Performance

### Optimization Strategies
1. **Caching**: 5-minute cache reduces API calls
2. **Lazy loading**: Components load as needed
3. **Code splitting**: Vite automatically optimizes bundles
4. **Responsive images**: Efficient map tile loading
5. **Minimal dependencies**: Only essential libraries

### Expected Performance
- **Initial load**: < 3 seconds
- **API response**: < 500ms (cached)
- **Map rendering**: < 1 second
- **Chart rendering**: < 500ms

## 🎨 Design Philosophy

### User Experience
- **Clarity**: Information is clear and easy to understand
- **Accessibility**: Large fonts, good contrast, intuitive navigation
- **Responsiveness**: Works on all screen sizes
- **Speed**: Fast loading and smooth interactions
- **Reliability**: Graceful error handling

### Visual Design
- **Modern**: Clean, contemporary interface
- **Colorful**: Magnitude-based color coding
- **Spacious**: Plenty of whitespace
- **Professional**: Suitable for emergency services and public use

## 🔮 Future Enhancements

### Phase 1 (Near-term)
- Email/SMS notifications
- Historical data analysis
- Data export (CSV/JSON)
- User preferences

### Phase 2 (Mid-term)
- Mobile app (React Native)
- Multi-language support
- Advanced filtering
- Community features

### Phase 3 (Long-term)
- User accounts
- Predictive modeling (educational)
- Social features
- Integration with emergency services

## 📋 Use Cases

### For General Public
- Check recent earthquake activity
- Learn about nearby volcanoes
- Understand seismic risks
- Educational purposes

### For Researchers
- Access structured earthquake data
- Analyze patterns and trends
- Export data for further study
- Quick reference tool

### For Emergency Services
- Monitor real-time seismic activity
- Track volcanic alert levels
- Rapid situation assessment
- Public information resource

### For Media
- Current earthquake information
- Visual assets (maps, charts)
- Statistical context
- Verified data sources

## 🤝 Contributing

This is an open-source project. Contributions are welcome in:
- Code improvements
- Bug fixes
- Documentation
- Feature suggestions
- Design enhancements

See CONTRIBUTING.md for guidelines.

## 📞 Support & Resources

- **Documentation**: README.md, SETUP_GUIDE.md, API_DOCUMENTATION.md
- **Official Sources**: PHIVOLCS, USGS
- **Emergency**: Always follow official government advisories

## ⚠️ Important Disclaimer

This application is **for informational purposes only**. 

**In case of emergency:**
- Follow official PHIVOLCS warnings
- Contact local disaster management offices
- Call emergency services (911 in Philippines)
- Evacuate if instructed by authorities

**This is NOT a substitute for official emergency communications.**

---

**Built with ❤️ for Philippines earthquake and volcano awareness**

*Last Updated: October 2025*
*Version: 1.0.0*
