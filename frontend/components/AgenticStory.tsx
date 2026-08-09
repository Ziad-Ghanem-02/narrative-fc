import { BackendChart } from "@/components/BackendChart";
import type { ChartSpec } from "@/lib/story-types";


interface AgenticStoryProps {
  story: string;
  charts: ChartSpec[];
}


const chartMarker = /^\[chart:([a-z0-9-]+)\]$/;


export function AgenticStory({ story, charts }: AgenticStoryProps) {
  const chartsById = new Map(charts.map((chart) => [chart.id, chart]));
  const referencedChartIds = new Set<string>();
  const content = story.split(/(\[chart:[a-z0-9-]+\])/g);

  return (
    <div className="space-y-5 text-sm leading-7 text-slate-200">
      {content.map((part, index) => {
        const marker = part.match(chartMarker);
        if (marker) {
          const chart = chartsById.get(marker[1]);
          if (!chart) {
            return null;
          }

          referencedChartIds.add(chart.id);
          return <ChartCard chart={chart} key={chart.id} />;
        }

        return part
          .split(/\n{2,}/)
          .filter(Boolean)
          .map((paragraph, paragraphIndex) => (
            <p key={`${index}-${paragraphIndex}`}>{paragraph.trim()}</p>
          ));
      })}

      {charts
        .filter((chart) => !referencedChartIds.has(chart.id))
        .map((chart) => <ChartCard chart={chart} key={chart.id} />)}
    </div>
  );
}


function ChartCard({ chart }: { chart: ChartSpec }) {
  return (
    <figure className="my-8 rounded-xl border border-white/10 bg-[#07131c] p-4">
      <figcaption className="mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wide text-white">
          {chart.title}
        </h3>
        {chart.description && (
          <p className="mt-1 text-xs leading-5 text-slate-400">
            {chart.description}
          </p>
        )}
      </figcaption>
      <BackendChart chart={chart} />
    </figure>
  );
}
