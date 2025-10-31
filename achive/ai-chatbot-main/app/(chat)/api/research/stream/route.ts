/**
 * Research Stream API Route
 *
 * This route acts as a proxy between the Next.js frontend and the FastAPI backend.
 * It receives research requests from the client and forwards them to the FastAPI
 * /research/stream endpoint, then streams the SSE events back to the client.
 *
 * Phase 3: User-Triggered Research Architecture
 */

import { NextRequest } from "next/server";
import { auth } from "@/app/(auth)/auth";
import { ChatSDKError } from "@/lib/errors";

export const runtime = "nodejs";
export const maxDuration = 300; // 5 minutes for long research tasks

/**
 * POST /api/research/stream
 *
 * Request body:
 * {
 *   "prompt": string  // Research query/topic
 * }
 *
 * Response: Server-Sent Events stream with the following event types:
 * - start: Research task started
 * - plan: Research plan generated
 * - progress: Research progress update (search results, web pages, etc.)
 * - done: Research completed with final report
 * - error: Error occurred during research
 */
export async function POST(request: NextRequest) {
  // Verify authentication
  const session = await auth();

  if (!session || !session.user) {
    return new Response(
      JSON.stringify({
        error: "Unauthorized: Please sign in to use research features",
      }),
      {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // Parse request body
  let prompt: string;

  try {
    const body = await request.json();
    prompt = body.prompt;

    if (!prompt || typeof prompt !== "string" || prompt.trim().length === 0) {
      return new Response(
        JSON.stringify({
          error: "Invalid prompt: must be a non-empty string",
        }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: "Invalid request body: expected JSON with 'prompt' field",
      }),
      {
        status: 400,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // Get FastAPI backend URL from environment
  const researchApiUrl = process.env.RESEARCH_API_URL || "http://localhost:8000";
  const backendUrl = `${researchApiUrl}/research/stream`;

  try {
    // Forward request to FastAPI backend
    const response = await fetch(backendUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ prompt: prompt.trim() }),
    });

    // Check if backend request was successful
    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `FastAPI backend error (${response.status}): ${errorText}`
      );

      return new Response(
        JSON.stringify({
          error: `Backend error: ${response.statusText}`,
          details: errorText,
        }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Check if response is SSE
    const contentType = response.headers.get("content-type");
    if (!contentType?.includes("text/event-stream")) {
      const errorText = await response.text();
      console.error(
        `FastAPI backend returned non-SSE response: ${contentType}`
      );

      return new Response(
        JSON.stringify({
          error: "Backend did not return SSE stream",
          contentType,
          details: errorText,
        }),
        {
          status: 502,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Stream SSE events from backend to client
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          controller.close();
          return;
        }

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              controller.close();
              break;
            }

            // Forward the SSE data chunk to the client
            const chunk = decoder.decode(value, { stream: true });
            controller.enqueue(new TextEncoder().encode(chunk));
          }
        } catch (error) {
          console.error("Error streaming SSE events:", error);

          // Send error event to client
          const errorEvent = `event: error\ndata: ${JSON.stringify({
            error: "Stream interrupted",
            message: error instanceof Error ? error.message : "Unknown error",
          })}\n\n`;

          controller.enqueue(new TextEncoder().encode(errorEvent));
          controller.close();
        } finally {
          reader.releaseLock();
        }
      },
    });

    // Return SSE stream response
    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no", // Disable Nginx buffering
      },
    });
  } catch (error) {
    console.error("Error connecting to FastAPI backend:", error);

    return new Response(
      JSON.stringify({
        error: "Failed to connect to research backend",
        message: error instanceof Error ? error.message : "Unknown error",
        backend: backendUrl,
      }),
      {
        status: 502,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
