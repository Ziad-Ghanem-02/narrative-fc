import { NextResponse } from "next/server";


const backendUrl = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";


export const dynamic = "force-dynamic";


type RouteContext = {
  params: Promise<{ path: string[] }>;
};


async function proxy(request: Request, context: RouteContext) {
  const { path } = await context.params;
  const method = request.method;
  const hasBody = method !== "GET" && method !== "HEAD";

  try {
    const response = await fetch(
      `${backendUrl}/api/${path.join("/")}/`,
      {
        method,
        headers: hasBody
          ? { "Content-Type": request.headers.get("Content-Type") ?? "application/json" }
          : undefined,
        body: hasBody ? await request.text() : undefined,
        cache: "no-store",
      },
    );

    return new Response(await response.text(), {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch (error) {
    if (error instanceof TypeError) {
      return NextResponse.json(
        { detail: "The backend API is currently unavailable." },
        { status: 502 },
      );
    }

    throw error;
  }
}


export const GET = proxy;
export const POST = proxy;
