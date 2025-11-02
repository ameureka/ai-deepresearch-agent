import { expect as baseExpect, test as baseTest } from "@playwright/test";
import { getUnixTime } from "date-fns";
import { createAuthenticatedContext, type UserContext } from "./helpers";
import type { ResearchEvent } from "@/hooks/use-research-progress";
import {
  mockResearchEvents,
  mockResearchPrompt,
} from "./fixtures/research";

type Fixtures = {
  adaContext: UserContext;
  babbageContext: UserContext;
  curieContext: UserContext;
  researchPrompt: string;
  researchEvents: ResearchEvent[];
};

export const test = baseTest.extend<object, Fixtures>({
  adaContext: [
    async ({ browser }, use, workerInfo) => {
      const ada = await createAuthenticatedContext({
        browser,
        name: `ada-${workerInfo.workerIndex}-${getUnixTime(new Date())}`,
      });

      await use(ada);
      await ada.context.close();
    },
    { scope: "worker" },
  ],
  babbageContext: [
    async ({ browser }, use, workerInfo) => {
      const babbage = await createAuthenticatedContext({
        browser,
        name: `babbage-${workerInfo.workerIndex}-${getUnixTime(new Date())}`,
      });

      await use(babbage);
      await babbage.context.close();
    },
    { scope: "worker" },
  ],
  curieContext: [
    async ({ browser }, use, workerInfo) => {
      const curie = await createAuthenticatedContext({
        browser,
        name: `curie-${workerInfo.workerIndex}-${getUnixTime(new Date())}`,
      });

      await use(curie);
      await curie.context.close();
    },
    { scope: "worker" },
  ],
  researchPrompt: [
    async ({}, use) => {
      await use(mockResearchPrompt);
    },
    { scope: "test" },
  ],
  researchEvents: [
    async ({}, use) => {
      await use(mockResearchEvents);
    },
    { scope: "test" },
  ],
});

export const expect = baseExpect;
