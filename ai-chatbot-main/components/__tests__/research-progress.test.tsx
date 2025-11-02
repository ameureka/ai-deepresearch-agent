import { act, fireEvent, render, screen } from "@testing-library/react";
import { ResearchProgress } from "@/components/research-progress";
import type { ResearchEvent } from "@/hooks/use-research-progress";
import { vi } from "vitest";

const baseEvents: ResearchEvent[] = [
  {
    type: "start",
    data: { message: "Research request received" },
  },
  {
    type: "plan",
    data: {
      steps: ["Collect sources", "Summarise findings"],
    },
  },
  {
    type: "progress",
    data: {
      message: "Collect sources",
      step: 1,
      total: 2,
    },
  },
];

describe("ResearchProgress", () => {
  it("renders idle state without progress bar", () => {
    render(<ResearchProgress events={[]} status="idle" />);
    expect(screen.getByText(/Ready/i)).toBeInTheDocument();
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("shows running status and progress summary", () => {
    render(
      <ResearchProgress
        events={baseEvents}
        status="running"
        onCancel={vi.fn()}
      />
    );

    expect(
      screen.getByText(/Research in progress/i)
    ).toBeInTheDocument();
    expect(screen.getAllByText(/Step 1 of 2/i).length).toBeGreaterThan(0);
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("calculates progress percentage based on events", () => {
    render(
      <ResearchProgress
        events={[
          ...baseEvents,
          {
            type: "progress",
            data: { message: "Summarise findings", step: 1, total: 2 },
          },
        ]}
        status="running"
      />
    );

    expect(screen.getByText(/50%/)).toBeInTheDocument();
  });

  it("caps progress percentage at 95% until done", () => {
    const steps = Array.from({ length: 4 }, (_, index) => `Step ${index + 1}`);
    const manyEvents: ResearchEvent[] = [
      { type: "start", data: { message: "Queued" } },
      { type: "plan", data: { steps } },
      ...steps.map((title, index) => ({
        type: "progress" as const,
        data: { message: title, step: index + 1, total: steps.length },
      })),
    ];

    render(
      <ResearchProgress
        events={manyEvents}
        status="running"
        onCancel={vi.fn()}
      />
    );
    expect(screen.getByText(/95%/)).toBeInTheDocument();
  });

  it("hides cancel button when onCancel not provided", () => {
    render(<ResearchProgress events={baseEvents} status="running" />);
    expect(
      screen.queryByRole("button", { name: /cancel/i })
    ).not.toBeInTheDocument();
  });

  it("renders success state when done", () => {
    render(
      <ResearchProgress
        events={[...baseEvents, { type: "done", data: { report: "Ready" } }]}
        status="done"
        report="Ready"
      />
    );

    expect(
      screen.getByText(/Research completed successfully/i)
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /cancel/i })
    ).not.toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("renders error state and retry action", () => {
    render(
      <ResearchProgress
        events={[...baseEvents, { type: "error", data: { message: "Timeout" } }]}
        status="error"
        error={new Error("Timeout")}
        onRetry={vi.fn()}
      />
    );

    expect(screen.getByText(/Research failed/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Timeout/i).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
  });

  it("does not show retry button when handler missing", () => {
    render(
      <ResearchProgress
        events={[...baseEvents, { type: "error", data: { message: "Timeout" } }]}
        status="error"
        error={new Error("Timeout")}
      />
    );
    expect(
      screen.queryByRole("button", { name: /retry/i })
    ).not.toBeInTheDocument();
  });

  it("renders event messages in timeline", () => {
    render(
      <ResearchProgress
        events={baseEvents}
        status="running"
        onCancel={vi.fn()}
      />
    );

    expect(
      screen.getByText(/Research request received/i)
    ).toBeInTheDocument();
    expect(screen.getAllByText(/Collect sources/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Summarise findings/i).length).toBeGreaterThan(0);
  });

  it("shows error alert with fallback when error message missing", () => {
    render(
      <ResearchProgress
        events={[...baseEvents, { type: "error", data: {} }]}
        status="error"
        error={new Error()}
        onRetry={vi.fn()}
      />
    );

    expect(screen.getByText(/Research failed/i)).toBeInTheDocument();
  });

  it("displays queue information when queued", () => {
    render(
      <ResearchProgress
        events={[]}
        status="queued"
        queueInfo={{
          enqueuedAt: "2025-11-02T03:23:31Z",
          retryCount: 1,
        }}
      />
    );

    expect(screen.getAllByText(/Queued/i).length).toBeGreaterThan(0);
    expect(
      screen.getByText(/Waiting for an available research worker/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Queued for/i)).toBeInTheDocument();
    expect(screen.getByText(/Retry attempt 2/i)).toBeInTheDocument();
  });

  it("omits event count text when not running", () => {
    render(<ResearchProgress events={baseEvents} status="done" />);
    expect(
      screen.queryByText(/events received/i)
    ).not.toBeInTheDocument();
  });

  it("renders progress bar value for running", () => {
    render(<ResearchProgress events={baseEvents} status="running" />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toBeInTheDocument();
  });

  it("renders no timeline when there are no events", () => {
    render(<ResearchProgress events={[]} status="running" />);
    expect(
      screen.getByText(/Preparing research workflow/i)
    ).toBeInTheDocument();
  });

  it("keeps Cancel button only while running", () => {
    const { rerender } = render(
      <ResearchProgress events={baseEvents} status="running" onCancel={vi.fn()} />
    );
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();

    rerender(
      <ResearchProgress
        events={[...baseEvents, { type: "done", data: {} }]}
        status="done"
        onCancel={vi.fn()}
      />
    );
    expect(
      screen.queryByRole("button", { name: /cancel/i })
    ).not.toBeInTheDocument();
  });

  it("exposes data attributes for telemetry", () => {
    render(
      <ResearchProgress
        events={baseEvents}
        status="running"
        taskId="task-xyz"
      />
    );

    const container = screen.getByTestId("research-progress");
    expect(container).toHaveAttribute("data-task-id", "task-xyz");
    expect(container).toHaveAttribute("data-status", "running");
  });

  it("renders report action buttons when report available", async () => {
    const onView = vi.fn();
    const onCopy = vi.fn();
    const onExport = vi.fn();

    render(
      <ResearchProgress
        events={[...baseEvents, { type: "done", data: {} }]}
        status="done"
        report="# Summary"
        onViewReport={onView}
        onCopyReport={onCopy}
        onExportReport={onExport}
      />
    );

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /view full report/i }));
    });
    expect(onView).toHaveBeenCalled();

    const copyButton = screen.getByRole("button", { name: /^copy$/i });
    await act(async () => {
      fireEvent.click(copyButton);
    });
    expect(onCopy).toHaveBeenCalled();
    expect(
      screen.getByRole("button", { name: /copied!/i })
    ).toBeInTheDocument();

    const exportButton = screen.getByRole("button", { name: /^export$/i });
    await act(async () => {
      fireEvent.click(exportButton);
    });
    expect(onExport).toHaveBeenCalled();
    expect(
      screen.getByRole("button", { name: /exported!/i })
    ).toBeInTheDocument();
  });
});
