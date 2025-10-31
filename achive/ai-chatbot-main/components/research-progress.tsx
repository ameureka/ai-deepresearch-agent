"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertCircle,
  CheckCircle2,
  Circle,
  Loader2,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type {
  ResearchEvent,
  ResearchStatus,
} from "@/hooks/use-research-progress";

export interface ResearchProgressProps {
  events: ResearchEvent[];
  status: ResearchStatus;
  error?: Error | null;
  onCancel?: () => void;
  onRetry?: () => void;
}

/**
 * Get status icon based on research status
 */
function StatusIcon({ status }: { status: ResearchStatus }) {
  switch (status) {
    case "connecting":
    case "streaming":
      return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
    case "done":
      return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    case "error":
      return <XCircle className="h-5 w-5 text-red-500" />;
    default:
      return <Circle className="h-5 w-5 text-gray-400" />;
  }
}

/**
 * Get status text based on research status
 */
function getStatusText(status: ResearchStatus): string {
  switch (status) {
    case "connecting":
      return "Connecting to research backend...";
    case "streaming":
      return "Research in progress...";
    case "done":
      return "Research completed successfully";
    case "error":
      return "Research failed";
    default:
      return "Ready";
  }
}

/**
 * ResearchProgress Component
 *
 * Displays real-time research progress with events and status.
 * Shows different UI based on event types: start, plan, progress, done, error.
 */
export function ResearchProgress({
  events,
  status,
  error,
  onCancel,
  onRetry,
}: ResearchProgressProps) {
  // Calculate progress percentage based on events
  const progressPercentage = (() => {
    if (status === "done") return 100;
    if (status === "error") return 0;
    if (status === "idle") return 0;

    // Estimate progress based on event types
    const hasStart = events.some((e) => e.type === "start");
    const hasPlan = events.some((e) => e.type === "plan");
    const progressCount = events.filter((e) => e.type === "progress").length;

    let progress = 0;
    if (hasStart) progress += 10;
    if (hasPlan) progress += 20;
    progress += Math.min(progressCount * 10, 70);

    return Math.min(progress, 95); // Cap at 95% until done
  })();

  return (
    <div className="space-y-4 p-4" data-testid="research-progress">
      {/* Header with Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusIcon status={status} />
          <div>
            <p className="font-medium text-foreground text-sm">
              {getStatusText(status)}
            </p>
            {status === "streaming" && (
              <p className="mt-0.5 text-muted-foreground text-xs">
                {events.length} events received
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {status === "streaming" && onCancel && (
            <Button
              className="text-xs"
              onClick={onCancel}
              size="sm"
              variant="ghost"
            >
              Cancel
            </Button>
          )}
          {status === "error" && onRetry && (
            <Button
              className="text-xs"
              onClick={onRetry}
              size="sm"
              variant="outline"
            >
              Retry
            </Button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {(status === "connecting" || status === "streaming") && (
        <div className="space-y-2">
          <Progress className="h-2" value={progressPercentage} />
          <p className="text-right text-muted-foreground text-xs">
            {progressPercentage}%
          </p>
        </div>
      )}

      {/* Error Display */}
      {status === "error" && error && (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-950/20"
          initial={{ opacity: 0, y: -10 }}
        >
          <div className="flex items-start gap-2">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
            <div className="min-w-0 flex-1">
              <p className="font-medium text-red-900 text-sm dark:text-red-100">
                Error
              </p>
              <p className="mt-1 text-red-700 text-xs dark:text-red-300">
                {error.message}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Events Timeline */}
      {events.length > 0 && (
        <div className="max-h-[300px] space-y-2 overflow-y-auto">
          <AnimatePresence>
            {events.map((event, index) => (
              <EventItem event={event} index={index} key={index} />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}

/**
 * Individual Event Item
 */
function EventItem({ event, index }: { event: ResearchEvent; index: number }) {
  const getEventIcon = () => {
    switch (event.type) {
      case "start":
        return <Circle className="h-4 w-4 text-blue-500" />;
      case "plan":
        return <Circle className="h-4 w-4 text-purple-500" />;
      case "progress":
        return <Loader2 className="h-4 w-4 text-blue-500" />;
      case "done":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Circle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getEventLabel = () => {
    switch (event.type) {
      case "start":
        return "Research Started";
      case "plan":
        return "Research Plan";
      case "progress":
        return event.data.status || "Progress Update";
      case "done":
        return "Research Completed";
      case "error":
        return "Error Occurred";
      default:
        return "Event";
    }
  };

  const getEventDescription = () => {
    if (typeof event.data === "string") {
      return event.data;
    }

    if (event.data.message) {
      return event.data.message;
    }

    if (event.data.url) {
      return `Searching: ${event.data.url}`;
    }

    if (event.data.report) {
      return "Research report generated";
    }

    return null;
  };

  return (
    <motion.div
      animate={{ opacity: 1, x: 0 }}
      className="flex items-start gap-3 rounded-md p-2 transition-colors hover:bg-accent/50"
      exit={{ opacity: 0, x: 20 }}
      initial={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
    >
      <div className="mt-0.5 shrink-0">{getEventIcon()}</div>
      <div className="min-w-0 flex-1">
        <p className="font-medium text-foreground text-sm">{getEventLabel()}</p>
        {getEventDescription() && (
          <p className="mt-0.5 line-clamp-2 text-muted-foreground text-xs">
            {getEventDescription()}
          </p>
        )}
        {event.timestamp && (
          <p className="mt-1 text-muted-foreground text-xs">
            {new Date(event.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </motion.div>
  );
}
