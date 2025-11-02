import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ResearchPanel } from "@/components/research-panel";
import type { ResearchEvent } from "@/hooks/use-research-progress";

const sampleEvents: ResearchEvent[] = [
  { type: "start", data: { message: "Research started" } },
  { type: "plan", data: { outline: ["Gather sources", "Draft report"] } },
];

const mockFetchResponse = (data: unknown) =>
  Promise.resolve({
    ok: true,
    json: async () => data,
  } as Response);

describe("ResearchPanel", () => {
  const prompt = "Analyse 2025 quantum computing milestones.";

  beforeEach(() => {
    vi.spyOn(global, "fetch").mockImplementation(() =>
      mockFetchResponse({ tasks: [] })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const renderPanel = async (
    props: React.ComponentProps<typeof ResearchPanel>
  ) => {
    await act(async () => {
      render(<ResearchPanel {...props} />);
    });
  };

  it("renders ResearchButton when idle", async () => {
    await renderPanel({
      prompt,
      isActive: false,
      events: [],
      status: "idle",
      onStart: vi.fn(),
    });

    expect(screen.getByTestId("research-panel")).toBeInTheDocument();
    expect(screen.getByTestId("research-button")).toBeInTheDocument();
    expect(screen.queryByTestId("research-progress")).not.toBeInTheDocument();
  });

  it("shows ResearchProgress when active", async () => {
    await renderPanel({
      prompt,
      isActive: true,
      events: sampleEvents,
      status: "running",
      onStart: vi.fn(),
    });

    expect(screen.getByTestId("research-progress")).toBeInTheDocument();
    expect(screen.queryByTestId("research-button")).not.toBeInTheDocument();
  });

  it("invokes onStart when button clicked", async () => {
    const onStart = vi.fn().mockResolvedValue(undefined);
    await renderPanel({
      prompt,
      isActive: false,
      events: [],
      status: "idle",
      onStart,
    });

    fireEvent.click(screen.getByRole("button", { name: /start research/i }));

    await waitFor(() => {
      expect(onStart).toHaveBeenCalledWith(prompt);
    });
  });

  it("does not render panel when prompt missing", async () => {
    await renderPanel({
      prompt: "",
      isActive: false,
      events: [],
      status: "idle",
      onStart: vi.fn(),
    });

    expect(screen.queryByTestId("research-panel")).not.toBeInTheDocument();
  });

  it("renders panel container when status not idle", async () => {
    await renderPanel({
      prompt,
      isActive: true,
      events: sampleEvents,
      status: "running",
      onStart: vi.fn(),
    });

    expect(screen.getByTestId("research-panel")).toBeInTheDocument();
  });

  it("forwards onCancel handler", async () => {
    const onCancel = vi.fn();
    await renderPanel({
      prompt,
      isActive: true,
      events: sampleEvents,
      status: "running",
      onStart: vi.fn(),
      onCancel,
    });

    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });

  it("forwards onRetry handler", async () => {
    const onRetry = vi.fn();
    await renderPanel({
      prompt,
      isActive: true,
      events: [...sampleEvents, { type: "error", data: { message: "fail" } }],
      status: "error",
      onStart: vi.fn(),
      onRetry,
      error: new Error("fail"),
    });

    fireEvent.click(screen.getByRole("button", { name: /retry/i }));
    expect(onRetry).toHaveBeenCalled();
  });

  it("shows error message when status error", async () => {
    await renderPanel({
      prompt,
      isActive: true,
      events: [...sampleEvents, { type: "error", data: { message: "fail" } }],
      status: "error",
      error: new Error("fail"),
      onStart: vi.fn(),
    });

    expect(screen.getByText(/research failed/i)).toBeInTheDocument();
  });

  it("retains research prompt text when idle", async () => {
    await renderPanel({
      prompt,
      isActive: false,
      events: [],
      status: "idle",
      onStart: vi.fn(),
    });

    expect(
      screen.getByText("Start research on this topic?")
    ).toBeInTheDocument();
  });

  it("passes task metadata to ResearchProgress", async () => {
    await renderPanel({
      prompt,
      isActive: true,
      events: sampleEvents,
      status: "running",
      onStart: vi.fn(),
      taskId: "task-123",
    });

    expect(screen.getByTestId("research-panel")).toHaveAttribute(
      "data-task-id",
      "task-123"
    );
    expect(screen.getByTestId("research-panel")).toHaveAttribute(
      "data-status",
      "running"
    );
    expect(screen.getByTestId("research-progress")).toHaveAttribute(
      "data-task-id",
      "task-123"
    );
  });
});
