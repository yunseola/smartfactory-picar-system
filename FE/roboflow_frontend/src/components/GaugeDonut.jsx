// src/components/GaugeDonut.jsx
import React from "react";

export default function GaugeDonut({
  value = 0,
  min = 0,
  max = 100,
  unit = "",
  label = "",
  size = 150,              // 게이지 외경
  stroke = 14,             // 두께
  color = "#9fb1ff",       // 진행색
  track = "#263241",       // 트랙색
  valueClassName = "text-3xl md:text-4xl font-bold text-white",
  labelClassName = "mt-2 text-sm md:text-base text-slate-300",
}) {
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const pct = clamp((value - min) / (max - min || 1), 0, 1);

  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = c * pct;

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* 트랙 */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={track}
            strokeWidth={stroke}
          />
          {/* 진행 */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${c - dash}`}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        </svg>

        {/* 중앙 값 */}
        <div className="absolute inset-0 grid place-items-center pointer-events-none">
          <div className={valueClassName}>
            {Math.round(value)}
            <span className="ml-1 align-middle opacity-80 text-sm">{unit}</span>
          </div>
        </div>
      </div>

      {/* 라벨(온도/습도) */}
      <div className={labelClassName}>{label}</div>
    </div>
  );
}
