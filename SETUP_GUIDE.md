# PhilEarthStats - Quick Setup Guide 🚀

This guide will help you get PhilEarthStats up and running in minutes.

## Quick Start

### Step 1: Backend Setup (Python)

1. Open a terminal and navigate to the backend folder:
```bash
cd backend
```

2. Create and activate a virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

✅ Backend should now be running at `http://localhost:5000`

### Step 2: Frontend Setup (React)

1. Open a **new terminal** and navigate to the frontend folder:
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

✅ Frontend should now be running at `http://localhost:3000`

### Step 3: Access the Application

Open your browser and go to: **http://localhost:3000**

You should see the PhilEarthStats dashboard with real-time earthquake and volcano data!

## Troubleshooting 🔧

### Backend Issues

**Problem: "ModuleNotFoundError"**
- Solution: Make sure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

**Problem: "Port 5000 already in use"**
- Solution: Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Frontend Issues

**Problem: "npm command not found"**
- Solution: Install Node.js from https://nodejs.org/

**Problem: "EADDRINUSE: Port 3000 already in use"**
- Solution: The dev server will automatically ask if you want to use another port, choose 'y'

**Problem: Map not displaying**
- Solution: Check browser console for errors. Ensure internet connection for OpenStreetMap tiles

### Data Issues

**Problem: "No earthquakes to display"**
- Possible reasons:
  1. No recent earthquakes in Philippines region (good news!)
  2. USGS API temporarily unavailable
  3. Network connectivity issues
- Solution: Click the "Refresh" button or wait a few minutes and try again

**Problem: "Failed to fetch earthquake data"**
- Solution: 
  1. Check internet connection
  2. Verify backend is running
  3. Check browser console for CORS errors

## Testing the Setup ✅

1. **Backend Test**: Visit http://localhost:5000/api/health
   - You should see: `{"status": "healthy", ...}`

2. **API Test**: Visit http://localhost:5000/api/info
   - You should see API documentation

3. **Frontend Test**: Visit http://localhost:3000
   - You should see the dashboard with data

## Features to Try 🎯

1. **Interactive Map**: Click on earthquake markers to see details
2. **Volcano Tab**: Check active volcano information
3. **Statistics**: View earthquake patterns and distributions
4. **Earthquake List**: Sort and filter earthquake data
5. **Auto-refresh**: Wait 5 minutes to see automatic data updates

## Production Deployment 🌐

### Backend (Flask)

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (React)

Build the production version:

```bash
cd frontend
npm run build
```

Serve the `dist/` folder with any static file server (Nginx, Apache, etc.)

## Environment Variables 🔐

Create a `.env` file in the backend folder if needed:

```
FLASK_ENV=development
FLASK_DEBUG=True
```

## System Requirements 📋

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **RAM**: 2GB minimum
- **Internet**: Required for fetching real-time data

## Need Help? 💬

- Check the main README.md for detailed documentation
- Review API endpoints at http://localhost:5000/api/info
- Check browser console for frontend errors
- Check terminal output for backend errors

## Next Steps 🎓

1. Explore the codebase in `frontend/src/components/`
2. Customize the UI styling in `tailwind.config.js`
3. Add more data sources or features
4. Deploy to a cloud platform (Heroku, Vercel, AWS, etc.)

---

Happy monitoring! Stay safe! 🌏
