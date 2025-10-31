"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ResearchButton } from "@/components/research-button";
import { ResearchProgress } from "@/components/research-progress";
import type {
  ResearchEvent,
  ResearchStatus,
} from "@/hooks/use-research-progress";

export interface ResearchPanelProps {
  prompt: string; // Research query
  isActive: boolean; // Whether research is active (started)
  events: ResearchEvent[]; // Research events
  status: ResearchStatus; // Research status
  error?: Error | null; // Error if any
  onStart: (prompt: string) => void; // Start research callback
  onCancel?: () => void; // Cancel research callback
  onRetry?: () => void; // Retry research callback
}

/**
 * ResearchPanel Component
 *
 * Container for Research UI that switches between ResearchButton and ResearchProgress.
 * Uses sticky positioning to stay above the chat input (bottom-[72px]).
 *
 * State transitions:
 * - Initial: Shows ResearchButton when AI suggests research
 * - Active: Shows ResearchProgress when user clicks "Start Research"
 * - Completed: Hides panel after research completes and report is sent
 *
 * @example
 * ```tsx
 * <ResearchPanel
 *   prompt="quantum computing"
 *   isActive={isResearching}
 *   events={researchEvents}
 *   status={researchStatus}
 *   onStart={(prompt) => setResearchPrompt(prompt)}
 *   onCancel={() => cancelResearch()}
 * />
 * ```
 */
export function ResearchPanel({
  prompt,
  isActive,
  events,
  status,
  error,
  onStart,
  onCancel,
  onRetry,
}: ResearchPanelProps) {
  // Don't show panel if status is idle and not active
  const shouldShow = isActive || status !== "idle";

  return (
    <AnimatePresence>
      {shouldShow && (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="sticky bottom-[72px] z-10 mx-4 mb-4"
          data-testid="research-panel"
          exit={{ opacity: 0, y: 20 }}
          initial={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        >
          <div className="max-h-[400px] overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-800 dark:bg-gray-900">
            {/* Show ResearchButton when not active */}
            {!isActive && status === "idle" && (
              <ResearchButton
                disabled={false}
                onStart={onStart}
                prompt={prompt}
              />
            )}

            {/* Show ResearchProgress when active */}
            {isActive && (
              <ResearchProgress
                error={error}
                events={events}
                onCancel={onCancel}
                onRetry={onRetry}
                status={status}
              />
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
