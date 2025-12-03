// src/api/environment.js
import getJson from "./client";

export async function fetchEnvironment() {
  console.log("fetchEnvironment called");
  const raw = await getJson("/api/environment");

  const temperatureC =
    typeof raw.temperatureC === "number"
      ? raw.temperatureC  // ✅ 오타 수정
      : parseFloat(
          String(raw.temperature ?? raw.temperatureC ?? "")
            .replace(/[^\d.]/g, "")
        ) || 0;

  const humidityPct =
    typeof raw.humidityPct === "number"
      ? raw.humidityPct
      : parseFloat(
          String(raw.humidity ?? raw.humidityPct ?? "")
            .replace(/[^\d.]/g, "")
        ) || 0;

  const data = { temperatureC, humidityPct };
  console.log("Normalized environment:", data);
  return data;
}
export default fetchEnvironment;
