import { createDeepSeek } from "@ai-sdk/deepseek";
import {
  customProvider,
  extractReasoningMiddleware,
  wrapLanguageModel,
} from "ai";
import { isTestEnvironment } from "../constants";

// Create DeepSeek provider using official AI SDK provider
const deepseek = createDeepSeek({
  apiKey: process.env.DEEPSEEK_API_KEY || "",
});

export const myProvider = isTestEnvironment
  ? (() => {
      const {
        artifactModel,
        chatModel,
        reasoningModel,
        titleModel,
      } = require("./models.mock");
      return customProvider({
        languageModels: {
          "chat-model": chatModel,
          "chat-model-reasoning": reasoningModel,
          "title-model": titleModel,
          "artifact-model": artifactModel,
        },
      });
    })()
  : customProvider({
      languageModels: {
        // Use DeepSeek for all models (unified architecture)
        "chat-model": deepseek("deepseek-chat"),
        "chat-model-reasoning": wrapLanguageModel({
          model: deepseek("deepseek-reasoner"),
          middleware: extractReasoningMiddleware({ tagName: "think" }),
        }),
        "title-model": deepseek("deepseek-chat"),
        "artifact-model": deepseek("deepseek-chat"),
      },
    });
