"use client";

import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useCallback, useEffect, useRef, useState } from "react";

/**
 * SSE Event Types from FastAPI Backend
 */
export type ResearchEventType =
  | "start"
  | "plan"
  | "progress"
  | "done"
  | "error";

/**
 * Research Event Structure
 */
export interface ResearchEvent {
  type: ResearchEventType;
  data: any;
  timestamp?: number;
}

/**
 * Research Status
 */
export type ResearchStatus =
  | "idle" // Not started
  | "connecting" // Connecting to backend
  | "streaming" // Receiving events
  | "done" // Completed successfully
  | "error"; // Failed with error

/**
 * Hook Options
 */
export interface UseResearchProgressOptions {
  prompt: string | null; // Research query (null = don't start)
  onComplete?: (report: string) => void; // Callback when research completes
  onError?: (error: Error) => void; // Callback when error occurs
}

/**
 * Hook Return Value
 */
export interface UseResearchProgressReturn {
  events: ResearchEvent[]; // All events received
  status: ResearchStatus; // Current status
  error: Error | null; // Error if status is "error"
  cancel: () => void; // Cancel current research
  retry: () => void; // Retry failed research
}

/**
 * useResearchProgress Hook
 *
 * Connects to the research API endpoint and streams SSE events.
 * Automatically starts when prompt changes from null to a string.
 * Calls onComplete when research finishes with the final report.
 *
 * @example
 * ```tsx
 * const { events, status } = useResearchProgress({
 *   prompt: "quantum computing",
 *   onComplete: (report) => {
 *     sendMessage({
 *       role: 'user',
 *       parts: [{ type: 'text', text: `Research completed:\n\n${report}` }]
 *     });
 *   }
 * });
 * ```
 */
export function useResearchProgress({
  prompt,
  onComplete,
  onError,
}: UseResearchProgressOptions): UseResearchProgressReturn {
  const [events, setEvents] = useState<ResearchEvent[]>([]);
  const [status, setStatus] = useState<ResearchStatus>("idle");
  const [error, setError] = useState<Error | null>(null);

  // Use refs to track abort controller and prevent duplicate connections
  const abortControllerRef = useRef<AbortController | null>(null);
  const currentPromptRef = useRef<string | null>(null);

  /**
   * Cancel current research
   */
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setStatus("idle");
  }, []);

  /**
   * Retry failed research
   */
  const retry = useCallback(() => {
    if (currentPromptRef.current) {
      setError(null);
      setEvents([]);
      setStatus("connecting");
      // Trigger re-connection by updating a ref
      startResearch(currentPromptRef.current);
    }
  }, []);

  /**
   * Start research with given prompt
   */
  const startResearch = useCallback(
    async (researchPrompt: string) => {
      // Cancel any existing connection
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      const abortController = new AbortController();
      abortControllerRef.current = abortController;
      currentPromptRef.current = researchPrompt;

      // Reset state
      setEvents([]);
      setError(null);
      setStatus("connecting");

      try {
        await fetchEventSource("/api/research/stream", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt: researchPrompt }),
          signal: abortController.signal,

          onopen: async (response) => {
            if (response.ok) {
              setStatus("streaming");
              return; // Connection established
            }

            // Handle HTTP errors
            const errorData = await response.json().catch(() => ({}));
            const errorMessage =
              errorData.error ||
              `HTTP ${response.status}: ${response.statusText}`;

            throw new Error(errorMessage);
          },

          onmessage: (event) => {
            // Parse event data
            let eventData: any;

            try {
              eventData = JSON.parse(event.data);
            } catch {
              eventData = event.data;
            }

            const researchEvent: ResearchEvent = {
              type: (event.event || "progress") as ResearchEventType,
              data: eventData,
              timestamp: Date.now(),
            };

            // Add event to list
            setEvents((prev) => [...prev, researchEvent]);

            // Handle done event
            if (researchEvent.type === "done") {
              setStatus("done");

              // Extract report and call onComplete
              const report = eventData.report || eventData.message || "";
              if (onComplete) {
                onComplete(report);
              }

              // Clean up
              abortControllerRef.current = null;
            }

            // Handle error event
            if (researchEvent.type === "error") {
              const errorMsg =
                eventData.error || eventData.message || "Unknown error";
              const err = new Error(errorMsg);
              setError(err);
              setStatus("error");

              if (onError) {
                onError(err);
              }

              // Clean up
              abortControllerRef.current = null;
            }
          },

          onerror: (err) => {
            // Check if this was intentional cancellation
            if (abortController.signal.aborted) {
              return; // Don't treat abort as error
            }

            const error =
              err instanceof Error
                ? err
                : new Error(
                    typeof err === "string"
                      ? err
                      : "Failed to connect to research backend"
                  );

            setError(error);
            setStatus("error");

            if (onError) {
              onError(error);
            }

            // Clean up
            abortControllerRef.current = null;

            // Don't retry automatically - let user decide
            throw error; // Stop fetchEventSource
          },

          onclose: () => {
            // Connection closed normally
            if (status !== "done" && status !== "error") {
              // Unexpected close
              const error = new Error("Connection closed unexpectedly");
              setError(error);
              setStatus("error");

              if (onError) {
                onError(error);
              }
            }

            // Clean up
            abortControllerRef.current = null;
          },
        });
      } catch (err) {
        // fetchEventSource throws when onerror throws
        // Error already handled in onerror callback
        console.error("Research connection error:", err);
      }
    },
    [onComplete, onError, status]
  );

  /**
   * Effect: Start research when prompt changes
   */
  useEffect(() => {
    if (prompt && prompt.trim().length > 0) {
      // Only start if not already running
      if (status === "idle" || status === "error") {
        startResearch(prompt.trim());
      }
    }
  }, [prompt, status, startResearch]); // Include all dependencies

  /**
   * Effect: Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, []);

  return {
    events,
    status,
    error,
    cancel,
    retry,
  };
}
