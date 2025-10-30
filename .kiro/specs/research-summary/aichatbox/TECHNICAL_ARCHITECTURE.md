# Technical Architecture

This document outlines the technical architecture of the "Chat SDK" project, a modern chatbot application built with Next.js and the Vercel AI SDK.

## Frontend Architecture

The frontend is built using Next.js and its App Router, which enables advanced routing and server-side rendering capabilities. The UI is constructed with shadcn/ui, a component library that utilizes Tailwind CSS for styling and Radix UI for accessible and flexible component primitives.

### Key Frontend Components:

*   **`app/layout.tsx`**: The root layout of the application, responsible for setting up the theme, fonts, and session provider.
*   **`app/(chat)/layout.tsx`**: The layout for the chat interface, which includes the application sidebar and a provider for handling data streams.
*   **`app/(chat)/page.tsx`**: The main page for the chat interface, which renders the `<Chat>` component and handles user authentication.
*   **`components/chat.tsx`**: The core component for the chat interface, responsible for displaying messages and handling user input.
*   **`components/data-stream-handler.tsx`**: A component that likely handles the processing of real-time data streams from the AI models.

## Backend Architecture

The backend logic is primarily located in the `lib` directory and is responsible for handling AI model interactions, database operations, and other core functionalities.

### Key Backend Components:

*   **`lib/ai/models.ts`**: Defines the AI models supported by the application, which currently include Grok Vision and Grok Reasoning.
*   **`lib/db/schema.ts`**: Defines the database schema using `drizzle-orm`. The schema includes tables for users, chats, messages, votes, documents, and suggestions.
*   **`lib/auth/auth.ts`**: (Inferred) Handles user authentication and session management using Auth.js.

## API and Data Flow

The application uses API routes within the `app` directory to handle client-server communication. The data flow for a typical chat interaction is as follows:

1.  The user sends a message through the chat interface.
2.  The frontend sends a request to the backend API.
3.  The backend processes the request, interacts with the AI model, and streams the response back to the frontend.
4.  The frontend receives the streamed data and updates the chat interface in real-time.

## Technology Stack

*   **Framework**: Next.js
*   **UI**: shadcn/ui, Tailwind CSS, Radix UI
*   **AI**: Vercel AI SDK, xAI (Grok)
*   **Database**: Neon Serverless Postgres, Drizzle ORM
*   **Authentication**: Auth.js
*   **File Storage**: Vercel Blob