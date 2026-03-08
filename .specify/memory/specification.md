# AssignMind — Formal MVP Specification
**Version:** 1.1 | **Status:** Finalized | **Date:** 2026-03-06  
**Source Documents:** [srs.md](file:///d:/AssignMind/.specify/memory/srs.md) · [constitution.md](file:///d:/AssignMind/.specify/memory/constitution.md) · [clarifications.md](file:///d:/AssignMind/.specify/memory/clarifications.md)  
**Scope:** Phase 1 MVP (Weeks 1–3)

---

## Table of Contents

1. [F-001: User Registration & Authentication](#f-001-user-registration--authentication)
2. [F-002: Assignment Upload & AI-Powered Analysis](#f-002-assignment-upload--ai-powered-analysis)
3. [F-003: Workspace Creation & Member Invitation](#f-003-workspace-creation--member-invitation)
4. [F-004: Intelligent Task Distribution](#f-004-intelligent-task-distribution)
5. [F-005: Basic Kanban Board](#f-005-basic-kanban-board)
6. [F-006: Group Chat with Team Supervisor Agent](#f-006-group-chat-with-team-supervisor-agent)
7. [F-007: Automated Email Notifications](#f-007-automated-email-notifications)
8. [F-008: Credit System & Lemon Squeezy Payment Integration](#f-008-credit-system--lemon-squeezy-payment-integration)

---

## F-001: User Registration & Authentication

### User Story

**As a** university student,  
**I want to** register for an AssignMind account using my Google or GitHub account and verify my phone number,  
**so that** I can securely access the platform with a verified identity and receive my 30 free starting Credits.

### Acceptance Criteria

1. User can initiate registration via **Google OAuth** or **GitHub OAuth** through Supabase Auth
2. After OAuth, user is prompted to verify a **phone number** via SMS OTP before the account is activated
3. A single phone number can only be associated with **one** account — duplicate phone numbers are rejected with a clear error message
4. Upon successful phone verification, the account is activated and **30 free Credits** are credited to the user's personal balance
5. The 30 free Credits are a **one-time, non-renewable** grant tied to the verified phone number
6. A **verification email** is sent upon registration; a **welcome email** is sent upon account activation
7. After activation, user is redirected to the dashboard with an authenticated session
8. Authenticated sessions use **Supabase Auth JWT tokens**, verified server-side on every subsequent API request (Constitution §V)
9. No API keys or auth secrets are exposed in client-side code (Constitution §II)
10. Login flow for returning users authenticates via the same OAuth provider and does not require re-verification
11. All auth-related inputs (phone number, OAuth callback parameters) are **sanitized and validated** server-side (Constitution §III)
12. OTP SMS requests are **rate-limited** to 3 requests per phone number per 10 minutes *(Decision Q15)*

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-001.1 | User tries to register with a phone number already linked to another account | Registration blocked; error message: "This phone number is already associated with an account" |
| E-001.2 | User enters an invalid or unreachable phone number | SMS not sent; error message prompting a valid number; user can retry |
| E-001.3 | SMS OTP expires before the user enters it | OTP invalidated; user can request a new OTP (rate-limited to 3 attempts per 10 minutes) |
| E-001.4 | User completes OAuth but closes the browser before phone verification | Account exists in an unverified state; on next login, user is redirected to complete phone verification |
| E-001.5 | User attempts to access any endpoint without completing phone verification | All non-auth endpoints return `403 Forbidden` with message "Phone verification required" |
| E-001.6 | OAuth provider is temporarily unavailable | Graceful error message: "Authentication service temporarily unavailable — please try again"; no stack traces exposed |
| E-001.7 | User registers with Google, then later tries to log in with GitHub using the same email | Supabase handles account linking per its configured identity linking behavior; if not linked, user is guided to log in with the original provider |
| E-001.8 | JWT token expires during an active session | Frontend detects 401 response, attempts a silent token refresh via Supabase; if refresh fails, user is redirected to login |

---

## F-002: Assignment Upload & AI-Powered Analysis

### User Story

**As a** team leader,  
**I want to** upload an assignment document (PDF or text) and have the AI analyze it into a structured breakdown,  
**so that** my team can clearly understand the requirements, expected deliverables, and constraints without re-reading the raw document.

### Acceptance Criteria

1. Only the **Team Leader** of a Workspace can upload assignment documents — regular members cannot upload *(Decision Q6)*
2. The Team Leader can upload a document in **PDF** or **plain text** format within a Workspace
3. The document is parsed **once** upon upload, converted into a structured summary, and stored in the database (Constitution §VIII)
4. The structured summary is stored as a **JSON object** in a PostgreSQL `jsonb` column, with the following defined keys: `{ requirements: string[], constraints: string[], deliverables: string[], deadlines: { description: string, date: string }[], tools: string[] }`. A Pydantic model (`AssignmentSummary`) mirrors this structure on the backend *(Decision Q4)*
5. The raw document is **never** re-sent to the Anthropic Claude API after the initial processing — all subsequent interactions use the stored summary
6. The AI response follows the Prompt Engine pattern: requirements breakdown → step-by-step plan → recommended tools → illustrative scenarios → expected deliverable criteria (Constitution §I)
7. The AI **does not** provide direct answers to assignment questions — it provides a structured analysis that guides understanding (Constitution §I)
8. The AI auto-detects user language (**Arabic** or **English**) and responds in the same language (SRS §4.1)
9. The API call is routed through the **AI service layer** (`services/ai_service.py`) — never called directly from the route handler (Constitution §IV)
10. **10 Credits** are **reserved** (marked as "pending") from the Team Leader's balance before the AI call is made. On success, the reservation is committed. On failure, the reservation is released — no credits are lost *(Decision Q1: reserve-then-commit pattern)*
11. If the user has fewer than 10 Credits, the upload is blocked with a message: "Insufficient credits — you need 10 credits to analyze an assignment"
12. The upload input is **sanitized** for XSS and prompt injection before processing (Constitution §III)
13. User inputs embedded into prompt templates are delimited and treated as **untrusted data** (Constitution §III)
14. The endpoint requires a **valid authenticated session** and verifies the requester is the **Team Leader** of the Workspace (Constitution §V)
15. Only members of the Workspace can view the structured summary
16. Assignment upload & analysis is **rate-limited** to 5 requests per user per hour *(Decision Q15)*
17. Guided-learning compliance is enforced primarily through **strong prompt engineering**. The prompt template explicitly instructs Claude: "Do NOT provide direct answers." A lightweight **keyword check** scans responses for obvious violation patterns (e.g., "The answer is...", code blocks that solve the assignment). If detected, the system retries **once** with a reinforced prompt. If the second attempt also fails, a generic guided-learning response is returned and the incident is logged for prompt tuning. Full AI-based compliance checking is deferred to Phase 2 *(Decision Q11)*

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-002.1 | User uploads a PDF that is scanned images with no selectable text | System attempts OCR extraction; if extraction yields insufficient content, return error: "Unable to extract text from this document — please upload a text-based PDF or paste the content manually" |
| E-002.2 | User uploads an empty file or a file with only whitespace | Upload rejected: "The uploaded document contains no extractable content" |
| E-002.3 | User uploads a file exceeding the size limit (defined: 10 MB) | Upload rejected: "File exceeds the maximum size of 10 MB" |
| E-002.4 | User uploads a non-PDF, non-text file (e.g., .docx, .zip) | Upload rejected: "Unsupported file format — please upload a PDF or plain text file" |
| E-002.5 | Anthropic API is temporarily unavailable or returns an error | Reserved credits are **released** (not committed); user sees: "AI analysis temporarily unavailable — please try again"; the failed attempt is logged server-side |
| E-002.6 | Anthropic API returns a response that violates the guided-learning principle (e.g., contains direct answers) | Lightweight keyword check detects violation → retry once with reinforced prompt → if second attempt also fails, return generic guided-learning response and log the incident for prompt tuning *(Decision Q11)* |
| E-002.7 | User uploads a second document to the same Workspace (assignment update) | A new processing cycle is triggered; the new structured summary is stored as a new version; previous version is retained for reference |
| E-002.8 | User's credit balance drops to exactly 10 during the upload process (race condition) | The **reserve-then-commit** pattern handles this atomically — credits are reserved before the call, preventing double-spending from concurrent requests *(Decision Q1)* |
| E-002.9 | Document contains content in both Arabic and English | AI detects the dominant language and responds in that language; mixed-language content is preserved in the structured summary |
| E-002.10 | Document contains potentially malicious content (script tags, SQL fragments) | All content is sanitized before storage and before embedding into AI prompts; malicious fragments are escaped, not executed |
| E-002.11 | A non-Team-Leader member attempts to upload a document | Request returns `403 Forbidden`: "Only the Team Leader can upload assignment documents" *(Decision Q6)* |

---

## F-003: Workspace Creation & Member Invitation

### User Story

**As a** university student working on a group assignment,  
**I want to** create a Workspace for my assignment and invite my team members via email,  
**so that** we have a centralized space to collaborate with AI-powered tools, task management, and group communication.

### Acceptance Criteria

1. An authenticated user can create a new Workspace by providing: **assignment title**, **description** (optional), and **deadline** (optional)
2. The user who creates the Workspace is automatically designated as the **Team Leader**
3. The Team Leader can **voluntarily transfer leadership** to another Workspace member via a "Transfer Leadership" action in Workspace settings. The original leader retains membership as a regular member *(Decision Q8)*
4. One Workspace corresponds to exactly **one** assignment or project (SRS §4.2)
5. A Workspace has a **maximum of 10 members** (including the Team Leader). Invitations beyond this limit are rejected with: "Maximum team size reached (10 members)" *(Decision Q9)*
6. Team Leader can invite members by entering their **email addresses**
7. An **invitation email** is sent to each invited member via Resend + React Email (SRS §4.6)
8. If the invited email belongs to an existing AssignMind user, they see a **notification badge + invitation prompt** on their dashboard and can **accept or decline** the invitation *(Decision Q12)*
9. If the invited email does not belong to an existing user, the invitation email contains a link to register; upon registration and verification, they are auto-added to the Workspace (the registration link itself constitutes implicit acceptance)
10. Each Workspace contains: **assignment details**, **Kanban board**, and **group chat** (SRS §4.2)
11. Workspace names and all text inputs are **sanitized** before storage (Constitution §III)
12. Only Workspace members can access the Workspace's data — server-side authorization verifies membership on every request (Constitution §V)
13. Workspace creation does **not** consume Credits
14. The endpoint requires a **valid authenticated session** (Constitution §V)
15. In the MVP, Workspaces can be **archived** by the Team Leader (hidden from active dashboard for all members, data retained) but **cannot be hard-deleted**. Full deletion with cascading cleanup is deferred to Phase 2 *(Decision Q14)*

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-003.1 | Team Leader invites an email address that is already a member of the Workspace | Duplicate invitation is silently ignored; no duplicate email sent; UI shows "Already a member" |
| E-003.2 | Team Leader invites themselves | Invitation is silently ignored; user is already the Team Leader |
| E-003.3 | Invited user's registration link expires before they sign up | The invitation record persists; if the user later registers with that email, they are prompted to join the pending Workspace |
| E-003.4 | Team Leader tries to create a Workspace with an empty title | Creation blocked: "Workspace title is required" |
| E-003.5 | Workspace title contains XSS payload (e.g., `<script>alert('x')</script>`) | Input is sanitized; the script tags are escaped and stored as plain text; no script execution occurs on render |
| E-003.6 | Resend email service is temporarily unavailable | Invitation is saved to the database; a background retry mechanism re-attempts email delivery; Team Leader sees: "Invitation saved — email delivery will be retried" |
| E-003.7 | A member is removed from the Workspace | Member loses access immediately; their tasks remain on the Kanban board (reassignable by Team Leader); member's chat history is retained |
| E-003.8 | Team Leader deletes their own account | Workspace ownership transfers automatically to the longest-standing member, or the Workspace is archived if no other members exist *(Decision Q7)* |
| E-003.9 | Team Leader tries to invite an 11th member | Invitation rejected: "Maximum team size reached (10 members)" *(Decision Q9)* |
| E-003.10 | Existing user declines a Workspace invitation | Invitation is marked as declined; Team Leader is notified: "{User} declined the invitation"; the slot remains available for re-invitation *(Decision Q12)* |
| E-003.11 | Team Leader transfers leadership and then tries to perform leader-only actions | Request returns `403 Forbidden` — the former leader is now a regular member *(Decision Q8)* |

---

## F-004: Intelligent Task Distribution

### User Story

**As a** team leader,  
**I want** the AI to analyze my assignment and propose a fair, constraint-aware distribution of tasks among team members,  
**so that** work is divided equitably, respects project constraints, and every member has clear responsibilities with deadlines.

### Acceptance Criteria

1. Team Leader can request an AI-generated task distribution from within a Workspace that has an analyzed assignment (F-002 completed)
2. The AI uses the **stored structured summary** (not the raw document) to generate the distribution (Constitution §VIII)
3. Before generating the distribution, the Team Leader is shown **auto-extracted constraints** from the structured summary (the `constraints` field of the `AssignmentSummary` JSON object). These are displayed as **editable, pre-populated fields** that the Team Leader can modify, delete, or supplement with additional manual constraints before requesting the AI distribution *(Decision Q10)*
4. Each proposed task includes: **task title**, **description**, **assigned member**, **deadline** (stored as UTC `timestamptz`; displayed in each user's local timezone), and **initial status** (To Do) *(Decision Q13)*
5. The AI proposes the distribution but **does not finalize it** — the Team Leader must review and can modify assignments, deadlines, or task descriptions before confirming
6. The AI **guides** the team leader's thinking about distribution (e.g., "Consider that Task 3 depends on Task 1 — you may want to assign them sequentially") — it does **not** dictate decisions (Constitution §I)
7. **5 Credits** are **reserved** from the Team Leader's balance before the AI call. On success, the reservation is committed. On failure, the reservation is released *(Decision Q1: reserve-then-commit pattern)*
8. If the Team Leader has fewer than 5 Credits, the action is blocked: "Insufficient credits — you need 5 credits to generate a task distribution"
9. The API call goes through the **AI service layer** (Constitution §IV)
10. All inputs (member names, constraints) are **sanitized** (Constitution §III)
11. Once the Team Leader finalizes the distribution, tasks appear on the **Kanban board** in the "To Do" column
12. The endpoint requires authentication and verifies the requester is the **Team Leader** of the Workspace (Constitution §V)
13. AI task distribution is **rate-limited** to 3 requests per user per hour *(Decision Q15)*

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-004.1 | Workspace has only one member (the Team Leader) | AI proposes all tasks assigned to the Team Leader; distribution still follows the structured breakdown |
| E-004.2 | Team Leader requests distribution before an assignment has been uploaded/analyzed | Action blocked: "Please upload and analyze an assignment before generating task distribution" |
| E-004.3 | Team Leader modifies the distribution to assign all tasks to one member | System allows it (Team Leader has final authority) but displays a warning: "Uneven distribution detected — one member has been assigned all tasks" |
| E-004.4 | A non-Team-Leader member attempts to generate or finalize a task distribution | Request returns `403 Forbidden`: "Only the Team Leader can manage task distribution" |
| E-004.5 | Team Leader requests a second distribution after tasks already exist | System warns: "Generating a new distribution will replace the current task assignments — proceed?" Existing task statuses are preserved if tasks are re-assigned |
| E-004.6 | Assignment has constraints that conflict (e.g., "everyone does frontend" + "only 2 people on frontend") | AI identifies the conflict and presents it to the Team Leader: "The following constraints appear to conflict — please clarify before finalizing" |
| E-004.7 | Anthropic API fails during distribution generation | Reserved credits are **released** (not committed); user sees a retry prompt; failure is logged |
| E-004.8 | Team has more members than there are logical tasks | AI proposes paired assignments or sub-task decomposition; Team Leader reviews and adjusts |
| E-004.9 | Team Leader adds manual constraints that contradict auto-extracted constraints | AI flags the contradiction in its response and asks the Team Leader to clarify before finalizing *(Decision Q10)* |

---

## F-005: Basic Kanban Board

### User Story

**As a** team member,  
**I want to** see all my team's tasks on a Kanban board organized into columns and manually update my own task statuses,  
**so that** everyone has visibility into the project's progress at a glance.

### Acceptance Criteria

1. Each Workspace has a Kanban board with exactly **three columns**: **To Do**, **In Progress**, **Done** (SRS §4.4)
2. Tasks appear on the board after the Team Leader **finalizes** the task distribution (F-004)
3. Each task card displays: **task title**, **assigned member name**, **deadline** (displayed in the viewer's local timezone via browser `Intl` API), and **current status** *(Decision Q13)*
4. Any Workspace member can update the status of **their own assigned tasks** by moving them between columns
5. The **Team Leader** can update the status of **any task** in the Workspace
6. Task status changes are persisted to the database immediately
7. In the MVP, board updates are visible to other members **on manual page refresh only** (real-time updates via Supabase Realtime are Phase 2) *(Decision Q5)*
8. The Kanban board endpoint requires authentication and verifies Workspace membership (Constitution §V)
9. All task title and description inputs are **sanitized** (Constitution §III)
10. Task status changes do **not** consume Credits (the Team Supervisor Agent is rule-based in MVP — see F-006)

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-005.1 | Member tries to update a task assigned to another member | Action blocked: "You can only update your own tasks"; Team Leaders are exempt from this restriction |
| E-005.2 | Member moves a task backward (e.g., from "Done" back to "In Progress") | Allowed — legitimate scenario (task needs rework); status change is logged |
| E-005.3 | A task's deadline has passed and it is still in "To Do" or "In Progress" | Task card displays a **visual overdue indicator** (e.g., red border or badge); this triggers the deadline-missed email notification (F-007) |
| E-005.4 | All tasks are moved to "Done" | Workspace dashboard displays a "All tasks completed" banner; no automatic Workspace archival |
| E-005.5 | Team Leader manually adds a task outside of AI distribution | Allowed — Team Leader can create ad-hoc tasks with title, description, assigned member, and deadline |
| E-005.6 | Task title or description contains excessively long text | Frontend enforces a character limit (title: 200 chars, description: 2000 chars); backend validates and rejects over-limit inputs |
| E-005.7 | Two members attempt to update the same task simultaneously | Last-write-wins with timestamp; alternatively, optimistic concurrency control returns a conflict error prompting a refresh |
| E-005.8 | A member is removed from the Workspace but has assigned tasks | Tasks remain on the board marked as "Unassigned"; Team Leader is notified to reassign them |

---

## F-006: Group Chat with Team Supervisor Agent

### User Story

**As a** team member,  
**I want to** communicate with my team in a group chat where a Team Supervisor Agent automatically posts progress updates,  
**so that** everyone stays informed about task completions (including task name, member, and timestamp) without relying on manual status meetings.

### Acceptance Criteria

1. Each Workspace has a **single group chat** accessible to all Workspace members (SRS §4.2)
2. Any Workspace member can send text messages in the group chat
3. In the MVP, the **Team Supervisor Agent** is a **rule-based automation** (not AI-powered). When a task status changes, it posts a **formatted template message** to group chat (e.g., "{member} completed {task_title} — {time_ago}"). **No Claude API call is made** and **no credits are consumed** for these automated updates *(Decision Q16)*
4. Team Supervisor Agent messages are visually distinct from human messages (e.g., different avatar, "Bot" badge, distinct styling)
5. The Team Supervisor Agent **does not** provide direct answers to assignment questions — its role is limited to status reporting and coordination (Constitution §I)
6. Chat messages are persisted and loadable in **reverse chronological order** with pagination
7. Sending a human message in the group chat does **not** consume Credits (it is team communication, not AI chat)
8. All chat message content is **sanitized** for XSS before storage and rendering (Constitution §III)
9. The chat endpoint requires authentication and verifies Workspace membership (Constitution §V)
10. In the MVP, new messages are visible to other members via **30-second polling**. The frontend polls the chat endpoint every 30 seconds for new messages. Supabase Realtime WebSocket integration replaces polling in Phase 2 *(Decision Q5)*

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-006.1 | User sends a message containing HTML or script tags | Content is sanitized and rendered as plain text; no script execution |
| E-006.2 | User sends an empty message or whitespace-only message | Submission blocked: frontend validation prevents sending; backend rejects if bypassed |
| E-006.3 | Multiple task status changes happen within a short window (e.g., 5 tasks completed in 1 minute) | Team Supervisor Agent batches updates into a single message to avoid chat spam: "3 tasks were completed in the last 5 minutes: [list]" |
| E-006.4 | Chat history grows very large (thousands of messages) | Pagination loads messages in batches (e.g., 50 per page); older messages are loaded on scroll-up |
| E-006.5 | A message contains a very long text (>5000 characters) | Backend enforces a maximum message length; excess is truncated or the message is rejected with a character limit error |
| E-006.6 | User who is no longer a Workspace member's historical messages | Messages remain visible (attributed to "[Removed Member]"); the removed user cannot send new messages |
| E-006.7 | Team Supervisor Agent posts an update for a task that was subsequently deleted | Update remains in chat history as a historical record; no retroactive deletion of agent messages |
| E-006.8 | A deleted user's historical messages in the chat | Messages are **anonymized** — author is set to "[Deleted User]". Messages remain for team context *(Decision Q7)* |

---

## F-007: Automated Email Notifications

### User Story

**As a** user of AssignMind,  
**I want to** receive timely email notifications for important events (registration, workspace invitations, approaching deadlines, and missed deadlines),  
**so that** I never miss critical updates and my team stays accountable to deadlines.

### Acceptance Criteria

1. All emails are sent via **Resend + React Email** (SRS §4.6)
2. The following email triggers are implemented:

| # | Trigger | Recipient | Timing |
|---|---------|-----------|--------|
| N-1 | Account registration | User | Immediately on registration |
| N-2 | Account activation (phone verified) | User | Immediately on verification |
| N-3 | Credits purchase | User | Immediately on payment confirmation |
| N-4 | Added to Workspace | Invited member | Immediately on invitation |
| N-5 | 72 hours before task deadline | Assigned member | Scheduled (72h before deadline, computed in UTC) |
| N-6 | 24 hours before task deadline | Assigned member | Scheduled (24h before deadline, computed in UTC) |
| N-7 | Task deadline missed | Team Leader | When deadline passes (UTC) with task not in "Done" |

3. All deadline computations (72h, 24h, missed) are calculated against **UTC timestamps**. Deadline times displayed in email bodies are rendered in the **recipient's timezone** (stored in user profile or defaulted to UTC) *(Decision Q13)*
4. Deadline reminder emails (N-5, N-6) include: **task title**, **deadline date/time**, and a **link to the Workspace**
5. Missed deadline emails (N-7) include: **member name**, **task name**, **delay duration**, and a link to the Workspace
6. Emails are HTML-formatted using **React Email** templates with consistent AssignMind branding
7. Email sending does **not** consume user Credits
8. No sensitive data (API keys, internal IDs, JWT tokens) is included in email content (Constitution §II)
9. Email addresses are validated and sanitized before use (Constitution §III)
10. The scheduled email system runs as a **background job** (cron or task queue) that checks upcoming deadlines periodically

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-007.1 | Resend API is temporarily unavailable | Email is queued for retry with exponential backoff (max 3 retries over 1 hour); failures are logged |
| E-007.2 | A task deadline is set to less than 72 hours in the future | Only applicable reminders are sent (e.g., if deadline is 48h away, only the 24h reminder is scheduled) |
| E-007.3 | A task deadline is updated after reminder emails have already been sent | Previous scheduled reminders are cancelled; new reminders are scheduled based on the updated deadline |
| E-007.4 | A task is moved to "Done" before the deadline | Pending reminder emails for that task are **cancelled**; no missed-deadline email is sent |
| E-007.5 | Team Leader is also the assigned member who missed a deadline | Team Leader receives the missed-deadline alert (they are both leader and assignee) |
| E-007.6 | User's email address bounces or is invalid | Bounce is logged; after 3 consecutive bounces, the user's email is flagged for review; notifications are paused for that address |
| E-007.7 | A Workspace is archived while scheduled emails are pending | All pending scheduled emails for that Workspace are cancelled *(Decision Q14)* |
| E-007.8 | Multiple tasks have deadlines within the same hour | Each task generates its own notification — no batching of deadline reminders (clarity over conciseness) |
| E-007.9 | A task has no deadline set | No reminder or missed-deadline emails are generated for that task |

---

## F-008: Credit System & Lemon Squeezy Payment Integration

### User Story

**As a** user whose free Credits are depleted,  
**I want to** purchase additional Credit packages through a simple, secure payment flow,  
**so that** I can continue using AI-powered features without interruption.

### Acceptance Criteria

1. Each user has a **personal Credit balance**, visible on their dashboard — Credits are **never** shared with team members (SRS §5, Constitution — Credit isolation)
2. New accounts receive **30 free Credits** upon phone verification — this grant is one-time and non-renewable (SRS §5)
3. Credits are consumed per the following cost table:

| Action | Credits | MVP Status |
|--------|---------|------------|
| Upload and analyze new assignment | 10 | ✅ Active |
| Send a message in AI chat (Personal Agent) | 2 | ⏳ Phase 2 only |
| Generate AI task distribution for team | 5 | ✅ Active |
| Automated Agent background update | 1 | ⏳ Phase 2 only |

> **Note:** In the MVP, the "AI chat" (Personal Agent) does not exist — no chat message costs credits. The Team Supervisor Agent is rule-based and does not consume credits. Both the 2-credit and 1-credit line items activate in Phase 2 when the Personal Agent and AI-powered Supervisor Agent are introduced. The backend should define these cost constants now for Phase 2 readiness. *(Decisions Q3, Q16)*

> **Note:** When the 1-credit automated agent update activates in Phase 2, the **triggering user** (the member whose action caused the update, e.g., the member who moved the task) pays the 1 credit — not the Team Leader. *(Decision Q2)*

4. Three top-up packages are available:

| Package | Credits | Price |
|---------|---------|-------|
| Starter | 100 | $2.00 |
| Standard | 300 | $5.00 |
| Pro | 700 | $10.00 |

5. Payments are processed through **Lemon Squeezy** (Merchant of Record) — AssignMind never directly handles credit card data (SRS §3)
6. Upon clicking "Buy", user is redirected to a **Lemon Squeezy checkout page**; upon successful payment, a **webhook** notifies the backend to credit the user's balance
7. A **payment confirmation email** is sent to the user upon successful purchase (F-007, trigger N-3)
8. Credit deduction follows the **reserve-then-commit** pattern: credits are reserved (marked "pending") before the AI call, committed on success, and released on failure. This prevents double-spending from concurrent requests without needing refund logic *(Decision Q1)*
9. Credit balance is checked **before** initiating any AI API call — not after (Constitution §IV — service layer responsibility)
10. The Lemon Squeezy API key is stored **server-side only** — never exposed to the client (Constitution §II)
11. Webhook payloads from Lemon Squeezy are **verified** using the webhook signing secret before processing
12. The Lemon Squeezy webhook endpoint is **rate-limited** to 100 requests per IP per minute *(Decision Q15)*
13. The credit balance endpoint requires authentication (Constitution §V)
14. All payment-related inputs and webhook payloads are validated and sanitized (Constitution §III)

### Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| E-008.1 | User initiates a payment but cancels on the Lemon Squeezy checkout page | No credits are added; no confirmation email is sent; user is redirected back to AssignMind with their balance unchanged |
| E-008.2 | Lemon Squeezy webhook arrives but the user's account cannot be identified | Webhook payload is logged for manual investigation; credits are not applied; an admin alert is generated |
| E-008.3 | Duplicate webhook received (Lemon Squeezy retries) | Webhook handler is **idempotent** — each transaction is processed exactly once using the unique transaction/order ID as a deduplication key |
| E-008.4 | User has exactly 10 Credits and uploads an assignment (cost: 10) | Credits are reserved to 0; API call proceeds; on success, reservation is committed; user is shown a "You have 0 credits remaining — top up to continue using AI features" message |
| E-008.5 | User has 4 Credits and attempts to generate a task distribution (cost: 5) | Action is blocked: "Insufficient credits — you need 5 credits to generate a task distribution" |
| E-008.6 | Two concurrent AI actions attempt to deduct from the same user's balance simultaneously | Reserve-then-commit ensures no overdraft — the first reservation succeeds, the second is blocked if the remaining (unreserved) balance is insufficient *(Decision Q1)* |
| E-008.7 | User requests a refund | Refunds are handled through Lemon Squeezy's dashboard; upon refund webhook, the corresponding Credits are deducted from the user's balance (if balance permits) or flagged for manual review |
| E-008.8 | Lemon Squeezy API or checkout is down | User sees: "Payment service temporarily unavailable — please try again later"; no partial transactions are created |
| E-008.9 | User's credit balance reaches a low threshold (≤10 Credits) | A **low-balance warning** is displayed on the dashboard: "You have X credits remaining — consider topping up" (SRS §9, OQ-4) |
| E-008.10 | Free credits are abused by creating multiple accounts with different phone numbers | Phone verification limits this vector; additional abuse detection (IP-based, device fingerprinting) is considered for Phase 2 |

---

## Account Deletion & Data Erasure *(Decision Q7)*

When a user requests account deletion, the following cascade applies:

| Entity | Behavior |
|--------|----------|
| **User account** | Deactivated immediately; **hard-deleted after 14-day grace period** |
| **Chat messages** | **Anonymized** — author set to "[Deleted User]"; messages remain for team context |
| **Assigned tasks** | Marked as **"Unassigned"** — tasks remain on Kanban board for the team |
| **Team Leader role** | **Automatically transferred** to the longest-standing member; if no members remain, Workspace is archived |
| **Credit balance** | Forfeited upon hard deletion; not refundable |
| **Personal data** | Hard-deleted after 14-day grace period (email, phone, OAuth identifiers) |

- During the 14-day grace period, the user can **reactivate** their account by logging in
- An email is sent at the start of the grace period confirming the deletion request and explaining the 14-day window
- A final confirmation email is sent 24 hours before hard deletion
- After hard deletion, the data is irrecoverable

---

## Cross-Cutting Concerns

The following constraints apply to **every** feature above and are enforced by the [AssignMind Constitution](file:///d:/AssignMind/.specify/memory/constitution.md):

| Concern | Enforcement Rule |
|---------|-----------------|
| **Authentication** | Every endpoint validates Supabase Auth JWT server-side; unauthenticated requests → `401`; unauthorized requests → `403` (Constitution §V) |
| **Authorization** | Users access only their own Workspaces; Team-Leader-only actions are scoped (Constitution §V) |
| **Input Sanitization** | All inputs validated via Pydantic (backend) and form validation (frontend); XSS, SQL injection, and prompt injection prevention on every input surface (Constitution §III) |
| **AI Guided Learning** | No AI response ever provides a direct answer; enforced via strong prompt engineering + lightweight keyword check with one retry (Constitution §I) *(Decision Q11)* |
| **Secrets Isolation** | All API keys server-side only; `NEXT_PUBLIC_*` vars contain only non-sensitive values (Constitution §II) |
| **AI Service Layer** | All Claude API calls route through `services/ai_service.py`; credit reservation and commitment happen in this layer (Constitution §IV) |
| **Credit Model** | Reserve-then-commit pattern; per-user isolation; cost table enforced in AI service layer *(Decision Q1)* |
| **TypeScript Strict** | `strict: true` in `tsconfig.json`; no `any` types; all API response types mirrored as TypeScript interfaces (Constitution §VI) |
| **Function Size** | No function exceeds 50 lines; complex logic decomposed into helpers (Constitution §VII) |
| **Process Once** | Assignment documents parsed once → stored as `jsonb` structured summaries → never re-sent raw (Constitution §VIII) *(Decision Q4)* |
| **Error Handling** | All API errors use standardized envelope `{ "error": { "code", "message" } }`; no stack traces to client |
| **Multi-Language** | AI auto-detects Arabic or English; UI supports RTL layout for Arabic |
| **Timezone** | All datetime values stored as UTC `timestamptz`; frontend converts to local timezone for display via browser `Intl` API *(Decision Q13)* |
| **Rate Limiting** | AI-consuming and sensitive endpoints enforce per-user or per-IP rate limits (see table below) *(Decision Q15)* |

### Rate Limits

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| Assignment upload & analysis | 5 requests | per user per hour |
| AI task distribution | 3 requests | per user per hour |
| AI chat message (Phase 2) | 30 requests | per user per hour |
| Lemon Squeezy webhook | 100 requests | per IP per minute |
| General API (non-AI) | 200 requests | per user per minute |
| OTP SMS request | 3 requests | per phone per 10 min |

---

## Finalized Decisions Log

All 16 clarification questions resolved and integrated into the specification:

| # | Topic | Final Decision | Spec Sections Updated |
|---|-------|----------------|----------------------|
| Q1 | Credit deduction pattern | **Reserve-then-commit.** Credits are reserved (pending) before the AI call, committed on success, released on failure. Prevents double-spending without refund logic. | F-002 AC-10, F-004 AC-7, F-008 AC-8, E-002.5, E-002.8, E-004.7, E-008.6 |
| Q2 | Automated agent credit billing | **Triggering user pays** (Phase 2). The member whose action caused the Supervisor Agent update pays 1 credit. Not the Team Leader. In MVP, no credit cost (see Q16). | F-008 credit table note |
| Q3 | "AI chat" in MVP scope | **Phase 2 only.** No chat message costs credits in the MVP. "(Phase 2 only)" noted in credit table. Backend defines cost constant for readiness. | F-008 credit table |
| Q4 | Structured summary format | **JSON object in `jsonb` column.** Keys: `requirements`, `constraints`, `deliverables`, `deadlines`, `tools`. Pydantic model `AssignmentSummary` mirrors the structure. | F-002 AC-4 |
| Q5 | Polling interval for MVP | **Chat: 30-second polling. Kanban: manual refresh only.** Supabase Realtime replaces polling in Phase 2. | F-005 AC-7, F-006 AC-10 |
| Q6 | Assignment upload permissions | **Team Leader only.** Regular members cannot upload assignment documents. | F-002 AC-1, AC-14, E-002.11 |
| Q7 | Account deletion cascade | **Anonymize** chat messages (author → "[Deleted User]"). Tasks marked **"Unassigned."** Leadership **auto-transfers.** **14-day grace period** before hard deletion. | New "Account Deletion" section, E-003.8, E-006.8 |
| Q8 | Team Leader transfer | **Allow voluntary transfer.** "Transfer Leadership" action in Workspace settings. Original leader becomes regular member. | F-003 AC-3, E-003.11 |
| Q9 | Workspace member limit | **Max 10 members** per Workspace (including Team Leader). | F-003 AC-5, E-003.9 |
| Q10 | Constraints input method | **Both auto-extracted + manual.** Constraints from structured summary are pre-populated as editable fields. Team Leader can modify/add before generating distribution. | F-004 AC-3, E-004.9 |
| Q11 | AI response validation mechanism | **Prompt engineering + lightweight keyword check.** Retry once on violation. Generic fallback on second failure. Log for tuning. Full AI-based checking in Phase 2. | F-002 AC-17, E-002.6, Cross-Cutting Concerns |
| Q12 | Invitation acceptance flow | **Accept/decline for existing users.** Notification badge + prompt on dashboard. New users auto-join via registration link (implicit acceptance). | F-003 AC-8, E-003.10 |
| Q13 | Timezone handling | **Store UTC (`timestamptz`), display in local timezone** via browser `Intl` API. Deadline scheduling computed in UTC. | F-004 AC-4, F-005 AC-3, F-007 AC-3, Cross-Cutting Concerns |
| Q14 | Workspace deletion | **Archive only in MVP.** Team Leader can archive (hide from dashboard). Data retained. Hard deletion deferred to Phase 2. | F-003 AC-15, E-007.7 |
| Q15 | Rate limits | **Defined limits per endpoint** (see Rate Limits table). Per-user for AI endpoints; per-IP for webhooks; per-phone for OTP. | F-001 AC-12, F-002 AC-16, F-004 AC-13, F-008 AC-12, Cross-Cutting Concerns |
| Q16 | Supervisor Agent: AI or rule-based? | **Rule-based in MVP.** Posts template messages on task status changes. No AI call, no credit cost. AI-powered version with 1-credit cost activates in Phase 2. | F-006 AC-3, F-008 credit table |

---

**Version**: 1.1 | **Created**: 2026-03-06 | **Last Updated**: 2026-03-06
