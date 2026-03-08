# AssignMind Constitution

## Core Principles

### I. Guided Learning Only (NON-NEGOTIABLE)
- The AI must **never** provide direct answers to assignment questions — it exists to guide students through structured thinking
- All AI responses must follow the Prompt Engine pattern: requirements breakdown → step-by-step plan → recommended tools → illustrative scenarios → deliverable criteria
- If a student asks for a direct answer, the AI must reframe the response as guiding questions and reasoning scaffolds
- This principle applies to every AI interaction surface: Personal Agent, Team Supervisor Agent, and assignment analysis
- **Violation of this principle is a critical defect — treat as P0**

### II. Secrets Never Touch the Client (NON-NEGOTIABLE)
- No API keys, tokens, database credentials, or secrets of any kind in client-side code — ever
- All sensitive values must live in server-side environment variables (`ANTHROPIC_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `LEMON_SQUEEZY_API_KEY`, etc.)
- Next.js environment variables exposed to the client (`NEXT_PUBLIC_*`) must contain only non-sensitive, public-facing values (e.g., Supabase anon key, public URLs)
- Server-side secrets must never be logged, serialized to responses, or included in error messages returned to the client
- **Any PR that introduces a secret in client-accessible code must be rejected immediately**

### III. Input Sanitization Everywhere (NON-NEGOTIABLE)
- All user inputs must be sanitized before processing — no exceptions
- **XSS prevention:** Sanitize and escape all user-generated content before rendering (assignment text, chat messages, workspace names, member names)
- **SQL injection prevention:** Use parameterized queries exclusively — never construct SQL strings via concatenation or f-strings; Supabase client and SQLAlchemy ORM must always be used with bound parameters
- **AI prompt injection prevention:** User inputs embedded into prompt templates must be clearly delimited and treated as untrusted data
- Validation must occur at both the API boundary (FastAPI request models via Pydantic) and the frontend form layer

### IV. AI Service Layer Isolation (NON-NEGOTIABLE)
- All Anthropic Claude API calls must go through a dedicated service layer (e.g., `services/ai_service.py`) — never called directly from route handlers
- The service layer is responsible for: prompt template selection, context injection, token budget enforcement, credit deduction, response parsing, and error handling
- Route handlers receive processed, structured results from the service layer — they never construct prompts or interpret raw AI responses
- This isolation enables: centralized rate limiting, consistent credit accounting, prompt versioning, and AI provider swapability
- The service layer must enforce the credit cost table (upload analysis = 10, chat message = 2, task distribution = 5, background update = 1) before making any API call

### V. Authentication on Every Endpoint (NON-NEGOTIABLE)
- Every API endpoint must validate authentication before executing any business logic
- Supabase Auth JWT tokens must be verified server-side on each request — no endpoint is implicitly trusted
- Authorization must also be scoped: users can only access workspaces they belong to, and only team leaders can perform leader-restricted actions (finalize task distribution, modify workspace settings)
- Unauthenticated or unauthorized requests must return appropriate HTTP status codes (`401` / `403`) with no data leakage
- WebSocket connections (Supabase Realtime) must also verify authentication on connection establishment

### VI. TypeScript Strict Mode (NON-NEGOTIABLE)
- The frontend must run with TypeScript strict mode enabled (`"strict": true` in `tsconfig.json`)
- No `any` type — implicit or explicit — is permitted; all variables, parameters, return types, and props must be explicitly typed
- API response types must be defined as TypeScript interfaces that mirror the FastAPI Pydantic response models
- Shared types (Credit balances, Workspace models, Task models, Agent message formats) must live in a dedicated `types/` directory
- **Any PR that introduces `any` or disables a strict-mode check must be rejected**

### VII. Function Size Limit — 50 Lines Max (NON-NEGOTIABLE)
- No function or method may exceed 50 lines of code — if it does, it must be decomposed into smaller, well-named helper functions
- This applies to both frontend (TypeScript/React components) and backend (Python/FastAPI handlers and services)
- React components rendering complex UI must extract sub-sections into child components
- FastAPI route handlers must delegate to service functions; service functions must delegate to focused utility functions
- This constraint ensures readability, testability, and maintainability across the entire codebase

### VIII. Process Once, Store Structured (NON-NEGOTIABLE)
- Assignment documents (PDF or text) are processed **once** upon upload — parsed into a structured summary and stored in the database
- Subsequent AI interactions reference the stored structured summary — the raw document is never re-sent to the AI API
- This saves ~70% on token costs and ensures consistent context across all agent interactions within a workspace
- The structured summary must include: extracted requirements, identified constraints, deliverable expectations, and deadline information
- If the original document is updated, a new processing cycle is triggered and the stored summary is versioned

## Security & Privacy Standards

- **Data minimization:** Collect and store only the data necessary for platform functionality
- **Right to erasure:** Users can request deletion of their account and all associated data (assignment content, chat history, workspace membership)
- **Transparent AI data usage:** Terms of Service must clearly state that assignment content is sent to Anthropic's Claude API for processing; no assignment data is retained by the AI provider beyond the API request scope
- **Phone verification:** Required on registration to prevent duplicate accounts and abuse of the 30 free Credits
- **Credit isolation:** Credit balances are per-user, never shared with teams — the system must never allow one user to spend another user's credits
- **CORS policy:** Backend must whitelist only the production frontend domain and local development origin — no wildcard origins in production
- **Rate limiting:** API endpoints must enforce rate limits to prevent abuse, especially on AI-consuming routes (chat, analysis, task distribution)
- **Dependency auditing:** All npm and pip dependencies must be regularly audited for known vulnerabilities (`npm audit`, `pip-audit`)

## Code Quality & Development Standards

- **Pydantic for all API contracts:** Every FastAPI request and response must use Pydantic models — no raw `dict` returns
- **Component-driven frontend:** UI must be built from reusable, typed React components — no monolithic page files
- **Consistent error handling:** All API errors must return a standardized error envelope (`{ "error": { "code": string, "message": string } }`) — never expose stack traces or internal details to the client
- **Environment parity:** Local development must mirror production configuration as closely as possible (same database schema, same auth flow, same environment variable names)
- **Multi-language support:** AI responses must auto-detect user language (Arabic or English) and respond accordingly; UI text must support RTL layout for Arabic
- **Git hygiene:** Feature branches, descriptive commit messages, no direct pushes to `main`
- **Logging:** Structured logging on the backend (JSON format) with correlation IDs per request; no sensitive data in logs

## Governance

- This Constitution supersedes all other development practices, conventions, and ad-hoc decisions
- Every code review must verify compliance with all NON-NEGOTIABLE principles — non-compliant code must not be merged
- Amendments to this Constitution require: documented rationale, team review, and an updated version number
- When a principle conflicts with a feature deadline, **the principle wins** — shortcuts that violate the Constitution create technical and security debt that compounds
- Use the SRS (`srs.md`) as the source of truth for feature scope and business logic; use this Constitution as the source of truth for how code is written and structured

**Version**: 1.0.0 | **Ratified**: 2026-03-06 | **Last Amended**: 2026-03-06