# Quick Reference Guide

This guide provides a quick reference for setting up, running, and customizing the "Chat SDK" project.

## Installation and Setup

1.  **Install Dependencies:**

    ```bash
    pnpm install
    ```

2.  **Configure Environment Variables:**

    Copy the `.env.example` file to a new file named `.env` and fill in the required environment variables. It is recommended to use Vercel Environment Variables for this.

    ```bash
    cp .env.example .env
    ```

## Running the Project

To start the development server, run the following command:

```bash
pnpm dev
```

The application will be available at `http://localhost:3000`.

## Key Scripts

The following are some of the key scripts defined in `package.json`:

*   `dev`: Starts the development server.
*   `build`: Builds the application for production.
*   `start`: Starts the production server.
*   `lint`: Lints the codebase for errors.
*   `format`: Formats the codebase.
*   `db:migrate`: Runs database migrations.
*   `test`: Runs Playwright tests.

## Project Structure

*   **`/app`**: Contains the application's routes, pages, and layouts.
*   **`/components`**: Contains the application's React components.
*   **`/lib`**: Contains the application's backend logic, including AI, database, and authentication code.
*   **`/public`**: Contains the application's static assets.
*   **`/tests`**: Contains the application's tests.