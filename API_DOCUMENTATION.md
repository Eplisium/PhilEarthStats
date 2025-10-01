# PhilEarthStats API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
No authentication required. All endpoints are publicly accessible.

## Rate Limiting
The API implements a 5-minute cache to reduce load on external data sources. Data is automatically refreshed every 5 minutes.

## Version
Current Version: **1.1.0** (October 2025 Update)
- Added `/api/earthquakes/all` endpoint for all earthquakes including aftershocks
- Added `/api/time` endpoint for server time information
- Added `/api/phivolcs/latest` endpoint (placeholder)
- All responses now include `server_time_utc` in metadata

---

## Endpoints

### 1. Health Check

**GET** `/api/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890000,
  "server_time_utc": "2025-10-01T16:39:09Z",
  "service": "PhilEarthStats API"
}
```

---

### 2. API Information

**GET** `/api/info`

Get information about the API and available endpoints.

**Response:**
```json
{
  "name": "PhilEarthStats API",
  "version": "1.0.0",
  "description": "Real-time Philippines earthquake and volcano monitoring system",
  "endpoints": {
    "/api/earthquakes/all": "Get ALL earthquakes including aftershocks (7 days, no magnitude filter)",
    "/api/earthquakes/recent": "Get recent earthquakes (7 days, M ≥ 2.5)",
    "/api/earthquakes/significant": "Get significant earthquakes (M ≥ 4.5, 30 days)",
    "/api/earthquakes/statistics": "Get earthquake statistics (30 days)",
    "/api/volcanoes/active": "Get active volcanoes information",
    "/api/phivolcs/latest": "Get PHIVOLCS earthquake bulletins (pending implementation)",
    "/api/time": "Get server time information",
    "/api/health": "Health check",
    "/api/info": "API information"
  },
  "data_sources": [
    "USGS Earthquake Catalog (earthquake.usgs.gov)",
    "PHIVOLCS - Philippine Institute of Volcanology and Seismology"
  ],
  "cache_timeout": "300 seconds"
}
```

---

### 3. All Earthquakes (Including Aftershocks) 🆕

**GET** `/api/earthquakes/all`

Get **ALL** earthquakes in the Philippines region from the last 7 days, including tiny aftershocks. No minimum magnitude filter is applied.

**Query Parameters:** None

**Magnitude Filter:** None (M ≥ 0.0)

**Response:**
```json
{
  "success": true,
  "count": 150,
  "earthquakes": [
    {
      "id": "us1000xyz",
      "magnitude": 1.2,
      "place": "3 km NE of Batangas, Philippines",
      "time": 1234567890000,
      "updated": 1234567900000,
      "timezone": 480,
      "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us1000xyz",
      "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=us1000xyz&format=geojson",
      "felt": null,
      "alert": null,
      "status": "automatic",
      "tsunami": 0,
      "significance": 23,
      "type": "earthquake",
      "title": "M 1.2 - 3 km NE of Batangas, Philippines",
      "longitude": 121.05,
      "latitude": 13.75,
      "depth": 8.2
    }
  ],
  "metadata": {
    "generated": 1234567890000,
    "server_time_utc": "2025-10-01T16:39:09Z",
    "title": "All Philippines Earthquakes Including Aftershocks (7 days)",
    "source": "USGS Earthquake Catalog"
  }
}
```

**Use Case:** 
This endpoint is ideal for:
- Scientific research requiring complete seismic data
- Aftershock sequence monitoring
- Detailed seismic activity analysis
- Understanding earthquake clustering patterns

**Note:** This endpoint may return a large number of results as it includes all seismic activity without magnitude filtering.

---

### 4. Recent Earthquakes

**GET** `/api/earthquakes/recent`

Get earthquakes in the Philippines region from the last 7 days with magnitude ≥ 2.5.

**Magnitude Filter:** M ≥ 2.5

**Query Parameters:** None

**Response:**
```json
{
  "success": true,
  "count": 25,
  "earthquakes": [
    {
      "id": "us1000abcd",
      "magnitude": 5.2,
      "place": "12 km SE of Manila, Philippines",
      "time": 1234567890000,
      "updated": 1234567900000,
      "timezone": 480,
      "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us1000abcd",
      "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=us1000abcd&format=geojson",
      "felt": 150,
      "alert": "green",
      "status": "reviewed",
      "tsunami": 0,
      "significance": 456,
      "type": "earthquake",
      "title": "M 5.2 - 12 km SE of Manila, Philippines",
      "longitude": 121.05,
      "latitude": 14.50,
      "depth": 10.5
    }
  ],
  "metadata": {
    "generated": 1234567890000,
    "server_time_utc": "2025-10-01T16:39:09Z",
    "title": "Recent Philippines Earthquakes (7 days, M ≥ 2.5)",
    "source": "USGS Earthquake Catalog"
  }
}
```

**Earthquake Object Fields:**
- `id` (string): Unique earthquake identifier
- `magnitude` (float): Earthquake magnitude (Richter scale)
- `place` (string): Location description
- `time` (integer): Occurrence time (Unix timestamp in milliseconds)
- `updated` (integer): Last update time (Unix timestamp in milliseconds)
- `url` (string): Link to detailed USGS event page
- `felt` (integer|null): Number of "Did You Feel It?" reports
- `alert` (string|null): Alert level: "green", "yellow", "orange", "red"
- `tsunami` (integer): 1 if tsunami generated, 0 otherwise
- `significance` (integer): Event significance score
- `longitude` (float): Longitude coordinate
- `latitude` (float): Latitude coordinate
- `depth` (float): Depth below surface in kilometers

---

### 5. Significant Earthquakes

**GET** `/api/earthquakes/significant`

Get earthquakes with magnitude ≥ 4.5 in the Philippines region from the last 30 days.

**Query Parameters:** None

**Response:**
```json
{
  "success": true,
  "count": 8,
  "earthquakes": [...],
  "metadata": {
    "generated": 1234567890000,
    "server_time_utc": "2025-10-01T16:39:09Z",
    "title": "Significant Philippines Earthquakes (30 days, M ≥ 4.5)",
    "source": "USGS Earthquake Catalog"
  }
}
```

Response structure is identical to `/api/earthquakes/recent`, but filtered for significant events.

---

### 5. Earthquake Statistics

**GET** `/api/earthquakes/statistics`

Get statistical analysis of earthquakes in the Philippines region from the last 30 days.

**Query Parameters:** None

**Response:**
```json
{
  "success": true,
  "period": "30 days",
  "total_earthquakes": 142,
  "magnitude_stats": {
    "max": 6.2,
    "min": 2.1,
    "average": 3.8,
    "distribution": {
      "micro": 45,
      "minor": 67,
      "light": 22,
      "moderate": 6,
      "strong": 2,
      "major": 0,
      "great": 0
    }
  },
  "depth_stats": {
    "max": 185.3,
    "min": 2.0,
    "average": 45.7,
    "distribution": {
      "shallow": 98,
      "intermediate": 40,
      "deep": 4
    }
  },
  "metadata": {
    "generated": 1234567890000,
    "source": "USGS Earthquake Catalog"
  }
}
```

**Magnitude Distribution:**
- `micro`: < 3.0
- `minor`: 3.0 - 3.9
- `light`: 4.0 - 4.9
- `moderate`: 5.0 - 5.9
- `strong`: 6.0 - 6.9
- `major`: 7.0 - 7.9
- `great`: ≥ 8.0

**Depth Distribution:**
- `shallow`: < 70 km
- `intermediate`: 70 - 300 km
- `deep`: ≥ 300 km

---

### 6. Active Volcanoes

**GET** `/api/volcanoes/active`

Get information about active volcanoes in the Philippines.

**Query Parameters:** None

**Response:**
```json
{
  "success": true,
  "count": 6,
  "volcanoes": [
    {
      "id": 1,
      "name": "Mayon",
      "location": "Albay",
      "latitude": 13.2572,
      "longitude": 123.6856,
      "elevation": 2463,
      "type": "Stratovolcano",
      "status": "Alert Level 0 (Normal)",
      "last_eruption": "2018",
      "alert_level": 0,
      "description": "Most active volcano in the Philippines, known for its perfect cone shape"
    }
  ],
  "metadata": {
    "generated": 1234567890000,
    "title": "Active Volcanoes in the Philippines",
    "source": "PHIVOLCS Records",
    "note": "Alert levels and status should be verified with official PHIVOLCS sources"
  }
}
```

**Volcano Object Fields:**
- `id` (integer): Volcano identifier
- `name` (string): Volcano name
- `location` (string): Province/region location
- `latitude` (float): Latitude coordinate
- `longitude` (float): Longitude coordinate
- `elevation` (integer): Height in meters above sea level
- `type` (string): Volcano type (e.g., "Stratovolcano")
- `status` (string): Current status description
- `last_eruption` (string): Year of last eruption
- `alert_level` (integer): PHIVOLCS alert level (0-5)
- `description` (string): Additional information

**PHIVOLCS Alert Levels:**
- **Level 0**: No alert - Normal condition
- **Level 1**: Abnormal - Increased unrest
- **Level 2**: Moderate - Increased tendency towards hazardous eruption
- **Level 3**: High - Hazardous eruption possible within weeks
- **Level 4**: Intense - Hazardous eruption in progress
- **Level 5**: Critical - Hazardous eruption imminent or ongoing

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200`: Success
- `500`: Internal server error or external API failure

---

### 8. Server Time 🆕

**GET** `/api/time`

Get server time information including UTC time and Philippine Time (Asia/Manila, UTC+8).

**Query Parameters:** None

**Response:**
```json
{
  "success": true,
  "utc": "2025-10-01T16:39:09Z",
  "philippine_time": "2025-10-02T00:39:09+08:00",
  "timestamp": 1727802549000,
  "timezone": "Asia/Manila (UTC+8)"
}
```

**Use Case:**
- Synchronize client time with server time
- Display Philippine local time to users
- Time zone conversion reference

---

### 9. PHIVOLCS Latest Data 🆕

**GET** `/api/phivolcs/latest`

Get latest earthquake bulletins from PHIVOLCS (Philippine Institute of Volcanology and Seismology).

**Query Parameters:** None

**Status:** Currently a placeholder endpoint. PHIVOLCS does not provide a public API.

**Response:**
```json
{
  "success": true,
  "message": "PHIVOLCS integration pending",
  "note": "PHIVOLCS does not provide a public API. To access their earthquake bulletins, consider: 1) Web scraping their official website, 2) Using Facebook Graph API to access their public posts, 3) Monitoring their RSS feed if available",
  "official_sources": [
    "https://earthquake.phivolcs.dost.gov.ph/",
    "https://www.facebook.com/phivolcs.dost",
    "https://twitter.com/phivolcs_dost"
  ],
  "metadata": {
    "generated": 1727802549000,
    "server_time_utc": "2025-10-01T16:39:09Z"
  }
}
```

**Future Implementation Options:**
1. **Web Scraping**: Automated extraction from PHIVOLCS website
2. **Facebook Graph API**: Access public posts (requires API credentials)
3. **RSS Feed**: If PHIVOLCS implements one
4. **Official API**: If PHIVOLCS releases a public API

---

## Data Freshness

- Data is cached for 5 minutes (300 seconds)
- The `metadata.generated` field shows the timestamp when the data was last fetched
- Cache applies per endpoint independently

---

## Geographic Bounds

Philippines region filtering uses the following coordinates:

```
Minimum Latitude: 4.5°
Maximum Latitude: 21.5°
Minimum Longitude: 116.0°
Maximum Longitude: 127.0°
```

---

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Get recent earthquakes
fetch('http://localhost:5000/api/earthquakes/recent')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} earthquakes`);
    data.earthquakes.forEach(eq => {
      console.log(`M${eq.magnitude} - ${eq.place}`);
    });
  });
```

### Python (Requests)

```python
import requests

# Get earthquake statistics
response = requests.get('http://localhost:5000/api/earthquakes/statistics')
data = response.json()

if data['success']:
    print(f"Total earthquakes: {data['total_earthquakes']}")
    print(f"Max magnitude: {data['magnitude_stats']['max']}")
```

### cURL

```bash
# Get active volcanoes
curl http://localhost:5000/api/volcanoes/active

# Get significant earthquakes
curl http://localhost:5000/api/earthquakes/significant
```

---

## Data Sources

### USGS Earthquake Catalog
- **URL**: https://earthquake.usgs.gov/
- **API**: https://earthquake.usgs.gov/fdsnws/event/1/
- **Update Frequency**: Real-time (minutes after event)
- **Accuracy**: Scientific-grade seismological data

### PHIVOLCS
- **URL**: https://www.phivolcs.dost.gov.ph/
- **Data Type**: Volcano monitoring and seismological information
- **Authority**: Official Philippine government agency

---

## Important Notes

1. **Real-time Data**: Earthquake data is near real-time from USGS. There may be a delay of a few minutes after an event occurs.

2. **Data Accuracy**: While data sources are official and scientific, initial reports may be revised as more information becomes available.

3. **Caching**: To reduce load on external APIs and improve performance, data is cached for 5 minutes.

4. **Official Warnings**: This API is for informational purposes. For official warnings and emergency information, always consult PHIVOLCS directly.

5. **Rate Limiting**: No explicit rate limiting is implemented, but excessive requests may be throttled.

---

## Support

For issues or questions about the API:
1. Check the main README.md
2. Verify backend is running with `/api/health`
3. Check server logs for errors
4. Ensure internet connectivity for external data sources

---

**Last Updated**: 2025
**API Version**: 1.0.0
