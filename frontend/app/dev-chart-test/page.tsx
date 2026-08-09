"use client";

import { BackendChart } from "@/components/BackendChart";
import type { ChartSpec } from "@/lib/story-types";

const radarChart: ChartSpec = {
  id: "chart-radar",
  type: "radar",
  title: "Underdog multi-metric profile",
  description: "Each metric is scaled 0-100 across the compared teams so it can share one radar chart.",
  x_axis: { data_key: "metric", label: "Metric" },
  y_axis: { label: "Relative score (0-100)", format: "number" },
  series: [
    { data_key: "japan", label: "Japan", color: "#EAB308", render_as: "line" },
    { data_key: "croatia", label: "Croatia", color: "#14B8A6", render_as: "line" },
    { data_key: "morocco", label: "Morocco", color: "#F97316", render_as: "line" },
  ],
  data: [
    { metric: "Goals", japan: 25.0, croatia: 100.0, morocco: 15.0 },
    { metric: "Wins", japan: 30.0, croatia: 100.0, morocco: 20.0 },
    { metric: "Quarterfinals", japan: 0.0, croatia: 100.0, morocco: 0.0 },
    { metric: "Avg Gd Vs Big", japan: 44.0, croatia: 100.0, morocco: 22.0 },
  ],
};

const pieChart: ChartSpec = {
  id: "chart-pie",
  type: "pie",
  title: "Confederation composition snapshot",
  description: "test",
  x_axis: { data_key: "confederation", label: "Confederation" },
  y_axis: { label: "Team Count", format: "number" },
  series: [{ data_key: "team_count", label: "Team Count", color: "#EAB308", render_as: "bar" }],
  data: [
    { confederation: "UEFA", team_count: 4 },
    { confederation: "CONMEBOL", team_count: 2 },
    { confederation: "CAF", team_count: 1 },
    { confederation: "AFC", team_count: 1 },
  ],
};

const scatterChart: ChartSpec = {
  id: "chart-scatter",
  type: "scatter",
  title: "Team performance relationship",
  description: "test",
  x_axis: { data_key: "win_rate", label: "Win Rate" },
  y_axis: { label: "Avg Goal Difference", format: "number" },
  series: [{ data_key: "avg_goal_difference", label: "Avg Goal Difference", color: "#38BDF8", render_as: "line" }],
  data: [
    { team_name: "Japan", win_rate: 45.0, avg_goal_difference: 0.8 },
    { team_name: "Croatia", win_rate: 55.0, avg_goal_difference: 1.1 },
    { team_name: "Morocco", win_rate: 50.0, avg_goal_difference: 0.9 },
  ],
};

const charts = [radarChart, pieChart, scatterChart];

export default function DevChartTest() {
  return (
    <div style={{ background: "#07131c", padding: 40 }}>
      {charts.map((c) => (
        <div key={c.id} style={{ width: 500, marginBottom: 40 }}>
          <h3 style={{ color: "white" }}>{c.title}</h3>
          <BackendChart chart={c} />
        </div>
      ))}
    </div>
  );
}
