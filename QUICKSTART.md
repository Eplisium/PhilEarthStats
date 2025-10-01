# PhilEarthStats - Quick Start Guide ⚡

Get up and running in 5 minutes!

## 🚀 Option 1: Windows Quick Start (Easiest)

1. **Double-click** `start-all.bat`
2. Wait for both servers to start
3. Open browser to **http://localhost:3000**
4. Done! 🎉

## 💻 Option 2: Manual Start

### Terminal 1 - Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
python app.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```

### Open Browser
http://localhost:3000

## 🐳 Option 3: Docker (Production-like)

```bash
docker-compose up
```

Open: http://localhost:5000

## ✅ Verify Installation

1. **Backend Health**: http://localhost:5000/api/health
2. **Recent Earthquakes**: http://localhost:5000/api/earthquakes/recent
3. **Frontend**: http://localhost:3000

## 📱 What You'll See

- **Dashboard** with earthquake statistics
- **Interactive Map** showing earthquake locations and volcanoes
- **Earthquake List** with filtering and sorting
- **Volcano Monitoring** with alert levels
- **Statistics** with charts and graphs

## 🎯 Key Features

- ✅ Real-time earthquake data (USGS)
- ✅ Philippines volcanoes with alert levels
- ✅ Interactive maps
- ✅ Auto-refresh every 5 minutes
- ✅ Beautiful, modern UI
- ✅ Mobile responsive

## 📊 Data Sources

- **USGS Earthquake Catalog**: https://earthquake.usgs.gov/
- **PHIVOLCS**: https://www.phivolcs.dost.gov.ph/

## 🛠️ Requirements

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Internet connection** (for fetching data)

## ❓ Common Issues

**Port already in use?**
- Backend: Change port in `backend/app.py` (line: `app.run(port=5000)`)
- Frontend: Vite will offer alternative port

**Dependencies not installing?**
- Update pip: `python -m pip install --upgrade pip`
- Update npm: `npm install -g npm@latest`

**No data showing?**
- Check internet connection
- Click "Refresh" button
- Check browser console (F12)

## 📚 More Information

- **Full Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API Docs**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Project Info**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

## 🆘 Need Help?

1. Check if both backend and frontend are running
2. Verify http://localhost:5000/api/health returns `{"status": "healthy"}`
3. Check terminal/console for errors
4. Read SETUP_GUIDE.md for detailed troubleshooting

---

**Enjoy monitoring Philippines earthquakes and volcanoes! 🌏🌋**
