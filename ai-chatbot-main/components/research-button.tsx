"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { SparklesIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";

export interface ResearchButtonProps {
  prompt: string;
  onStart: (prompt: string) => void;
  disabled?: boolean;
}

export function ResearchButton({
  prompt,
  onStart,
  disabled = false,
}: ResearchButtonProps) {
  const [isStarting, setIsStarting] = useState(false);

  const handleClick = async () => {
    if (isStarting || disabled) return;

    setIsStarting(true);
    try {
      await onStart(prompt);
    } catch (error) {
      console.error("Failed to start research:", error);
      setIsStarting(false);
    }
  };

  return (
    <motion.div
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between gap-3 p-4"
      exit={{ opacity: 0, y: 10 }}
      initial={{ opacity: 0, y: 10 }}
      transition={{ duration: 0.2 }}
    >
      <div className="min-w-0 flex-1">
        <p className="font-medium text-foreground text-sm">
          Start research on this topic?
        </p>
        <p className="mt-1 truncate text-muted-foreground text-xs">{prompt}</p>
      </div>

      <Button
        className="shrink-0 gap-2"
        data-testid="research-button"
        disabled={disabled || isStarting}
        onClick={handleClick}
        size="sm"
        variant="default"
      >
        <SparklesIcon size={14} />
        {isStarting ? "Starting..." : "Start Research"}
      </Button>
    </motion.div>
  );
}
