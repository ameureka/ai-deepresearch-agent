```
/Users/ameureka/Desktop/agentic-ai-public-main/achive/ai-chatbot-main/
├── .cursor/
│   └── rules/
│       └── ultracite.mdc
├── .env.example
├── .github/
│   └── workflows/
│       ├── lint.yml
│       └── playwright.yml
├── .gitignore
├── .vscode/
│   ├── extensions.json
│   └── settings.json
├── LICENSE
├── README.md
├── app/
│   ├── (auth)/
│   │   ├── actions.ts
│   │   ├── api/
│   │   ├── auth.config.ts
│   │   ├── auth.ts
│   │   ├── login/
│   │   └── register/
│   ├── (chat)/
│   │   ├── actions.ts
│   │   ├── api/
│   │   ├── chat/
│   │   ├── layout.tsx
│   │   ├── opengraph-image.png
│   │   ├── page.tsx
│   │   └── twitter-image.png
│   ├── favicon.ico
│   ├── globals.css
│   └── layout.tsx
├── artifacts/
│   ├── actions.ts
│   ├── code/
│   │   ├── client.tsx
│   │   └── server.ts
│   ├── image/
│   │   └── client.tsx
│   ├── sheet/
│   │   ├── client.tsx
│   │   └── server.ts
│   └── text/
│       ├── client.tsx
│       └── server.ts
├── biome.jsonc
├── components.json
├── components/
│   ├── app-sidebar.tsx
│   ├── artifact-actions.tsx
│   ├── artifact-close-button.tsx
│   ├── artifact-messages.tsx
│   ├── artifact.tsx
│   ├── auth-form.tsx
│   ├── chat-header.tsx
│   ├── chat.tsx
│   ├── code-editor.tsx
│   ├── console.tsx
│   ├── create-artifact.tsx
│   ├── data-stream-handler.tsx
│   ├── data-stream-provider.tsx
│   ├── diffview.tsx
│   ├── document-preview.tsx
│   ├── document-skeleton.tsx
│   ├── document.tsx
│   ├── elements/
│   │   ├── actions.tsx
│   │   ├── branch.tsx
│   │   ├── code-block.tsx
│   │   ├── context.tsx
│   │   ├── conversation.tsx
│   │   ├── image.tsx
│   │   ├── inline-citation.tsx
│   │   ├── loader.tsx
│   │   ├── message.tsx
│   │   ├── prompt-input.tsx
│   │   ├── reasoning.tsx
│   │   ├── response.tsx
│   │   ├── source.tsx
│   │   ├── suggestion.tsx
│   │   ├── task.tsx
│   │   ├── tool.tsx
│   │   └── web-preview.tsx
│   ├── greeting.tsx
│   ├── icons.tsx
│   ├── image-editor.tsx
│   ├── message-actions.tsx
│   ├── message-editor.tsx
│   ├── message-reasoning.tsx
│   ├── message.tsx
│   ├── messages.tsx
│   ├── model-selector.tsx
│   ├── multimodal-input.tsx
│   ├── preview-attachment.tsx
│   ├── sheet-editor.tsx
│   ├── sidebar-history-item.tsx
│   ├── sidebar-history.tsx
│   ├── sidebar-toggle.tsx
│   ├── sidebar-user-nav.tsx
│   ├── sign-out-form.tsx
│   ├── submit-button.tsx
│   ├── suggested-actions.tsx
│   ├── suggestion.tsx
│   ├── text-editor.tsx
│   ├── theme-provider.tsx
│   ├── toast.tsx
│   ├── toolbar.tsx
│   ├── ui/
│   │   ├── alert-dialog.tsx
│   │   ├── avatar.tsx
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── carousel.tsx
│   │   ├── collapsible.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── hover-card.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── progress.tsx
│   │   ├── scroll-area.tsx
│   │   ├── select.tsx
│   │   ├── separator.tsx
│   │   ├── sheet.tsx
│   │   ├── sidebar.tsx
│   │   ├── skeleton.tsx
│   │   ├── textarea.tsx
│   │   └── tooltip.tsx
│   ├── version-footer.tsx
│   ├── visibility-selector.tsx
│   └── weather.tsx
├── drizzle.config.ts
├── hooks/
│   ├── use-artifact.ts
│   ├── use-auto-resume.ts
│   ├── use-chat-visibility.ts
│   ├── use-messages.tsx
│   ├── use-mobile.ts
│   └── use-scroll-to-bottom.tsx
├── instrumentation.ts
├── lib/
│   ├── ai/
│   │   ├── entitlements.ts
│   │   ├── models.mock.ts
│   │   ├── models.test.ts
│   │   ├── models.ts
│   │   ├── prompts.ts
│   │   ├── providers.ts
│   │   └── tools/
│   ├── artifacts/
│   │   └── server.ts
│   ├── constants.ts
│   ├── db/
│   │   ├── helpers/
│   │   ├── migrate.ts
│   │   ├── migrations/
│   │   ├── queries.ts
│   │   ├── schema.ts
│   │   └── utils.ts
│   ├── editor/
│   │   ├── config.ts
│   │   ├── diff.js
│   │   ├── functions.tsx
│   │   ├── react-renderer.tsx
│   │   └── suggestions.tsx
│   ├── errors.ts
│   ├── types.ts
│   ├── usage.ts
│   └── utils.ts
├── middleware.ts
├── next-env.d.ts
├── next.config.ts
├── package.json
├── playwright.config.ts
├── pnpm-lock.yaml
├── postcss.config.mjs
├── public/
│   └── images/
│       ├── demo-thumbnail.png
│       └── mouth of the seine, monet.jpg
├── tests/
│   ├── e2e/
│   │   ├── artifacts.test.ts
│   │   ├── chat.test.ts
│   │   ├── reasoning.test.ts
│   │   └── session.test.ts
│   ├── fixtures.ts
│   ├── helpers.ts
│   ├── pages/
│   │   ├── artifact.ts
│   │   ├── auth.ts
│   │   └── chat.ts
│   ├── prompts/
│   │   ├── basic.ts
│   │   ├── routes.ts
│   │   └── utils.ts
│   └── routes/
│       ├── chat.test.ts
│       └── document.test.ts
├── tsconfig.json
└── vercel-template.json
```