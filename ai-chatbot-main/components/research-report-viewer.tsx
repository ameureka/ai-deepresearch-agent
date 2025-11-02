"use client";

import { Button } from "@/components/ui/button";
import { AnimatePresence, motion } from "framer-motion";
import { Copy, Download, Share2, X } from "lucide-react";
import { useState } from "react";
import { Streamdown } from "streamdown";

export interface ResearchReportViewerProps {
  report: string;
  isOpen: boolean;
  onClose: () => void;
  onShareWithAI?: (report: string) => void;
}

/**
 * ResearchReportViewer Component
 *
 * Displays research report in a side panel with actions:
 * - Copy to clipboard
 * - Export as Markdown
 * - Share with AI (optional)
 *
 * Phase 3 v2.0: Direct report display without AI processing
 */
export function ResearchReportViewer({
  report,
  isOpen,
  onClose,
  onShareWithAI,
}: ResearchReportViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(report);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `research-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleShareWithAI = () => {
    if (onShareWithAI) {
      onShareWithAI(report);
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            animate={{ opacity: 1 }}
            className="fixed inset-0 z-40 bg-black/50"
            exit={{ opacity: 0 }}
            initial={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            animate={{ x: 0 }}
            className="fixed inset-y-0 right-0 z-50 flex w-full flex-col bg-background shadow-2xl md:w-[600px]"
            exit={{ x: "100%" }}
            initial={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b p-4">
              <div>
                <h2 className="font-semibold text-lg">Research Report</h2>
                <p className="text-muted-foreground text-sm">
                  {new Date().toLocaleDateString()}
                </p>
              </div>
              <Button onClick={onClose} size="icon" variant="ghost">
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <Streamdown className="prose prose-sm dark:prose-invert max-w-none">
                {report}
              </Streamdown>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap items-center gap-2 border-t p-4">
              <Button
                className="gap-2"
                onClick={handleCopy}
                size="sm"
                variant="outline"
              >
                <Copy className="h-4 w-4" />
                {copied ? "Copied!" : "Copy"}
              </Button>

              <Button
                className="gap-2"
                onClick={handleDownload}
                size="sm"
                variant="outline"
              >
                <Download className="h-4 w-4" />
                Export
              </Button>

              {onShareWithAI && (
                <Button
                  className="ml-auto gap-2"
                  onClick={handleShareWithAI}
                  size="sm"
                  variant="default"
                >
                  <Share2 className="h-4 w-4" />
                  Share with AI
                </Button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
