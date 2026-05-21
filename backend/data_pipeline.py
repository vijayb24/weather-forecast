import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("API_KEY")

district_coords = {
    "Ariyalur": {"lat": 11.1381, "lon": 79.0756},
    "Chengalpattu": {"lat": 12.7, "lon": 79.9833},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "Cuddalore": {"lat": 11.75, "lon": 79.75},
    "Dharmapuri": {"lat": 12.1357, "lon": 78.1582},
    "Dindigul": {"lat": 10.3673, "lon": 77.9803},
    "Erode": {"lat": 11.341, "lon": 77.7172},
    "Kallakurichi": {"lat": 11.738, "lon": 78.9629},
    "Kancheepuram": {"lat": 12.8352, "lon": 79.7001},
    "Karur": {"lat": 10.9577, "lon": 78.0815},
    "Krishnagiri": {"lat": 12.5186, "lon": 78.2137},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},
    "Mayiladuthurai": {"lat": 11.1036, "lon": 79.655},
    "Nagapattinam": {"lat": 10.77, "lon": 79.84},
    "Namakkal": {"lat": 11.2196, "lon": 78.1652},
    "Nilgiris": {"lat": 11.4916, "lon": 76.7337},
    "Perambalur": {"lat": 11.2333, "lon": 78.8833},
    "Pudukkottai": {"lat": 10.3833, "lon": 78.8167},
    "Ramanathapuram": {"lat": 9.3667, "lon": 78.8333},
    "Ranipet": {"lat": 12.944, "lon": 79.32},
    "Salem": {"lat": 11.6643, "lon": 78.146},
    "Sivaganga": {"lat": 9.847, "lon": 78.4836},
    "Tenkasi": {"lat": 8.959, "lon": 77.315},
    "Thanjavur": {"lat": 10.787, "lon": 79.1378},
    "Theni": {"lat": 10.01, "lon": 77.48},
    "Thoothukudi": {"lat": 8.7642, "lon": 78.1348},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "Tirupathur": {"lat": 12.5, "lon": 78.57},
    "Tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "Tiruvallur": {"lat": 13.1437, "lon": 79.9089},
    "Tiruvannamalai": {"lat": 12.2253, "lon": 79.0747},
    "Tiruvarur": {"lat": 10.77, "lon": 79.63},
    "Vellore": {"lat": 12.9165, "lon": 79.1325},
    "Viluppuram": {"lat": 11.9401, "lon": 79.4861},
    "Virudhunagar": {"lat": 9.574, "lon": 77.9624},
}

def generate_forecast_advisory(f):
    """Generate advisory for a single forecast slot."""
    advisories = []
    temp = float(f["temperature"].replace(" °C", ""))
    humidity = int(f["humidity"].replace("%", ""))
    wind = float(f["wind"].replace(" m/s", ""))
    rain_vol = float(f["rain_volume"].replace(" mm", "").split()[0])

    if temp >= 38:
        advisories.append("Heat wave conditions expected. Stay hydrated and avoid outdoor activities in the afternoon.")
    if rain_vol >= 20:
        advisories.append("Heavy rainfall likely. Avoid low-lying areas and check for flood alerts.")
    if wind >= 15:
        advisories.append("Strong winds expected. Secure loose objects and avoid sea travel.")
    if humidity >= 80 and temp >= 30:
        advisories.append("High humidity with heat may cause discomfort. Use light clothing and stay in ventilated areas.")

    return advisories if advisories else ["No significant advisory for this slot."]

def get_forecast(district: str, hours: int = 24):
    if API_KEY is None:
        return {"error": "API key not found. Please set API_KEY in .env file."}

    if district not in district_coords:
        return {"error": f"District '{district}' not recognized."}

    coords = district_coords[district]
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except Exception as e:
        return {"error": "Failed to fetch weather data", "details": str(e)}

    raw = response.json()
    forecasts, count = [], 0
    end_time = datetime.utcnow() + timedelta(hours=hours)

    for item in raw.get("list", []):
        dt_txt = item.get("dt_txt")
        dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
        if dt > end_time:
            break

        rain_chance = "Yes" if "rain" in item else "No"
        rain_volume = f"{item.get('rain', {}).get('3h', 0)} mm"

        forecast_entry = {
            "time": dt_txt,
            "summary": item["weather"][0]["description"].capitalize(),
            "temperature": f"{item['main']['temp']} °C",
            "humidity": f"{item['main']['humidity']}%",
            "wind": f"{item['wind']['speed']} m/s",
            "rain_chance": rain_chance,
            "rain_volume": rain_volume
        }

        # Add advisory for this slot
        forecast_entry["advisory"] = generate_forecast_advisory(forecast_entry)

        forecasts.append(forecast_entry)
        count += 1

     # Generate overall advisory from all forecasts
    overall_advisories = generate_forecast_advisory({
        "temperature": f"{max([float(f['temperature'].replace(' °C', '')) for f in forecasts])} °C",
        "humidity": f"{max([int(f['humidity'].replace('%', '')) for f in forecasts])}%",
        "wind": f"{max([float(f['wind'].replace(' m/s', '')) for f in forecasts])} m/s",
        "rain_volume": f"{max([float(f['rain_volume'].replace(' mm', '').split()[0]) for f in forecasts])} mm"
    })

    summary = f"Weather forecast for {district} with {len(forecasts)} time slots, including rain chances and expected rainfall."

    return {
        "district": district,
        "requested_hours": hours,
        "valid_for_hours": count * 3,  # each slot is 3h
        "summary": summary,
        "advisory": overall_advisories,  # overall summary advisory
        "source": "OpenWeatherMap",
        "forecasts": forecasts,           # individual slot advisories included
    }
