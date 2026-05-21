// App.js
import React from "react";
import WeatherForecast from './components/WeatherForecast'

function App() {
  return (
    <div style={{fontFamily:"Arial, sans-serif", maxWidth:900, margin:"20px auto"}}>
      <h1 className="text-center">KTCC / Tamil Nadu Weather</h1>
      <WeatherForecast />
    </div>
  );
}

export default App;
