import { NextRequest, NextResponse } from "next/server";

const FASTAPI_BASE =
  process.env.FASTAPI_BASE_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { threadId, message, mode } = body as {
      threadId?: string | null;
      message: string;
      mode?: "continue" | "start";
    };

    if (!message || typeof message !== "string") {
      return NextResponse.json(
        { error: "message is required" },
        { status: 400 }
      );
    }

    let upstream: Response;

    if (!threadId || mode === "start") {
      upstream = await fetch(`${FASTAPI_BASE}/api/v1/graph/simple/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: message }),
      });
    } else {
      upstream = await fetch(
        `${FASTAPI_BASE}/api/v1/graph/simple/${threadId}/continue`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ human_input: message }),
        }
      );
    }

    const data = await upstream.json();

    if (!upstream.ok || !data?.success) {
      return NextResponse.json(
        { error: data?.message || "Upstream error", raw: data },
        { status: 500 }
      );
    }

    return NextResponse.json({
      threadId: data.thread_id,
      waitingForHuman: data.waiting_for_human,
      finalResponse: data.data?.final_response,
      tokenUsage: data.data?.token_usage,
      filePath: data.data?.file_path,
      fileContent: data.data?.file_content,
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Unknown error" },
      { status: 500 }
    );
  }
}

