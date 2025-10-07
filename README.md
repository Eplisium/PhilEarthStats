# PhilEarthStats 🌏

A real-time monitoring system for Philippines earthquakes and volcanoes, pulling live data from official sources including USGS and PHIVOLCS.

![PhilEarthStats](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)

## Features ✨

### Real-time Monitoring
- **Real-time Earthquake Data**: Live earthquake information from USGS Earthquake Catalog
- **Dual Data Modes**: Toggle between filtered (M ≥ 2.5) and all earthquakes including tiny aftershocks
- **Interactive Map**: Advanced visual representation of earthquake epicenters and active volcanoes
- **Volcano Monitoring**: Track active volcanoes in the Philippines with alert levels and detailed metrics
- **Detailed Statistics**: Comprehensive analysis of earthquake patterns, magnitudes, and depths
- **Auto-refresh**: Automatic data updates every 5 minutes
- **Responsive Design**: Beautiful, modern UI that works seamlessly on desktop, tablet, and mobile

### Advanced Interactive Map 🗺️
- **Marker Clustering**: Intelligent grouping of nearby earthquakes for better visualization
- **Multiple Basemaps**: Choose from Street, Satellite, Dark mode, and Terrain views
- **Magnitude Filter**: Slider to filter earthquakes by magnitude threshold (0.0 to 8.0)
- **Layer Controls**: Toggle earthquake and volcano layers independently
- **Smart Navigation**: 
  - Zoom to extent (fit all data)
  - Reset to default Philippines view
  - Locate user with GPS
  - Fullscreen mode support
- **Interactive Selection**: Click earthquakes in the list to view them on the map with automatic flyTo animation
- **Color-Coded Markers**: Magnitude-based color coding from green (minor) to red (major)
- **Circle Overlays**: Radius represents earthquake intensity
- **Detailed Popups**: Click markers for comprehensive earthquake/volcano information

### AI-Powered Analysis 🤖
- **Multiple AI Models**: Choose from Grok, GPT-4o, Claude, and Gemini with automatic fallback
- **90-Day Analysis**: Comprehensive seismological analysis of the last 3 months
- **Regional Breakdown**: Detailed statistics for Luzon, Visayas, and Mindanao regions
- **Historical Comparison**: 
  - Compare with previous 90-day period
  - Compare with same period last year
- **Enhanced Depth Analysis**: Categorization by very shallow (<10km), shallow, intermediate, and deep
- **Regional Risk Scores**: Color-coded risk assessment (0-100) for each major region
- **Seismic Cluster Detection**: Identify geographic clusters of earthquake activity
- **Aftershock Sequence Analysis**: Detect mainshock-aftershock relationships
- **Temporal Trends**: Track increasing/decreasing activity patterns over time
- **Gutenberg-Richter b-value**: Calculate statistical seismic parameters
- **Energy Release Calculation**: Total energy released in joules
- **Progress Tracking**: Real-time progress indicators during AI analysis
- **Markdown Formatting**: Beautiful, formatted analysis with tables and lists

### Historical Data & Calendar 📚
- **SQLite Database**: Persistent storage of all detected earthquakes
- **Worst Years Ranking**: Interactive cards showing the most devastating earthquake years in Philippine history
- **Severity Scoring**: Advanced algorithm ranking years by total impact, casualties, and magnitude
- **Interactive Calendar View**: 
  - Visual calendar with color-coded magnitude indicators
  - Click dates to view all events for that day
  - Month/year picker dropdowns for easy navigation
  - "Go to Today" quick navigation button
- **On-Demand Historical Sync**: Manually fetch data for any past month/year from USGS
- **Date Range Queries**: Custom date filtering for detailed historical analysis
- **Notable Events**: Pre-seeded data for major Philippine earthquakes (1976-2019)
- **Automatic Data Tracking**: All recent earthquakes automatically stored for future reference

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
- **React 18**: Modern UI library with hooks
- **Vite**: Next-generation frontend tooling for blazing fast development
- **TailwindCSS**: Utility-first CSS framework for rapid UI development
- **Leaflet & React-Leaflet**: Interactive mapping library
- **Leaflet Marker Clustering**: Intelligent marker grouping for better performance
- **Recharts**: Beautiful, responsive data visualization and charts
- **Lucide React**: Beautiful, consistent icon system
- **date-fns**: Modern date formatting and manipulation
- **react-markdown**: Markdown rendering with GitHub Flavored Markdown support
- **remark-gfm & remark-breaks**: Enhanced markdown parsing plugins
- **Zustand**: Lightweight, fast state management with multiple stores
  - `useDataStore`: Main earthquake and volcano data
  - `aiAnalysisStore`: AI analysis state and progress
  - `useCalendarStore`: Calendar and historical data
  - `useMapStore`: Map interaction and selection
  - `tabStore`: Tab navigation state
  - `useStatisticsStore`: Statistics animations
  - `useEarthquakeListStore`: List sorting and filtering

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

### 1. Advanced Interactive Map
- **Real-time Plotting**: Live earthquake epicenters with automatic updates
- **Marker Clustering**: Groups nearby earthquakes for better performance and readability
- **Color-Coded System**: Magnitude-based color coding (green to red)
- **Circle Overlays**: Radius represents earthquake intensity and impact zone
- **Multiple Basemaps**: Switch between Street, Satellite, Dark, and Terrain views
- **Magnitude Filter**: Interactive slider to filter earthquakes (0.0 to 8.0)
- **Layer Toggles**: Show/hide earthquakes and volcanoes independently
- **Advanced Controls**:
  - Zoom to extent (fit all data in view)
  - Reset to default Philippines view
  - GPS-based user location
  - Fullscreen mode support
- **Smart Navigation**: Click "View on Map" from earthquake list to automatically fly to location
- **Detailed Popups**: Click markers for comprehensive information with external links

### 2. Enhanced Earthquake List
- **Flexible Sorting**: Sort by time (newest/oldest), magnitude, or depth
- **Smart Filtering**: Toggle between all earthquakes and significant events only
- **Interactive Cards**: Detailed information cards with magnitude color coding
- **Map Integration**: "View on Map" button that navigates to map and highlights the earthquake
- **External Links**: Direct links to USGS detailed event pages
- **Visual Indicators**: Tsunami warnings, alert levels, and significance badges
- **Responsive Layout**: Optimized for mobile, tablet, and desktop viewing

### 3. Comprehensive Volcano Monitoring
- **6 Active Volcanoes**: Mayon, Taal, Pinatubo, Bulusan, Kanlaon, and Hibok-Hibok
- **PHIVOLCS Alert Levels**: Real-time alert status (Level 0-5) with color coding
- **Detailed Eruption History**:
  - Total historical eruptions
  - Most recent significant eruption with VEI (Volcanic Explosivity Index)
  - Average years between eruptions
  - Casualty information
- **Hazard Zone Information**:
  - Primary hazards (pyroclastic flows, lahars, ashfall, etc.)
  - Permanent Danger Zone (PDZ) radius
  - Extended Danger Zone (EDZ) radius
  - Affected population estimates
  - Critical infrastructure impact
- **Real-Time Monitoring Data**:
  - Number of seismic stations
  - 24-hour earthquake count
  - Ground deformation status
  - SO₂ emission levels (tons/day)
  - Last observation timestamp
- **Practical Information**:
  - Observatory contacts
  - Nearest city and distance
  - Number of evacuation centers
  - Emergency contact numbers
- **Additional Context**:
  - Tectonic setting
  - Crater diameter and morphology
  - Cultural significance
  - Tourism status
- **Expandable Cards**: Click to reveal comprehensive details including historical eruptions, hazard assessments, and monitoring data
- **Summary Statistics**: Total volcanoes monitored, on alert count, normal status count, at-risk population, and seismic network capacity

### 4. Advanced Statistics Dashboard
- **Summary Cards** with animated count-up numbers:
  - Total events (last 30 days)
  - Maximum magnitude
  - Average magnitude
  - Average depth
- **Interactive Charts** with smooth animations:
  - Magnitude distribution (bar chart with color gradients)
  - Depth distribution (donut chart with percentages)
- **Detailed Statistics**:
  - Magnitude breakdown by classification (micro to great)
  - Depth classification (shallow, intermediate, deep)
  - Maximum, minimum, and average values with precision
- **Calendar Integration**: Historical earthquake calendar with worst years ranking
- **Chart Re-animation**: Charts animate each time you view the Statistics tab
- **Hover Effects**: Interactive chart elements with detailed tooltips

### 5. AI-Powered Seismological Analysis 🤖
- **Model Selection**: Choose from multiple AI models:
  - xAI Grok (latest)
  - OpenAI GPT-4o
  - Anthropic Claude
  - Google Gemini
  - Automatic fallback if primary model fails
- **Comprehensive 90-Day Analysis**:
  - Total earthquake count and energy released
  - Maximum, average, and significant event statistics
- **Regional Breakdown** (Luzon, Visayas, Mindanao):
  - Event count and percentage
  - Average and maximum magnitude per region
  - Significant events count
  - Average depth analysis
- **Historical Comparison**:
  - Compare with previous 90-day period (percentage change)
  - Year-over-year comparison (same period last year)
  - Magnitude trend analysis
- **Enhanced Depth Distribution**:
  - Very Shallow (<10 km) - High damage risk
  - Shallow (10-70 km) - Moderate risk
  - Intermediate (70-300 km) - Lower impact
  - Deep (≥300 km) - Minimal impact
- **Regional Risk Scores** (0-100 scale):
  - Color-coded risk levels (Low, Moderate, High, Critical)
  - Factors: activity, magnitude, significant events, shallow depth
- **Seismic Cluster Detection**:
  - Geographic clusters of earthquake activity
  - Cluster location, count, and magnitude statistics
- **Aftershock Sequence Analysis**:
  - Mainshock identification
  - Aftershock count and largest aftershock magnitude
  - Location and temporal information
- **Temporal Trends**:
  - Increasing/Decreasing/Stable patterns
  - Segmented analysis by time periods
- **Gutenberg-Richter b-value**: Statistical analysis of magnitude-frequency distribution
- **Progress Tracking**: Real-time progress bar with detailed step indicators
- **Markdown Formatted Output**: Beautiful, readable analysis with tables, lists, and formatting

### 6. Historical Data Explorer & Calendar 📚
- **Worst Years Ranking**:
  - Top 6 most devastating earthquake years displayed
  - Severity score calculation based on magnitude, events, and casualties
  - Damage level indicators (Severe, High, Moderate, Low)
  - Max magnitude, total events, and major events count
  - Estimated deaths (when applicable)
  - Notable event descriptions
- **Interactive Calendar View**:
  - Month/year grid showing earthquake activity
  - Color-coded dates by maximum magnitude
  - Event count badges on each date
  - Click dates to view all events for that day
  - Month/year dropdown selectors for easy navigation
  - "Go to Today" quick navigation button
- **Historical Data Sync**:
  - Manual "Refresh" button to fetch data for specific months
  - Automatic detection of missing data with fetch prompts
  - Support for historical data back to early 2000s
  - Progress indicators during data synchronization
- **Date Details Panel**:
  - Expandable view showing all earthquakes on selected date
  - Time, magnitude, location, depth, and coordinates
  - Significance scores
- **Database Features**:
  - SQLite persistent storage
  - Automatic tracking of all recent earthquakes
  - Year-based statistics with severity scoring
  - Notable historical events pre-seeded (1976-2019)

## UI/UX Features 🎨

### Design & Responsiveness
- **Modern Gradient Design**: Beautiful purple-to-blue gradients throughout the interface
- **Fully Responsive**: Optimized layouts for mobile (320px+), tablet, and desktop
- **Dark Mode Support**: Dark basemap option for night-time viewing
- **Custom Tooltips**: Helpful tooltips on hover for all interactive elements
- **Smooth Animations**: 
  - Animated count-up numbers using custom `useCountUp` hook
  - Chart animations with staggered delays
  - Tab transition animations
  - Map flyTo animations with easing
  - Hover effects and scale transitions
- **Loading States**: Beautiful spinners and progress indicators
- **Color Coding**: Consistent color scheme for magnitude levels across all views
- **Interactive Elements**: 
  - Hover effects on cards and buttons
  - Click feedback animations
  - Expandable/collapsible sections
- **Accessibility**: Proper ARIA labels, keyboard navigation support

### User Experience
- **Real-time Clock**: Live local time display in header
- **Last Update Indicator**: Shows when data was last refreshed
- **Scroll to Top**: Click logo to quickly scroll to top of page
- **Tab Navigation**: Persistent tab state with smooth transitions
- **Data Filter Toggle**: Easy switch between filtered and all earthquake data
- **Quick Actions**: 
  - Manual refresh button
  - "View on Map" quick navigation
  - "Go to Today" in calendar
  - Reset map view
- **Error Handling**: User-friendly error messages with actionable suggestions
- **GitHub Attribution**: Link to developer profile in footer

## Database & Caching 💾

### Database (SQLite)
- **Automatic Initialization**: Database and tables created automatically on first run
- **Earthquake Storage**: 
  - Stores all earthquake events with complete USGS metadata
  - Fields: ID, magnitude, place, time, coordinates, depth, URL, significance, tsunami flag, etc.
- **Year Statistics**: 
  - Aggregated statistics by year
  - Severity scoring algorithm based on:
    - Maximum magnitude (weighted heavily)
    - Total event count
    - Major events (M ≥ 6.0)
    - Estimated casualties
  - Damage level classification (Severe, High, Moderate, Low)
- **Notable Events**: Pre-seeded historical earthquakes from Philippine history (1976-2019)
- **Historical Seeding**: Database automatically seeds with major historical events on first run

### Caching System
The API implements an intelligent 5-minute cache system:
- **Cache Keys**: Separate caches for different endpoints (recent, all, significant, statistics)
- **Automatic Expiration**: Cache expires after 300 seconds (5 minutes)
- **Benefits**:
  - Reduces load on USGS and external APIs
  - Improves response times dramatically
  - Ensures data consistency across concurrent requests
  - Complies with API rate limiting
  - Minimizes bandwidth usage

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
│   ├── app.py              # Flask API server with all endpoints
│   ├── database.py         # SQLite database models and services
│   ├── ai_config.py        # AI model configuration and fallback
│   ├── ai_prompts.py       # AI prompt templates and configuration
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── earthquakes.db      # SQLite database (auto-created)
│   └── instance/           # Database instance directory
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EarthquakeMap.jsx       # Advanced interactive map
│   │   │   ├── EarthquakeList.jsx      # Sortable earthquake list
│   │   │   ├── Statistics.jsx          # Charts and statistics
│   │   │   ├── VolcanoList.jsx         # Comprehensive volcano data
│   │   │   ├── AIAnalysis.jsx          # AI-powered analysis
│   │   │   ├── EarthquakeCalendar.jsx  # Calendar view
│   │   │   └── CustomTooltip.jsx       # Reusable tooltip component
│   │   ├── store/                       # Zustand state management
│   │   │   ├── useDataStore.js          # Main data store
│   │   │   ├── aiAnalysisStore.js       # AI analysis state
│   │   │   ├── useCalendarStore.js      # Calendar state
│   │   │   ├── useMapStore.js           # Map interaction state
│   │   │   ├── tabStore.js              # Tab navigation
│   │   │   ├── useStatisticsStore.js    # Statistics animations
│   │   │   ├── useEarthquakeListStore.js # List filtering/sorting
│   │   │   ├── selectors.js             # Memoized selectors
│   │   │   └── index.js                 # Store exports
│   │   ├── hooks/
│   │   │   └── useCountUp.js            # Animated counter hook
│   │   ├── assets/
│   │   │   └── logo.jpg                 # Application logo
│   │   ├── App.jsx         # Main application component
│   │   ├── main.jsx        # React entry point
│   │   └── index.css       # Global styles with Tailwind
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite bundler configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   └── postcss.config.js   # PostCSS configuration
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose setup
├── start-all.bat           # Windows: Start both servers
├── start-backend.bat       # Windows: Start backend only
├── start-frontend.bat      # Windows: Start frontend only
├── .gitignore              # Git ignore patterns
├── README.md               # This file
├── SETUP_GUIDE.md          # Detailed setup instructions
├── QUICKSTART.md           # Quick start guide
├── DEPLOYMENT.md           # Deployment guide
├── CONTRIBUTING.md         # Contribution guidelines
└── LICENSE                 # License information
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

### Data Providers
- **USGS Earthquake Hazards Program** for providing comprehensive, real-time earthquake data
- **PHIVOLCS** (Philippine Institute of Volcanology and Seismology) for volcano monitoring and seismological data
- **OpenRouter** for AI/LLM API access enabling intelligent seismological analysis

### Technologies & Libraries

**Backend:**
- **Flask** - Python web framework
- **Flask-SQLAlchemy** - Database ORM
- **Requests** - HTTP library
- **python-dotenv** - Environment management

**Frontend:**
- **React** - UI library
- **Vite** - Build tool
- **TailwindCSS** - Styling framework
- **Leaflet** & **React-Leaflet** - Interactive maps
- **Leaflet.markercluster** - Marker clustering
- **Recharts** - Data visualization
- **Zustand** - State management
- **Lucide React** - Icon system
- **date-fns** - Date formatting
- **react-markdown**, **remark-gfm**, **remark-breaks** - Markdown rendering

**AI Models:**
- **xAI Grok** - Advanced reasoning
- **OpenAI GPT Models** - Natural language processing
- **Anthropic Claude** - Analytical AI
- **Google Gemini** - Multi-modal AI

**Map Tiles:**
- **OpenStreetMap** contributors
- **Esri** (satellite imagery)
- **CARTO** (dark mode tiles)
- **OpenTopoMap** (terrain tiles)

### Special Thanks
- All open-source contributors who make projects like this possible
- The seismology and volcanology community for their dedication to public safety
- **Eplisium** - Developer and maintainer

## Support 💬

For issues, questions, or suggestions, please open an issue in the repository.

---

**Built with ❤️ for Philippines earthquake and volcano awareness**
