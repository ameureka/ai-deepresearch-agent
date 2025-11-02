import { NextRequest } from "next/server";
import { auth } from "@/app/(auth)/auth";
import { getResearchTaskRecord } from "@/lib/db/queries";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ taskId: string }> }
) {
  const session = await auth();

  if (!session?.user) {
    return new Response(
      JSON.stringify({
        error: "Unauthorized: Please sign in to view research tasks",
      }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  const { taskId } = await context.params;

  if (!taskId) {
    return new Response(
      JSON.stringify({ error: "Task id is required" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const record = await getResearchTaskRecord({
    taskId,
    userId: session.user.id,
  });

  if (!record) {
    return new Response(
      JSON.stringify({ error: "Research task not found" }),
      { status: 404, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({
      taskId: record.taskId,
      status: record.status,
      topic: record.topic,
      progress: record.progress,
      report: record.report,
      userId: record.userId,
      chatId: record.chatId,
      queueInfo: record.queueInfo ?? null,
      startedAt: record.startedAt ?? null,
      completedAt: record.completedAt ?? null,
      failedAt: record.failedAt ?? null,
      createdAt: record.createdAt,
      updatedAt: record.updatedAt,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
