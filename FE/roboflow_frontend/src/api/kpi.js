// src/api/kpi.js
import getJson from "./client";

// KPI 합계 1회 조회
export async function fetchKpiSummary() {
  return getJson("/api/kpi/summary");
}
