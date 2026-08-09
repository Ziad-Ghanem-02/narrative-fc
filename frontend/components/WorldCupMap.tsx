"use client";

import { useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
} from "react-simple-maps";
import { scaleLinear } from "d3-scale";

import {
  worldCupStats,
  type CountryStats,
} from "@/lib/worldCupData";

const geoUrl = "/world-countries.json";

const colorScale = scaleLinear<string>()
  .domain([0, 10, 40, 75])
  .range(["#122637", "#315d68", "#4d925d", "#a8cf57"]);

const emptyCountry = (name: string): CountryStats => ({
  name,
  wins: 0,
  draws: 0,
  losses: 0,
  matches: 0,
  peakStage: "Did not qualify",
  confed: "N/A",
});

export default function WorldCupMap() {
  const [hoveredCountry, setHoveredCountry] =
    useState<CountryStats | null>(null);

  return (
    <section className="grid w-full grid-cols-1 gap-5 lg:grid-cols-[minmax(0,2fr)_minmax(260px,1fr)]">
      {/* Map */}
      <div className="relative h-[340px] overflow-hidden rounded-2xl border border-[#183143] bg-[#07131c] shadow-xl sm:h-[420px] lg:h-[480px]">
        <ComposableMap
          projection="geoEqualEarth"
          projectionConfig={{ scale: 140 }}
          className="h-full w-full"
        >
          <Geographies geography={geoUrl}>
            {({ geographies }: { geographies: any[] }) =>
              geographies.map((geo: any) => {
                const countryName =
                  geo.properties?.name ||
                  geo.properties?.NAME ||
                  geo.properties?.ADMIN ||
                  "Unlisted Country";

                const matchedData = worldCupStats[countryName];
                const wins = matchedData?.wins ?? 0;

                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    onMouseEnter={() => {
                      setHoveredCountry(
                        matchedData ?? emptyCountry(countryName)
                      );
                    }}
                    onMouseLeave={() => {
                      setHoveredCountry(null);
                    }}
                    style={{
                      default: {
                        fill: matchedData
                          ? colorScale(wins)
                          : "#122637",
                        stroke: "#284357",
                        strokeWidth: 0.5,
                        outline: "none",
                        transition:
                          "fill 180ms ease, stroke 180ms ease",
                      },
                      hover: {
                        fill: "#efbc42",
                        stroke: "#ffe49b",
                        strokeWidth: 0.9,
                        outline: "none",
                        cursor: "pointer",
                      },
                      pressed: {
                        fill: "#d99f22",
                        stroke: "#ffe49b",
                        outline: "none",
                      },
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ComposableMap>

        <div className="pointer-events-none absolute bottom-4 left-4 rounded-full border border-white/10 bg-[#07131c]/85 px-3 py-1.5 text-xs text-slate-300 backdrop-blur">
          Hover over a country
        </div>
      </div>

      {/* Statistics panel */}
      <aside className="flex min-h-[340px] flex-col justify-between rounded-2xl border border-[#1b3548] bg-[#0b1b28] p-5 shadow-xl sm:p-6 lg:min-h-[480px]">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#efbc42]">
            Live database inspector
          </p>

          {hoveredCountry ? (
            <div className="mt-6">
              <div>
                <p className="text-xs font-medium text-slate-500">
                  Country selected
                </p>

                <h3 className="mt-1 text-2xl font-black text-white sm:text-3xl">
                  {hoveredCountry.name}
                </h3>

                <p className="mt-1 text-xs font-medium text-slate-400">
                  Confederation: {hoveredCountry.confed}
                </p>
              </div>

              <div className="mt-5 rounded-xl border border-[#284357] bg-[#07131c] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  Peak tournament stage
                </p>

                <p className="mt-1 font-bold text-[#efbc42]">
                  {hoveredCountry.peakStage}
                </p>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3">
                <StatCard
                  value={hoveredCountry.wins}
                  label="Wins"
                  valueClassName="text-[#a8cf57]"
                />

                <StatCard
                  value={hoveredCountry.draws}
                  label="Draws"
                  valueClassName="text-[#efbc42]"
                />

                <StatCard
                  value={hoveredCountry.losses}
                  label="Losses"
                  valueClassName="text-rose-400"
                />

                <StatCard
                  value={hoveredCountry.matches}
                  label="Matches"
                  valueClassName="text-sky-300"
                />
              </div>

              {hoveredCountry.matches > 0 && (
                <div className="mt-5 rounded-xl border border-[#284357] bg-[#07131c] p-4">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Historical win rate</span>

                    <span className="font-bold text-white">
                      {(
                        (hoveredCountry.wins /
                          hoveredCountry.matches) *
                        100
                      ).toFixed(1)}
                      %
                    </span>
                  </div>

                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-[#183143]">
                    <div
                      className="h-full rounded-full bg-[#a8cf57] transition-all duration-300"
                      style={{
                        width: `${Math.min(
                          (hoveredCountry.wins /
                            hoveredCountry.matches) *
                            100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="mt-6 flex min-h-[280px] items-center justify-center rounded-xl border border-dashed border-[#284357] bg-[#07131c]/60 p-6 text-center">
              <div>
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#183143] text-xl">
                  🌍
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-400">
                  Hover over any country to inspect its World Cup wins,
                  draws, losses, matches, and best tournament result.
                </p>
              </div>
            </div>
          )}
        </div>

        <p className="mt-6 border-t border-[#1b3548] pt-4 text-xs text-slate-500">
          Source: Fjelstul World Cup Database
        </p>
      </aside>
    </section>
  );
}

interface StatCardProps {
  value: number;
  label: string;
  valueClassName: string;
}

function StatCard({
  value,
  label,
  valueClassName,
}: StatCardProps) {
  return (
    <div className="rounded-xl border border-[#284357] bg-[#07131c] p-4">
      <p className={`text-2xl font-black ${valueClassName}`}>
        {value}
      </p>

      <p className="mt-1 text-xs font-medium text-slate-400">
        {label}
      </p>
    </div>
  );
}