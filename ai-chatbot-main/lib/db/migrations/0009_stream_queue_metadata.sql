ALTER TABLE "research_tasks"
ALTER COLUMN "status" SET DEFAULT 'queued';
--> statement-breakpoint
UPDATE "research_tasks"
SET "status" = 'queued'
WHERE "status" IN ('pending');
--> statement-breakpoint
UPDATE "research_tasks"
SET "status" = 'running'
WHERE "status" IN ('planning', 'researching', 'writing', 'streaming');
--> statement-breakpoint
ALTER TABLE "research_tasks"
ADD COLUMN IF NOT EXISTS "queue_info" jsonb;
--> statement-breakpoint
ALTER TABLE "research_tasks"
ADD COLUMN IF NOT EXISTS "started_at" timestamp;
--> statement-breakpoint
ALTER TABLE "research_tasks"
ADD COLUMN IF NOT EXISTS "completed_at" timestamp;
--> statement-breakpoint
ALTER TABLE "research_tasks"
ADD COLUMN IF NOT EXISTS "failed_at" timestamp;
