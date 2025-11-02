import { neon } from "@neondatabase/serverless";

export interface ResearchTaskProgress {
  currentStep?: string | null;
  totalSteps?: number | null;
  completedSteps?: number | null;
  events?: Array<{
    type: string;
    message: string;
    timestamp: string;
  }>;
}

export interface ResearchTaskRecord {
  id: string;
  task_id: string;
  user_id: string;
  chat_id: string;
  topic: string;
  status: string;
  progress: ResearchTaskProgress | null;
  report: string | null;
  created_at: string;
  updated_at: string;
}

function resolveConnectionString(): string {
  const connectionString =
    process.env.POSTGRES_URL ??
    process.env.POSTGRES_PRISMA_URL ??
    process.env.DATABASE_URL;

  if (!connectionString) {
    throw new Error(
      "Missing Neon connection string. Set POSTGRES_URL or DATABASE_URL before running DB helpers."
    );
  }

  return connectionString;
}

function createClient() {
  const sql = neon(resolveConnectionString());
  return sql;
}

export async function getResearchTask(
  taskId: string
): Promise<ResearchTaskRecord | null> {
  const sql = createClient();
  const rows =
    await sql<ResearchTaskRecord[]>`SELECT * FROM research_tasks WHERE task_id = ${taskId} LIMIT 1`;
  return rows[0] ?? null;
}

export async function getUserResearchTasks(
  userId: string
): Promise<ResearchTaskRecord[]> {
  const sql = createClient();
  return sql<ResearchTaskRecord[]>`SELECT * FROM research_tasks WHERE user_id = ${userId} ORDER BY created_at DESC`;
}

export async function verifyTaskProgress(
  taskId: string,
  expectedStatus: string
): Promise<boolean> {
  const record = await getResearchTask(taskId);
  return record?.status === expectedStatus;
}

export async function verifyProgressEvents(taskId: string): Promise<boolean> {
  const record = await getResearchTask(taskId);
  if (!record || !record.progress) return false;

  const events = record.progress.events ?? [];
  return Array.isArray(events) && events.length > 0;
}

export async function cleanupTestData(userId: string): Promise<void> {
  const sql = createClient();
  await sql`DELETE FROM research_tasks WHERE user_id = ${userId}`;
}
