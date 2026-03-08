# AssignMind — MVP Technical Plan
**Version:** 1.0 | **Status:** Ready for Implementation | **Date:** 2026-03-06  
**Source Documents:** [srs.md](file:///d:/AssignMind/.specify/memory/srs.md) · [constitution.md](file:///d:/AssignMind/.specify/memory/constitution.md) · [specification.md](file:///d:/AssignMind/.specify/memory/specification.md)  
**Scope:** Phase 1 MVP (Weeks 1–3)

---

## Table of Contents

1. [Full Folder Structure](#1-full-folder-structure)
2. [Database Schema](#2-database-schema)
3. [API Endpoints](#3-api-endpoints)
4. [AI Service Architecture](#4-ai-service-architecture)
5. [Email System Design](#5-email-system-design)
6. [Credit System Design](#6-credit-system-design)
7. [Environment Variables](#7-environment-variables)
8. [Key Implementation Notes per Feature](#8-key-implementation-notes-per-feature)

---

## 1. Full Folder Structure

### Backend — FastAPI (Python 3.11+)

```
backend/
├── main.py                          # FastAPI app factory, CORS, lifespan events
├── requirements.txt                 # Pinned dependencies
├── .env                             # Local environment variables (gitignored)
├── .env.example                     # Template for environment setup
├── alembic.ini                      # Database migration config
├── alembic/
│   ├── env.py                       # Migration environment setup
│   └── versions/                    # Auto-generated migration scripts
│
├── app/
│   ├── __init__.py
│   │
│   ├── config.py                    # Pydantic Settings: loads all env vars
│   │
│   ├── database.py                  # Async SQLAlchemy engine + session factory
│   │
│   ├── dependencies.py              # FastAPI dependency injection (get_db, get_current_user, etc.)
│   │
│   ├── models/                      # SQLAlchemy ORM models (database tables)
│   │   ├── __init__.py
│   │   ├── user.py                  # Users table
│   │   ├── workspace.py             # Workspaces table
│   │   ├── workspace_member.py      # Workspace membership + roles
│   │   ├── invitation.py            # Workspace invitations
│   │   ├── assignment.py            # Assignment documents + structured summaries
│   │   ├── task.py                  # Kanban tasks
│   │   ├── chat_message.py          # Group chat messages
│   │   ├── credit_transaction.py    # Credit ledger (purchases, reservations, commits)
│   │   └── scheduled_email.py       # Scheduled email queue
│   │
│   ├── schemas/                     # Pydantic request/response models (API contracts)
│   │   ├── __init__.py
│   │   ├── user.py                  # UserResponse, PhoneVerifyRequest, etc.
│   │   ├── workspace.py             # WorkspaceCreate, WorkspaceResponse, etc.
│   │   ├── invitation.py            # InviteRequest, InvitationResponse, etc.
│   │   ├── assignment.py            # AssignmentUploadResponse, AssignmentSummary (jsonb schema)
│   │   ├── task.py                  # TaskResponse, TaskStatusUpdate, TaskDistributionRequest
│   │   ├── chat.py                  # ChatMessageCreate, ChatMessageResponse
│   │   ├── credit.py                # CreditBalanceResponse, PurchaseRequest
│   │   └── common.py                # ErrorResponse, PaginationParams
│   │
│   ├── routers/                     # FastAPI route handlers (thin — delegate to services)
│   │   ├── __init__.py
│   │   ├── auth.py                  # OAuth callback, phone verification, token refresh
│   │   ├── users.py                 # Profile, account deletion
│   │   ├── workspaces.py            # CRUD, archive, transfer leadership
│   │   ├── invitations.py           # Invite, accept, decline, list pending
│   │   ├── assignments.py           # Upload, get summary
│   │   ├── tasks.py                 # CRUD, status update, distribution
│   │   ├── chat.py                  # Send message, list messages (polling)
│   │   ├── credits.py               # Balance, purchase (checkout URL), webhook
│   │   └── health.py                # Health check endpoint
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_service.py            # Claude API calls, prompt templates, keyword validation
│   │   ├── credit_service.py        # Reserve → commit/release, balance checks
│   │   ├── email_service.py         # Resend API wrapper, template selection
│   │   ├── workspace_service.py     # Workspace business logic
│   │   ├── invitation_service.py    # Invitation logic, user lookup
│   │   ├── assignment_service.py    # Upload processing, text extraction, summary storage
│   │   ├── task_service.py          # Task distribution, status updates, supervisor agent
│   │   ├── chat_service.py          # Message persistence, supervisor agent messages
│   │   └── user_service.py          # Account activation, deletion cascade
│   │
│   ├── utils/                       # Pure utility functions
│   │   ├── __init__.py
│   │   ├── sanitize.py              # XSS, SQL injection, prompt injection sanitizers
│   │   ├── auth.py                  # JWT verification, Supabase token validation
│   │   ├── rate_limit.py            # Rate limiting middleware/decorator
│   │   ├── pdf_parser.py            # PDF text extraction (PyPDF2 / pdfplumber)
│   │   └── datetime_utils.py        # UTC conversion, timezone helpers
│   │
│   ├── prompts/                     # AI prompt templates (versioned)
│   │   ├── __init__.py
│   │   ├── assignment_analysis.py   # Prompt template for assignment analysis
│   │   ├── task_distribution.py     # Prompt template for task distribution
│   │   └── validation.py            # Keyword violation patterns + reinforced prompts
│   │
│   └── jobs/                        # Background tasks / cron jobs
│       ├── __init__.py
│       ├── deadline_checker.py      # Cron: check upcoming deadlines → queue emails
│       ├── email_sender.py          # Worker: process email queue → call Resend
│       └── account_cleanup.py       # Cron: hard-delete expired deactivated accounts
│
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Test fixtures, test DB setup
    ├── test_auth.py
    ├── test_workspaces.py
    ├── test_assignments.py
    ├── test_tasks.py
    ├── test_chat.py
    ├── test_credits.py
    └── test_ai_service.py
```

### Frontend — Next.js 14 + Tailwind CSS

```
frontend/
├── package.json
├── next.config.js                    # Next.js configuration
├── tailwind.config.ts                # Tailwind CSS configuration
├── tsconfig.json                     # TypeScript strict mode enabled
├── postcss.config.js
├── .env.local                        # Local environment variables (gitignored)
├── .env.example                      # Template for environment setup
├── middleware.ts                      # Auth middleware: redirect unauthenticated users
│
├── public/
│   ├── manifest.json                 # PWA manifest
│   ├── sw.js                         # Service worker (basic offline)
│   ├── icons/                        # App icons for PWA
│   └── images/                       # Static images
│
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout (providers, fonts, RTL support)
│   │   ├── page.tsx                  # Landing page / redirect to dashboard
│   │   ├── globals.css               # Global styles + Tailwind base
│   │   │
│   │   ├── (auth)/                   # Auth route group (no sidebar)
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # OAuth login buttons (Google, GitHub)
│   │   │   ├── verify-phone/
│   │   │   │   └── page.tsx          # Phone verification OTP screen
│   │   │   └── callback/
│   │   │       └── page.tsx          # OAuth callback handler
│   │   │
│   │   ├── (dashboard)/              # Authenticated route group (with sidebar)
│   │   │   ├── layout.tsx            # Dashboard layout (sidebar, header, credit badge)
│   │   │   ├── page.tsx              # Dashboard home (workspace list, invitations, credit balance)
│   │   │   │
│   │   │   ├── workspaces/
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx      # Create workspace form
│   │   │   │   └── [workspaceId]/
│   │   │   │       ├── layout.tsx    # Workspace layout (tabs: Board, Chat, Assignment, Settings)
│   │   │   │       ├── page.tsx      # Workspace overview / redirect to board
│   │   │   │       ├── board/
│   │   │   │       │   └── page.tsx  # Kanban board
│   │   │   │       ├── chat/
│   │   │   │       │   └── page.tsx  # Group chat
│   │   │   │       ├── assignment/
│   │   │   │       │   └── page.tsx  # Assignment upload + structured summary view
│   │   │   │       ├── distribute/
│   │   │   │       │   └── page.tsx  # AI task distribution (constraints + review)
│   │   │   │       └── settings/
│   │   │   │           └── page.tsx  # Members, invitations, transfer leadership, archive
│   │   │   │
│   │   │   ├── credits/
│   │   │   │   └── page.tsx          # Credit balance + purchase packages
│   │   │   │
│   │   │   └── settings/
│   │   │       └── page.tsx          # User profile, account deletion
│   │   │
│   │   └── api/                      # Next.js API routes (if needed for BFF pattern)
│   │       └── auth/
│   │           └── callback/
│   │               └── route.ts      # Supabase Auth callback handler
│   │
│   ├── components/                   # Reusable React components
│   │   ├── ui/                       # Primitive UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── EmptyState.tsx
│   │   │
│   │   ├── layout/                   # Layout components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── CreditBadge.tsx
│   │   │   └── InvitationBanner.tsx
│   │   │
│   │   ├── workspace/                # Workspace-specific components
│   │   │   ├── WorkspaceCard.tsx
│   │   │   ├── MemberList.tsx
│   │   │   ├── InviteMemberForm.tsx
│   │   │   └── TransferLeadershipModal.tsx
│   │   │
│   │   ├── board/                    # Kanban board components
│   │   │   ├── KanbanBoard.tsx
│   │   │   ├── KanbanColumn.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── AddTaskModal.tsx
│   │   │   └── OverdueIndicator.tsx
│   │   │
│   │   ├── chat/                     # Chat components
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── AgentMessageBubble.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── PollingProvider.tsx
│   │   │
│   │   ├── assignment/               # Assignment components
│   │   │   ├── UploadForm.tsx
│   │   │   ├── StructuredSummaryView.tsx
│   │   │   └── ConstraintsEditor.tsx
│   │   │
│   │   ├── distribution/             # Task distribution components
│   │   │   ├── DistributionReview.tsx
│   │   │   ├── TaskAssignmentCard.tsx
│   │   │   └── ConstraintsList.tsx
│   │   │
│   │   └── credits/                  # Credit components
│   │       ├── CreditBalance.tsx
│   │       ├── PackageCard.tsx
│   │       └── LowBalanceWarning.tsx
│   │
│   ├── hooks/                        # Custom React hooks
│   │   ├── useAuth.ts                # Auth state, login, logout
│   │   ├── useWorkspace.ts           # Workspace data fetching
│   │   ├── useCredits.ts             # Credit balance + purchase flow
│   │   ├── useChat.ts                # Chat messages + 30s polling
│   │   ├── useTasks.ts               # Task CRUD + status updates
│   │   └── useInvitations.ts         # Pending invitations
│   │
│   ├── lib/                          # Utility libraries
│   │   ├── supabase.ts               # Supabase client initialization
│   │   ├── api.ts                    # Axios/fetch wrapper with JWT injection
│   │   ├── sanitize.ts               # Client-side input sanitization
│   │   ├── datetime.ts               # Timezone formatting via Intl API
│   │   └── constants.ts              # App-wide constants (polling intervals, limits)
│   │
│   ├── types/                        # TypeScript interfaces (mirrors Pydantic models)
│   │   ├── user.ts
│   │   ├── workspace.ts
│   │   ├── invitation.ts
│   │   ├── assignment.ts             # AssignmentSummary interface (jsonb schema)
│   │   ├── task.ts
│   │   ├── chat.ts
│   │   ├── credit.ts
│   │   └── api.ts                    # ErrorResponse, PaginatedResponse, etc.
│   │
│   └── providers/                    # React context providers
│       ├── AuthProvider.tsx           # Supabase auth session context
│       ├── ToastProvider.tsx          # Toast notification context
│       └── ThemeProvider.tsx          # Theme + RTL direction context
│
└── emails/                           # React Email templates (compiled server-side)
    ├── WelcomeEmail.tsx
    ├── VerificationEmail.tsx
    ├── InvitationEmail.tsx
    ├── PaymentConfirmationEmail.tsx
    ├── DeadlineReminderEmail.tsx
    ├── DeadlineMissedEmail.tsx
    ├── AccountDeletionEmail.tsx
    └── DeletionFinalEmail.tsx
```

---

## 2. Database Schema

All tables use PostgreSQL via Supabase. UUIDs for all primary keys. All timestamps stored as `timestamptz` (UTC).

### 2.1 `users`

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_id     UUID NOT NULL UNIQUE,               -- Supabase Auth user ID
    email           TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    avatar_url      TEXT,
    phone           TEXT UNIQUE,                         -- Verified phone number
    phone_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    timezone        TEXT DEFAULT 'UTC',                   -- IANA timezone (e.g., 'Asia/Riyadh')
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,       -- FALSE during deletion grace period
    deactivated_at  TIMESTAMPTZ,                         -- Set when deletion requested
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_supabase_id ON users(supabase_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
```

### 2.2 `credits`

```sql
CREATE TABLE credits (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    balance             INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    reserved            INTEGER NOT NULL DEFAULT 0 CHECK (reserved >= 0),
    free_credits_granted BOOLEAN NOT NULL DEFAULT FALSE,  -- Prevent double-granting
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Available balance = balance - reserved
-- Constraint: reserved <= balance
ALTER TABLE credits ADD CONSTRAINT chk_reserved_lte_balance CHECK (reserved <= balance);
```

### 2.3 `credit_transactions`

```sql
CREATE TABLE credit_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            TEXT NOT NULL CHECK (type IN (
                        'free_grant',          -- Initial 30 credits
                        'purchase',            -- Lemon Squeezy top-up
                        'reservation',         -- Credits reserved before AI call
                        'commit',              -- Reserved credits committed (AI call succeeded)
                        'release',             -- Reserved credits released (AI call failed)
                        'refund',              -- Lemon Squeezy refund
                        'forfeit'              -- Account deletion
                    )),
    amount          INTEGER NOT NULL,           -- Positive = credit, negative = debit
    description     TEXT,                        -- Human-readable (e.g., "Assignment analysis — Workspace: CS101")
    reference_id    TEXT,                        -- External ID (Lemon Squeezy order ID, reservation ID)
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_credit_tx_user ON credit_transactions(user_id, created_at DESC);
CREATE INDEX idx_credit_tx_ref ON credit_transactions(reference_id);
```

### 2.4 `workspaces`

```sql
CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL,
    description     TEXT,
    deadline        TIMESTAMPTZ,                 -- Overall assignment deadline (UTC)
    is_archived     BOOLEAN NOT NULL DEFAULT FALSE,
    archived_at     TIMESTAMPTZ,
    created_by      UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workspaces_created_by ON workspaces(created_by);
```

### 2.5 `workspace_members`

```sql
CREATE TABLE workspace_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role            TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('leader', 'member')),
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_wm_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_wm_user ON workspace_members(user_id);
```

### 2.6 `invitations`

```sql
CREATE TABLE invitations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email           TEXT NOT NULL,
    invited_by      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at    TIMESTAMPTZ,

    UNIQUE(workspace_id, email)
);

CREATE INDEX idx_invitations_email ON invitations(email);
CREATE INDEX idx_invitations_workspace ON invitations(workspace_id);
```

### 2.7 `assignments`

```sql
CREATE TABLE assignments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    original_filename TEXT NOT NULL,
    file_url        TEXT,                        -- Supabase Storage path (optional, for PDF re-download)
    raw_text        TEXT NOT NULL,               -- Extracted plaintext from PDF/text
    structured_summary JSONB NOT NULL,           -- AssignmentSummary schema (see §4)
    detected_language TEXT DEFAULT 'en' CHECK (detected_language IN ('en', 'ar')),
    uploaded_by     UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(workspace_id, version)
);

-- JSONB index for querying structured summary fields
CREATE INDEX idx_assignments_workspace ON assignments(workspace_id);
CREATE INDEX idx_assignments_summary ON assignments USING GIN (structured_summary);
```

### 2.8 `tasks`

```sql
CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'done')),
    assigned_to     UUID REFERENCES users(id) ON DELETE SET NULL,  -- NULL = Unassigned
    deadline        TIMESTAMPTZ,                 -- UTC
    position        INTEGER NOT NULL DEFAULT 0,  -- Ordering within column
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
    created_by      UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_workspace ON tasks(workspace_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_deadline ON tasks(deadline) WHERE deadline IS NOT NULL AND status != 'done';
```

### 2.9 `chat_messages`

```sql
CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    sender_id       UUID REFERENCES users(id) ON DELETE SET NULL,  -- NULL for anonymized
    sender_type     TEXT NOT NULL DEFAULT 'human' CHECK (sender_type IN ('human', 'agent')),
    sender_name     TEXT NOT NULL,               -- Denormalized name (or "[Deleted User]")
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_workspace ON chat_messages(workspace_id, created_at DESC);
```

### 2.10 `scheduled_emails`

```sql
CREATE TABLE scheduled_emails (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    task_id         UUID REFERENCES tasks(id) ON DELETE CASCADE,
    recipient_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_type      TEXT NOT NULL CHECK (email_type IN (
                        'deadline_72h', 'deadline_24h', 'deadline_missed'
                    )),
    scheduled_for   TIMESTAMPTZ NOT NULL,        -- When to send (UTC)
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
                        'pending', 'sent', 'cancelled', 'failed'
                    )),
    attempts        INTEGER NOT NULL DEFAULT 0,
    last_error      TEXT,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scheduled_pending ON scheduled_emails(scheduled_for)
    WHERE status = 'pending';
CREATE INDEX idx_scheduled_task ON scheduled_emails(task_id);
```

### 2.11 `payment_transactions`

```sql
CREATE TABLE payment_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lemon_squeezy_order_id TEXT NOT NULL UNIQUE,  -- Idempotency key
    package_name        TEXT NOT NULL,
    credits_amount      INTEGER NOT NULL,
    amount_usd          DECIMAL(10, 2) NOT NULL,
    status              TEXT NOT NULL DEFAULT 'completed' CHECK (status IN ('completed', 'refunded')),
    webhook_payload     JSONB,                    -- Raw webhook for debugging
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_user ON payment_transactions(user_id);
```

### Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o| credits : "has"
    users ||--o{ credit_transactions : "logs"
    users ||--o{ workspace_members : "joins"
    users ||--o{ invitations : "sends/receives"
    users ||--o{ assignments : "uploads"
    users ||--o{ tasks : "assigned"
    users ||--o{ chat_messages : "sends"
    users ||--o{ scheduled_emails : "receives"
    users ||--o{ payment_transactions : "purchases"

    workspaces ||--|{ workspace_members : "contains"
    workspaces ||--o{ invitations : "has"
    workspaces ||--o{ assignments : "has"
    workspaces ||--o{ tasks : "has"
    workspaces ||--o{ chat_messages : "has"
    workspaces ||--o{ scheduled_emails : "triggers"

    tasks ||--o{ scheduled_emails : "triggers"
```

---

## 3. API Endpoints

### Auth Routes — `POST /api/auth/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/api/auth/callback` | No | — | Handle OAuth callback from Supabase, create/update user record |
| `POST` | `/api/auth/verify-phone` | JWT | — | Submit OTP for phone verification, activate account, grant 30 credits |
| `POST` | `/api/auth/resend-otp` | JWT | — | Resend OTP (rate-limited: 3/10min per phone) |
| `GET`  | `/api/auth/me` | JWT | — | Get current user profile + verification status |
| `POST` | `/api/auth/refresh` | JWT | — | Refresh JWT token |

### User Routes — `/api/users/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `GET`  | `/api/users/me` | JWT | — | Get user profile (name, email, timezone, credit balance) |
| `PATCH`| `/api/users/me` | JWT | — | Update profile (full_name, timezone) |
| `POST` | `/api/users/me/delete` | JWT | — | Request account deletion (starts 14-day grace) |
| `POST` | `/api/users/me/reactivate` | JWT | — | Cancel deletion during grace period |

### Workspace Routes — `/api/workspaces/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST`   | `/api/workspaces` | JWT | — | Create new workspace (user becomes leader) |
| `GET`    | `/api/workspaces` | JWT | — | List user's active workspaces |
| `GET`    | `/api/workspaces/{id}` | JWT | Member | Get workspace details |
| `PATCH`  | `/api/workspaces/{id}` | JWT | Leader | Update workspace (title, description, deadline) |
| `POST`   | `/api/workspaces/{id}/archive` | JWT | Leader | Archive workspace |
| `POST`   | `/api/workspaces/{id}/transfer-leadership` | JWT | Leader | Transfer leadership to another member |
| `DELETE` | `/api/workspaces/{id}/members/{userId}` | JWT | Leader | Remove a member from workspace |
| `GET`    | `/api/workspaces/{id}/members` | JWT | Member | List workspace members |

### Invitation Routes — `/api/invitations/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/api/workspaces/{id}/invitations` | JWT | Leader | Invite member by email |
| `GET`  | `/api/invitations/pending` | JWT | — | List user's pending invitations |
| `POST` | `/api/invitations/{id}/accept` | JWT | — | Accept a workspace invitation |
| `POST` | `/api/invitations/{id}/decline` | JWT | — | Decline a workspace invitation |

### Assignment Routes — `/api/workspaces/{id}/assignments/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/api/workspaces/{id}/assignments` | JWT | Leader | Upload assignment document (PDF/text) → AI analysis. Rate: 5/hr |
| `GET`  | `/api/workspaces/{id}/assignments/latest` | JWT | Member | Get latest structured summary |
| `GET`  | `/api/workspaces/{id}/assignments` | JWT | Member | List all assignment versions |

### Task Routes — `/api/workspaces/{id}/tasks/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/api/workspaces/{id}/tasks/distribute` | JWT | Leader | Generate AI task distribution. Rate: 3/hr. Cost: 5 credits |
| `POST` | `/api/workspaces/{id}/tasks/finalize` | JWT | Leader | Finalize proposed distribution → create tasks on board |
| `GET`  | `/api/workspaces/{id}/tasks` | JWT | Member | List all tasks (board data) |
| `POST` | `/api/workspaces/{id}/tasks` | JWT | Leader | Create ad-hoc task manually |
| `PATCH`| `/api/workspaces/{id}/tasks/{taskId}` | JWT | Owner/Leader | Update task (title, description, deadline, assigned_to — Leader only for last two) |
| `PATCH`| `/api/workspaces/{id}/tasks/{taskId}/status` | JWT | Owner/Leader | Update task status (todo ↔ in_progress ↔ done) |
| `DELETE`| `/api/workspaces/{id}/tasks/{taskId}` | JWT | Leader | Delete a task |

### Chat Routes — `/api/workspaces/{id}/chat/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/api/workspaces/{id}/chat` | JWT | Member | Send a message to group chat |
| `GET`  | `/api/workspaces/{id}/chat` | JWT | Member | Get messages (paginated, supports `?after=<timestamp>` for polling) |

### Credit Routes — `/api/credits/*`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `GET`  | `/api/credits/balance` | JWT | — | Get credit balance (total, reserved, available) |
| `GET`  | `/api/credits/history` | JWT | — | Get credit transaction history (paginated) |
| `POST` | `/api/credits/checkout` | JWT | — | Generate Lemon Squeezy checkout URL for selected package |
| `POST` | `/api/webhooks/lemon-squeezy` | Signature | — | Lemon Squeezy webhook handler. Rate: 100/min/IP |

### Health — `/api/health`

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `GET`  | `/api/health` | No | — | Health check (DB connectivity, service status) |

---

## 4. AI Service Architecture

### 4.1 Service Layer Design (`services/ai_service.py`)

```
┌──────────────────────────────────────────────────────────────────┐
│                        ai_service.py                             │
│                                                                  │
│  ┌─────────────┐   ┌─────────────────┐   ┌──────────────────┐  │
│  │ Prompt       │   │ Credit           │   │ Response         │  │
│  │ Template     │──▶│ Reservation      │──▶│ Validation       │  │
│  │ Selection    │   │ (reserve-then-   │   │ (keyword check)  │  │
│  └─────────────┘   │  commit)         │   └──────────────────┘  │
│                     └─────────────────┘             │            │
│                            │                        │            │
│                            ▼                        ▼            │
│                    ┌───────────────┐      ┌────────────────┐    │
│                    │ Claude API    │      │ Retry Logic    │    │
│                    │ Call          │      │ (1 retry max)  │    │
│                    └───────────────┘      └────────────────┘    │
│                            │                        │            │
│                            ▼                        ▼            │
│                    ┌───────────────┐      ┌────────────────┐    │
│                    │ Response      │      │ Commit/Release │    │
│                    │ Parsing       │      │ Credits        │    │
│                    └───────────────┘      └────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Key Methods:**

```python
class AIService:
    async def analyze_assignment(
        self, raw_text: str, language: str, user_id: UUID, workspace_id: UUID
    ) -> AssignmentSummary:
        """
        1. Reserve 10 credits
        2. Build prompt from assignment_analysis template
        3. Call Claude API
        4. Validate response (keyword check)
        5. Parse response into AssignmentSummary JSON
        6. Commit credits on success / release on failure
        """

    async def generate_task_distribution(
        self, summary: AssignmentSummary, members: list[Member],
        constraints: list[str], user_id: UUID, workspace_id: UUID
    ) -> TaskDistributionProposal:
        """
        1. Reserve 5 credits
        2. Build prompt from task_distribution template
        3. Call Claude API
        4. Parse response into TaskDistributionProposal
        5. Commit/release credits
        """
```

### 4.2 Prompt Templates

#### Assignment Analysis Prompt (`prompts/assignment_analysis.py`)

```python
ASSIGNMENT_ANALYSIS_PROMPT = """
You are an academic assignment analysis assistant. Your role is to help students
UNDERSTAND their assignment — you must NEVER provide direct answers or solutions.

INSTRUCTIONS:
- Do NOT provide direct answers to any questions in the assignment
- Do NOT write code, essays, or solutions that complete the assignment
- Do NOT give step-by-step solutions that a student could copy directly
- INSTEAD: Break down requirements, identify constraints, suggest approaches,
  and guide the student's thinking

Respond in the SAME LANGUAGE as the document ({language}).

Analyze the following assignment document and produce a structured JSON summary:

<assignment_document>
{sanitized_text}
</assignment_document>

Respond with a JSON object containing exactly these keys:
{{
    "requirements": ["list of extracted requirements"],
    "constraints": ["list of identified constraints or rules"],
    "deliverables": ["list of expected deliverables"],
    "deadlines": [
        {{"description": "milestone description", "date": "YYYY-MM-DD or 'not specified'"}}
    ],
    "tools": ["list of recommended tools, frameworks, or resources"]
}}

IMPORTANT: Output ONLY the JSON object. No markdown formatting, no explanation.
"""
```

#### Task Distribution Prompt (`prompts/task_distribution.py`)

```python
TASK_DISTRIBUTION_PROMPT = """
You are a team task distribution assistant. Propose a fair distribution of tasks
among team members based on the assignment analysis.

INSTRUCTIONS:
- Distribute tasks equitably among all members
- Respect all constraints listed below
- Suggest logical task dependencies where applicable
- GUIDE the team leader's thinking, do not dictate — use phrases like
  "Consider that..." or "You may want to..."
- Do NOT provide solutions to the assignment itself

TEAM MEMBERS: {member_names}

ASSIGNMENT SUMMARY:
{summary_json}

CONSTRAINTS:
{constraints_list}

Respond with a JSON object:
{{
    "tasks": [
        {{
            "title": "Task title",
            "description": "Task description (what to do, not how to solve)",
            "assigned_to": "member name",
            "deadline": "YYYY-MM-DDTHH:MM:SSZ",
            "dependencies": ["titles of tasks this depends on"]
        }}
    ],
    "guidance": "Brief message to the team leader about the distribution rationale
                 and any considerations they should review"
}}

IMPORTANT: Output ONLY the JSON object.
"""
```

### 4.3 Structured Summary Schema (jsonb)

```typescript
// TypeScript interface (frontend/src/types/assignment.ts)
interface AssignmentSummary {
    requirements: string[];        // e.g., ["Build a REST API with CRUD endpoints"]
    constraints: string[];         // e.g., ["All members must contribute to frontend and backend"]
    deliverables: string[];        // e.g., ["Deployed web application", "Technical report"]
    deadlines: Deadline[];         // e.g., [{ description: "Final submission", date: "2026-04-15" }]
    tools: string[];               // e.g., ["React", "Node.js", "PostgreSQL"]
}

interface Deadline {
    description: string;
    date: string;                  // ISO 8601 date string or "not specified"
}
```

```python
# Pydantic model (backend/app/schemas/assignment.py)
class DeadlineItem(BaseModel):
    description: str
    date: str  # ISO 8601 or "not specified"

class AssignmentSummary(BaseModel):
    requirements: list[str]
    constraints: list[str]
    deliverables: list[str]
    deadlines: list[DeadlineItem]
    tools: list[str]
```

### 4.4 Keyword Validation Mechanism (`prompts/validation.py`)

```python
# Patterns that indicate a direct-answer violation
VIOLATION_PATTERNS = [
    r"(?i)\bthe answer is\b",
    r"(?i)\bhere(?:'s| is) the (?:solution|answer|code)\b",
    r"(?i)\bsolution:\s*\n",
    r"(?i)\bjust copy\b",
    r"(?i)\bhere(?:'s| is) (?:a |the )?(?:complete|full|working)\b",
    # Code block patterns for solution-type code
    r"```(?:python|javascript|java|c\+\+|sql|html)[\s\S]{200,}```",  # Large code blocks
]

REINFORCED_SUFFIX = """

CRITICAL REMINDER: You have been flagged for providing what appears to be a
direct answer or solution. You MUST NOT do this. Reframe your entire response
as guiding questions, requirement breakdowns, and thinking scaffolds.
Do NOT include any code solutions, direct answers, or copyable work.
"""

def validate_response(response_text: str) -> bool:
    """Returns True if the response passes validation (no violations detected)."""
    for pattern in VIOLATION_PATTERNS:
        if re.search(pattern, response_text):
            return False
    return True
```

**Validation Flow:**
1. Call Claude API → get response
2. Run `validate_response(response)` against keyword patterns
3. If **passes** → parse into `AssignmentSummary` → commit credits → return
4. If **fails** → retry **once** with `REINFORCED_SUFFIX` appended to prompt
5. If second attempt **passes** → parse → commit → return
6. If second attempt **fails** → log incident → return generic guided-learning fallback → release credits (no charge for a blocked response)

---

## 5. Email System Design

### 5.1 Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Email System                                │
│                                                                │
│  ┌─────────────────┐          ┌──────────────────────┐        │
│  │ Event Triggers   │          │ Scheduled Email       │        │
│  │ (immediate)      │          │ Checker (cron)        │        │
│  │                  │          │                       │        │
│  │ • Registration   │          │ Runs every 5 minutes  │        │
│  │ • Activation     │          │ Queries:              │        │
│  │ • Purchase       │          │   scheduled_emails    │        │
│  │ • Invitation     │          │   WHERE status =      │        │
│  └────────┬─────────┘          │   'pending' AND       │        │
│           │                    │   scheduled_for <=    │        │
│           ▼                    │   NOW()               │        │
│  ┌─────────────────┐          └───────────┬───────────┘        │
│  │ email_service.py │◀─────────────────────┘                   │
│  │                  │                                           │
│  │ select_template()│                                           │
│  │ render_html()    │                                           │
│  │ send_via_resend()│                                           │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Resend API       │                                           │
│  └─────────────────┘                                           │
└───────────────────────────────────────────────────────────────┘
```

### 5.2 Immediate Emails (Event-Driven)

These are sent synchronously or via a lightweight async task when an event occurs:

| Trigger | When | Template |
|---------|------|----------|
| N-1: Registration | `POST /api/auth/callback` creates user | `VerificationEmail` |
| N-2: Activation | `POST /api/auth/verify-phone` succeeds | `WelcomeEmail` |
| N-3: Purchase | Lemon Squeezy webhook confirms payment | `PaymentConfirmationEmail` |
| N-4: Invitation | `POST /api/workspaces/{id}/invitations` | `InvitationEmail` |

### 5.3 Scheduled Emails (Cron Job)

**`jobs/deadline_checker.py`** runs every **5 minutes** as a cron job:

```python
async def check_deadlines():
    """
    Called every 5 minutes by cron/APScheduler.
    
    1. Query all tasks WHERE:
       - deadline IS NOT NULL
       - status != 'done'
       - workspace is not archived
    
    2. For each task:
       a. If (deadline - NOW) <= 72h AND no 'deadline_72h' email exists for this task:
          → INSERT scheduled_email (type='deadline_72h', scheduled_for=deadline-72h)
       b. If (deadline - NOW) <= 24h AND no 'deadline_24h' email exists for this task:
          → INSERT scheduled_email (type='deadline_24h', scheduled_for=deadline-24h)
       c. If deadline < NOW AND no 'deadline_missed' email exists for this task:
          → INSERT scheduled_email (type='deadline_missed', scheduled_for=NOW,
            recipient=team_leader_id)
    
    3. Process email queue: query scheduled_emails WHERE status='pending'
       AND scheduled_for <= NOW()
       → For each: send via Resend → update status to 'sent'
       → On failure: increment attempts, retry if attempts < 3, else mark 'failed'
    """
```

### 5.4 Email Cancellation Logic

Emails are cancelled when:
- **Task moved to "Done"**: Cancel all pending `deadline_72h`, `deadline_24h`, and `deadline_missed` for that task
- **Task deadline updated**: Cancel old reminders, schedule new ones based on updated deadline
- **Workspace archived**: Cancel all pending scheduled emails for that workspace
- **User account deactivated**: Cancel pending emails for that user (they'll be hard-deleted after 14 days)

```python
async def cancel_task_emails(task_id: UUID):
    """Cancel all pending scheduled emails for a specific task."""
    await db.execute(
        update(ScheduledEmail)
        .where(ScheduledEmail.task_id == task_id)
        .where(ScheduledEmail.status == 'pending')
        .values(status='cancelled')
    )
```

### 5.5 Retry Strategy

| Attempt | Delay After Failure |
|---------|--------------------|
| 1st retry | 5 minutes |
| 2nd retry | 20 minutes |
| 3rd retry | 60 minutes |
| After 3rd | Mark as `failed`, log for manual review |

---

## 6. Credit System Design

### 6.1 Reserve-Then-Commit Transaction Flow

```
Step 1: CHECK                    Step 2: RESERVE                 Step 3: API CALL
┌──────────────┐                ┌──────────────┐                ┌──────────────┐
│ Query credits │                │ UPDATE credits│                │ Call Claude   │
│ WHERE         │──▶ Sufficient? │ SET reserved  │──▶ Reserved ──▶│ API          │
│ (balance -    │    Yes ──────▶ │ = reserved +  │                │              │
│  reserved)    │                │   cost        │                └──────┬───────┘
│ >= cost       │    No ─▶ 403  └──────────────┘                       │
└──────────────┘                                                  Success? ──┐
                                                                       │     │
                                                           ┌───────────┘     │
                                                           │                 │
                                                    Step 4a: COMMIT    Step 4b: RELEASE
                                                    ┌──────────────┐   ┌──────────────┐
                                                    │ UPDATE credits│   │ UPDATE credits│
                                                    │ SET balance   │   │ SET reserved  │
                                                    │ = balance -   │   │ = reserved -  │
                                                    │   cost,       │   │   cost        │
                                                    │ reserved =    │   │              │
                                                    │ reserved -    │   └──────────────┘
                                                    │   cost        │
                                                    └──────────────┘
```

### 6.2 SQL Transaction Implementation

```python
# services/credit_service.py

class CreditService:

    async def reserve_credits(self, user_id: UUID, amount: int, description: str) -> str:
        """
        Atomically reserve credits. Returns reservation_id.
        Raises InsufficientCreditsError if (balance - reserved) < amount.
        """
        reservation_id = str(uuid4())

        async with self.db.begin():  # Transaction
            # Row-level lock prevents concurrent modifications
            result = await self.db.execute(
                select(Credit)
                .where(Credit.user_id == user_id)
                .with_for_update()  # SELECT ... FOR UPDATE
            )
            credit = result.scalar_one()

            available = credit.balance - credit.reserved
            if available < amount:
                raise InsufficientCreditsError(
                    f"Insufficient credits: need {amount}, available {available}"
                )

            # Reserve
            credit.reserved += amount
            credit.updated_at = utcnow()

            # Log transaction
            self.db.add(CreditTransaction(
                user_id=user_id,
                type='reservation',
                amount=-amount,
                description=description,
                reference_id=reservation_id,
            ))

        return reservation_id

    async def commit_reservation(self, user_id: UUID, reservation_id: str, amount: int):
        """Finalize a reservation — actually deduct credits."""
        async with self.db.begin():
            result = await self.db.execute(
                select(Credit)
                .where(Credit.user_id == user_id)
                .with_for_update()
            )
            credit = result.scalar_one()

            credit.balance -= amount
            credit.reserved -= amount
            credit.updated_at = utcnow()

            self.db.add(CreditTransaction(
                user_id=user_id,
                type='commit',
                amount=-amount,
                reference_id=reservation_id,
            ))

    async def release_reservation(self, user_id: UUID, reservation_id: str, amount: int):
        """Release a reservation — credits are freed back to available."""
        async with self.db.begin():
            result = await self.db.execute(
                select(Credit)
                .where(Credit.user_id == user_id)
                .with_for_update()
            )
            credit = result.scalar_one()

            credit.reserved -= amount
            credit.updated_at = utcnow()

            self.db.add(CreditTransaction(
                user_id=user_id,
                type='release',
                amount=amount,
                reference_id=reservation_id,
            ))
```

### 6.3 Credit Cost Constants

```python
# app/config.py or services/credit_service.py

class CreditCosts:
    ASSIGNMENT_ANALYSIS = 10      # F-002: Upload + AI analysis
    TASK_DISTRIBUTION = 5         # F-004: AI task distribution
    AI_CHAT_MESSAGE = 2           # Phase 2: Personal Agent chat
    AGENT_BACKGROUND_UPDATE = 1   # Phase 2: AI-powered Supervisor Agent

    FREE_GRANT = 30               # Initial free credits on registration
```

### 6.4 Lemon Squeezy Webhook Flow

```
User clicks "Buy Starter"
    │
    ▼
POST /api/credits/checkout
    │ → Generate Lemon Squeezy checkout URL with user_id in metadata
    │ → Return checkout URL to frontend
    ▼
User redirected to Lemon Squeezy checkout
    │
    ▼ (payment completed)
    │
Lemon Squeezy sends webhook to POST /api/webhooks/lemon-squeezy
    │
    ▼
Backend:
    1. Verify webhook signature using LEMON_SQUEEZY_WEBHOOK_SECRET
    2. Extract order_id from payload
    3. Check if order_id already processed (idempotency via payment_transactions)
    4. Extract user_id from metadata, credits_amount from package
    5. UPDATE credits SET balance = balance + credits_amount
    6. INSERT payment_transaction record
    7. INSERT credit_transaction (type='purchase')
    8. Send payment confirmation email (N-3)
```

---

## 7. Environment Variables

### 7.1 Backend (.env)

```bash
# ──── APP ────
APP_ENV=development                         # development | staging | production
APP_PORT=8000                               # FastAPI server port
APP_HOST=0.0.0.0                            # Bind address
FRONTEND_URL=http://localhost:3000           # For CORS + email links
BACKEND_URL=http://localhost:8000            # For webhook URLs

# ──── DATABASE ────
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/assignmind   # Async connection string
SUPABASE_URL=https://your-project.supabase.co                      # Supabase project URL
SUPABASE_SERVICE_ROLE_KEY=eyJ...                                    # Service role key (NEVER expose to client)
SUPABASE_JWT_SECRET=your-jwt-secret                                 # For verifying Supabase JWTs server-side

# ──── AI ────
ANTHROPIC_API_KEY=sk-ant-...                # Claude API key
ANTHROPIC_MODEL=claude-sonnet-4-20250514       # Model identifier
ANTHROPIC_MAX_TOKENS=4096                   # Max tokens per response
ANTHROPIC_TIMEOUT_SECONDS=60                # Request timeout

# ──── EMAIL ────
RESEND_API_KEY=re_...                       # Resend API key for sending emails
EMAIL_FROM=noreply@assignmind.com           # Sender email address
EMAIL_FROM_NAME=AssignMind                  # Sender display name

# ──── PAYMENTS ────
LEMON_SQUEEZY_API_KEY=ls_...               # Lemon Squeezy API key
LEMON_SQUEEZY_WEBHOOK_SECRET=whsec_...     # Webhook signing secret
LEMON_SQUEEZY_STORE_ID=12345              # Store identifier
LEMON_SQUEEZY_STARTER_VARIANT_ID=67890    # Product variant IDs for each package
LEMON_SQUEEZY_STANDARD_VARIANT_ID=67891
LEMON_SQUEEZY_PRO_VARIANT_ID=67892

# ──── RATE LIMITING ────
RATE_LIMIT_REDIS_URL=redis://localhost:6379  # Redis for rate limit counters (optional: in-memory fallback)

# ──── LOGGING ────
LOG_LEVEL=INFO                              # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json                             # json | text
```

### 7.2 Frontend (.env.local)

```bash
# ──── PUBLIC (safe for client) ────
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co           # Public Supabase URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...                                 # Supabase anon key (public, RLS-restricted)
NEXT_PUBLIC_API_URL=http://localhost:8000/api                         # Backend API base URL
NEXT_PUBLIC_APP_URL=http://localhost:3000                             # Frontend self-URL
NEXT_PUBLIC_LEMON_SQUEEZY_STORE_URL=https://assignmind.lemonsqueezy.com  # Public store URL

# ──── BUILD-TIME ONLY ────
NEXT_PUBLIC_APP_NAME=AssignMind
NEXT_PUBLIC_CHAT_POLL_INTERVAL_MS=30000                              # 30-second polling interval
NEXT_PUBLIC_LOW_CREDIT_THRESHOLD=10                                   # Show warning at ≤10 credits
```

> **Note:** The frontend `.env.local` contains **only** `NEXT_PUBLIC_*` values. No API keys, no service role keys, no secrets of any kind. *(Constitution §II)*

---

## 8. Key Implementation Notes per Feature

### F-001: User Registration & Authentication

- **OAuth flow**: Use `@supabase/supabase-js` on the frontend to initiate Google/GitHub OAuth. The callback URL redirects to `/callback`, which exchanges the code for a session.
- **Phone verification**: After OAuth, redirect to `/verify-phone`. Use Supabase's built-in phone auth or integrate Twilio. OTP expiry: 5 minutes.
- **JWT middleware**: Create a FastAPI dependency `get_current_user()` that extracts the JWT from the `Authorization: Bearer <token>` header, verifies it using `SUPABASE_JWT_SECRET`, and fetches the user record.
- **Phone uniqueness**: Add a `UNIQUE` constraint on `users.phone`. Check uniqueness before sending OTP.
- **30 free credits**: Granted exactly once. The `credits.free_credits_granted` flag prevents re-granting on re-verification.

### F-002: Assignment Upload & AI-Powered Analysis

- **File upload**: Accept `multipart/form-data` with a single file field. Validate MIME type (`application/pdf`, `text/plain`) and size (10 MB max) before processing.
- **PDF extraction**: Use `pdfplumber` (preferred for text-based PDFs) with fallback to `pytesseract` for scanned PDFs (OCR). If extraction yields < 50 characters, return the OCR error.
- **Prompt injection defense**: Wrap user content in XML-like delimiters (`<assignment_document>...</assignment_document>`) and instruct Claude to treat it as untrusted data.
- **JSON parsing**: Claude's response should be pure JSON. Use `json.loads()` wrapped in try/except; if parsing fails, log the raw response and retry once.
- **Team Leader auth**: Create a dependency `require_team_leader(workspace_id)` that checks `workspace_members` for `role = 'leader'`.

### F-003: Workspace Creation & Member Invitation

- **Member cap enforcement**: Before inserting an invitation, count existing members + pending invitations. Reject if >= 10.
- **Accept/decline flow**: When an existing user receives an invitation, store it in `invitations` table with `status = 'pending'`. The frontend polls `/api/invitations/pending` to show notification badges.
- **New user auto-join**: When a new user registers with an email that has pending invitations, the registration callback queries `invitations` and auto-accepts them.
- **Leadership transfer**: Single transaction: update old leader to `role = 'member'`, update new leader to `role = 'leader'`. Validate target is an existing member.

### F-004: Intelligent Task Distribution

- **Constraints UI**: Frontend fetches the structured summary's `constraints` array, renders them as editable chips/tags. Team Leader can delete, edit, or add new ones. The combined list is sent with the distribution request.
- **AI response parsing**: Claude returns a JSON array of tasks. Parse into Pydantic `TaskDistributionProposal` model. If a member name doesn't match an existing member, flag it in the review UI.
- **Finalization**: The Team Leader reviews the proposed distribution on the frontend, makes modifications, then submits the final list to `POST /api/workspaces/{id}/tasks/finalize`. This bulk-creates tasks and triggers Supervisor Agent messages.

### F-005: Basic Kanban Board

- **Authorization check**: On `PATCH /tasks/{taskId}/status`, verify `assigned_to == current_user.id` OR `current_user.role == 'leader'`.
- **Supervisor Agent trigger**: When a task status changes, `task_service.py` calls `chat_service.post_agent_message()` synchronously within the same request. No AI call — just template string formatting.
- **Overdue detection**: Frontend checks `task.deadline < Date.now()` and renders a red badge. The backend cron job handles email notifications separately.

### F-006: Group Chat with Team Supervisor Agent

- **Polling endpoint**: `GET /api/workspaces/{id}/chat?after=2026-03-06T12:00:00Z` returns only messages created after the given timestamp. Frontend polls every 30 seconds using this parameter.
- **Agent message batching**: When `task_service` triggers a Supervisor Agent message, it checks if an agent message was posted in the last 5 minutes. If so, it updates that message to include the new status change (batching).
- **Message sanitization**: Use `bleach.clean()` (Python) to strip all HTML tags from message content before storage. Frontend renders as plain text with `white-space: pre-wrap`.

### F-007: Automated Email Notifications

- **Cron setup**: Use `APScheduler` with `AsyncIOScheduler` inside FastAPI's lifespan. Schedule `deadline_checker` to run every 5 minutes.
- **React Email**: Email templates live in `frontend/emails/`. Compile them to HTML using `@react-email/render` during a build step. The backend stores pre-compiled HTML templates or calls a server-side render function.
- **Timezone in emails**: When rendering deadline times in email bodies, convert UTC to the recipient's `users.timezone` value using `pytz` or `zoneinfo`.

### F-008: Credit System & Lemon Squeezy Payment Integration

- **Webhook security**: Verify the `X-Signature` header on incoming Lemon Squeezy webhooks using HMAC-SHA256 with `LEMON_SQUEEZY_WEBHOOK_SECRET`. Reject unverified payloads.
- **Idempotency**: Use `lemon_squeezy_order_id` as the deduplication key. Before processing, check `payment_transactions` for an existing record with that order ID.
- **Checkout flow**: `POST /api/credits/checkout` calls the Lemon Squeezy API to create a checkout session with `custom_data: { user_id: "..." }`. Returns the checkout URL. Frontend redirects the user.
- **Low-balance warning**: Frontend checks `availableBalance <= 10` on every dashboard render and shows a persistent banner.
- **Concurrent safety**: The `SELECT ... FOR UPDATE` lock in `reserve_credits` ensures that two simultaneous requests from the same user can't both succeed if only enough credits for one exist.

---

**Version**: 1.0 | **Created**: 2026-03-06 | **Last Updated**: 2026-03-06
