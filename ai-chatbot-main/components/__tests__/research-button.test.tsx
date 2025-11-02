import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { ResearchButton } from "@/components/research-button";

describe("ResearchButton", () => {
  const prompt =
    "Investigate the latest breakthroughs in quantum computing hardware.";

  it("renders prompt text and sparkles action", () => {
    const onStart = vi.fn().mockResolvedValue(undefined);
    render(<ResearchButton prompt={prompt} onStart={onStart} />);

    expect(
      screen.getByText("Start research on this topic?")
    ).toBeInTheDocument();
    expect(screen.getByText(prompt)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /start research/i })).toBeEnabled();
  });

  it("disables action when prompt is empty", () => {
    const onStart = vi.fn();
    render(<ResearchButton prompt="   " onStart={onStart} />);

    const button = screen.getByRole("button", { name: /start research/i });
    expect(button).toBeDisabled();
    expect(
      screen.getByText(/Enter a research topic above/i)
    ).toBeInTheDocument();
  });

  it("invokes onStart handler and disables while running", async () => {
    let resolveStart: () => void = () => undefined;
    const onStart = vi
      .fn()
      .mockImplementation(
        () =>
          new Promise<void>((resolve) => {
            resolveStart = resolve;
          })
      );
    render(<ResearchButton prompt={prompt} onStart={onStart} />);

    const button = screen.getByRole("button", { name: /start research/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(onStart).toHaveBeenCalledWith(prompt);
    });
    await waitFor(() => {
      expect(button).toBeDisabled();
    });

    resolveStart();
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  it("respects disabled prop", () => {
    const onStart = vi.fn();
    render(<ResearchButton prompt={prompt} onStart={onStart} disabled />);

    const button = screen.getByRole("button", { name: /start research/i });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(onStart).not.toHaveBeenCalled();
  });

  it("shows loading label while starting", async () => {
    let resolvePromise: () => void = () => undefined;
    const onStart = vi
      .fn()
      .mockImplementation(
        () =>
          new Promise<void>((resolve) => {
            resolvePromise = resolve;
          })
      );

    render(<ResearchButton prompt={prompt} onStart={onStart} />);
    const button = screen.getByRole("button", { name: /start research/i });
    fireEvent.click(button);

    expect(screen.getByText(/Starting.../i)).toBeInTheDocument();
    resolvePromise();
    await waitFor(() => {
      expect(screen.getByText(/Start Research/i)).toBeInTheDocument();
    });
  });

  it("resets loading state when onStart throws", async () => {
    const onStart = vi.fn().mockRejectedValue(new Error("network error"));
    render(<ResearchButton prompt={prompt} onStart={onStart} />);

    const button = screen.getByRole("button", { name: /start research/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(button).toBeDisabled();
    });
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  it("truncates prompt with ellipsis for long text", () => {
    const longPrompt = "A".repeat(200);
    render(<ResearchButton prompt={longPrompt} onStart={vi.fn()} />);

    const promptText = screen.getByText((content, element) => {
      return element?.tagName.toLowerCase() === "p" && content.startsWith("A");
    });
    expect(promptText).toHaveClass("truncate");
  });

  it("prevents multiple invocations while pending", async () => {
    let resolver: () => void = () => undefined;
    const onStart = vi
      .fn()
      .mockImplementation(
        () =>
          new Promise<void>((resolve) => {
            resolver = resolve;
          })
      );

    render(<ResearchButton prompt={prompt} onStart={onStart} />);
    const button = screen.getByRole("button", { name: /start research/i });

    fireEvent.click(button);
    fireEvent.click(button);
    expect(onStart).toHaveBeenCalledTimes(1);

    resolver();
    await waitFor(() => expect(button).not.toBeDisabled());
  });

  it("passes unique prompt to onStart when prompt changes", async () => {
    const onStart = vi.fn().mockResolvedValue(undefined);
    const { rerender } = render(
      <ResearchButton prompt="first prompt" onStart={onStart} />
    );

    fireEvent.click(screen.getByRole("button"));
    await waitFor(() => {
      expect(onStart).toHaveBeenNthCalledWith(1, "first prompt");
    });
    await waitFor(() =>
      expect(screen.getByRole("button")).not.toBeDisabled()
    );

    rerender(<ResearchButton prompt="second prompt" onStart={onStart} />);
    fireEvent.click(screen.getByRole("button"));

    expect(onStart).toHaveBeenNthCalledWith(1, "first prompt");
    expect(onStart).toHaveBeenNthCalledWith(2, "second prompt");
  });

  it("exposes button via data-testid for E2E selectors", () => {
    render(<ResearchButton prompt={prompt} onStart={vi.fn()} />);
    expect(screen.getByTestId("research-button")).toBeInTheDocument();
  });

  it("renders sparkles icon inside button", () => {
    render(<ResearchButton prompt={prompt} onStart={vi.fn()} />);
    const button = screen.getByRole("button", { name: /start research/i });
    expect(button.querySelector("svg")).not.toBeNull();
  });
});
