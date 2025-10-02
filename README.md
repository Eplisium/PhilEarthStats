# PhilEarthStats 🌏

A real-time monitoring system for Philippines earthquakes and volcanoes, pulling live data from official sources including USGS and PHIVOLCS.

![PhilEarthStats](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)

## Features ✨

### Real-time Monitoring
- **Real-time Earthquake Data**: Live earthquake information from USGS Earthquake Catalog
- **Interactive Map**: Visual representation of earthquake epicenters and active volcanoes
- **Volcano Monitoring**: Track active volcanoes in the Philippines with alert levels
- **Detailed Statistics**: Comprehensive analysis of earthquake patterns, magnitudes, and depths
- **Auto-refresh**: Automatic data updates every 5 minutes
- **Responsive Design**: Beautiful, modern UI that works on desktop and mobile

### AI-Powered Analysis 🤖
- **Intelligent Insights**: AI-powered seismological analysis using OpenRouter LLMs
- **Expert Analysis**: Get comprehensive assessments of seismic activity patterns
- **Risk Assessment**: AI-generated risk evaluations and safety recommendations
- **Pattern Detection**: Identify trends, clustering, and earthquake sequences
- **Multiple AI Models**: Supports Grok, GPT-4o, and Gemini models with automatic fallback

### Historical Data 📚
- **Historical Earthquake Database**: SQLite database storing all detected earthquakes
- **Worst Years Ranking**: Analysis of most severe earthquake years in Philippine history
- **Year Statistics**: Comprehensive yearly earthquake statistics and trends
- **Calendar View**: Visual calendar showing earthquake activity by date
- **Date Range Queries**: Filter and analyze earthquakes within custom date ranges
- **Historical Data Sync**: Import historical earthquake data from USGS
- **Notable Events**: Pre-seeded data for major Philippine earthquakes (1976, 1990, 2012, 2013, 2019)

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
- **Flask-SQLAlchemy**: SQL database ORM for historical data storage
- **SQLAlchemy**: Database toolkit and ORM
- **Requests**: HTTP library for fetching data from external APIs
- **python-dotenv**: Environment variable management
- **pytz**: Timezone handling for Philippine time
- **OpenRouter API**: AI integration for intelligent earthquake analysis

### Frontend
- **React 18**: Modern UI library
- **Vite**: Next-generation frontend tooling
- **TailwindCSS**: Utility-first CSS framework
- **Leaflet & React-Leaflet**: Interactive mapping
- **Recharts**: Data visualization and charts
- **Lucide React**: Beautiful icon system
- **date-fns**: Date formatting utilities
- **react-markdown**: Markdown rendering for AI analysis
- **Zustand**: Lightweight state management

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- (Optional) OpenRouter API key for AI analysis features
- (Optional) Docker and Docker Compose for containerized deployment

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

4. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key for AI features
```

5. Run the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

**Note**: The database will be automatically created and seeded with historical data on first run.

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

### Quick Start (Windows)

Use the provided batch files for easy startup:
```bash
# Start both backend and frontend
start-all.bat

# Or start individually
start-backend.bat
start-frontend.bat
```

### Docker Deployment 🐳

```bash
# Using Docker Compose
docker-compose up -d

# Or using Docker directly
docker build -t philearthstats .
docker run -d -p 5000:5000 philearthstats
```

Access at `http://localhost:5000`

## API Endpoints 🔌

### Earthquake Data Endpoints

**GET `/api/earthquakes/recent`**
Get recent earthquakes in the Philippines (M ≥ 2.5, last 7 days)

**GET `/api/earthquakes/all`**
Get ALL earthquakes including aftershocks (no magnitude filter, last 7 days)

**GET `/api/earthquakes/significant`**
Get significant earthquakes (M ≥ 4.5, last 30 days)

**GET `/api/earthquakes/statistics`**
Get earthquake statistics including magnitude and depth distributions

### AI Analysis Endpoint 🤖

**POST `/api/ai/analyze`**
Get AI-powered analysis of earthquake data with expert insights
- Requires OpenRouter API key in `.env` file
- Analyzes last 30 days of earthquake activity
- Provides risk assessment, pattern detection, and recommendations
- Supports multiple LLM models with automatic fallback

### Historical Data Endpoints 📚

**GET `/api/history/worst-years?limit=10`**
Get the worst earthquake years in Philippine history ranked by severity score

**GET `/api/history/year/<year>`**
Get comprehensive earthquake data for a specific year

**GET `/api/calendar?year=2024&month=10`**
Get calendar view of earthquakes organized by date

**GET `/api/history/date-range?start=2024-01-01&end=2024-12-31`**
Get earthquakes within a custom date range

**POST `/api/history/sync`**
Sync and import historical earthquake data from USGS

### Volcano & Other Endpoints

**GET `/api/volcanoes/active`**
Get information about active volcanoes in the Philippines

**GET `/api/phivolcs/latest`**
PHIVOLCS earthquake bulletins (pending implementation)

**GET `/api/time`**
Get server time information (UTC and Philippine time)

**GET `/api/health`**
Health check endpoint

**GET `/api/info`**
Get comprehensive API information and available endpoints

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

### 5. AI-Powered Analysis 🤖
- Expert seismological analysis of earthquake patterns
- Risk assessment and safety recommendations
- Pattern detection and trend identification
- Geographic distribution analysis
- Actionable insights for residents and authorities

### 6. Historical Data Explorer 📚
- Browse worst earthquake years in Philippine history
- View yearly statistics and notable events
- Calendar view of earthquake activity
- Custom date range filtering
- Historical database with automatic tracking

## Database & Caching 💾

### Database
- **SQLite** database for historical earthquake storage
- Automatic database creation and seeding on first run
- Stores all earthquake events with full metadata
- Year-based statistics with severity scoring
- Notable historical events pre-loaded (1976-2019)

### Caching
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
│   ├── database.py         # Database models and services
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── earthquakes.db      # SQLite database (auto-created)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EarthquakeMap.jsx
│   │   │   ├── EarthquakeList.jsx
│   │   │   ├── Statistics.jsx
│   │   │   ├── VolcanoList.jsx
│   │   │   ├── AIAnalysis.jsx          # AI analysis component
│   │   │   └── EarthquakeCalendar.jsx  # Calendar view
│   │   ├── App.jsx         # Main application
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   └── tailwind.config.js  # Tailwind configuration
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose setup
├── start-all.bat           # Windows: Start both servers
├── start-backend.bat       # Windows: Start backend only
├── start-frontend.bat      # Windows: Start frontend only
├── README.md               # This file
├── SETUP_GUIDE.md          # Detailed setup instructions
├── QUICKSTART.md           # Quick start guide
├── DEPLOYMENT.md           # Deployment guide
└── CONTRIBUTING.md         # Contribution guidelines
```

### Environment Configuration

Create a `.env` file in the `backend/` directory:

```bash
# Copy from example
cp backend/.env.example backend/.env
```

**Environment Variables:**
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_DEBUG`: Enable/disable debug mode
- `CACHE_TIMEOUT`: Cache duration in seconds (default: 300)
- `OPENROUTER_API_KEY`: Your OpenRouter API key for AI features

**Getting an OpenRouter API Key:**
1. Visit https://openrouter.ai/keys
2. Sign up or log in
3. Create a new API key
4. Add to `.env` file: `OPENROUTER_API_KEY=your_key_here`

### Building for Production

#### Backend
The Flask application can be deployed using:
- Gunicorn (recommended)
- uWSGI
- Docker

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend
```bash
cd frontend
npm run build
```

The optimized production build will be in the `dist/` folder.

#### Docker Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:
- Docker and Docker Compose setup
- Cloud platform deployment (AWS, Heroku, GCP, DigitalOcean)
- Nginx/Apache configuration
- SSL/HTTPS setup
- Monitoring and scaling

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

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
- **OpenRouter** for AI/LLM API access (Grok, GPT-4o, Gemini)
- **OpenStreetMap** contributors for map tiles
- **React**, **Flask**, and all open-source libraries used in this project

## Support 💬

For issues, questions, or suggestions, please open an issue in the repository.

---

**Built with ❤️ for Philippines earthquake and volcano awareness**
