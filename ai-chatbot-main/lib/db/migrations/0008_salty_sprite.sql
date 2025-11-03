CREATE TABLE IF NOT EXISTS "research_tasks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"task_id" varchar(255) NOT NULL,
	"user_id" uuid NOT NULL,
	"chat_id" uuid NOT NULL,
	"topic" text NOT NULL,
	"status" varchar(50) DEFAULT 'pending' NOT NULL,
	"progress" jsonb,
	"report" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	CONSTRAINT "research_tasks_task_id_unique" UNIQUE("task_id")
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "research_tasks" ADD CONSTRAINT "research_tasks_user_id_User_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."User"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "research_tasks" ADD CONSTRAINT "research_tasks_chat_id_Chat_id_fk" FOREIGN KEY ("chat_id") REFERENCES "public"."Chat"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
