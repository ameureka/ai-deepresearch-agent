import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "node:crypto";
import { auth } from "@/app/(auth)/auth";
import { ChatSDKError } from "@/lib/errors";
import {
  createResearchTaskRecord,
  getChatById,
  listResearchTasksByUserId,
  saveChat,
  updateResearchTaskRecord,
  type ResearchTaskProgressSummary,
} from "@/lib/db/queries";
import type { ResearchTaskQueueInfo } from "@/lib/db/queries";

interface CreateResearchTaskBody {
  prompt?: string;
  chatId?: string;
  model?: string | null;
  visibility?: string | null;
}

type VisibilityType = "private" | "public";

const DEFAULT_VISIBILITY: VisibilityType = "private";
const MAX_CHAT_TITLE_LENGTH = 80;

function isVisibilityType(value: unknown): value is VisibilityType {
  return value === "private" || value === "public";
}

function buildChatTitleFromPrompt(prompt: string): string {
  const cleaned = prompt.replace(/\s+/g, " ").trim();
  if (!cleaned) {
    return "Research session";
  }
  if (cleaned.length <= MAX_CHAT_TITLE_LENGTH) {
    return cleaned;
  }
  return `${cleaned.slice(0, MAX_CHAT_TITLE_LENGTH - 3)}...`;
}

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

  let prompt: string | undefined;
  let chatId: string | undefined;
  let model: string | null | undefined;
  let visibility: VisibilityType = DEFAULT_VISIBILITY;

  try {
    const body = (await request.json()) as CreateResearchTaskBody;
    prompt = body.prompt?.trim();
    chatId = body.chatId?.trim();
    model = body.model ?? null;
    if (isVisibilityType(body.visibility)) {
      visibility = body.visibility;
    }
  } catch {
    return new Response(
      JSON.stringify({ error: "Malformed request body" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  if (!prompt || prompt.length === 0) {
    return new Response(
      JSON.stringify({ error: "Invalid prompt" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  if (!chatId || chatId.length === 0) {
    return new Response(
      JSON.stringify({ error: "Invalid chatId" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const taskId = randomUUID();
  const userId = session.user.id;

  try {
    const existingChat = await getChatById({ id: chatId });

    if (existingChat) {
      if (existingChat.userId !== userId) {
        return new Response(
          JSON.stringify({
            error: "Forbidden",
            message: "You do not have access to this chat",
          }),
          { status: 403, headers: { "Content-Type": "application/json" } }
        );
      }
    } else {
      await saveChat({
        id: chatId,
        userId,
        title: buildChatTitleFromPrompt(prompt),
        visibility,
      });
    }
  } catch (error) {
    const message =
      error instanceof ChatSDKError
        ? error.message
        : "Failed to ensure chat exists";

    return new Response(
      JSON.stringify({ error: message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    await createResearchTaskRecord({
      taskId,
      userId,
      chatId,
      topic: prompt,
    });
  } catch (error) {
    const message =
      error instanceof ChatSDKError ? error.message : "Failed to create record";
    return new Response(
      JSON.stringify({ error: message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  const researchApiUrl =
    process.env.RESEARCH_API_URL || "http://localhost:8000";
  const backendUrl = `${researchApiUrl}/api/research/tasks`;

  try {
    const backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        taskId,
        prompt,
        model,
      }),
    });

    if (!backendResponse.ok) {
      const errorPayload = await backendResponse.json().catch(() => ({}));
      const detail =
        typeof errorPayload.error === "string"
          ? errorPayload.error
          : backendResponse.statusText;
      throw new Error(detail);
    }
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    const timestamp = new Date().toISOString();
    const failureProgress: ResearchTaskProgressSummary = {
      currentStep: undefined,
      totalSteps: 0,
      completedSteps: 0,
      events: [
        {
          type: "error",
          message: `Failed to queue research task: ${errorMessage}`,
          timestamp,
        },
      ],
    };

    const queueInfoUpdate: ResearchTaskQueueInfo = {
      enqueuedAt: timestamp,
      failedAt: timestamp,
      retryCount: 0,
    };

    await updateResearchTaskRecord({
      taskId,
      status: "failed",
      progress: failureProgress,
      report: null,
      queueInfo: queueInfoUpdate,
      failedAt: new Date(timestamp),
    });

    return new Response(
      JSON.stringify({
        error: "Failed to queue research task",
        message: errorMessage,
      }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({
      taskId,
      status: "queued",
    }),
    {
      status: 202,
      headers: { "Content-Type": "application/json" },
    }
  );
}

export async function GET(request: NextRequest) {
  const session = await auth();

  if (!session?.user) {
    return new Response(
      JSON.stringify({
        error: "Unauthorized: Please sign in to view research history",
      }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  const { searchParams } = new URL(request.url);
  const limitParam = searchParams.get("limit");
  const limitCandidate = limitParam ? Number.parseInt(limitParam, 10) : 10;
  const limit = Number.isFinite(limitCandidate) ? limitCandidate : 10;

  const records = await listResearchTasksByUserId({
    userId: session.user.id,
    limit,
  });

  const tasks = records.map((record) => ({
    taskId: record.taskId,
    topic: record.topic,
    status: record.status,
    queuedAt:
      (record.queueInfo && typeof record.queueInfo.enqueuedAt === "string"
        ? record.queueInfo.enqueuedAt
        : null) ?? null,
    startedAt: record.startedAt ? record.startedAt.toISOString() : null,
    completedAt: record.completedAt ? record.completedAt.toISOString() : null,
    failedAt: record.failedAt ? record.failedAt.toISOString() : null,
    updatedAt: record.updatedAt ? record.updatedAt.toISOString() : null,
    reportAvailable: Boolean(record.report && record.report.trim().length > 0),
  }));

  return NextResponse.json({
    tasks,
  });
}
