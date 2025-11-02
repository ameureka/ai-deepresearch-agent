"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type ResearchEventType =
  | "queued"
  | "start"
  | "plan"
  | "progress"
  | "done"
  | "error";

export interface ResearchEvent {
  type: ResearchEventType;
  data: Record<string, unknown>;
  timestamp?: number;
  taskId?: string;
  chatId?: string;
  userId?: string;
}

export type ResearchStatus =
  | "idle"
  | "queued"
  | "running"
  | "done"
  | "error";

export interface ResearchQueueInfo {
  enqueuedAt?: string;
  startedAt?: string;
  finishedAt?: string;
  failedAt?: string;
  workerId?: string;
  retryCount?: number;
}

type VisibilityType = "private" | "public";

export interface UseResearchProgressOptions {
  prompt: string | null;
  chatId?: string | null;
  onComplete?: (report: string) => void;
  onError?: (error: Error) => void;
  visibility?: VisibilityType;
}

export interface UseResearchProgressReturn {
  events: ResearchEvent[];
  status: ResearchStatus;
  error: Error | null;
  report: string | null;
  isAutoRetrying: boolean;
  cancel: () => void;
  retry: () => void;
  taskId: string | null;
  taskOwnerId: string | null;
  queueInfo: ResearchQueueInfo | null;
}

type RawProgressEvent = {
  type?: string;
  message?: string;
  timestamp?: string;
  [key: string]: unknown;
};

const POLL_INTERVAL_MS = 2000;

const mapEvents = (
  rawEvents: RawProgressEvent[],
  taskId: string,
  chatId?: string | null,
  userId?: string | null
): ResearchEvent[] =>
  rawEvents.map(raw => ({
    type: (raw.type as ResearchEventType) ?? "progress",
    data: {
      ...raw,
      taskId,
      chatId,
      userId,
    },
    timestamp: raw.timestamp ? Date.parse(raw.timestamp) : undefined,
    taskId,
    chatId: chatId ?? undefined,
    userId: userId ?? undefined,
  }));

const extractFailureMessage = (events: ResearchEvent[]): string | null => {
  for (let i = events.length - 1; i >= 0; i -= 1) {
    const evt = events[i];
    const message = evt.data?.message;
    if (evt.type === "error" && typeof message === "string") {
      return message;
    }
  }
  return null;
};

type TaskStatusResponse = {
  taskId: string;
  status: string;
  topic?: string | null;
  progress?: {
    currentStep?: string | null;
    totalSteps?: number | null;
    completedSteps?: number | null;
    events?: RawProgressEvent[];
  } | null;
  report?: string | null;
  userId?: string | null;
  chatId?: string | null;
  queueInfo?: ResearchQueueInfo | null;
  startedAt?: string | null;
  completedAt?: string | null;
  failedAt?: string | null;
};

export function useResearchProgress({
  prompt,
  chatId,
  onComplete,
  onError,
  visibility = "private",
}: UseResearchProgressOptions): UseResearchProgressReturn {
  const [events, setEvents] = useState<ResearchEvent[]>([]);
  const [status, setStatus] = useState<ResearchStatus>("idle");
  const [error, setError] = useState<Error | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskOwnerId, setTaskOwnerId] = useState<string | null>(null);
  const [queueInfo, setQueueInfo] = useState<ResearchQueueInfo | null>(null);

  const statusRef = useRef<ResearchStatus>("idle");
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const currentPromptRef = useRef<string | null>(null);
  const currentTaskIdRef = useRef<string | null>(null);

  const updateStatus = useCallback((next: ResearchStatus) => {
    statusRef.current = next;
    setStatus(next);
  }, []);

  const clearPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const fetchTaskStatus = useCallback(
    async (taskIdValue: string) => {
      const response = await fetch(`/api/research/tasks/${taskIdValue}`);

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const message =
          payload.error ||
          payload.message ||
          `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(message);
      }

      const payload = (await response.json()) as TaskStatusResponse;
      const mappedEvents = mapEvents(
        payload.progress?.events ?? [],
        payload.taskId,
        payload.chatId ?? null,
        payload.userId ?? null
      );

      setEvents(mappedEvents);
      setTaskOwnerId(payload.userId ?? null);
      setQueueInfo(payload.queueInfo ?? null);

      if (typeof payload.report === "string") {
        setReport(payload.report);
      }

      switch (payload.status) {
        case "queued":
        case "pending":
          updateStatus("queued");
          break;
        case "running":
        case "planning":
        case "researching":
        case "writing":
          updateStatus("running");
          break;
        case "completed": {
          updateStatus("done");
          clearPolling();
          const finalReport = payload.report ?? "";
          if (finalReport && onComplete) {
            onComplete(finalReport);
          }
          break;
        }
        case "failed": {
          const failureMessage =
            extractFailureMessage(mappedEvents) ?? "Research failed";
          const failureError = new Error(failureMessage);
          setError(failureError);
          updateStatus("error");
          clearPolling();
          if (onError) {
            onError(failureError);
          }
          break;
        }
        case "cancelled": {
          const cancellationError = new Error("Research task was cancelled");
          setError(cancellationError);
          updateStatus("error");
          clearPolling();
          if (onError) {
            onError(cancellationError);
          }
          break;
        }
        default:
          updateStatus("running");
          break;
      }
    },
    [clearPolling, onComplete, onError, updateStatus]
  );

  const schedulePolling = useCallback(
    (taskIdValue: string) => {
      const poll = async () => {
        try {
          await fetchTaskStatus(taskIdValue);
        } catch (err) {
          const errorObj =
            err instanceof Error
              ? err
              : new Error("Failed to fetch research status");
          setError(errorObj);
          updateStatus("error");
          clearPolling();
          if (onError) {
            onError(errorObj);
          }
        }
      };

      poll();
      pollingRef.current = setInterval(poll, POLL_INTERVAL_MS);
    },
    [clearPolling, fetchTaskStatus, onError, updateStatus]
  );

  const startResearch = useCallback(
    async (researchPrompt: string) => {
      clearPolling();
      setEvents([]);
      setError(null);
      setReport(null);
      setTaskId(null);
      setTaskOwnerId(null);
      setQueueInfo(null);
      updateStatus("queued");

      currentPromptRef.current = researchPrompt;
      currentTaskIdRef.current = null;

      try {
        const response = await fetch("/api/research/tasks", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: researchPrompt,
            chatId: chatId ?? null,
            visibility,
          }),
        });

        if (!response.ok) {
          const payload = await response.json().catch(() => ({}));
          const message =
            payload.error ||
            payload.message ||
            `HTTP ${response.status}: ${response.statusText}`;
          throw new Error(message);
        }

        const payload = (await response.json()) as { taskId: string };
        const newTaskId = payload.taskId;
        setTaskId(newTaskId);
        currentTaskIdRef.current = newTaskId;
        updateStatus("queued");
        setQueueInfo({
          enqueuedAt: new Date().toISOString(),
          retryCount: 0,
        });
        schedulePolling(newTaskId);
      } catch (err) {
        const errorObj =
          err instanceof Error
            ? err
            : new Error("Failed to start research task");
        setError(errorObj);
        updateStatus("error");
        if (onError) {
          onError(errorObj);
        }
      }
    },
    [chatId, clearPolling, onError, schedulePolling, updateStatus]
  );

  const cancel = useCallback(() => {
    clearPolling();
    setEvents([]);
    setError(null);
    setReport(null);
    setTaskId(null);
    setTaskOwnerId(null);
    setQueueInfo(null);
    updateStatus("idle");
    currentTaskIdRef.current = null;
    currentPromptRef.current = null;
  }, [clearPolling, updateStatus]);

  const retry = useCallback(() => {
    if (currentPromptRef.current) {
      startResearch(currentPromptRef.current);
    }
  }, [startResearch]);

  useEffect(() => {
    if (!prompt) {
      return;
    }

    const trimmed = prompt.trim();
    if (!trimmed) {
      return;
    }

    if (
      currentPromptRef.current === trimmed &&
      statusRef.current !== "idle" &&
      statusRef.current !== "error"
    ) {
      return;
    }

    startResearch(trimmed);
  }, [prompt, startResearch]);

  useEffect(() => {
    return () => {
      clearPolling();
    };
  }, [clearPolling]);

  return {
    events,
    status,
    error,
    report,
    isAutoRetrying: false,
    cancel,
    retry,
    taskId,
    taskOwnerId,
    queueInfo,
  };
}
