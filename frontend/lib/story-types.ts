export type ChartType =
  | "area"
  | "bar"
  | "composed"
  | "horizontal_bar"
  | "line"
  | "pie"
  | "radar"
  | "scatter"
  | "stacked_bar"
  | "table";

export interface ChartSeries {
  data_key: string;
  label: string;
  color: string;
  render_as?: "area" | "bar" | "line";
}

export interface ChartSpec {
  id: string;
  type: ChartType;
  title: string;
  description: string;
  x_axis: {
    data_key: string;
    label: string;
  };
  y_axis?: {
    label: string;
    format: "number" | "percentage";
  };
  series: ChartSeries[];
  data: Array<Record<string, string | number | null>>;
}

export interface StoryResponse {
  id: string;
  question: string;
  story: string;
  charts: ChartSpec[];
  created_at: string;
  updated_at: string;
}

export type StoryJobStatus = "queued" | "processing" | "succeeded" | "failed";

export interface StoryJobResponse {
  id: string;
  status: StoryJobStatus;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  story?: StoryResponse;
  detail?: string;
}
