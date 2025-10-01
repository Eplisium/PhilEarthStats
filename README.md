# PhilEarthStats 🌏

A real-time monitoring system for Philippines earthquakes and volcanoes, pulling live data from official sources including USGS and PHIVOLCS.

![PhilEarthStats](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)

## Features ✨

- **Real-time Earthquake Data**: Live earthquake information from USGS Earthquake Catalog
- **Interactive Map**: Visual representation of earthquake epicenters and active volcanoes
- **Volcano Monitoring**: Track active volcanoes in the Philippines with alert levels
- **Detailed Statistics**: Comprehensive analysis of earthquake patterns, magnitudes, and depths
- **Auto-refresh**: Automatic data updates every 5 minutes
- **Responsive Design**: Beautiful, modern UI that works on desktop and mobile

## Data Sources 📊

1. **USGS Earthquake Catalog** (earthquake.usgs.gov)
   - Real-time earthquake data with geographic filtering for Philippines region
   - Comprehensive event details including magnitude, depth, location, and timing
   - Official scientific data with high accuracy

2. **PHIVOLCS** (Philippine Institute of Volcanology and Seismology)
   - Active volcano information and alert levels
   - Official monitoring data for Philippine volcanic activity

## Technology Stack 🛠️

### Backend
- **Flask**: Python web framework for API endpoints
- **Flask-CORS**: Cross-Origin Resource Sharing support
- **Requests**: HTTP library for fetching data from external APIs

### Frontend
- **React 18**: Modern UI library
- **Vite**: Next-generation frontend tooling
- **TailwindCSS**: Utility-first CSS framework
- **Leaflet & React-Leaflet**: Interactive mapping
- **Recharts**: Data visualization and charts
- **Lucide React**: Beautiful icon system
- **date-fns**: Date formatting utilities

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## API Endpoints 🔌

### GET `/api/earthquakes/recent`
Get recent earthquakes in the Philippines (last 7 days)

**Response:**
```json
{
  "success": true,
  "count": 25,
  "earthquakes": [...],
  "metadata": {
    "generated": 1234567890,
    "title": "Recent Philippines Earthquakes (7 days)",
    "source": "USGS Earthquake Catalog"
  }
}
```

### GET `/api/earthquakes/significant`
Get significant earthquakes (M ≥ 4.5) in the last 30 days

### GET `/api/earthquakes/statistics`
Get earthquake statistics including magnitude and depth distributions

### GET `/api/volcanoes/active`
Get information about active volcanoes in the Philippines

### GET `/api/health`
Health check endpoint

### GET `/api/info`
Get API information and available endpoints

## Features in Detail 📱

### 1. Interactive Map View
- Real-time plotting of earthquake epicenters
- Color-coded markers based on magnitude
- Circle radius representing earthquake intensity
- Volcano markers with detailed information
- Click on markers for detailed popups

### 2. Earthquake List
- Sort by time, magnitude, or depth
- Filter between all earthquakes and significant events
- Detailed information cards with direct links to USGS
- Visual indicators for tsunami warnings and alerts

### 3. Volcano Monitoring
- Comprehensive list of active Philippine volcanoes
- PHIVOLCS alert level indicators
- Detailed information including elevation, location, and last eruption
- Alert level descriptions and safety information

### 4. Statistics Dashboard
- Total earthquake count and trends
- Magnitude distribution charts
- Depth distribution analysis
- Maximum, minimum, and average values
- Visual data representation with charts

## Caching 🔄

The API implements a 5-minute cache system to:
- Reduce load on external APIs
- Improve response times
- Ensure data consistency
- Comply with rate limiting

## Data Accuracy 📍

This application pulls data from official scientific sources:
- **USGS**: Provides real-time, accurate earthquake data with scientific rigor
- **PHIVOLCS**: Official Philippine government agency for volcano and earthquake monitoring

**Important**: While this application uses official data sources, always refer to PHIVOLCS official website (phivolcs.dost.gov.ph) for official warnings and emergency information.

## Development 💻

### Project Structure
```
PhilEarthStats/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main application
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   └── tailwind.config.js  # Tailwind configuration
└── README.md               # This file
```

### Building for Production

#### Backend
The Flask application can be deployed using:
- Gunicorn (recommended)
- uWSGI
- Docker

#### Frontend
```bash
cd frontend
npm run build
```

The optimized production build will be in the `dist/` folder.

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is open source and available for educational and research purposes.

## Disclaimer ⚠️

This application is for informational purposes only. For official earthquake and volcano warnings, always consult:
- **PHIVOLCS**: https://www.phivolcs.dost.gov.ph
- **NDRRMC**: https://ndrrmc.gov.ph

In case of emergency, follow official government advisories and evacuation orders.

## Credits 🙏

- **USGS Earthquake Hazards Program** for providing comprehensive earthquake data
- **PHIVOLCS** for volcano monitoring and seismological data
- OpenStreetMap contributors for map tiles

## Support 💬

For issues, questions, or suggestions, please open an issue in the repository.

---

**Built with ❤️ for Philippines earthquake and volcano awareness**
