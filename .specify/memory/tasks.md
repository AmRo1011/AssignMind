# AssignMind — MVP Development Tasks
**Version:** 1.0 | **Date:** 2026-03-06  
**Source:** [plan.md](file:///d:/AssignMind/.specify/memory/plan.md) · [specification.md](file:///d:/AssignMind/.specify/memory/specification.md) · [constitution.md](file:///d:/AssignMind/.specify/memory/constitution.md)  
**Scope:** Phase 1 MVP (Weeks 1–3)

---

## Legend

- **[P]** = Can run in parallel with other [P] tasks in the same phase
- **Depends:** = Must be completed before this task can start
- **Files:** = Files to create or modify
- **Test:** = How to verify the task is complete
- **Est:** = Estimated time (max 4 hours)

---

## Phase 1: Project Setup & Infrastructure

### T1.1 — Initialize Backend Project [P]
**Est:** 2h  
**Files:**
- `backend/main.py`
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/database.py`

**Work:**
1. Create `backend/` directory structure
2. Initialize FastAPI app with CORS (whitelist `FRONTEND_URL`)
3. Set up Pydantic `Settings` class loading all env vars from `.env`
4. Configure async SQLAlchemy engine + session factory (`asyncpg`)
5. Add health check endpoint at `GET /api/health`
6. Create `requirements.txt` with pinned versions: `fastapi`, `uvicorn`, `sqlalchemy[asyncio]`, `asyncpg`, `pydantic-settings`, `python-dotenv`, `alembic`

**Test:** `uvicorn main:app --reload` starts successfully; `GET /api/health` returns `200 OK`

---

### T1.2 — Initialize Frontend Project [P]
**Est:** 2h  
**Files:**
- `frontend/package.json`
- `frontend/next.config.js`
- `frontend/tsconfig.json` (strict: true)
- `frontend/tailwind.config.ts`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/globals.css`
- `frontend/.env.example`

**Work:**
1. `npx -y create-next-app@latest ./` with TypeScript, Tailwind, App Router, src directory
2. Enable `"strict": true` in `tsconfig.json` — verify no `any` types (Constitution §VI)
3. Configure Tailwind with custom theme colors
4. Set up root layout with Inter/Outfit font from Google Fonts
5. Add RTL support via `dir` attribute on `<html>` (Constitution — multi-language)
6. Create `.env.example` with all `NEXT_PUBLIC_*` vars

**Test:** `npm run dev` starts; homepage renders at `localhost:3000`; `npm run build` has zero TS errors

---

### T1.3 — Database Migrations Setup
**Est:** 1.5h  
**Depends:** T1.1  
**Files:**
- `backend/alembic.ini`
- `backend/alembic/env.py`

**Work:**
1. Initialize Alembic with `alembic init alembic`
2. Configure `env.py` to use async engine from `app/database.py`
3. Point Alembic at `DATABASE_URL` from settings
4. Verify migration generation works with a test model

**Test:** `alembic revision --autogenerate -m "init"` generates a migration file; `alembic upgrade head` runs without errors

---

### T1.4 — Create All Database Models & Initial Migration
**Est:** 4h  
**Depends:** T1.3  
**Files:**
- `backend/app/models/__init__.py`
- `backend/app/models/user.py`
- `backend/app/models/workspace.py`
- `backend/app/models/workspace_member.py`
- `backend/app/models/invitation.py`
- `backend/app/models/assignment.py`
- `backend/app/models/task.py`
- `backend/app/models/chat_message.py`
- `backend/app/models/credit_transaction.py`
- `backend/app/models/scheduled_email.py`
- `backend/app/models/payment_transaction.py`

**Work:**
1. Create all 11 SQLAlchemy ORM models matching the schema in `plan.md §2`
2. Include all constraints, indexes, CHECK constraints, and foreign keys
3. Include the `credits` table with `balance`, `reserved`, and `CHECK (reserved <= balance)`
4. Generate and apply Alembic migration

**Test:** `alembic upgrade head` creates all 11 tables in PostgreSQL; verify with `\dt` in psql

---

### T1.5 — Shared Utilities: Sanitization, Auth, Rate Limiting [P]
**Est:** 3h  
**Depends:** T1.1  
**Files:**
- `backend/app/utils/__init__.py`
- `backend/app/utils/sanitize.py`
- `backend/app/utils/auth.py`
- `backend/app/utils/rate_limit.py`
- `backend/app/utils/datetime_utils.py`

**Work:**
1. `sanitize.py`: XSS sanitizer using `bleach.clean()`, SQL injection prevention notes (ORM-only), prompt injection delimiter function
2. `auth.py`: JWT verification using `SUPABASE_JWT_SECRET`, decode and validate `exp`, `sub` claims
3. `rate_limit.py`: Decorator/middleware for rate limiting (in-memory with `defaultdict` for MVP; Redis-ready interface)
4. `datetime_utils.py`: UTC helpers, timezone conversion via `zoneinfo`

**Test:** Unit tests for sanitize (strips `<script>` tags), JWT verification (valid/invalid tokens), rate limiter (blocks after threshold)

---

### T1.6 — FastAPI Dependencies & Common Schemas
**Est:** 2h  
**Depends:** T1.4, T1.5  
**Files:**
- `backend/app/dependencies.py`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/common.py`

**Work:**
1. `dependencies.py`: `get_db()` (async session), `get_current_user()` (JWT → User), `require_verified_user()` (phone check), `require_workspace_member(workspace_id)`, `require_team_leader(workspace_id)`
2. `schemas/common.py`: `ErrorResponse`, `PaginationParams`, `PaginatedResponse[T]`

**Test:** Dependencies resolve correctly in a test route; `ErrorResponse` validates

---

### T1.7 — Frontend Core Libraries & Providers [P]
**Est:** 3h  
**Depends:** T1.2  
**Files:**
- `frontend/src/lib/supabase.ts`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/sanitize.ts`
- `frontend/src/lib/datetime.ts`
- `frontend/src/lib/constants.ts`
- `frontend/src/providers/AuthProvider.tsx`
- `frontend/src/providers/ToastProvider.tsx`
- `frontend/src/types/api.ts`

**Work:**
1. `supabase.ts`: Initialize Supabase client with `NEXT_PUBLIC_SUPABASE_URL` + anon key
2. `api.ts`: Fetch wrapper that injects `Authorization: Bearer <token>` from Supabase session, standardized error handling
3. `sanitize.ts`: Client-side XSS sanitization for user inputs
4. `datetime.ts`: Format UTC timestamps to local timezone via `Intl.DateTimeFormat`
5. `constants.ts`: `CHAT_POLL_INTERVAL`, `LOW_CREDIT_THRESHOLD`, `MAX_WORKSPACE_MEMBERS`
6. `AuthProvider.tsx`: Supabase auth session listener, exposes `user`, `session`, `isLoading`
7. `types/api.ts`: `ErrorResponse`, `PaginatedResponse<T>`

**Test:** Supabase client initializes; API wrapper adds auth header; datetime formats correctly

---

### T1.8 — Frontend UI Component Library [P]
**Est:** 3h  
**Depends:** T1.2  
**Files:**
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/Input.tsx`
- `frontend/src/components/ui/Modal.tsx`
- `frontend/src/components/ui/Badge.tsx`
- `frontend/src/components/ui/Card.tsx`
- `frontend/src/components/ui/Avatar.tsx`
- `frontend/src/components/ui/Spinner.tsx`
- `frontend/src/components/ui/Toast.tsx`
- `frontend/src/components/ui/EmptyState.tsx`

**Work:**
1. Build reusable, typed UI primitives with Tailwind styling
2. All props must be explicitly typed — no `any` (Constitution §VI)
3. Each component ≤ 50 lines (Constitution §VII)
4. Include hover states, focus rings, disabled states, loading states

**Test:** Each component renders without TS errors; visual review in Storybook or a test page

---

## Phase 2: Authentication & User Management

### T2.1 — Backend Auth Routes
**Est:** 3h  
**Depends:** T1.6  
**Files:**
- `backend/app/routers/auth.py`
- `backend/app/services/user_service.py`
- `backend/app/schemas/user.py`

**Work:**
1. `POST /api/auth/callback`: Receive Supabase user data, upsert into `users` table
2. `POST /api/auth/verify-phone`: Accept OTP, verify phone, check uniqueness, activate account, grant 30 free credits
3. `POST /api/auth/resend-otp`: Rate-limited (3/10min per phone)
4. `GET /api/auth/me`: Return user profile + verification status
5. `user_service.py`: `create_or_update_user()`, `verify_phone()`, `grant_free_credits()`

**Test:** API tests: callback creates user, verify-phone activates + grants credits, duplicate phone rejected, rate limit enforced

---

### T2.2 — Backend User Profile & Account Deletion
**Est:** 2h  
**Depends:** T2.1  
**Files:**
- `backend/app/routers/users.py`
- Modify `backend/app/services/user_service.py`

**Work:**
1. `GET /api/users/me`: Profile with credit balance
2. `PATCH /api/users/me`: Update name, timezone
3. `POST /api/users/me/delete`: Deactivate account, set `deactivated_at`, anonymize chat messages, mark tasks unassigned, transfer leadership
4. `POST /api/users/me/reactivate`: Re-enable if within 14-day grace period

**Test:** Profile returns correct data; deletion cascades correctly (chat anonymized, tasks unassigned, leader transferred); reactivation works within grace period

---

### T2.3 — Frontend Login & OAuth Flow [P]
**Est:** 3h  
**Depends:** T1.7  
**Files:**
- `frontend/src/app/(auth)/login/page.tsx`
- `frontend/src/app/(auth)/callback/page.tsx`
- `frontend/src/app/api/auth/callback/route.ts`
- `frontend/src/hooks/useAuth.ts`

**Work:**
1. Login page with Google + GitHub OAuth buttons
2. Callback handler exchanges code for session
3. `useAuth` hook: login, logout, session state, auto-redirect based on verification status
4. Redirect unverified users to phone verification

**Test:** Clicking Google/GitHub initiates OAuth; callback sets session; unverified user redirected to `/verify-phone`

---

### T2.4 — Frontend Phone Verification
**Est:** 2h  
**Depends:** T2.3  
**Files:**
- `frontend/src/app/(auth)/verify-phone/page.tsx`
- `frontend/src/types/user.ts`

**Work:**
1. Phone number input with country code selector
2. OTP input (6 digits) with auto-focus
3. Resend OTP button with countdown timer (disabled during cooldown)
4. Success → redirect to dashboard
5. Error handling: duplicate phone, invalid OTP, expired OTP

**Test:** Phone input validates format; OTP submits correctly; success redirects; errors display

---

### T2.5 — Frontend Auth Middleware & Dashboard Layout
**Est:** 2.5h  
**Depends:** T2.3  
**Files:**
- `frontend/middleware.ts`
- `frontend/src/app/(dashboard)/layout.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/layout/CreditBadge.tsx`

**Work:**
1. Middleware: redirect unauthenticated users to `/login`; redirect unverified to `/verify-phone`
2. Dashboard layout: sidebar (workspace list, credit badge), header (user avatar, logout)
3. `CreditBadge`: Shows credit balance, low-balance warning at ≤10

**Test:** Unauthenticated user can't access `/workspaces`; layout renders with sidebar + header; credit badge shows balance

---

### T2.6 — Frontend User Settings Page
**Est:** 1.5h  
**Depends:** T2.5  
**Files:**
- `frontend/src/app/(dashboard)/settings/page.tsx`

**Work:**
1. Profile edit form (name, timezone selector)
2. Account deletion section with confirmation modal + 14-day warning
3. Reactivation button (shown during grace period)

**Test:** Name update saves; deletion shows confirmation; reactivation within grace period works

---

## Phase 3: Assignment Upload & AI Analysis

### T3.1 — AI Service Layer & Prompt Engine
**Est:** 4h  
**Depends:** T1.6  
**Files:**
- `backend/app/services/ai_service.py`
- `backend/app/prompts/__init__.py`
- `backend/app/prompts/assignment_analysis.py`
- `backend/app/prompts/task_distribution.py`
- `backend/app/prompts/validation.py`

**Work:**
1. `AIService` class with `analyze_assignment()` and `generate_task_distribution()`
2. Assignment analysis prompt template with guided-learning guardrails + language detection
3. Task distribution prompt template with member/constraint injection
4. Keyword validation: regex patterns for violation detection, reinforced prompt suffix
5. Validation flow: check → retry once → fallback → log
6. All user inputs delimited with `<assignment_document>` tags (Constitution §III)

**Test:** Unit tests with mocked Claude responses: valid JSON parsed correctly, violation detected and retried, double-violation returns fallback

---

### T3.2 — PDF Parser & Text Extractor [P]
**Est:** 2h  
**Depends:** T1.1  
**Files:**
- `backend/app/utils/pdf_parser.py`

**Work:**
1. Extract text from PDF using `pdfplumber`
2. Fallback to `pytesseract` for scanned PDFs (OCR)
3. Language detection using `langdetect` library
4. Validation: empty content check (< 50 chars), size limit (10 MB)
5. Sanitize extracted text (strip script tags, SQL fragments)

**Test:** Text PDF returns content; scanned PDF triggers OCR; empty PDF returns error; oversized file rejected

---

### T3.3 — Assignment Upload Endpoint
**Est:** 3h  
**Depends:** T3.1, T3.2  
**Files:**
- `backend/app/routers/assignments.py`
- `backend/app/services/assignment_service.py`
- `backend/app/schemas/assignment.py`

**Work:**
1. `POST /api/workspaces/{id}/assignments`: Accept multipart file upload (PDF/text only)
2. Validate: file type, size, user is Team Leader, rate limit (5/hr)
3. Extract text → sanitize → call `ai_service.analyze_assignment()`
4. Credit flow: reserve 10 → call AI → commit on success / release on failure
5. Store `AssignmentSummary` in `jsonb` column, increment version
6. `GET /api/workspaces/{id}/assignments/latest`: Return structured summary
7. `GET /api/workspaces/{id}/assignments`: List all versions

**Test:** PDF upload returns structured summary; text upload works; non-leader gets 403; insufficient credits gets 402; rate limit returns 429

---

### T3.4 — Frontend Assignment Upload & Summary View
**Est:** 3h  
**Depends:** T3.3, T2.5  
**Files:**
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/assignment/page.tsx`
- `frontend/src/components/assignment/UploadForm.tsx`
- `frontend/src/components/assignment/StructuredSummaryView.tsx`
- `frontend/src/types/assignment.ts`
- `frontend/src/hooks/useWorkspace.ts`

**Work:**
1. Upload form: drag-and-drop zone, file type validation, credit cost warning
2. Loading state during AI processing (can take 10-30s)
3. Structured summary view: render `requirements`, `constraints`, `deliverables`, `deadlines`, `tools` in organized cards
4. Show upload button only to Team Leader
5. Version history dropdown

**Test:** File upload works; loading spinner during AI processing; summary renders all 5 sections; non-leader doesn't see upload button

---

## Phase 4: Workspace & Task Distribution

### T4.1 — Workspace CRUD Backend
**Est:** 3h  
**Depends:** T1.6  
**Files:**
- `backend/app/routers/workspaces.py`
- `backend/app/services/workspace_service.py`
- `backend/app/schemas/workspace.py`

**Work:**
1. `POST /api/workspaces`: Create workspace, creator becomes leader
2. `GET /api/workspaces`: List user's active (non-archived) workspaces
3. `GET /api/workspaces/{id}`: Get workspace details (members, role)
4. `PATCH /api/workspaces/{id}`: Update title/description/deadline (leader only)
5. `POST /api/workspaces/{id}/archive`: Archive workspace (leader only)
6. `POST /api/workspaces/{id}/transfer-leadership`: Transfer role (leader only)
7. `DELETE /api/workspaces/{id}/members/{userId}`: Remove member (leader only)
8. `GET /api/workspaces/{id}/members`: List members with roles

**Test:** CRUD operations work; non-members get 403; archive hides from list; leadership transfer updates roles

---

### T4.2 — Invitation System Backend
**Est:** 3h  
**Depends:** T4.1  
**Files:**
- `backend/app/routers/invitations.py`
- `backend/app/services/invitation_service.py`
- `backend/app/schemas/invitation.py`

**Work:**
1. `POST /api/workspaces/{id}/invitations`: Invite by email (leader only, max 10 members)
2. `GET /api/invitations/pending`: List user's pending invitations
3. `POST /api/invitations/{id}/accept`: Join workspace
4. `POST /api/invitations/{id}/decline`: Decline + notify leader
5. Duplicate invite check, self-invite check
6. Auto-accept logic for new users registering with invited email (hook into `user_service`)

**Test:** Invite creates record; 11th member rejected; accept adds to workspace; decline notifies; duplicate silently ignored

---

### T4.3 — Task Distribution Endpoint
**Est:** 3h  
**Depends:** T3.1, T4.1  
**Files:**
- `backend/app/routers/tasks.py`
- `backend/app/services/task_service.py`
- `backend/app/schemas/task.py`

**Work:**
1. `POST /api/workspaces/{id}/tasks/distribute`: Generate AI distribution (leader only, rate limit 3/hr, cost 5 credits)
2. Accept `constraints` array in request body (auto-extracted + manual)
3. Credit flow: reserve 5 → call AI → commit/release
4. `POST /api/workspaces/{id}/tasks/finalize`: Bulk-create tasks from approved distribution
5. `POST /api/workspaces/{id}/tasks`: Create single ad-hoc task (leader only)
6. `GET /api/workspaces/{id}/tasks`: List all tasks for board

**Test:** Distribution returns task proposals; finalization creates tasks; constraints are passed to AI; insufficient credits blocks; rate limit enforced

---

### T4.4 — Frontend Workspace List & Creation
**Est:** 2.5h  
**Depends:** T4.1, T2.5  
**Files:**
- `frontend/src/app/(dashboard)/page.tsx`
- `frontend/src/app/(dashboard)/workspaces/new/page.tsx`
- `frontend/src/components/workspace/WorkspaceCard.tsx`
- `frontend/src/components/layout/InvitationBanner.tsx`
- `frontend/src/hooks/useInvitations.ts`
- `frontend/src/types/workspace.ts`

**Work:**
1. Dashboard: list workspace cards, pending invitation banners, credit balance
2. Create workspace form: title (required), description (optional), deadline (optional)
3. Workspace card: title, member count, deadline, role badge
4. Invitation banner: accept/decline buttons

**Test:** Workspaces listed; creation works; invitations shown; accept/decline updates list

---

### T4.5 — Frontend Workspace Layout & Settings
**Est:** 3h  
**Depends:** T4.4  
**Files:**
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/layout.tsx`
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/page.tsx`
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/settings/page.tsx`
- `frontend/src/components/workspace/MemberList.tsx`
- `frontend/src/components/workspace/InviteMemberForm.tsx`
- `frontend/src/components/workspace/TransferLeadershipModal.tsx`
- `frontend/src/types/invitation.ts`

**Work:**
1. Workspace layout with tabs: Board, Chat, Assignment, Settings
2. Settings page: member list, invite form (email input), transfer leadership modal, archive button
3. Show leader-only actions conditionally
4. Member removal with confirmation

**Test:** Tab navigation works; invite sends email; transfer updates roles; archive hides workspace

---

### T4.6 — Frontend Task Distribution Flow
**Est:** 3h  
**Depends:** T4.3, T3.4  
**Files:**
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/distribute/page.tsx`
- `frontend/src/components/distribution/DistributionReview.tsx`
- `frontend/src/components/distribution/TaskAssignmentCard.tsx`
- `frontend/src/components/distribution/ConstraintsList.tsx`
- `frontend/src/components/assignment/ConstraintsEditor.tsx`

**Work:**
1. Constraints editor: display auto-extracted constraints as editable chips, add/remove manual constraints
2. "Generate Distribution" button with credit cost warning (5 credits)
3. Loading state during AI call
4. Review screen: list proposed tasks with editable title, description, assignee, deadline
5. "Finalize" button → creates tasks on board
6. Warning for uneven distribution

**Test:** Constraints editable; distribution generates; tasks reviewable/editable; finalization creates board tasks

---

## Phase 5: Kanban Board

### T5.1 — Task Status Update Endpoint
**Est:** 2h  
**Depends:** T4.3  
**Files:**
- Modify `backend/app/routers/tasks.py`
- Modify `backend/app/services/task_service.py`

**Work:**
1. `PATCH /api/workspaces/{id}/tasks/{taskId}/status`: Update status (todo ↔ in_progress ↔ done)
2. Authorization: only assigned user OR team leader can update
3. `PATCH /api/workspaces/{id}/tasks/{taskId}`: Update title/description/deadline/assignee (leader only for assignee)
4. `DELETE /api/workspaces/{id}/tasks/{taskId}`: Delete task (leader only)
5. Trigger Supervisor Agent message on status change (calls chat_service — T6.1)

**Test:** Owner can update own task; non-owner gets 403; leader can update any; status changes persist

---

### T5.2 — Frontend Kanban Board
**Est:** 4h  
**Depends:** T5.1, T4.5  
**Files:**
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/board/page.tsx`
- `frontend/src/components/board/KanbanBoard.tsx`
- `frontend/src/components/board/KanbanColumn.tsx`
- `frontend/src/components/board/TaskCard.tsx`
- `frontend/src/components/board/AddTaskModal.tsx`
- `frontend/src/components/board/OverdueIndicator.tsx`
- `frontend/src/hooks/useTasks.ts`
- `frontend/src/types/task.ts`

**Work:**
1. Three-column layout: To Do, In Progress, Done
2. Task cards: title, assignee avatar, deadline (local timezone), overdue indicator (red badge)
3. Drag-and-drop between columns (or click-to-move buttons for MVP simplicity)
4. Authorization: disable drag for tasks not owned by current user (unless leader)
5. Add Task button (leader only) → modal with title, description, assignee dropdown, deadline picker
6. Manual refresh button (no auto-refresh — Decision Q5)

**Test:** Tasks render in correct columns; drag/move updates status; overdue tasks show red badge; non-owner can't move others' tasks; leader can move any

---

## Phase 6: Group Chat & Supervisor Agent

### T6.1 — Chat Backend & Supervisor Agent
**Est:** 3h  
**Depends:** T1.6  
**Files:**
- `backend/app/routers/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/schemas/chat.py`

**Work:**
1. `POST /api/workspaces/{id}/chat`: Send human message (sanitize content, max 5000 chars)
2. `GET /api/workspaces/{id}/chat?after=<timestamp>&limit=50`: Paginated messages (supports polling)
3. `chat_service.post_agent_message()`: Template-based Supervisor Agent messages for task status changes
4. Agent message batching: if agent posted in last 5 min, update that message instead of creating new
5. Empty/whitespace messages rejected
6. Sender name denormalized for deleted/removed users

**Test:** Human message saved; polling returns new messages since timestamp; agent message posted on task change; batch within 5 min; empty message rejected

---

### T6.2 — Frontend Group Chat
**Est:** 3.5h  
**Depends:** T6.1, T4.5  
**Files:**
- `frontend/src/app/(dashboard)/workspaces/[workspaceId]/chat/page.tsx`
- `frontend/src/components/chat/ChatWindow.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/AgentMessageBubble.tsx`
- `frontend/src/components/chat/ChatInput.tsx`
- `frontend/src/components/chat/PollingProvider.tsx`
- `frontend/src/hooks/useChat.ts`
- `frontend/src/types/chat.ts`

**Work:**
1. Chat window: message list (newest at bottom), auto-scroll on new messages
2. Human messages: avatar, name, content, timestamp (local timezone)
3. Agent messages: distinct bot avatar + "Bot" badge, different background color
4. Chat input: text area, send button, empty validation
5. 30-second polling via `setInterval` with `?after=` parameter
6. Load older messages on scroll-up (pagination)

**Test:** Messages render; polling fetches new messages every 30s; agent messages visually distinct; send works; empty message blocked

---

## Phase 7: Email Notifications

### T7.1 — Email Service & Templates
**Est:** 3h  
**Depends:** T1.1  
**Files:**
- `backend/app/services/email_service.py`
- `frontend/emails/WelcomeEmail.tsx`
- `frontend/emails/VerificationEmail.tsx`
- `frontend/emails/InvitationEmail.tsx`
- `frontend/emails/PaymentConfirmationEmail.tsx`
- `frontend/emails/DeadlineReminderEmail.tsx`
- `frontend/emails/DeadlineMissedEmail.tsx`
- `frontend/emails/AccountDeletionEmail.tsx`
- `frontend/emails/DeletionFinalEmail.tsx`

**Work:**
1. `email_service.py`: Resend API wrapper with `send_email(to, template, data)`, exponential retry (3 attempts max)
2. React Email templates with AssignMind branding
3. Deadline emails: convert UTC deadline to recipient's timezone
4. No sensitive data in any email (Constitution §II)

**Test:** Resend API call formats correctly; templates render valid HTML; timezone conversion correct

---

### T7.2 — Immediate Email Triggers
**Est:** 2h  
**Depends:** T7.1, T2.1, T4.2  
**Files:**
- Modify `backend/app/services/user_service.py` (N-1, N-2)
- Modify `backend/app/services/invitation_service.py` (N-4)

**Work:**
1. Hook registration → send verification email (N-1)
2. Hook phone verification → send welcome email (N-2)
3. Hook invitation → send invitation email (N-4)
4. Payment confirmation email (N-3) — wired in T8.2

**Test:** Registration triggers email; verification triggers welcome; invitation triggers invite email (verify via Resend logs or mock)

---

### T7.3 — Deadline Checker Cron Job
**Est:** 3h  
**Depends:** T7.1, T5.1  
**Files:**
- `backend/app/jobs/__init__.py`
- `backend/app/jobs/deadline_checker.py`
- `backend/app/jobs/email_sender.py`
- Modify `backend/main.py` (add APScheduler)

**Work:**
1. `deadline_checker.py`: Query tasks with upcoming/missed deadlines, insert into `scheduled_emails`
2. `email_sender.py`: Process pending queue, send via Resend, retry with backoff
3. Cancellation logic: cancel emails when task completed, deadline updated, workspace archived
4. Schedule with APScheduler: run every 5 minutes
5. Deduplicate: don't schedule if same type+task already exists

**Test:** Task with deadline in 20h creates `deadline_24h` email; task moved to "done" cancels pending emails; cron runs on interval; retries work

---

### T7.4 — Account Cleanup Cron Job
**Est:** 1.5h  
**Depends:** T2.2, T7.1  
**Files:**
- `backend/app/jobs/account_cleanup.py`
- Modify `backend/main.py`

**Work:**
1. Query users where `is_active = false` and `deactivated_at + 14 days < NOW()`
2. Send final confirmation email 24h before hard deletion
3. Hard-delete: remove user record (cascades to FK-referenced data)
4. Schedule: run daily at 02:00 UTC

**Test:** 15-day-old deactivated account is deleted; 10-day-old account is not; 13-day-old account gets warning email

---

## Phase 8: Credit System & Payments

### T8.1 — Credit Service Backend
**Est:** 3h  
**Depends:** T1.4  
**Files:**
- `backend/app/services/credit_service.py`
- `backend/app/routers/credits.py`
- `backend/app/schemas/credit.py`

**Work:**
1. `CreditService`: `reserve_credits()`, `commit_reservation()`, `release_reservation()` — all with `SELECT ... FOR UPDATE` row-level locking
2. `grant_free_credits()`: One-time 30 credits, check `free_credits_granted` flag
3. `GET /api/credits/balance`: Return `{ balance, reserved, available }`
4. `GET /api/credits/history`: Paginated transaction history
5. Credit cost constants: `ASSIGNMENT_ANALYSIS=10`, `TASK_DISTRIBUTION=5`, Phase 2 constants defined

**Test:** Reserve blocks concurrent overdraft; commit deducts; release restores; double-grant prevented; balance endpoint accurate

---

### T8.2 — Lemon Squeezy Payment Integration
**Est:** 3h  
**Depends:** T8.1, T7.1  
**Files:**
- Modify `backend/app/routers/credits.py`
- `backend/app/models/payment_transaction.py` (already created in T1.4)

**Work:**
1. `POST /api/credits/checkout`: Accept package name → call Lemon Squeezy API → return checkout URL with `custom_data: { user_id }`
2. `POST /api/webhooks/lemon-squeezy`: Verify HMAC signature, extract order, idempotency check, credit user, send payment confirmation email (N-3)
3. Rate limit webhook: 100/min/IP
4. Handle refund webhooks: deduct credits

**Test:** Checkout returns valid URL; webhook credits user; duplicate webhook ignored (idempotent); invalid signature rejected; refund deducts credits

---

### T8.3 — Frontend Credits Page
**Est:** 2.5h  
**Depends:** T8.2, T2.5  
**Files:**
- `frontend/src/app/(dashboard)/credits/page.tsx`
- `frontend/src/components/credits/CreditBalance.tsx`
- `frontend/src/components/credits/PackageCard.tsx`
- `frontend/src/components/credits/LowBalanceWarning.tsx`
- `frontend/src/hooks/useCredits.ts`
- `frontend/src/types/credit.ts`

**Work:**
1. Credit balance display (total, reserved, available)
2. Three package cards: Starter ($2/100), Standard ($5/300), Pro ($10/700)
3. Buy button → redirect to Lemon Squeezy checkout URL
4. Transaction history table
5. Low-balance warning component (reused in sidebar CreditBadge)

**Test:** Balance renders; clicking buy redirects to checkout; transaction history loads; low-balance warning shows at ≤10

---

## Phase 9: Integration, Testing & Deployment

### T9.1 — Backend Integration Tests
**Est:** 4h  
**Depends:** All backend tasks  
**Files:**
- `backend/tests/conftest.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_workspaces.py`
- `backend/tests/test_assignments.py`
- `backend/tests/test_tasks.py`
- `backend/tests/test_chat.py`
- `backend/tests/test_credits.py`
- `backend/tests/test_ai_service.py`

**Work:**
1. Test fixtures: test DB, authenticated user factory, workspace factory
2. Full flow tests: register → create workspace → upload assignment → distribute tasks → move tasks → chat
3. Auth tests: unverified user blocked, non-member blocked, non-leader blocked
4. Credit tests: reserve-commit-release cycle, concurrent requests, insufficient balance
5. Edge case tests per specification

**Test:** `pytest` passes all tests; coverage > 80% on services/

---

### T9.2 — Frontend End-to-End Smoke Tests
**Est:** 3h  
**Depends:** All frontend tasks  
**Files:**
- `frontend/src/__tests__/` (or Playwright/Cypress test files)

**Work:**
1. Login flow: OAuth → phone verification → dashboard
2. Workspace flow: create → invite → upload → distribute → board → chat
3. Credit flow: view balance → purchase → verify balance update
4. Auth guard: verify unauthenticated redirect
5. Responsive checks: mobile viewport

**Test:** All smoke tests pass; no TS build errors; no console errors in browser

---

### T9.3 — Deploy Backend to Railway
**Est:** 2h  
**Depends:** T9.1  
**Files:**
- `backend/Dockerfile`
- `backend/railway.toml` (or Procfile)

**Work:**
1. Create Dockerfile: Python 3.11, install deps, run uvicorn
2. Configure Railway project + environment variables
3. Run `alembic upgrade head` on Railway's postgres
4. Verify health check endpoint

**Test:** `GET https://api.assignmind.com/api/health` returns 200; CORS allows frontend origin

---

### T9.4 — Deploy Frontend to Vercel
**Est:** 1.5h  
**Depends:** T9.2  
**Files:**
- `frontend/vercel.json` (if needed)

**Work:**
1. Connect repo to Vercel
2. Set environment variables (`NEXT_PUBLIC_*` only)
3. Verify build + deploy
4. Configure custom domain (if available)

**Test:** `https://assignmind.com` loads; OAuth redirect works; API calls to Railway backend succeed

---

### T9.5 — PWA Configuration
**Est:** 1.5h  
**Depends:** T9.4  
**Files:**
- `frontend/public/manifest.json`
- `frontend/public/sw.js`
- `frontend/public/icons/` (app icons)
- Modify `frontend/src/app/layout.tsx` (manifest link)

**Work:**
1. PWA manifest: app name, icons, theme color, display: standalone
2. Basic service worker: cache app shell for offline loading
3. Add to homescreen prompt

**Test:** Lighthouse PWA audit passes; "Add to Home Screen" prompt works on mobile Chrome

---

### T9.6 — Security Audit & Hardening
**Est:** 2h  
**Depends:** T9.3, T9.4  
**Files:**
- Modify various files as needed

**Work:**
1. Run `npm audit` + `pip-audit` — fix all high/critical vulnerabilities
2. Verify no secrets in client bundle (`grep` for API keys in build output)
3. Verify CORS is restricted to production frontend domain (no wildcard)
4. Test all rate limits are active
5. Verify all endpoints require auth (except health, webhook, callback)
6. SQL injection test: parameterized queries verified
7. XSS test: script tag in workspace name, chat message, task title

**Test:** Zero high/critical vulnerabilities; no secrets in client; all security tests pass

---

## Task Summary

| Phase | Tasks | Parallelizable | Total Est. Hours |
|-------|-------|----------------|-----------------|
| 1. Setup & Infrastructure | T1.1–T1.8 | T1.1∥T1.2∥T1.5∥T1.7∥T1.8 | 20.5h |
| 2. Auth & Users | T2.1–T2.6 | T2.3∥T2.4 after T1.7 | 14h |
| 3. Assignment & AI | T3.1–T3.4 | T3.1∥T3.2 | 12h |
| 4. Workspace & Distribution | T4.1–T4.6 | T4.1∥T4.2 backend | 17.5h |
| 5. Kanban Board | T5.1–T5.2 | — | 6h |
| 6. Chat & Agent | T6.1–T6.2 | — | 6.5h |
| 7. Email Notifications | T7.1–T7.4 | — | 9.5h |
| 8. Credits & Payments | T8.1–T8.3 | — | 8.5h |
| 9. Integration & Deploy | T9.1–T9.6 | T9.3∥T9.4 | 14h |
| **Total** | **40 tasks** | | **~108.5h** |

---

## Dependency Graph (Critical Path)

```
T1.1 ──▶ T1.3 ──▶ T1.4 ──▶ T1.6 ──▶ T2.1 ──▶ T3.1 ──▶ T3.3 ──▶ T3.4
  │                  │                    │         │
  │                  │                    ├──▶ T4.1 ──▶ T4.3 ──▶ T5.1 ──▶ T5.2
  │                  │                    │              │
  ├──▶ T1.5 ────────▶│                    ├──▶ T4.2     ├──▶ T6.1 ──▶ T6.2
  │                                       │
  │                                       ├──▶ T8.1 ──▶ T8.2
  │                                       │
  │                                       └──▶ T7.1 ──▶ T7.2, T7.3, T7.4
  │
T1.2 ──▶ T1.7 ──▶ T2.3 ──▶ T2.4
  │         │         │
  │         │         └──▶ T2.5 ──▶ T4.4 ──▶ T4.5 ──▶ T4.6
  │         │                                           │
  └──▶ T1.8 │                                    T8.3 ──┘
             │
             └──▶ T2.6
```

**Critical path:** T1.1 → T1.3 → T1.4 → T1.6 → T4.1 → T4.3 → T5.1 → T5.2

---

**Version**: 1.0 | **Created**: 2026-03-06
