/**
 * Research Stream API Route
 *
 * Acts as a proxy between the Next.js app and the FastAPI backend while
 * persisting research task progress to the database for telemetry and
 * verification during Phase 4.5.
 */

import { NextRequest } from "next/server";
import { randomUUID } from "node:crypto";
import { auth } from "@/app/(auth)/auth";
import { Agent, type Dispatcher } from "undici";
import { ChatSDKError } from "@/lib/errors";
import {
  createResearchTaskRecord,
  getResearchTaskRecord,
  updateResearchTaskRecord,
  type ResearchTaskProgressEvent,
  type ResearchTaskProgressSummary,
  type ResearchTaskStatus,
} from "@/lib/db/queries";

export const runtime = "nodejs";
export const maxDuration = 300; // 5 minutes for long research tasks

const summarizeEvent = (eventType: string, data: unknown): string => {
  if (typeof data === "string") {
    return data.length > 180 ? `${data.slice(0, 177)}...` : data;
  }

  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;

    if (typeof record.message === "string") {
      return record.message;
    }

    if (typeof record.title === "string") {
      return record.title;
    }

    if (eventType === "plan" && Array.isArray(record.steps)) {
      return `Plan generated with ${record.steps.length} steps`;
    }

    if (
      eventType === "progress" &&
      typeof record.step === "number" &&
      typeof record.total === "number"
    ) {
      return `Progress ${record.step}/${record.total}`;
    }

    if (eventType === "done" && typeof record.report === "string") {
      return record.report.slice(0, 140);
    }
  }

  try {
    return JSON.stringify(data);
  } catch {
    return String(data);
  }
};

const deriveStatus = (
  previousStatus: ResearchTaskStatus,
  eventType: string
): ResearchTaskStatus => {
  switch (eventType) {
    case "start":
    case "plan":
      return "running";
    case "progress":
      return "running";
    case "done":
      return "completed";
    case "error":
      return "failed";
    default:
      return previousStatus;
  }
};

const parseSseBlock = (
  block: string
): { event: string; data: string } | null => {
  let eventType: string | null = null;
  const dataLines: string[] = [];

  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) {
      eventType = line.slice("event:".length).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trim());
    }
  }

  if (!eventType) {
    return null;
  }

  return {
    event: eventType,
    data: dataLines.join("\n"),
  };
};

export async function POST(request: NextRequest) {
  const session = await auth();

  if (!session?.user) {
    return new Response(
      JSON.stringify({
        error: "Unauthorized: Please sign in to use research features",
      }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  const userId = session.user.id;

  let prompt: string;
  let chatId: string;
  let requestedTaskId: string | null = null;
  let existingTask:
    | Awaited<ReturnType<typeof getResearchTaskRecord>>
    | null = null;

  let body: Record<string, unknown>;

  try {
    body = (await request.json()) as Record<string, unknown>;
  } catch (error) {
    const detail =
      error instanceof ChatSDKError ? error.message : "Malformed request body";
    return new Response(JSON.stringify({ error: detail }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (typeof body.taskId === "string" && body.taskId.trim().length > 0) {
    requestedTaskId = body.taskId.trim();
  }

  if (requestedTaskId) {
    existingTask = await getResearchTaskRecord({
      taskId: requestedTaskId,
      userId,
    });

    if (!existingTask) {
      return new Response(
        JSON.stringify({ error: "Research task not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    prompt = existingTask.topic;
    chatId = existingTask.chatId;
  } else {
    const incomingPrompt = body.prompt;
    const incomingChatId = body.chatId;

    if (
      !incomingPrompt ||
      typeof incomingPrompt !== "string" ||
      incomingPrompt.trim().length === 0
    ) {
      return new Response(
        JSON.stringify({ error: "Invalid prompt" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    if (
      !incomingChatId ||
      typeof incomingChatId !== "string" ||
      incomingChatId.trim().length === 0
    ) {
      return new Response(
        JSON.stringify({ error: "Invalid chatId" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    prompt = incomingPrompt.trim();
    chatId = incomingChatId.trim();
  }

  const researchApiUrl =
    process.env.RESEARCH_API_URL || "http://localhost:8000";
  const backendUrl = `${researchApiUrl}/api/research/stream`;

  const taskId = requestedTaskId ?? randomUUID();

  if (!existingTask) {
    try {
      await createResearchTaskRecord({
        taskId,
        userId,
        chatId,
        topic: prompt,
      });
    } catch (error) {
      console.error("Failed to create research task", error);
      return new Response(
        JSON.stringify({ error: "Failed to initialize research task" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  }

  const existingProgress =
    (existingTask?.progress as ResearchTaskProgressSummary | null) ?? null;

  if (
    existingTask &&
    (existingTask.status === "completed" || existingTask.status === "failed")
  ) {
    return new Response(
      JSON.stringify({
        taskId: existingTask.taskId,
        status: existingTask.status,
        topic: existingTask.topic,
        progress: existingProgress ?? { events: [] },
        report: existingTask.report ?? null,
        createdAt: existingTask.createdAt,
        updatedAt: existingTask.updatedAt,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  let latestStatus: ResearchTaskStatus =
    existingTask?.status ?? "queued";
  let totalSteps: number | undefined = existingProgress?.totalSteps;
  let completedSteps = existingProgress?.completedSteps ?? 0;
  let currentStep: string | undefined = existingProgress?.currentStep;
  const persistedEvents: ResearchTaskProgressEvent[] = existingProgress?.events
    ? [...existingProgress.events]
    : [];
  let finalReport: string | null = existingTask?.report ?? null;

  const buildProgressSummary = (): ResearchTaskProgressSummary => ({
    currentStep,
    totalSteps,
    completedSteps,
    events: [...persistedEvents],
  });

  const persistUpdate = (
    payload: Parameters<typeof updateResearchTaskRecord>[0]
  ) => {
    updateResearchTaskRecord(payload).catch(error => {
      console.error("Failed to persist research task update", {
        error,
        taskId: payload.taskId,
        status: payload.status,
      });
    });
  };

  try {
    const dispatcher = new Agent({
      headersTimeout: 180_000, // 3 minutes to accommodate long planner/writer phases
      bodyTimeout: 0,
    });
    type NodeFetchInit = RequestInit & { dispatcher?: Dispatcher };

    const maxConnectionAttempts = 3;
    let upstream: Response | null = null;
    let lastConnectionError: unknown = null;

    for (let attempt = 0; attempt < maxConnectionAttempts; attempt++) {
      try {
        const fetchOptions: NodeFetchInit = {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify({ prompt: prompt.trim() }),
          dispatcher,
        };

        upstream = await fetch(backendUrl, fetchOptions);
        break;
      } catch (error) {
        lastConnectionError = error;
        const message =
          error instanceof Error ? error.message : "Unknown error";
        const timestamp = new Date().toISOString();
        persistedEvents.push({
          type: "connection_error",
          message: `Connection attempt ${attempt + 1} failed: ${message}`,
          timestamp,
        });
        persistUpdate({
          taskId,
          status: latestStatus,
          progress: buildProgressSummary(),
          report: finalReport,
        });

        if (attempt < maxConnectionAttempts - 1) {
          const delay = 500 * Math.pow(2, attempt);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    if (!upstream) {
      console.error("Error connecting to FastAPI backend:", lastConnectionError);

      return new Response(
        JSON.stringify({
          error: "Failed to connect to research backend",
          message:
            lastConnectionError instanceof Error
              ? lastConnectionError.message
              : "Unknown error",
          backend: backendUrl,
          taskId,
        }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    }

    if (!upstream.ok) {
      const errorText = await upstream.text();
      console.error(
        `FastAPI backend error (${upstream.status}): ${errorText}`
      );
      const timestamp = new Date().toISOString();
      persistedEvents.push({
        type: "error",
        message: `Backend error: ${upstream.statusText}`,
        timestamp,
      });
      persistUpdate({
        taskId,
        status: "failed",
        progress: buildProgressSummary(),
        report: null,
      });

      return new Response(
        JSON.stringify({
          error: `Backend error: ${upstream.statusText}`,
          details: errorText,
          taskId,
        }),
        { status: upstream.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const contentType = upstream.headers.get("content-type");
    if (!contentType?.includes("text/event-stream")) {
      const errorText = await upstream.text();
      console.error(
        `FastAPI backend returned non-SSE response: ${contentType}`
      );
      const timestamp = new Date().toISOString();
      persistedEvents.push({
        type: "error",
        message: "Backend did not return SSE stream",
        timestamp,
      });
      persistUpdate({
        taskId,
        status: "failed",
        progress: buildProgressSummary(),
        report: null,
      });

      return new Response(
        JSON.stringify({
          error: "Backend did not return SSE stream",
          contentType,
          details: errorText,
          taskId,
        }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    }

    const stream = new ReadableStream({
      async cancel() {
        const timestamp = new Date().toISOString();
        persistedEvents.push({
          type: "cancelled",
          message: "Stream cancelled by client",
          timestamp,
        });
        currentStep = undefined;
        latestStatus = "failed";
        persistUpdate({
          taskId,
          status: "failed",
          progress: buildProgressSummary(),
          report: finalReport,
        });
      },
      async start(controller) {
        const reader = upstream.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        const decoder = new TextDecoder();
        const encoder = new TextEncoder();
        let buffer = "";

        const persistEvent = (
          eventType: string,
          data: unknown,
          report?: string | null
        ) => {
          const timestamp = new Date().toISOString();
          const message = summarizeEvent(eventType, data);

          persistedEvents.push({ type: eventType, message, timestamp });

          if (
            eventType === "plan" &&
            data &&
            typeof data === "object"
          ) {
            const planSteps = (data as { steps?: unknown }).steps;
            if (Array.isArray(planSteps)) {
              totalSteps = planSteps.length;
            }
          }

          if (eventType === "progress" && data && typeof data === "object") {
            const record = data as Record<string, unknown>;
            if (typeof record.step === "number") {
              completedSteps = Math.max(completedSteps, record.step);
            } else {
              completedSteps += 1;
            }
            if (typeof record.total === "number") {
              totalSteps = record.total;
            }

            if (typeof record.message === "string") {
              currentStep = record.message;
            } else if (typeof record.title === "string") {
              currentStep = record.title;
            }
          }

          if (eventType === "error") {
            currentStep = undefined;
          }
          if (eventType === "done") {
            currentStep = undefined;
          }

          if (typeof report === "string") {
            finalReport = report;
          } else if (report === null) {
            finalReport = null;
          }

          const nextStatus = deriveStatus(latestStatus, eventType);
          const reportToPersist =
            typeof report === "undefined" ? finalReport : report;

          persistUpdate({
            taskId,
            status: nextStatus,
            progress: buildProgressSummary(),
            report: reportToPersist,
          });
          latestStatus = nextStatus;
        };

        const flushFailure = (message: string) => {
          const timestamp = new Date().toISOString();
          persistedEvents.push({ type: "error", message, timestamp });
          currentStep = undefined;
          persistUpdate({
            taskId,
            status: "failed",
            progress: buildProgressSummary(),
            report: finalReport,
          });
          latestStatus = "failed";
        };

        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              if (latestStatus !== "completed" && latestStatus !== "failed") {
                persistUpdate({
                  taskId,
                  status: latestStatus,
                  progress: buildProgressSummary(),
                  report: finalReport,
                });
              }
              controller.close();
              break;
            }

            buffer += decoder.decode(value, { stream: true });

            let delimiterIndex = buffer.indexOf("\n\n");
            while (delimiterIndex !== -1) {
              const rawBlock = buffer.slice(0, delimiterIndex);
              buffer = buffer.slice(delimiterIndex + 2);

              if (rawBlock.trim().length === 0) {
                delimiterIndex = buffer.indexOf("\n\n");
                continue;
              }

              const parsed = parseSseBlock(rawBlock);
              if (!parsed) {
                controller.enqueue(encoder.encode(`${rawBlock}\n\n`));
                delimiterIndex = buffer.indexOf("\n\n");
                continue;
              }

              let parsedData: unknown = parsed.data;
              let isJson = false;

              if (parsed.data) {
                try {
                  parsedData = JSON.parse(parsed.data);
                  isJson = true;
                } catch {
                  parsedData = parsed.data;
                }
              }

              if (parsedData && typeof parsedData === "object") {
                parsedData = {
                  ...(parsedData as Record<string, unknown>),
                  taskId,
                  chatId,
                  userId,
                };
              }

              const reportForEvent =
                parsed.event === "done" &&
                parsedData &&
                typeof parsedData === "object"
                  ? (parsedData as Record<string, unknown>).report
                  : undefined;

              persistEvent(
                parsed.event,
                parsedData,
                typeof reportForEvent === "string"
                  ? reportForEvent
                  : undefined
              );

              const payload =
                parsedData && typeof parsedData === "object"
                  ? JSON.stringify(parsedData)
                  : isJson
                  ? parsed.data
                  : String(parsedData ?? "");

              controller.enqueue(
                encoder.encode(`event: ${parsed.event}\ndata: ${payload}\n\n`)
              );

              delimiterIndex = buffer.indexOf("\n\n");
            }
          }
        } catch (error) {
          console.error("Error streaming SSE events:", error);
          const message =
            error instanceof Error ? error.message : "Unknown error";
          flushFailure(message);

          controller.enqueue(
            encoder.encode(
              `event: error\ndata: ${JSON.stringify({
                error: "Stream interrupted",
                message,
                taskId,
                chatId,
                userId,
              })}\n\n`
            )
          );
          controller.close();
        } finally {
          reader.releaseLock();
        }
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    console.error("Error connecting to FastAPI backend:", error);
    const timestamp = new Date().toISOString();
    persistedEvents.push({
      type: "error",
      message:
        error instanceof Error
          ? error.message
          : "Failed to connect to research backend",
      timestamp,
    });
    currentStep = undefined;
    latestStatus = "failed";
    persistUpdate({
      taskId,
      status: "failed",
      progress: buildProgressSummary(),
      report: finalReport,
    });

    return new Response(
      JSON.stringify({
        error: "Failed to connect to research backend",
        message: error instanceof Error ? error.message : "Unknown error",
        backend: backendUrl,
        taskId,
      }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }
}
