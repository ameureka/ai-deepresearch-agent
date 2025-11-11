"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import useSWR, { useSWRConfig } from "swr";
import { unstable_serialize } from "swr/infinite";
import { ChatHeader } from "@/components/chat-header";
import { ResearchPanel } from "@/components/research-panel";
import { ResearchReportViewer } from "@/components/research-report-viewer";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useArtifactSelector } from "@/hooks/use-artifact";
import { useAutoResume } from "@/hooks/use-auto-resume";
import { useChatVisibility } from "@/hooks/use-chat-visibility";
import { useResearchProgress } from "@/hooks/use-research-progress";
import type { Vote } from "@/lib/db/schema";
import { ChatSDKError } from "@/lib/errors";
import {
  detectResearchKeywords,
  extractResearchQuery,
  validateResearchQuery,
} from "@/lib/research-utils";
import { Button } from "@/components/ui/button";
import type { Attachment, ChatMessage } from "@/lib/types";
import type { AppUsage } from "@/lib/usage";
import { fetcher, fetchWithErrorHandlers, generateUUID } from "@/lib/utils";
import { Artifact } from "./artifact";
import { useDataStream } from "./data-stream-provider";
import { Messages } from "./messages";
import { MultimodalInput } from "./multimodal-input";
import { getChatHistoryPaginationKey } from "./sidebar-history";
import { toast } from "./toast";
import type { VisibilityType } from "./visibility-selector";

export function Chat({
  id,
  initialMessages,
  initialChatModel,
  initialVisibilityType,
  isReadonly,
  autoResume,
  initialLastContext,
}: {
  id: string;
  initialMessages: ChatMessage[];
  initialChatModel: string;
  initialVisibilityType: VisibilityType;
  isReadonly: boolean;
  autoResume: boolean;
  initialLastContext?: AppUsage;
}) {
  const { visibilityType } = useChatVisibility({
    chatId: id,
    initialVisibilityType,
  });

  const { mutate } = useSWRConfig();
  const { setDataStream } = useDataStream();

  const [input, setInput] = useState<string>("");
  const [usage, setUsage] = useState<AppUsage | undefined>(initialLastContext);
  const [showCreditCardAlert, setShowCreditCardAlert] = useState(false);
  const [currentModelId, setCurrentModelId] = useState(initialChatModel);
  const currentModelIdRef = useRef(currentModelId);
  const [lastResearchReport, setLastResearchReport] = useState<string | null>(null);
  const [isResearchReportOpen, setIsResearchReportOpen] = useState(false);
  const [researchCooldownUntil, setResearchCooldownUntil] = useState<number | null>(null);

  useEffect(() => {
    currentModelIdRef.current = currentModelId;
  }, [currentModelId]);

  useEffect(() => {
    if (researchCooldownUntil === null) {
      return;
    }
    const remaining = researchCooldownUntil - Date.now();
    if (remaining <= 0) {
      setResearchCooldownUntil(null);
      return;
    }
    const timer = window.setTimeout(() => {
      setResearchCooldownUntil(null);
    }, remaining);
    return () => {
      window.clearTimeout(timer);
    };
  }, [researchCooldownUntil]);

  const {
    messages,
    setMessages,
    sendMessage,
    status,
    stop,
    regenerate,
    resumeStream,
  } = useChat<ChatMessage>({
    id,
    messages: initialMessages,
    experimental_throttle: 100,
    generateId: generateUUID,
    transport: new DefaultChatTransport({
      api: "/api/chat",
      fetch: fetchWithErrorHandlers,
      prepareSendMessagesRequest(request) {
        return {
          body: {
            id: request.id,
            message: request.messages.at(-1),
            selectedChatModel: currentModelIdRef.current,
            selectedVisibilityType: visibilityType,
            ...request.body,
          },
        };
      },
    }),
    onData: (dataPart) => {
      setDataStream((ds) => (ds ? [...ds, dataPart] : []));
      if (dataPart.type === "data-usage") {
        setUsage(dataPart.data);
      }
    },
    onFinish: () => {
      mutate(unstable_serialize(getChatHistoryPaginationKey));
    },
    onError: (error) => {
      if (error instanceof ChatSDKError) {
        // Check if it's a credit card error
        if (
          error.message?.includes("AI Gateway requires a valid credit card")
        ) {
          setShowCreditCardAlert(true);
        } else {
          toast({
            type: "error",
            description: error.message,
          });
        }
      }
    },
  });

  const searchParams = useSearchParams();
  const query = searchParams.get("query");

  const [hasAppendedQuery, setHasAppendedQuery] = useState(false);

  useEffect(() => {
    if (query && !hasAppendedQuery) {
      sendMessage({
        role: "user" as const,
        parts: [{ type: "text", text: query }],
      });

      setHasAppendedQuery(true);
      window.history.replaceState({}, "", `/chat/${id}`);
    }
  }, [query, sendMessage, hasAppendedQuery, id]);

  const { data: votes } = useSWR<Vote[]>(
    messages.length >= 2 ? `/api/vote?chatId=${id}` : null,
    fetcher
  );

  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const isArtifactVisible = useArtifactSelector((state) => state.isVisible);

  // Phase 3: Research Integration
  const [researchPrompt, setResearchPrompt] = useState<string | null>(null);
  const [showResearchUI, setShowResearchUI] = useState(false);
  const [forcedResearchPrompt, setForcedResearchPrompt] = useState<string | null>(
    null
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    const forced = (window as any).__E2E_RESEARCH_PROMPT;
    if (typeof forced === "string" && forced.trim().length > 0) {
      setForcedResearchPrompt(forced);
    }
  }, []);

  // Get text content from message parts
  const getMessageText = (message: ChatMessage | undefined): string => {
    if (!message || !message.parts) return "";
    return message.parts
      .filter((part) => part.type === "text")
      .map((part) => (part.type === "text" ? part.text : ""))
      .join(" ");
  };

  const lastAiMessage = messages
    .slice()
    .reverse()
    .find((m) => m.role === "assistant");
  const lastUserMessage = messages
    .slice()
    .reverse()
    .find((m) => m.role === "user");

  const lastAiMessageText = getMessageText(lastAiMessage);
  const lastUserMessageText = getMessageText(lastUserMessage);
  const rawSuggestedResearchQuery = lastAiMessageText
    ? extractResearchQuery(lastAiMessageText)
    : "";
  const extractedUserQuery = lastUserMessageText
    ? extractResearchQuery(lastUserMessageText)
    : "";
  const inputResearchQuery = input
    ? extractResearchQuery(input)
    : "";

  const normalizePrompt = (candidate: string | null | undefined) => {
    if (!candidate) return null;
    const trimmed = candidate.trim();
    if (!trimmed) return null;
    return validateResearchQuery(trimmed) ? trimmed : null;
  };

  const normalizedForcedPrompt = normalizePrompt(forcedResearchPrompt);
  const normalizedUserExtract = normalizePrompt(extractedUserQuery);
  const normalizedUserMessage = normalizePrompt(lastUserMessageText);
  const normalizedAssistantExtract = normalizePrompt(rawSuggestedResearchQuery);
  const normalizedInputPrompt = normalizePrompt(inputResearchQuery || input);

  const manualResearchPromptFromMessages =
    normalizedUserExtract ?? normalizedUserMessage;
  const manualResearchPrompt =
    normalizedInputPrompt ?? manualResearchPromptFromMessages;

  const effectiveResearchPrompt =
    normalizedForcedPrompt ??
    manualResearchPromptFromMessages ??
    normalizedAssistantExtract ??
    "";
  const hasEffectivePrompt = effectiveResearchPrompt.length > 0;
  const isInResearchCooldown =
    researchCooldownUntil !== null && researchCooldownUntil > Date.now();
  const shouldShowResearchButton =
    hasEffectivePrompt &&
    !showResearchUI &&
    !isInResearchCooldown &&
    ((normalizedForcedPrompt && normalizedForcedPrompt.length > 0) ||
      (lastAiMessageText && detectResearchKeywords(lastAiMessageText)));

  // Extract research query from last AI message
  const suggestedResearchQuery = effectiveResearchPrompt;

  // Start research handler
  const handleStartResearch = useCallback(
    (prompt: string) => {
      const trimmedPrompt = prompt.trim();
      if (!trimmedPrompt) {
        return;
      }
      setIsResearchReportOpen(false);
      setLastResearchReport(null);
      setResearchPrompt(trimmedPrompt);
      setShowResearchUI(true);
    },
    []
  );

  // Research complete handler (Phase 3 v2.0 - Simplified)
  const handleResearchComplete = useCallback(
    (report: string) => {
      const trimmedReport = report.trim();
      if (!trimmedReport) {
        toast({
          type: "error",
          description: "Research completed but report is empty.",
        });
        return;
      }

      setLastResearchReport(trimmedReport);
      setIsResearchReportOpen(true);

      toast({
        type: "success",
        description: "Research completed successfully!",
      });

      setResearchPrompt(null);
      setShowResearchUI(false);
      setResearchCooldownUntil(Date.now() + 120_000);
    },
    []
  );

  // Research error handler
  const handleResearchError = useCallback((error: Error) => {
    toast({
      type: "error",
      description: `Research failed: ${error.message}`,
    });
  }, []);

  const handleShareResearchReport = useCallback(
    (content: string) => {
      setInput((prev) => (prev ? `${prev}\n\n${content}` : content));
      setIsResearchReportOpen(false);
    },
    []
  );

  // Use research progress hook
  const {
    events: researchEvents,
    status: researchStatus,
    error: researchError,
    report: researchReport,
    isAutoRetrying: isResearchAutoRetrying,
    cancel: cancelResearchTask,
    retry: retryResearch,
    taskId: researchTaskId,
    queueInfo: researchQueueInfo,
  } = useResearchProgress({
    prompt: researchPrompt,
    chatId: id,
    onComplete: handleResearchComplete,
    onError: handleResearchError,
    visibility: visibilityType,
  });

  const combinedResearchReport = useMemo(() => {
    const trimmedHook = researchReport?.trim();
    if (trimmedHook && trimmedHook.length > 0) {
      return trimmedHook;
    }
    const trimmedStored = lastResearchReport?.trim();
    if (trimmedStored && trimmedStored.length > 0) {
      return trimmedStored;
    }
    return "";
  }, [lastResearchReport, researchReport]);

  const hasStoredResearchReport = Boolean(lastResearchReport?.trim());

  useEffect(() => {
    const trimmed = researchReport?.trim();
    if (trimmed && trimmed.length > 0 && trimmed !== lastResearchReport) {
      setLastResearchReport(trimmed);
    }
  }, [researchReport, lastResearchReport]);

  const handleViewResearchReport = useCallback(() => {
    const trimmed = combinedResearchReport.trim();
    if (!trimmed) {
      toast({
        type: "error",
        description: "Research report is not available yet.",
      });
      return;
    }
    setLastResearchReport(trimmed);
    setIsResearchReportOpen(true);
  }, [combinedResearchReport]);

  const handleCopyResearchReport = useCallback(async () => {
    const trimmed = combinedResearchReport.trim();
    if (!trimmed) {
      toast({
        type: "error",
        description: "Research report is not available yet.",
      });
      return;
    }
    try {
      await navigator.clipboard.writeText(trimmed);
      toast({
        type: "success",
        description: "Report copied to clipboard.",
      });
    } catch (error) {
      console.error("Failed to copy research report:", error);
      toast({
        type: "error",
        description: "Failed to copy report. Please try again.",
      });
    }
  }, [combinedResearchReport]);

  const handleExportResearchReport = useCallback(() => {
    const trimmed = combinedResearchReport.trim();
    if (!trimmed) {
      toast({
        type: "error",
        description: "Research report is not available yet.",
      });
      return;
    }
    try {
      const blob = new Blob([trimmed], {
        type: "text/markdown;charset=utf-8",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      link.download = `research-report-${timestamp}.md`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast({
        type: "success",
        description: "Report exported as Markdown.",
      });
    } catch (error) {
      console.error("Failed to export research report:", error);
      toast({
        type: "error",
        description: "Failed to export report. Please try again.",
      });
    }
  }, [combinedResearchReport]);

  const handleCancelResearch = useCallback(() => {
    cancelResearchTask();
    setResearchPrompt(null);
    setShowResearchUI(false);
  }, [cancelResearchTask]);

  const handleOpenResearchHistoryTask = useCallback(
    async (taskId: string) => {
      try {
        const response = await fetch(`/api/research/tasks/${taskId}`);
        if (!response.ok) {
          const payload = await response.json().catch(() => ({}));
          const message =
            payload.error ||
            payload.message ||
            `HTTP ${response.status}: ${response.statusText}`;
          throw new Error(message);
        }
        const payload = (await response.json()) as {
          report?: string | null;
          topic?: string | null;
          status?: string | null;
        };
        const trimmed = payload.report?.trim() ?? "";
        if (trimmed.length === 0) {
          toast({
            type: "error",
            description: "未找到该任务的研究报告，请稍后再试。",
          });
          return;
        }
        setLastResearchReport(trimmed);
        setIsResearchReportOpen(true);
        setResearchPrompt(null);
        setShowResearchUI(false);
        toast({
          type: "success",
          description: `已打开历史研究：${payload.topic ?? taskId}`,
        });
      } catch (error) {
        console.error("Failed to open research history task:", error);
        toast({
          type: "error",
          description: "无法加载历史研究内容，请稍后再试。",
        });
      }
    },
    []
  );

  useAutoResume({
    autoResume,
    initialMessages,
    resumeStream,
    setMessages,
  });

  const isResearchBusy =
    researchStatus === "queued" || researchStatus === "running";
  const trimmedManualPrompt = manualResearchPrompt?.trim() ?? "";
  const hasManualPrompt = trimmedManualPrompt.length > 0;
  const manualButtonLabel = isResearchBusy
    ? researchStatus === "queued"
      ? "Queued..."
      : "Researching..."
    : hasManualPrompt
    ? "Research This Topic"
    : "Enter a topic";
  const manualButtonCompactLabel = isResearchBusy
    ? "Working..."
    : hasManualPrompt
    ? "Research"
    : "Topic";
  const shouldShowManualButton =
    !isReadonly &&
    !showResearchUI &&
    (messages.length > 0 || hasManualPrompt);

  return (
    <>
      <div className="overscroll-behavior-contain flex h-dvh min-w-0 touch-pan-y flex-col bg-background">
        <ChatHeader
          chatId={id}
          isReadonly={isReadonly}
          selectedVisibilityType={initialVisibilityType}
        />

        <Messages
          chatId={id}
          isArtifactVisible={isArtifactVisible}
          isReadonly={isReadonly}
          messages={messages}
          regenerate={regenerate}
          selectedModelId={initialChatModel}
          setMessages={setMessages}
          status={status}
          votes={votes}
        />

        {/* Phase 3: Research Panel */}
        {!isReadonly &&
          (shouldShowResearchButton || showResearchUI || hasStoredResearchReport) && (
          <ResearchPanel
            prompt={suggestedResearchQuery}
            isActive={showResearchUI}
            events={researchEvents}
            status={researchStatus}
            error={researchError}
            report={combinedResearchReport}
            isAutoRetrying={isResearchAutoRetrying}
            onStart={handleStartResearch}
            onCancel={handleCancelResearch}
            onRetry={retryResearch}
            taskId={researchTaskId}
            queueInfo={researchQueueInfo ?? undefined}
            onViewReport={handleViewResearchReport}
            onCopyReport={handleCopyResearchReport}
            onExportReport={handleExportResearchReport}
            onSelectHistoryTask={handleOpenResearchHistoryTask}
          />
        )}

        <div className="sticky bottom-0 z-1 mx-auto w-full max-w-3xl border-t-0 bg-background px-2 pb-3 md:px-4 md:pb-4">
          {!isReadonly && (
            <MultimodalInput
              attachments={attachments}
              chatId={id}
              input={input}
              messages={messages}
              onModelChange={setCurrentModelId}
              selectedModelId={currentModelId}
              selectedVisibilityType={visibilityType}
              sendMessage={sendMessage}
              setAttachments={setAttachments}
              setInput={setInput}
              setMessages={setMessages}
              status={status}
              stop={stop}
              usage={usage}
              secondaryAction={
                shouldShowManualButton ? (
                  <Button
                    onClick={() => {
                      if (isResearchBusy || !hasManualPrompt) {
                        return;
                      }
                      handleStartResearch(trimmedManualPrompt);
                    }}
                    variant="outline"
                    size="sm"
                    className="whitespace-nowrap gap-2 shadow-sm transition-all duration-200 ease-out hover:-translate-y-0.5 hover:shadow-md disabled:pointer-events-none disabled:opacity-60"
                    disabled={
                      showResearchUI || isResearchBusy || !hasManualPrompt
                    }
                  >
                    {isResearchBusy ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                      </svg>
                    )}
                    <span className="hidden sm:inline">{manualButtonLabel}</span>
                    <span className="sm:hidden">{manualButtonCompactLabel}</span>
                  </Button>
                ) : null
              }
            />
          )}
        </div>
      </div>

      <Artifact
        attachments={attachments}
        chatId={id}
        input={input}
        isReadonly={isReadonly}
        messages={messages}
        regenerate={regenerate}
        selectedModelId={currentModelId}
        selectedVisibilityType={visibilityType}
        sendMessage={sendMessage}
        setAttachments={setAttachments}
        setInput={setInput}
        setMessages={setMessages}
        status={status}
        stop={stop}
        votes={votes}
      />

      <AlertDialog
        onOpenChange={setShowCreditCardAlert}
        open={showCreditCardAlert}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Activate AI Gateway</AlertDialogTitle>
            <AlertDialogDescription>
              This application requires{" "}
              {process.env.NODE_ENV === "production" ? "the owner" : "you"} to
              activate Vercel AI Gateway.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                window.open(
                  "https://vercel.com/d?to=%2F%5Bteam%5D%2F%7E%2Fai%3Fmodal%3Dadd-credit-card",
                  "_blank"
                );
                window.location.href = "/";
              }}
            >
              Activate
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <ResearchReportViewer
        report={lastResearchReport ?? combinedResearchReport ?? ""}
        isOpen={Boolean(lastResearchReport && isResearchReportOpen)}
        onClose={() => setIsResearchReportOpen(false)}
        onShareWithAI={
          lastResearchReport ? handleShareResearchReport : undefined
        }
      />
    </>
  );
}
