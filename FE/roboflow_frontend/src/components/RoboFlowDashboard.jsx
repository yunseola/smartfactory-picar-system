// src/components/RoboFlowDashboard.jsx
import React, { useEffect, useState, useRef } from "react";
import { fetchKpiSummary, fetchEventLogs } from "../api";
import { fetchEnvironment } from "../api/environment";
import { fetchSystemStatus } from "../api/system";
import  createWebSocketClient  from "../api/webSocketClient";

import AgvCamera01 from "./AgvCamera01";
import AgvCamera02 from "./AgvCamera02";
import ConveyorCamera from "./ConveyorCamera";

import GaugeDonut from "./GaugeDonut";
import StatusDot from "./StatusDot";


const CAM_HEIGHT = 170;
const PAGE_SIZE = 4;

const sizeMap = {
  xs: "text-[0.7rem] md:text-xs",
  sm: "text-xs md:text-sm",
  md: "text-sm md:text-base",
  lg: "text-base md:text-lg",
  xl: "text-lg md:text-xl",
  xxl: "text-xl md:text-2xl",
};

function SectionTitle({ children, size = "xl", className = "" }) {
  return (
    <div
      role="heading"
      aria-level={3}
      className={`mb-1.5 md:mb-2.5 font-semibold tracking-wide text-slate-200 ${sizeMap[size]} ${className}`}
    >
      {children}
    </div>
  );
}

const KpiItem = ({ label, value }) => {
  const animated = useAnimatedNumber(value ?? 0, 700);
  const [bump, setBump] = useState(false);

  useEffect(() => {
    setBump(true);
    const id = setTimeout(() => setBump(false), 180);
    return () => clearTimeout(id);
  }, [value]);

  return (
    <div
      className="flex flex-col items-center justify-center
                 rounded-2xl bg-slate-900/80 border border-slate-600/70
                 px-2 md:px-2.5 py-2 md:py-2.5 shadow-md shadow-black/20"
    >
      <span className="text-xs md:text-sm font-semibold tracking-wide text-slate-200">
        {label}
      </span>

      <span
        className={
          "mt-1 md:mt-1.5 text-2xl md:text-3xl xl:text-4xl font-extrabold tracking-tight text-white " +
          "transform transition-transform duration-200 " +
          (bump ? "scale-110" : "scale-100")
        }
      >
        {Math.round(animated).toLocaleString()}
      </span>
    </div>
  );
};

export default function RoboFlowDashboard() {
  const [kpi, setKpi] = useState({
    total: 0,
    a: 0,
    b: 0,
    def: 0,
    loading: true,
    err: null,
  });

  const [env, setEnv] = useState({
    temperatureC: 0,
    humidityPct: 0,
    loading: true,
    err: null,
  });

  const [sys, setSys] = useState({ data: null, loading: true, err: null });

  const [logs, setLogs] = useState({
    content: [],
    page: 0,
    size: PAGE_SIZE,
    totalPages: 0,
    loading: true,
    err: null,
  });

  useEffect(() => {
    // 데이터 초기 로딩
    const loadData = async () => {
      try {
        const s = await fetchKpiSummary();
        setKpi({
          total: s.total ?? 0,
          a: s.lineA ?? s.a ?? 0,
          b: s.lineB ?? s.b ?? 0,
          def: s.defective ?? s.def ?? 0,
          loading: false,
          err: null,
        });
      } catch (e) {
        setKpi({ ...kpi, loading: false, err: e.message });
      }

      try {
        const e = await fetchEnvironment();
        setEnv({
          temperatureC: e.temperatureC,
          humidityPct: e.humidityPct,
          loading: false,
          err: null,
        });
      } catch (err) {
        setEnv({ ...env, loading: false, err: err.message });
      }

      try {
        const s = await fetchSystemStatus();
        console.log('System Status:', s);
        setSys({ data: s, loading: false, err: null });
      } catch (err) {
        setSys({ ...sys, loading: false, err: err.message });
      }

      loadLogs(0, PAGE_SIZE);
    };

    loadData();

    // WebSocket 연결 및 실시간 데이터 업데이트
    const webSocket = createWebSocketClient(); // 수정


    webSocket.onConnect(
      (body) => {
        setKpi({
          total: body.total ?? kpi.total,
          a: body.lineA ?? kpi.a,
          b: body.lineB ?? kpi.b,
          def: body.defective ?? kpi.def,
          loading: false,
          err: null,
        });
      },
      (body) => {
        setEnv({
          temperatureC: body.temperatureC ?? env.temperatureC,
          humidityPct: body.humidityPct ?? env.humidityPct,
          loading: false,
          err: null,
        });
      },
      (log) => {
        setLogs((prev) => ({ ...prev, content: [log, ...prev.content] }));
      }
    );

    return () => {
      webSocket.deactivate();
    };
  }, []);

  async function loadLogs(page = 0, size = PAGE_SIZE) {
    try {
      const r = await fetchEventLogs({ page, size });
      setLogs({
        content: r.content ?? [],
        page: r.page ?? page,
        size: r.size ?? size,
        totalPages: r.totalPages ?? 0,
        loading: false,
        err: null,
      });
    } catch (e) {
      setLogs({ ...logs, loading: false, err: e.message });
    }
  }

const filteredLogs = logs.content.filter(
  (row) => row.event_content === "불량 인덕터 감지"
);

  return (
    <div className="min-h-screen w-full bg-slate-900 px-3 md:px-4 py-2 text-slate-100">
      <div className="mx-auto w-full max-w-6xl">
        <h1 className="text-2xl md:text-3xl xl:text-4xl font-extrabold leading-none tracking-tight">
          RoboFlow
        </h1>

        {/* ---------- 1행: 카메라 3칸 ---------- */}
        <div className="grid grid-cols-12 gap-2.5">
          {/* AGV 01 : WebRTC */}
          <Card className="col-span-12 md:col-span-6 xl:col-span-4">
            <div className="mb-1 flex items-center justify-between">
              <SectionTitle size="lg" className="mb-0">
                AGV 01
              </SectionTitle>
              <Badge ok>정상</Badge>
            </div>
            <AgvCamera01 height={CAM_HEIGHT} />
          </Card>

          {/* AGV 02 : WebRTC */}
          <Card className="col-span-12 md:col-span-6 xl:col-span-4">
            <div className="mb-1 flex items-center justify-between">
              <SectionTitle size="lg" className="mb-0">
                AGV 02
              </SectionTitle>
              <Badge ok>정상</Badge>
            </div>
            <AgvCamera02 height={CAM_HEIGHT} />
          </Card>

          {/* Conveyor : WebRTC */}
          <Card className="col-span-12 md:col-span-12 xl:col-span-4">
            <div className="mb-1 flex items-center justify-between">
              <SectionTitle size="lg" className="mb-0">
                Conveyor
              </SectionTitle>
              <Badge warn>에러</Badge>
            </div>
            <ConveyorCamera height={CAM_HEIGHT} />
          </Card>
        </div>

        {/* ---------- 2행: KPI / Environment / System Status ---------- */}
        <div className="mt-2.5 grid grid-cols-12 gap-2.5">
          {/* KPI 숫자 카드 4개 */}
          <Card className="col-span-12 xl:col-span-6">
            <div className="flex h-full flex-col">
              <SectionTitle>KPI</SectionTitle>

              {kpi.loading ? (
                <div className="flex-1 flex items-center justify-center p-3 text-slate-300 text-xs md:text-sm">
                  불러오는 중…
                </div>
              ) : kpi.err ? (
                <div className="flex-1 flex items-center justify-center p-3 text-rose-300 text-xs md:text-sm">
                  KPI 로드 실패: {kpi.err}
                </div>
              ) : (
                <div
                  className="mt-1 flex-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4
                            gap-2.5 items-stretch"
                >
                  <KpiItem label="총 처리량" value={kpi.total} />
                  <KpiItem label="1번 제품" value={kpi.a} />
                  <KpiItem label="2번 제품" value={kpi.b} />
                  <KpiItem label="불량" value={kpi.def} />
                </div>
              )}
            </div>
          </Card>

          {/* Environment */}
          <Card className="col-span-12 md:col-span-6 xl:col-span-3">
            <SectionTitle>Environment</SectionTitle>
            {env.loading ? (
              <div className="p-3 text-slate-300 text-xs md:text-sm">
                불러오는 중…
              </div>
            ) : env.err ? (
              <div className="p-3 text-rose-300 text-xs md:text-sm">
                환경값 로드 실패: {env.err}
              </div>
            ) : (
              <div className="mt-1.5 flex flex-wrap items-center justify-evenly gap-2.5">
                <GaugeDonut
                  value={env.temperatureC}
                  unit="°"
                  label="온도"
                  size={100}
                  stroke={9}
                  color="#9fb1ff"
                  valueClassName="text-xl md:text-2xl font-extrabold text-white"
                  labelClassName="mt-1 text-xs md:text-sm text-slate-300"
                />
                <GaugeDonut
                  value={env.humidityPct}
                  unit="%"
                  label="습도"
                  size={100}
                  stroke={9}
                  color="#9fb1ff"
                  valueClassName="text-xl md:text-2xl font-extrabold text-white"
                  labelClassName="mt-1 text-xs md:text-sm text-slate-300"
                />
              </div>
            )}
          </Card>

          {/* System Status */}
          <Card className="col-span-12 md:col-span-6 xl:col-span-3">
            <div className="flex h-full flex-col">
              <SectionTitle className="mb-1">System Status</SectionTitle>

              {sys.loading ? (
                <div className="flex-1 flex items-center">
                  <div className="text-slate-300 text-xs md:text-sm">
                    불러오는 중…
                  </div>
                </div>
              ) : sys.err ? (
                <div className="flex-1 flex items-center">
                  <div className="text-rose-300 text-xs md:text-sm">
                    상태 로드 실패: {sys.err}
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex items-center">
                  <div className="grid grid-cols-2 gap-x-3 gap-y-2 text-xs md:text-sm w-full">
                    <Row label="Environment" value={sys.data?.environment} />
                    <Row label="Event Log" value={sys.data?.eventlog} />
                    <Row label="KPI" value={sys.data?.kpi} />
                    <Row label="AGV1 Camera" value={sys.data?.cameraAgv1} />
                    <Row label="AGV2 Camera" value={sys.data?.cameraAgv2} />
                    <Row label="Conveyor Cam" value={false} />
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* ---------- 3행: Event Log ---------- */}
        <Card className="mt-2.5">
          <SectionTitle>Event Log</SectionTitle>
          {logs.loading ? (
            <div className="p-3 text-slate-300 text-xs md:text-sm">
              불러오는 중…
            </div>
          ) : logs.err ? (
            <div className="p-3 text-rose-300 text-xs md:text-sm">
              EventLog 로드 실패: {logs.err}
            </div>
          ) : (
            <>
              <div className="overflow-hidden rounded-xl border border-slate-800">
                <table className="min-w-full divide-y divide-slate-800 text-xs md:text-sm">
                  <thead className="bg-slate-800/60 text-slate-300">
                    <tr>
                      <th className="px-3 md:px-4 py-1.5 text-left font-semibold">
                        제품명
                      </th>
                      <th className="px-3 md:px-4 py-1.5 text-left font-semibold">
                        위치
                      </th>
                      <th className="px-3 md:px-4 py-1.5 text-left font-semibold">
                        시간
                      </th>
                      <th className="px-3 md:px-4 py-1.5 text-left font-semibold">
                        이벤트
                      </th>
                      <th className="px-3 md:px-4 py-1.5 text-left font-semibold">
                        모듈
                      </th>
                      <th className="px-3 md:px-4 py-1.5 text-left font-semibold">
                        상태
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {filteredLogs.map((row, i) => (
                      <tr
                        key={i}
                        className="bg-slate-900/40 hover:bg-slate-800/40"
                      >
                        <td className="px-5 py-4 text-slate-200">
                          {row.product_name || "-"}
                        </td>
                        <td className="px-5 py-4 text-slate-300">
                          {row.event_location}
                        </td>
                        <td className="px-5 py-4 text-slate-300">
                          {formatDateTime(row.created_at)}
                        </td>
                        <td className="px-5 py-4 text-slate-300">
                          {row.event_content}
                        </td>
                        <td className="px-5 py-4 text-slate-300">
                          {row.module_name}
                        </td>
                        <td className="px-5 py-4">
                          <span className="rounded-md bg-rose-700/30 px-2.5 py-1 text-xs md:text-sm text-rose-200 ring-1 ring-rose-800/40">
                            오류
                          </span>
                        </td>
                      </tr>
                    ))}

                    {filteredLogs.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-5 py-8 text-center text-slate-400">
                          표시할 로그가 없습니다.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="mt-2 flex items-center justify-end gap-2.5">
                <button
                  className="rounded-md border border-slate-700 px-3 py-1 text-xs md:text-sm text-slate-200 disabled:opacity-40"
                  onClick={() => loadLogs(Math.max(0, logs.page - 1), logs.size)}
                  disabled={logs.page <= 0}
                >
                  이전
                </button>
                <span className="text-xs md:text-sm text-slate-300">
                  {logs.page + 1} / {Math.max(1, logs.totalPages)}
                </span>
                <button
                  className="rounded-md border border-slate-700 px-3 py-1 text-xs md:text-sm text-slate-200 disabled:opacity-40"
                  onClick={() =>
                    loadLogs(
                      Math.min((logs.totalPages || 1) - 1, logs.page + 1),
                      logs.size
                    )
                  }
                  disabled={logs.page + 1 >= logs.totalPages}
                >
                  다음
                </button>
              </div>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}

// 보조 컴포넌트
function Card({ className = "", children }) {
  return (
    <div
      className={`rounded-2xl border border-slate-800 bg-slate-850/40 p-2.5 md:p-3 ${className}`}
    >
      {children}
    </div>
  );
}

function Badge({ ok, warn, children }) {
  const cls = ok
    ? "bg-emerald-600/80"
    : warn
    ? "bg-amber-600/80"
    : "bg-slate-600/70";
  return (
    <span className={`rounded-md px-2 py-0.5 text-[0.7rem] md:text-xs font-semibold ${cls}`}>
      {children}
    </span>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate-300 text-xs md:text-sm">{label}</span>
      <StatusDot status={value} />
    </div>
  );
}

function formatDateTime(isoLike) {
  try {
    const d = new Date(isoLike);
    const yyyy = d.getFullYear();
    const MM = `${d.getMonth() + 1}`.padStart(2, "0");
    const dd = `${d.getDate()}`.padStart(2, "0");
    const hh = `${d.getHours()}`.padStart(2, "0");
    const mm = `${d.getMinutes()}`.padStart(2, "0");
    const ss = `${d.getSeconds()}`.padStart(2, "0");
    return `${yyyy}-${MM}-${dd} ${hh}:${mm}:${ss}`;
  } catch {
    return "";
  }
}

// 숫자 애니메이션 훅
function useAnimatedNumber(value, duration = 800) {
  const [display, setDisplay] = useState(value ?? 0);
  const prevRef = useRef(value ?? 0);

  useEffect(() => {
    const from = prevRef.current ?? 0;
    const to = value ?? 0;
    if (from === to) return;

    const start = performance.now();
    const diff = to - from;

    function frame(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out

      setDisplay(from + diff * eased);

      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        prevRef.current = to;
      }
    }

    requestAnimationFrame(frame);
  }, [value, duration]);

  return display;
}