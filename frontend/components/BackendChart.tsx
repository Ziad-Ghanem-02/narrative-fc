"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ChartSpec } from "@/lib/story-types";


interface BackendChartProps {
  chart: ChartSpec;
}


const tooltipStyle = {
  backgroundColor: "#07131c",
  border: "1px solid rgba(148,163,184,.2)",
  borderRadius: 8,
};


export function BackendChart({ chart }: BackendChartProps) {
  if (chart.type === "table") {
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="border-b border-white/10 text-slate-400">
              <th className="p-2">{chart.x_axis.label}</th>
              {chart.series.map((series) => (
                <th className="p-2" key={series.data_key}>{series.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {chart.data.map((row, index) => (
              <tr className="border-b border-white/5" key={index}>
                <td className="p-2">{String(row[chart.x_axis.data_key] ?? "")}</td>
                {chart.series.map((series) => (
                  <td className="p-2" key={series.data_key}>
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

  if (chart.type === "scatter") {
    const firstSeries = chart.series[0];
    return (
      <ResponsiveContainer height={280} width="100%">
        <ScatterChart>
          <CartesianGrid stroke="#18303f" />
          <XAxis dataKey={chart.x_axis.data_key} name={chart.x_axis.label} />
          <YAxis dataKey={firstSeries?.data_key} name={firstSeries?.label} />
          <Tooltip contentStyle={tooltipStyle} />
          <Scatter data={chart.data} fill={firstSeries?.color} />
        </ScatterChart>
      </ResponsiveContainer>
    );
  }

  const axes = (
    <>
      <CartesianGrid stroke="#18303f" />
      <XAxis dataKey={chart.x_axis.data_key} />
      <YAxis />
      <Tooltip contentStyle={tooltipStyle} />
      <Legend />
    </>
  );

  if (chart.type === "line") {
    return (
      <ResponsiveContainer height={280} width="100%">
        <LineChart data={chart.data}>
          {axes}
          {chart.series.map((series) => (
            <Line
              dataKey={series.data_key}
              key={series.data_key}
              name={series.label}
              stroke={series.color}
              strokeWidth={2}
              type="monotone"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer height={280} width="100%">
      <BarChart data={chart.data}>
        {axes}
        {chart.series.map((series) => (
          <Bar
            dataKey={series.data_key}
            fill={series.color}
            key={series.data_key}
            name={series.label}
            stackId={chart.type === "stacked_bar" ? "series" : undefined}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
