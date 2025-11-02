"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Clock,
  ExternalLink,
  Loader2,
  ChevronDown,
  History,
} from "lucide-react";
import { ResearchButton } from "@/components/research-button";
import { ResearchProgress } from "@/components/research-progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type {
  ResearchEvent,
  ResearchStatus,
  ResearchQueueInfo,
} from "@/hooks/use-research-progress";

export interface ResearchPanelProps {
  prompt: string;
  isActive: boolean;
  events: ResearchEvent[];
  status: ResearchStatus;
  error?: Error | null;
  report?: string | null;
  isAutoRetrying?: boolean;
  onStart: (prompt: string) => void;
  onCancel?: () => void;
  onRetry?: () => void;
  taskId?: string | null;
  queueInfo?: ResearchQueueInfo | null;
  onViewReport?: () => void;
  onCopyReport?: () => void | Promise<void>;
  onExportReport?: () => void;
  onSelectHistoryTask?: (taskId: string) => void;
}

type ResearchHistoryItem = {
  taskId: string;
  topic: string;
  status: string;
  queuedAt: string | null;
  updatedAt: string | null;
  completedAt: string | null;
  reportAvailable: boolean;
};

const HISTORY_LIMIT = 10;
const COLLAPSED_COUNT = 3;

export function ResearchPanel({
  prompt,
  isActive,
  events,
  status,
  error,
  report,
  isAutoRetrying,
  onStart,
  onCancel,
  onRetry,
  taskId,
  queueInfo,
  onViewReport,
  onCopyReport,
  onExportReport,
  onSelectHistoryTask,
}: ResearchPanelProps) {
  const hasPrompt = Boolean(prompt?.trim().length);
  const shouldShow = hasPrompt || isActive || status !== "idle";

  const [history, setHistory] = useState<ResearchHistoryItem[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [hasLoadedHistory, setHasLoadedHistory] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const fetchHistory = useCallback(async () => {
    setIsHistoryLoading(true);
    setHistoryError(null);

    try {
      const response = await fetch(`/api/research/tasks?limit=${HISTORY_LIMIT}`, {
        method: "GET",
        cache: "no-store",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const message =
          payload.error ||
          payload.message ||
          `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(message);
      }

      const payload = (await response.json()) as {
        tasks?: ResearchHistoryItem[];
      };
      setHistory(payload.tasks ?? []);
      setHasLoadedHistory(true);
    } catch (error) {
      if ((error as Error).name === "AbortError") {
        return;
      }
      console.error("Failed to load research history:", error);
      setHistoryError("无法加载研究历史，请稍后重试。");
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    if (status === "done" || status === "error") {
      fetchHistory();
    }
  }, [fetchHistory, status]);

  const historySubtitle = useMemo(() => {
    if (!history.length) {
      return hasLoadedHistory ? "暂无历史记录" : null;
    }
    return `共 ${history.length} 条研究记录`;
  }, [hasLoadedHistory, history.length]);

  const historyDataset = useMemo(() => {
    if (isExpanded) {
      return history;
    }
    return history.slice(0, COLLAPSED_COUNT);
  }, [history, isExpanded]);

  const renderStatusBadge = (historyStatus: string) => {
    switch (historyStatus) {
      case "completed":
        return (
          <Badge className="bg-emerald-500/10 text-emerald-600 dark:bg-emerald-400/10 dark:text-emerald-200">
            已完成
          </Badge>
        );
      case "queued":
        return (
          <Badge className="bg-amber-500/10 text-amber-600 dark:bg-amber-400/10 dark:text-amber-200">
            排队中
          </Badge>
        );
      case "running":
        return (
          <Badge className="bg-blue-500/10 text-blue-600 dark:bg-blue-400/10 dark:text-blue-200">
            进行中
          </Badge>
        );
      case "failed":
        return (
          <Badge className="bg-red-500/10 text-red-600 dark:bg-red-400/10 dark:text-red-200">
            失败
          </Badge>
        );
      case "cancelled":
        return (
          <Badge className="bg-gray-500/10 text-gray-600 dark:bg-gray-400/10 dark:text-gray-200">
            已取消
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="border-muted-foreground/40">
            {historyStatus}
          </Badge>
        );
    }
  };

  const formatRelativeTime = (timestamp: string | null) => {
    if (!timestamp) {
      return "--";
    }
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
      return "--";
    }
    const diffMs = Date.now() - date.getTime();
    if (diffMs < 60_000) {
      return "刚刚";
    }
    if (diffMs < 3_600_000) {
      const minutes = Math.floor(diffMs / 60_000);
      return `${minutes} 分钟前`;
    }
    if (diffMs < 86_400_000) {
      const hours = Math.floor(diffMs / 3_600_000);
      return `${hours} 小时前`;
    }
    return date.toLocaleString();
  };

  return (
    <AnimatePresence>
      {shouldShow && (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="sticky bottom-[72px] z-10 mx-auto mb-4 w-full max-w-3xl px-4"
          data-testid="research-panel"
          data-task-id={taskId ?? undefined}
          data-status={status}
          exit={{ opacity: 0, y: 20 }}
          initial={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        >
          <div className="max-h-[480px] overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-800 dark:bg-gray-900">
            {!isActive && status === "idle" && hasPrompt && (
              <ResearchButton
                disabled={
                  status === "queued" ||
                  status === "running" ||
                  !prompt.trim().length
                }
                onStart={onStart}
                prompt={prompt}
              />
            )}

            {(isActive || status !== "idle") && (
              <ResearchProgress
                taskId={taskId ?? undefined}
                error={error}
                events={events}
                isAutoRetrying={Boolean(isAutoRetrying)}
                onCancel={onCancel}
                onRetry={onRetry}
                report={report}
                status={status}
                queueInfo={queueInfo ?? null}
                onViewReport={onViewReport}
                onCopyReport={onCopyReport}
                onExportReport={onExportReport}
              />
            )}

            {(!isActive || status === "idle" || status === "done" || status === "error") && (
              <div className="border-t border-dashed border-muted-foreground/40 bg-muted/20 p-4">
                <div className="mb-3 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <History className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="font-medium text-sm text-foreground">
                        Recent Research
                      </p>
                      {historySubtitle && (
                        <p className="text-muted-foreground text-xs">
                          {historySubtitle}
                        </p>
                      )}
                    </div>
                  </div>
                  <Button
                    className="gap-2"
                    disabled={isHistoryLoading}
                    onClick={() => fetchHistory()}
                    size="xs"
                    variant="ghost"
                  >
                    {isHistoryLoading ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Clock className="h-3.5 w-3.5" />
                    )}
                    刷新
                  </Button>
                </div>

                {isHistoryLoading && !historyError && !history.length && (
                  <div className="space-y-2">
                    {Array.from({ length: COLLAPSED_COUNT }).map((_, index) => (
                      <div
                        key={index}
                        className="animate-pulse rounded-md bg-muted p-3"
                      >
                        <div className="h-3 w-2/3 rounded bg-muted-foreground/30" />
                        <div className="mt-2 h-3 w-1/3 rounded bg-muted-foreground/20" />
                      </div>
                    ))}
                  </div>
                )}

                {historyError && (
                  <p className="rounded-md bg-red-500/10 p-2 text-xs text-red-600 dark:text-red-300">
                    {historyError}
                  </p>
                )}

                {!historyError &&
                  history.length === 0 &&
                  hasLoadedHistory &&
                  !isHistoryLoading && (
                    <p className="text-muted-foreground text-xs">
                      目前没有可以展示的研究历史记录。
                    </p>
                  )}

                {!historyError && historyDataset.length > 0 && (
                  <ul className="space-y-2">
                    {historyDataset.map((item) => {
                      const hasReport =
                        item.reportAvailable && item.status === "completed";
                      const viewLabel = hasReport ? "查看报告" : "查看进度";
                      return (
                        <li
                          key={item.taskId}
                          className="rounded-md border border-transparent bg-background/70 p-3 transition hover:border-muted-foreground/20 hover:bg-background"
                        >
                          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                            <div className="flex flex-col gap-1">
                              <div className="flex items-center gap-2">
                                <p className="line-clamp-1 text-sm font-medium text-foreground">
                                  {item.topic || "未命名研究"}
                                </p>
                                {renderStatusBadge(item.status)}
                              </div>
                              <p className="text-muted-foreground text-xs">
                                更新于 {formatRelativeTime(item.updatedAt)}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                className="gap-1 text-xs"
                                onClick={() =>
                                  hasReport &&
                                  onSelectHistoryTask?.(item.taskId)
                                }
                                size="xs"
                                variant="outline"
                                disabled={!hasReport || !onSelectHistoryTask}
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                                {viewLabel}
                              </Button>
                            </div>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                )}

                {!historyError &&
                  history.length > COLLAPSED_COUNT &&
                  !isHistoryLoading && (
                    <Button
                      className="mt-3 w-full gap-2 text-xs"
                      onClick={() => setIsExpanded((prev) => !prev)}
                      size="xs"
                      variant="ghost"
                    >
                      <ChevronDown
                        className={`h-3.5 w-3.5 transition-transform ${
                          isExpanded ? "rotate-180" : ""
                        }`}
                      />
                      {isExpanded ? "收起历史记录" : "展开全部历史记录"}
                    </Button>
                  )}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
