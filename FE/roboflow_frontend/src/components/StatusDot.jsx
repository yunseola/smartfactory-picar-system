// src/components/StatusDot.jsx
export default function StatusDot({ statusValue }) {
  // statusValue가 undefined일 때 기본값을 설정하거나, `false`로 처리하도록
  const s = String(statusValue ?? "true").toUpperCase(); // "false"로 기본값 설정

  let bg = "bg-slate-500"; // 기본 값은 회색

  // 상태에 따른 색상 계산
  if (
    s === "OK" ||
    s === "ONLINE" ||
    s === "RUNNING" ||
    s === "NORMAL" ||
    s === "TRUE" ||
    statusValue === true // boolean true 확인
  ) {
    bg = "bg-emerald-500"; // 정상 (초록 불)
  } else if (s === "WARN" || s === "DEGRADED") {
    bg = "bg-amber-500"; // 경고 (황색 불)
  } else if (s === "ERROR" || s === "OFFLINE" || s === "FALSE" || statusValue === false) {
    bg = "bg-rose-500"; // 오류 또는 비정상 (빨간 불)
  }

  return (
    <div className="flex items-center justify-end">
      <span className={`inline-block h-3 w-3 rounded-full ${bg}`} />
    </div>
  );
}
