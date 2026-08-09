"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ChartSeries, ChartSpec } from "@/lib/story-types";


interface BackendChartProps {
  chart: ChartSpec;
}


const fallbackColors = ["#EAB308", "#14B8A6", "#F97316", "#8B5CF6", "#F43F5E"];
const tooltipStyle = {
  backgroundColor: "#07131c",
  border: "1px solid rgba(234,179,8,.35)",
  borderRadius: 12,
  boxShadow: "0 16px 36px rgba(0,0,0,.35)",
  color: "#f8fafc",
};


function formatValue(value: string | number, format: "number" | "percentage") {
  const numericValue = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(numericValue)) {
    return String(value);
  }
  if (format === "percentage") {
    return `${numericValue.toFixed(1)}%`;
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(numericValue);
}


export function BackendChart({ chart }: BackendChartProps) {
  const yAxis = chart.y_axis ?? { label: "Value", format: "number" as const };
  const firstSeries = chart.series[0];
  const axisProps = {
    stroke: "#94a3b8",
    tick: { fill: "#cbd5e1", fontSize: 11 },
  };
  const sharedAxes = [
    <CartesianGrid key="grid" stroke="#18303f" strokeDasharray="3 4" vertical={false} />,
    <XAxis
      {...axisProps}
      dataKey={chart.x_axis.data_key}
      height={44}
      key="x-axis"
      label={{
        value: chart.x_axis.label,
        fill: "#94a3b8",
        fontSize: 11,
        position: "insideBottom",
        offset: -4,
      }}
    />,
    <YAxis
      {...axisProps}
      key="y-axis"
      tickFormatter={(value) => formatValue(value, yAxis.format)}
      width={52}
      label={{
        value: yAxis.label,
        fill: "#94a3b8",
        fontSize: 11,
        angle: -90,
        position: "insideLeft",
        offset: 10,
      }}
    />,
    <Tooltip
      contentStyle={tooltipStyle}
      formatter={(value: string | number, name: string) => [
        formatValue(value, yAxis.format),
        name,
      ]}
      key="tooltip"
    />,
    <Legend key="legend" wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />,
  ];

  if (chart.type === "table") {
    return (
      <div className="max-h-80 overflow-auto rounded-lg border border-white/10">
        <table className="w-full border-collapse text-left text-xs">
          <thead className="sticky top-0 bg-[#0b1b28]">
            <tr className="border-b border-white/10 text-slate-300">
              <th className="p-3">{chart.x_axis.label}</th>
              {chart.series.map((series) => (
                <th className="p-3" key={series.data_key}>{series.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {chart.data.map((row, index) => (
              <tr className="border-b border-white/5 text-slate-300" key={index}>
                <td className="p-3">{String(row[chart.x_axis.data_key] ?? "")}</td>
                {chart.series.map((series) => (
                  <td className="p-3" key={series.data_key}>
                    {String(row[series.data_key] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (chart.type === "pie" && firstSeries) {
    return (
      <ResponsiveContainer height={320} width="100%">
        <PieChart>
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value: string | number) => formatValue(value, yAxis.format)}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Pie
            data={chart.data}
            dataKey={firstSeries.data_key}
            nameKey={chart.x_axis.data_key}
            outerRadius="76%"
            paddingAngle={3}
          >
            {chart.data.map((_, index) => (
              <Cell
                fill={
                  chart.series.length > 1
                    ? chart.series[index % chart.series.length]?.color ?? fallbackColors[index % fallbackColors.length]
                    : fallbackColors[index % fallbackColors.length]
                }
                key={index}
              />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (chart.type === "radar") {
    return (
      <ResponsiveContainer height={320} width="100%">
        <RadarChart data={chart.data}>
          <PolarGrid stroke="#284357" />
          <PolarAngleAxis dataKey={chart.x_axis.data_key} tick={{ fill: "#cbd5e1", fontSize: 11 }} />
          <PolarRadiusAxis tick={{ fill: "#94a3b8", fontSize: 10 }} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          {chart.series.map((series) => (
            <Radar
              dataKey={series.data_key}
              fill={series.color}
              fillOpacity={0.2}
              key={series.data_key}
              name={series.label}
              stroke={series.color}
              strokeWidth={2}
            />
          ))}
        </RadarChart>
      </ResponsiveContainer>
    );
  }

  if (chart.type === "scatter" && firstSeries) {
    return (
      <ResponsiveContainer height={320} width="100%">
        <ScatterChart margin={{ bottom: 16, left: 16, right: 16, top: 8 }}>
          <CartesianGrid stroke="#18303f" strokeDasharray="3 4" />
          <XAxis
            {...axisProps}
            dataKey={chart.x_axis.data_key}
            label={{ value: chart.x_axis.label, fill: "#94a3b8", fontSize: 11, position: "insideBottom", offset: -4 }}
          />
          <YAxis
            {...axisProps}
            dataKey={firstSeries.data_key}
            label={{ value: yAxis.label, fill: "#94a3b8", fontSize: 11, angle: -90, position: "insideLeft" }}
          />
          <Tooltip contentStyle={tooltipStyle} />
          <Scatter data={chart.data} fill={firstSeries.color} name={firstSeries.label} />
        </ScatterChart>
      </ResponsiveContainer>
    );
  }

  if (chart.type === "horizontal_bar") {
    return (
      <ResponsiveContainer height={320} width="100%">
        <BarChart data={chart.data} layout="vertical" margin={{ left: 24, right: 16 }}>
          <CartesianGrid stroke="#18303f" strokeDasharray="3 4" horizontal={false} />
          <XAxis {...axisProps} tickFormatter={(value) => formatValue(value, yAxis.format)} type="number" />
          <YAxis {...axisProps} dataKey={chart.x_axis.data_key} type="category" width={100} />
          <Tooltip contentStyle={tooltipStyle} />
          {chart.series.map((series) => (
            <Bar
              dataKey={series.data_key}
              fill={series.color}
              key={series.data_key}
              name={series.label}
              radius={[0, 6, 6, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (chart.type === "area") {
    return (
      <ResponsiveContainer height={320} width="100%">
        <AreaChart data={chart.data}>
          <defs>
            {chart.series.map((series) => (
              <linearGradient id={`fill-${chart.id}-${series.data_key}`} key={series.data_key} x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor={series.color} stopOpacity={0.55} />
                <stop offset="95%" stopColor={series.color} stopOpacity={0.03} />
              </linearGradient>
            ))}
          </defs>
          {sharedAxes}
          {chart.series.map((series) => (
            <Area
              dataKey={series.data_key}
              fill={`url(#fill-${chart.id}-${series.data_key})`}
              key={series.data_key}
              name={series.label}
              stroke={series.color}
              strokeWidth={2}
              type="monotone"
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  if (chart.type === "composed") {
    return (
      <ResponsiveContainer height={320} width="100%">
        <ComposedChart data={chart.data}>
          {sharedAxes}
          {chart.series.map((series) => renderComposedSeries(series, chart.type))}
        </ComposedChart>
      </ResponsiveContainer>
    );
  }

  if (chart.type === "line") {
    return (
      <ResponsiveContainer height={320} width="100%">
        <LineChart data={chart.data}>
          {sharedAxes}
          {chart.series.map((series) => (
            <Line
              activeDot={{ r: 5 }}
              dataKey={series.data_key}
              key={series.data_key}
              name={series.label}
              stroke={series.color}
              strokeWidth={2.5}
              type="monotone"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer height={320} width="100%">
      <BarChart data={chart.data}>
        {sharedAxes}
        {chart.series.map((series) => (
          <Bar
            dataKey={series.data_key}
            fill={series.color}
            key={series.data_key}
            name={series.label}
            radius={[6, 6, 0, 0]}
            stackId={chart.type === "stacked_bar" ? "series" : undefined}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}


function renderComposedSeries(series: ChartSeries, chartType: ChartSpec["type"]) {
  if (series.render_as === "area") {
    return (
      <Area
        dataKey={series.data_key}
        fill={series.color}
        fillOpacity={0.2}
        key={series.data_key}
        name={series.label}
        stroke={series.color}
        type="monotone"
      />
    );
  }
  if (series.render_as === "line" || chartType === "line") {
    return (
      <Line
        dataKey={series.data_key}
        key={series.data_key}
        name={series.label}
        stroke={series.color}
        strokeWidth={2.5}
        type="monotone"
      />
    );
  }
  return (
    <Bar
      dataKey={series.data_key}
      fill={series.color}
      key={series.data_key}
      name={series.label}
      radius={[6, 6, 0, 0]}
    />
  );
}
