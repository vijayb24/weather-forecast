import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const districts = [
  "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode",
  "Kallakurichi", "Kancheepuram", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam",
  "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga",
  "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur",
  "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"
];

const durations = [
  { label: "Next 3 hours", hours: 3 },
  { label: "Next 12 hours", hours: 12 },
  { label: "Next 24 hours", hours: 24 },
  { label: "Next 36 hours", hours: 36 },
  { label: "Next 48 hours", hours: 48 },
  { label: "Next 72 hours", hours: 72 },
  { label: "Next 5 days (~120h)", hours: 120 },
  { label: "Next 10 days (~240h)", hours: 240 },
];

function WeatherForecast() {
  const [district, setDistrict] = useState("Chennai");
  const [hours, setHours] = useState(3);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const fetchForecast = async () => {
    setError("");
    setData(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/forecast/${encodeURIComponent(district)}?hours=${hours}`);
      const json = await res.json();
      if (json.error) {
        setError(json.error + (json.details ? ` — ${json.details}` : ""));
      } else {
        setData(json);
      }
    } catch (e) {
      setError("Failed to fetch forecast. Check backend is running.");
    }
  };

  const getCardStyles = (idx) => {
    return idx % 2 === 0
      ? { backgroundColor: "#0B3D91", color: "#FFFFFF" } // deep navy
      : { backgroundColor: "#4B0082", color: "#FFFFFF" }; // deep purple
  };

  return (
    <div className="container py-5">
      <h1 className="text-center mb-4 text-primary fw-bold">
        Tamil Nadu Weather Forecast
      </h1>

      {/* Filters */}
      <div className="d-flex flex-wrap justify-content-center gap-3 mb-4">
        <div className="d-flex align-items-center">
          <label className="me-2 fw-medium">District:</label>
          <select
            className="form-select"
            style={{ width: "200px" }}
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          >
            {districts.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="d-flex align-items-center">
          <label className="me-2 fw-medium">Duration:</label>
          <select
            className="form-select"
            style={{ width: "200px" }}
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
          >
            {durations.map((d) => (
              <option key={d.hours} value={d.hours}>
                {d.label}
              </option>
            ))}
          </select>
        </div>

        <button onClick={fetchForecast} className="btn btn-primary shadow">
          Get Forecast
        </button>
      </div>

      {/* Error */}
      {error && <p className="text-danger text-center">{error}</p>}

      {/* Forecast Results */}
      {data && (
        <div className="row g-4">
          {data.forecasts.map((f, idx) => (
            <div key={idx} className="col-sm-6 col-md-4">
              <div className="card shadow-sm h-100 border-0" style={getCardStyles(idx)}>
                <div className="card-body">
                  <h5 className="card-title fw-bold">{f.time}</h5>
                  <p className="card-text">{f.summary || "No summary available."}</p>

                  <ul className="list-unstyled small">
                    <li>🌡 <strong>Temp:</strong> {f.temperature}</li>
                    <li>💧 <strong>Humidity:</strong> {f.humidity}</li>
                    <li>🌬 <strong>Wind:</strong> {f.wind}</li>
                    <li>☔ <strong>Rain chance:</strong> {f.rain_chance}</li>
                    <li>🌧 <strong>Rain volume:</strong> {f.rain_volume}</li>
                  </ul>

                  {f.advisory && (
                    <div className="alert alert-warning p-2 mt-3 small">
                      ⚠️ <strong>Advisory:</strong> {f.advisory}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default WeatherForecast;
