"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  AlertCircle,
  CheckCircle2,
  Circle,
  Copy,
  Download,
  Eye,
  Loader2,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useCallback, useEffect, useMemo, useState } from "react";
import type {
  ResearchEvent,
  ResearchStatus,
  ResearchQueueInfo,
} from "@/hooks/use-research-progress";

export interface ResearchProgressProps {
  events: ResearchEvent[];
  status: ResearchStatus;
  error?: Error | null;
  onCancel?: () => void;
  onRetry?: () => void;
  taskId?: string;
  isAutoRetrying?: boolean;
  report?: string | null;
  queueInfo?: ResearchQueueInfo | null;
  onViewReport?: () => void;
  onCopyReport?: () => void | Promise<void>;
  onExportReport?: () => void;
}

/**
 * Get status icon based on research status
 */
function StatusIcon({ status }: { status: ResearchStatus }) {
  switch (status) {
    case "queued":
      return <Loader2 className="h-5 w-5 animate-spin text-amber-500" />;
    case "running":
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
    case "queued":
      return "Queued and waiting for execution...";
    case "running":
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
  taskId,
  isAutoRetrying = false,
  report,
  queueInfo = null,
  onViewReport,
  onCopyReport,
  onExportReport,
}: ResearchProgressProps) {
  const [queueElapsed, setQueueElapsed] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<"idle" | "success" | "error">(
    "idle"
  );
  const [exportStatus, setExportStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [isCopying, setIsCopying] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const trimmedReport = useMemo(() => (report ?? "").trim(), [report]);
  const hasReport = trimmedReport.length > 0;

  useEffect(() => {
    if (!queueInfo?.enqueuedAt) {
      setQueueElapsed(null);
      return;
    }

    const enqueuedTime = new Date(queueInfo.enqueuedAt).getTime();
    const formatElapsed = (end: number) => {
      const diff = Math.max(0, end - enqueuedTime);
      if (diff <= 0) {
        return "0s";
      }
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
      }
      if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
      }
      return `${seconds}s`;
    };

    const resolveEndTimestamp = () => {
      const startedAt = queueInfo.startedAt
        ? new Date(queueInfo.startedAt).getTime()
        : undefined;
      const finishedAt = queueInfo.finishedAt
        ? new Date(queueInfo.finishedAt).getTime()
        : undefined;
      const failedAt = queueInfo.failedAt
        ? new Date(queueInfo.failedAt).getTime()
        : undefined;

      if (status === "queued") {
        return Date.now();
      }

      if (typeof startedAt === "number") {
        return startedAt;
      }
      if (typeof finishedAt === "number") {
        return finishedAt;
      }
      if (typeof failedAt === "number") {
        return failedAt;
      }

      const fallbackEvent = events.find(
        (event) =>
          (event.type === "start" || event.type === "progress") &&
          typeof event.timestamp === "number"
      );
      if (fallbackEvent?.timestamp) {
        return fallbackEvent.timestamp;
      }
      return Date.now();
    };

    if (status === "queued") {
      const updateElapsed = () => {
        setQueueElapsed(formatElapsed(Date.now()));
      };
      updateElapsed();
      const timer = window.setInterval(updateElapsed, 1000);
      return () => window.clearInterval(timer);
    }

    const resolvedEnd = resolveEndTimestamp();
    setQueueElapsed(formatElapsed(resolvedEnd));
  }, [
    events,
    queueInfo?.enqueuedAt,
    queueInfo?.failedAt,
    queueInfo?.finishedAt,
    queueInfo?.startedAt,
    status,
  ]);

  useEffect(() => {
    if (copyStatus === "idle") {
      return;
    }
    const timer = window.setTimeout(() => setCopyStatus("idle"), 2000);
    return () => window.clearInterval(timer);
  }, [copyStatus]);

  useEffect(() => {
    if (exportStatus === "idle") {
      return;
    }
    const timer = window.setTimeout(() => setExportStatus("idle"), 2000);
    return () => window.clearInterval(timer);
  }, [exportStatus]);

  const handleViewReport = useCallback(() => {
    if (!hasReport || !onViewReport) {
      return;
    }
    onViewReport();
  }, [hasReport, onViewReport]);

  const handleCopyReport = useCallback(async () => {
    if (!hasReport) {
      setCopyStatus("error");
      return;
    }
    setIsCopying(true);
    try {
      if (onCopyReport) {
        await Promise.resolve(onCopyReport());
      } else if (
        typeof navigator !== "undefined" &&
        navigator.clipboard?.writeText
      ) {
        await navigator.clipboard.writeText(trimmedReport);
      } else {
        throw new Error("Clipboard API is unavailable");
      }
      setCopyStatus("success");
    } catch (copyError) {
      console.error("Failed to copy research report:", copyError);
      setCopyStatus("error");
    } finally {
      setIsCopying(false);
    }
  }, [hasReport, onCopyReport, trimmedReport]);

  const handleExportReport = useCallback(() => {
    if (!hasReport) {
      setExportStatus("error");
      return;
    }
    setIsExporting(true);
    try {
      if (onExportReport) {
        onExportReport();
      } else if (typeof document !== "undefined" && trimmedReport) {
        const blob = new Blob([trimmedReport], {
          type: "text/markdown;charset=utf-8",
        });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
        anchor.href = url;
        anchor.download = `research-report-${timestamp}.md`;
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
        URL.revokeObjectURL(url);
      }
      setExportStatus("success");
    } catch (exportError) {
      console.error("Failed to export research report:", exportError);
      setExportStatus("error");
    } finally {
      setIsExporting(false);
    }
  }, [hasReport, onExportReport, trimmedReport]);

  const progressMeta = useMemo(() => {
    if (events.length === 0) {
      return {
        planSteps: undefined as string[] | undefined,
        totalSteps: undefined as number | undefined,
        completedSteps: 0,
        currentStepTitle: undefined as string | undefined,
      };
    }

    const reversed = [...events].reverse();
    const latestProgressEvent = reversed.find((event) => event.type === "progress");
    const planEvent = reversed.find((event) => event.type === "plan");

    const planSteps = Array.isArray(planEvent?.data?.steps)
      ? (planEvent?.data?.steps as string[])
      : undefined;

    let totalSteps: number | undefined;
    let completedSteps = 0;
    let currentStepTitle: string | undefined;

    if (
      latestProgressEvent &&
      latestProgressEvent.data &&
      typeof latestProgressEvent.data === "object"
    ) {
      const data = latestProgressEvent.data as Record<string, unknown>;
      if (typeof data.total === "number") {
        totalSteps = data.total;
      }
      if (typeof data.step === "number") {
        completedSteps = data.step;
      }
      if (typeof data.message === "string") {
        currentStepTitle = data.message;
      } else if (typeof data.title === "string") {
        currentStepTitle = data.title;
      }
    }

    if (!totalSteps && planSteps) {
      totalSteps = planSteps.length;
    }
    if (!completedSteps) {
      completedSteps = events.filter((event) => event.type === "progress").length;
    }

    return { planSteps, totalSteps, completedSteps, currentStepTitle };
  }, [events]);

  const progressPercentage = useMemo(() => {
    if (status === "done") {
      return 100;
    }
    if (status === "error" || status === "idle") {
      return 0;
    }
    if (status === "queued") {
      return 10;
    }
    if (progressMeta.totalSteps && progressMeta.totalSteps > 0) {
      return Math.min(
        Math.round(
          (Math.min(progressMeta.completedSteps, progressMeta.totalSteps) /
            progressMeta.totalSteps) *
            100
        ),
        95
      );
    }
    if (events.length > 0) {
      return Math.min(25 + progressMeta.completedSteps * 12, 90);
    }
    return status === "running" ? 15 : 0;
  }, [events.length, progressMeta.completedSteps, progressMeta.totalSteps, status]);

  const progressSummary = useMemo(() => {
    if (status === "done") {
      return "All steps completed";
    }
    if (progressMeta.totalSteps && progressMeta.totalSteps > 0) {
      const current = Math.min(progressMeta.completedSteps, progressMeta.totalSteps);
      return `Step ${current} of ${progressMeta.totalSteps}`;
    }
    if (progressMeta.completedSteps > 0) {
      return `${progressMeta.completedSteps} steps completed`;
    }
    return undefined;
  }, [progressMeta.completedSteps, progressMeta.totalSteps, status]);

  const activeEventIndex = events.length - 1;
  const reportPreview = useMemo(() => {
    if (!report) return null;
    const trimmed = report.trim();
    if (!trimmed) return null;
    return trimmed.length > 220 ? `${trimmed.slice(0, 217)}…` : trimmed;
  }, [report]);

  const queueDetails = useMemo(() => {
    if (!queueInfo) {
      return { attemptLabel: null as string | null };
    }

    const retryCount =
      typeof queueInfo.retryCount === "number" && queueInfo.retryCount > 0
        ? queueInfo.retryCount
        : 0;
    const attemptLabel =
      retryCount > 0 ? `Retry attempt ${retryCount + 1}` : null;

    return { attemptLabel };
  }, [queueInfo]);

  const showEmptyState =
    events.length === 0 && (status === "queued" || status === "running");
  const showReportActions = status === "done" && hasReport;
  const copyLabel =
    copyStatus === "success"
      ? "Copied!"
      : copyStatus === "error"
      ? "Copy failed"
      : "Copy";
  const exportLabel =
    exportStatus === "success"
      ? "Exported!"
      : exportStatus === "error"
      ? "Export failed"
      : "Export";

  return (
    <div
      className="space-y-4 p-4"
      data-task-id={taskId ?? undefined}
      data-testid="research-progress"
      data-status={status}
    >
      {/* Header with Status */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <StatusIcon status={status} />
          <div>
            <p className="font-medium text-foreground text-sm">
              {getStatusText(status)}
            </p>
            {status === "queued" && (
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                <Badge
                  variant="outline"
                  className="border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-400/70 dark:bg-amber-400/10 dark:text-amber-200"
                >
                  Queued
                </Badge>
                <span className="leading-tight">
                  Waiting for an available research worker…
                </span>
                {queueElapsed && (
                  <span className="leading-tight">Queued for {queueElapsed}</span>
                )}
                {queueDetails.attemptLabel && (
                  <span className="leading-tight">{queueDetails.attemptLabel}</span>
                )}
              </div>
            )}
            {status === "running" && (
              <p className="mt-0.5 text-muted-foreground text-xs">
                {progressSummary ?? `${events.length} events received`}
              </p>
            )}
            {status === "done" && progressSummary && (
              <p className="mt-0.5 text-muted-foreground text-xs">{progressSummary}</p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 sm:self-end">
          {(status === "queued" || status === "running") && onCancel && (
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

      {showReportActions && (
        <div className="flex flex-wrap items-center gap-2 rounded-md border border-muted-foreground/30 bg-muted/30 p-3">
          <Button
            className="gap-2"
            onClick={handleViewReport}
            size="sm"
            variant="outline"
            disabled={!onViewReport || !hasReport}
          >
            <Eye className="h-4 w-4" />
            View full report
          </Button>
          <Button
            className="gap-2"
            onClick={handleCopyReport}
            size="sm"
            variant="ghost"
            disabled={isCopying}
          >
            <Copy className="h-4 w-4" />
            {copyLabel}
          </Button>
          <Button
            className="gap-2"
            onClick={handleExportReport}
            size="sm"
            variant="ghost"
            disabled={isExporting}
          >
            <Download className="h-4 w-4" />
            {exportLabel}
          </Button>
        </div>
      )}

      {showEmptyState && (
        <div className="rounded-md border border-dashed border-muted bg-muted/40 p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Preparing research workflow…</span>
          </div>
          <div className="mt-3 space-y-2">
            <div className="h-2 w-full animate-pulse rounded-full bg-muted-foreground/30" />
            <div className="h-2 w-2/5 animate-pulse rounded-full bg-muted-foreground/20" />
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {(status === "queued" || status === "running") && (
        <div className="space-y-2">
          <Progress className="h-2" value={progressPercentage} />
          <p className="text-right text-muted-foreground text-xs">
            {progressPercentage}%
          </p>
        </div>
      )}
      {status === "done" && (
        <div className="space-y-2">
          <Progress className="h-2" value={100} />
          <p className="text-right text-muted-foreground text-xs">100%</p>
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
              <EventItem
                event={event}
                index={index}
                isActive={index === activeEventIndex}
                key={index}
                totalSteps={progressMeta.totalSteps}
                queueElapsed={queueElapsed}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Report Preview */}
      {status === "done" && reportPreview && (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="rounded-md border border-muted bg-muted/40 p-3 text-xs text-muted-foreground"
          initial={{ opacity: 0, y: 10 }}
        >
          <p className="mb-1 font-medium text-foreground text-sm">Report summary</p>
          <p className="leading-relaxed">{reportPreview}</p>
        </motion.div>
      )}
    </div>
  );
}

/**
 * Individual Event Item
 */
function EventItem({
  event,
  index,
  isActive,
  totalSteps,
  queueElapsed,
}: {
  event: ResearchEvent;
  index: number;
  isActive: boolean;
  totalSteps?: number;
  queueElapsed?: string | null;
}) {
  const getEventIcon = () => {
    switch (event.type) {
      case "queued":
        return (
          <Circle
            className={`h-4 w-4 ${isActive ? "text-amber-600" : "text-amber-500"}`}
          />
        );
      case "start":
        return (
          <Circle
            className={`h-4 w-4 ${isActive ? "text-blue-600" : "text-blue-500"}`}
          />
        );
      case "plan":
        return (
          <Circle
            className={`h-4 w-4 ${isActive ? "text-purple-600" : "text-purple-500"}`}
          />
        );
      case "progress":
        return (
          <Loader2
            className={`h-4 w-4 animate-spin ${
              isActive ? "text-blue-600" : "text-blue-500"
            }`}
          />
        );
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
      case "queued":
        return "Queued";
      case "start":
        return "Research Started";
      case "plan":
        if (Array.isArray(event.data?.steps)) {
          return `Research Plan (${event.data.steps.length} steps)`;
        }
        return "Research Plan";
      case "progress":
        if (
          typeof event.data === "object" &&
          event.data &&
          typeof event.data.step === "number"
        ) {
          const step = event.data.step as number;
          const total =
            typeof event.data.total === "number" ? (event.data.total as number) : totalSteps;
          if (total) {
            return `Step ${Math.min(step, total)} of ${total}`;
          }
          return `Step ${step}`;
        }
        return "Progress Update";
      case "done":
        return "Research Completed";
      case "error":
        return "Error Occurred";
      default:
        return "Event";
    }
  };

  const getEventDescription = () => {
    if (event.type === "queued") {
      if (queueElapsed) {
        return `Queued for ${queueElapsed}`;
      }
      if (event.timestamp) {
        return `Queued at ${new Date(event.timestamp).toLocaleTimeString()}`;
      }
      if (typeof event.data?.message === "string") {
        return event.data.message;
      }
      return "Waiting for an available research worker";
    }

    if (typeof event.data === "string") {
      return event.data;
    }

    if (event.data?.message) {
      return event.data.message as string;
    }

    if (event.data?.url) {
      return `Searching: ${event.data.url as string}`;
    }

    if (event.data?.report) {
      return "Research report generated";
    }

    if (
      event.type === "plan" &&
      Array.isArray(event.data?.steps) &&
      event.data.steps.length > 0
    ) {
      const [first, second] = event.data.steps as string[];
      const additional = event.data.steps.length - 2;
      const summary = [first, second].filter(Boolean).join(" • ");
      return additional > 0 ? `${summary} • +${additional} more` : summary;
    }

    return null;
  };

  return (
    <motion.div
      animate={{ opacity: 1, x: 0 }}
      className={
        event.type === "queued"
          ? "flex items-center justify-between rounded-md border border-dashed border-muted-foreground/40 bg-muted/30 px-3 py-2 text-xs text-muted-foreground"
          : `flex items-start gap-3 rounded-md p-2 transition-colors ${
              isActive ? "bg-accent/80" : "hover:bg-accent/40"
            }`
      }
      exit={{ opacity: 0, x: 20 }}
      initial={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
    >
      {event.type === "queued" ? (
        <>
          <div className="flex items-center gap-2">
            <Badge
              variant="secondary"
              className="border border-dashed border-muted-foreground/30 bg-transparent text-xs"
            >
              {getEventLabel()}
            </Badge>
            <span>{getEventDescription()}</span>
          </div>
          {event.timestamp && (
            <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
          )}
        </>
      ) : (
        <>
          <div className="mt-0.5 shrink-0">{getEventIcon()}</div>
          <div className="min-w-0 flex-1">
            <p className="font-medium text-foreground text-sm">{getEventLabel()}</p>
            {getEventDescription() && (
              <p className="mt-0.5 line-clamp-3 text-muted-foreground text-xs">
                {getEventDescription()}
              </p>
            )}
            {event.timestamp && (
              <p className="mt-1 text-muted-foreground text-xs">
                {new Date(event.timestamp).toLocaleTimeString()}
              </p>
            )}
          </div>
        </>
      )}
    </motion.div>
  );
}
