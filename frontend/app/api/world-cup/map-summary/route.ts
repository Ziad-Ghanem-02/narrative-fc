import { NextResponse } from "next/server";


const backendUrl = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";


export const dynamic = "force-dynamic";


export async function GET() {
  const response = await fetch(
    `${backendUrl}/api/world-cup/map-summary/`,
    { cache: "no-store" },
  );

  if (!response.ok) {
    return NextResponse.json(
      { detail: "The World Cup map data is currently unavailable." },
      { status: response.status },
    );
  }

  return NextResponse.json(await response.json());
}
