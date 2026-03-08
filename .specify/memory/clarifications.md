# AssignMind — Specification Clarifications
**Version:** 1.0 | **Date:** 2026-03-06  
**Purpose:** Identify ambiguities, underspecifications, and missing details in the MVP specification that could cause rework or wrong assumptions during technical planning.  
**Status:** ✅ All 16 decisions resolved — applied to [specification.md v1.1](file:///d:/AssignMind/.specify/memory/specification.md)

---

## How to Use This Document

Each issue below follows this format:
1. **Quote** — the unclear text from the spec
2. **Why it's ambiguous** — potential for misinterpretation or rework
3. **Clarifying question** — a specific, answerable question
4. **Suggested default** — recommended decision if you have no strong preference

Once you've answered each question, I'll update the specification accordingly.

---

## 1. Credit Deduction Timing — Before vs. After the AI Call

### Quote
> F-002 AC-9: "**10 Credits** are deducted from the uploading user's personal balance **before** the AI call is made"  
> F-002 E-002.5: "Credits are **not** deducted; user sees: 'AI analysis temporarily unavailable'"

### Why It's Ambiguous
These two statements describe conflicting flows. If credits are deducted **before** the API call, then on failure you need a **rollback** mechanism. If credits are only deducted **after** a successful call, the wording in AC-9 is wrong. This matters for the database transaction design — are we using a reserve-then-commit pattern, or deduct-then-refund-on-failure?

### Clarifying Question
**Which credit deduction pattern should we implement?**
- **(A)** Reserve → Call API → Commit on success / Release on failure (two-phase)
- **(B)** Deduct first → Call API → Refund on failure (deduct-then-rollback)
- **(C)** Check balance → Call API → Deduct only on success (optimistic)

### Suggested Default
**(A) Reserve-then-commit.** Mark credits as "pending" before the call, then finalize the deduction on success or release them on failure. This prevents double-spending from concurrent requests (unlike option C) without needing refund logic (unlike option B).

---

## 2. Automated Agent Credit Billing — Whose Balance?

### Quote
> F-006 AC-8: "Team Supervisor Agent automated updates consume **1 Credit** from the system or the triggering user's balance"

### Why It's Ambiguous
"The system **or** the triggering user" is an either/or with no decision. This needs a single answer because it affects database schema (do we need a system credit pool?) and the UX (is the user warned that moving a task will cost 1 credit?). Additionally, "the triggering user" is vague — when Ahmed moves a task to "Done", is Ahmed the triggering user? Or is it the Team Leader? Or no one, since the Agent acts autonomously?

### Clarifying Question
**Who pays the 1-credit cost when the Team Supervisor Agent posts an automated update?**
- **(A)** The user whose action triggered the update (e.g., Ahmed moves task → Ahmed pays 1 credit)
- **(B)** The Team Leader always pays for all automated updates in their Workspace
- **(C)** A system/platform credit pool absorbs the cost (no user is charged)
- **(D)** Automated updates are free in MVP; billing is deferred to Phase 2

### Suggested Default
**(A) The triggering user pays.** When Ahmed moves a task, the Supervisor Agent update costs 1 credit from Ahmed's balance. This is the fairest model and matches the "per-user, never shared" credit principle. The user should see a tooltip: "Moving a task to Done will trigger an automated team update (1 credit)."

---

## 3. "Send a message in AI chat" — Which Chat?

### Quote
> SRS §5 Credit Consumption: "Send a message in AI chat — 2 Credits"  
> F-006 AC-7: "Sending a human message in the group chat does **not** consume Credits"

### Why It's Ambiguous
The credit table says "AI chat" costs 2 credits, but the MVP scope only includes **group chat** (F-006), and the group chat is explicitly free. The **Personal Agent** private chat (which is the actual "AI chat") is listed as **Phase 2**. So in the MVP, when is a user ever charged 2 credits for a chat message? This creates a ghost entry in the credit table that may confuse developers.

### Clarifying Question
**In the MVP, is there any chat interface where users are charged 2 credits per message? Or is the "AI chat = 2 credits" cost exclusively for the Phase 2 Personal Agent?**

### Suggested Default
**The 2-credit "AI chat" cost applies exclusively to the Personal Agent (Phase 2).** In the MVP, no chat message costs credits. The credit table in the specification should note this with "(Phase 2 only)" next to the AI chat line item. The backend should still implement the cost constant so it's ready for Phase 2.

---

## 4. Structured Summary Schema — What Exactly Gets Stored?

### Quote
> F-002 AC-3: "The structured summary includes: **extracted requirements**, **identified constraints**, **deliverable expectations**, **deadline information**, and **recommended tools**"

### Why It's Ambiguous
This lists field names but doesn't define their data types or structure. Are these freeform text blocks? Structured JSON objects with specific keys? Array fields? This directly impacts the database schema, the prompt template that generates the summary, and the frontend components that render it. If one developer builds it as a JSON blob and another expects Markdown, that's a rework day.

### Clarifying Question
**What is the storage format for the structured summary?**
- **(A)** A single Markdown/text field stored as-is from the AI response
- **(B)** A JSON object with defined keys (e.g., `{ requirements: string[], constraints: string[], deliverables: string[], deadlines: { description: string, date: string }[], tools: string[] }`)
- **(C)** Separate database columns for each section

### Suggested Default
**(B) A JSON object with defined keys**, stored in a `jsonb` column in PostgreSQL. This gives us structured access for task distribution (F-004), frontend rendering, and future search/filtering, while remaining flexible. Define a Pydantic model (`AssignmentSummary`) that mirrors this structure.

---

## 5. Polling Interval for MVP Chat & Kanban

### Quote
> F-005 AC-7: "board updates are visible to other members **on page refresh**"  
> F-006 AC-11: "new messages are visible to other members **on page refresh or polling**"

### Why It's Ambiguous
The Kanban board says "page refresh" only. The chat says "page refresh **or polling**." Are these intentionally different, or is polling implied for both? If we implement polling for chat, what's the interval — 5 seconds? 30 seconds? This has direct backend load implications. 10 users × 5 workspaces × 5-second polling = 600 requests/minute from polling alone.

### Clarifying Question
**For the MVP, should we implement:**
- **(A)** Manual refresh only for both Kanban and chat (simplest, zero background load)
- **(B)** Manual refresh for Kanban, polling for chat (chat feels more real-time)
- **(C)** Polling for both Kanban and chat

**If polling, what interval?**
- **(X)** 10 seconds (near-real-time feel, higher load)
- **(Y)** 30 seconds (reasonable compromise)
- **(Z)** 60 seconds (minimal load, but feels sluggish)

### Suggested Default
**(B) Manual refresh for Kanban, 30-second polling for chat.** Chat has higher urgency expectations than a Kanban board. 30 seconds balances responsiveness with backend load. Long-polling or Supabase Realtime can replace this in Phase 2 without API changes.

---

## 6. Who Can Upload Assignments — Team Leader Only or Any Member?

### Quote
> F-002 User Story: "**As a** team leader, **I want to** upload an assignment document..."  
> F-002 AC-1: "User can upload a document in PDF or plain text format within a Workspace"

### Why It's Ambiguous
The user story says "team leader," but the acceptance criteria says "user" (generic). Can any Workspace member upload an assignment, or only the Team Leader? This is a significant authorization decision — if any member can upload, they can spend 10 credits and overwrite the analysis. If only the leader can upload, it creates a bottleneck.

### Clarifying Question
**Who is permitted to upload assignment documents to a Workspace?**
- **(A)** Team Leader only
- **(B)** Any Workspace member (and each upload costs the uploader 10 credits)

### Suggested Default
**(A) Team Leader only.** The assignment document defines the Workspace's scope and drives task distribution. Allowing any member to overwrite it is risky. This also matches the leader-centric workflow in F-004 (only the leader finalizes distribution).

---

## 7. Right to Erasure — Cascade Behavior Unspecified

### Quote
> Constitution, Security & Privacy: "Users can request deletion of their account and all associated data (assignment content, chat history, workspace membership)"

### Why It's Ambiguous
If User A deletes their account, what happens to:
- Chat messages they sent in group chats? (E-006.7 says "[Removed Member]" — but is this GDPR-compliant?)
- Tasks they were assigned to? (E-005.8 says "marked as Unassigned")
- Workspaces they created as Team Leader? (E-003.8 says "ownership transfers")
- The structured summary they uploaded?

The spec has edge cases spread across features but no unified deletion cascade flow. A developer implementing the "Delete Account" API could easily miss half of these.

### Clarifying Question
**When a user requests account deletion, which of the following apply?**
1. Chat messages are **anonymized** (author set to "[Deleted User]") or **hard-deleted**?
2. Their tasks are **reassigned to unassigned** or **deleted entirely**?
3. If they were Team Leader, does ownership transfer happen **automatically** or is it a **manual admin process**?
4. Is there a **grace period** (e.g., 30 days) before hard deletion, allowing the user to recover their account?

### Suggested Default
1. **Anonymized** — messages remain for team context but author is set to "[Deleted User]"
2. **Reassigned to unassigned** — tasks stay on the board for the team
3. **Automatic transfer** to the longest-standing member; if no members remain, Workspace is archived (soft-deleted) for 30 days
4. **14-day grace period** — account is deactivated immediately, hard-deleted after 14 days with email confirmation before final deletion

---

## 8. Team Leader Transfer — Is It Possible?

### Quote
> F-003 AC-2: "The user who creates the Workspace is automatically designated as the **Team Leader**"

### Why It's Ambiguous
The spec never mentions whether Team Leader status can be voluntarily transferred to another member. It only addresses forced transfer (leader deletes account, E-003.8). In real student teams, leadership changes happen. Without specifying this, a developer might not build the transfer UI, and users will be stuck.

### Clarifying Question
**Can a Team Leader voluntarily transfer leadership to another Workspace member in the MVP?**

### Suggested Default
**Yes.** The Team Leader can select a Workspace member and transfer leadership via a "Transfer Leadership" action in Workspace settings. The original leader retains membership as a regular member. This is a low-effort feature (one API endpoint, one UI button) that prevents a common pain point.

---

## 9. Workspace Member Limit — How Many?

### Quote
> The specification doesn't mention a maximum number of members per Workspace.

### Why It's Ambiguous
Without a limit, a Workspace could have 100 members, making the AI task distribution impractical and the group chat chaotic. It also affects the AI prompt — sending 100 member names + constraints to Claude would consume significant tokens. The SRS mentions "group assignments," which typically have 3–8 members.

### Clarifying Question
**What is the maximum number of members per Workspace?**

### Suggested Default
**10 members per Workspace.** This covers the largest realistic university team size while keeping AI token usage manageable. Display a clear error if the Team Leader tries to invite beyond this limit.

---

## 10. "Constraints" in Task Distribution — Where Do They Come From?

### Quote
> F-004 AC-3: "The distribution respects **explicit project constraints** (e.g., 'all members must contribute to both frontend and backend')"

### Why It's Ambiguous
Where does the Team Leader input these constraints? Are they:
- Extracted automatically from the assignment document by the AI?
- Manually entered by the Team Leader in a constraints text field?
- Both?

This affects the UI (does the task distribution screen have a constraints input?), the prompt template (does it include both extracted and manual constraints?), and the structured summary schema.

### Clarifying Question
**How are project constraints provided to the AI for task distribution?**
- **(A)** Automatically extracted from the assignment structured summary only
- **(B)** Manually entered by the Team Leader in a text field before generating the distribution
- **(C)** Both — extracted constraints are pre-populated; Team Leader can edit/add more

### Suggested Default
**(C) Both.** The structured summary from F-002 already extracts constraints. These are shown as pre-populated fields that the Team Leader can edit, delete, or supplement before requesting the AI distribution. This gives the most flexibility with the least effort per interaction.

---

## 11. AI Response Validation — How Is "Guided Learning" Enforced?

### Quote
> E-002.6: "AI service layer applies post-processing validation; non-compliant responses are flagged and reprocessed with reinforced guardrails"

### Why It's Ambiguous
"Post-processing validation" is vague. What does this validation look like technically? Keyword scanning? A second AI call to check compliance? Regex patterns? "Reprocessed with reinforced guardrails" — does this mean automatic retry with a modified prompt? How many retries? What happens if it fails 3 times?

### Clarifying Question
**What is the concrete mechanism for validating that AI responses comply with the guided-learning principle?**

### Suggested Default
**For MVP, rely on strong prompt engineering rather than post-processing validation.** The prompt template should explicitly instruct Claude: "Do NOT provide direct answers. Always respond with guiding questions, breakdowns, and reasoning scaffolds." Add a lightweight keyword check (scan for obvious answer patterns like "The answer is..." or code blocks that solve the assignment). If detected, retry once with a reinforced prompt. If the second attempt also fails, return a generic guided-learning response and log the incident for prompt tuning. Full AI-based compliance checking is deferred to Phase 2.

---

## 12. Invitation Acceptance Flow — Explicit Accept or Auto-Join?

### Quote
> F-003 AC-6: "If the invited email belongs to an existing AssignMind user, they can **accept the invitation** and join the Workspace immediately"  
> F-003 AC-7: "upon registration and verification, they are **auto-added** to the Workspace"

### Why It's Ambiguous
For existing users, there's an explicit "accept" step. For new users, it's "auto-added." Are these intentionally different? If an existing user gets invited, do they see a notification/prompt to accept, or are they auto-added too? The word "can" in AC-6 implies choice — but if it's auto-added for new users, why require acceptance for existing ones?

### Clarifying Question
**For existing users who are invited to a Workspace, is the flow:**
- **(A)** Auto-join (added immediately, notified by email, no acceptance required)
- **(B)** Accept/decline (user sees an invitation prompt and must explicitly accept)

### Suggested Default
**(B) Accept/decline for existing users.** Users should have agency over which Workspaces they join — an unwanted invitation shouldn't force membership. New users who register through an invitation link have already implicitly accepted by clicking it. Show a notification badge + invitation prompt on the dashboard for existing users.

---

## 13. Timezone Handling for Deadlines

### Quote
> F-004 AC-4: "Each proposed task includes: task title, description, assigned member, **deadline**"  
> F-007 N-5/N-6: "72 hours before task deadline / 24 hours before task deadline"

### Why It's Ambiguous
"Deadline" is not specified as timezone-aware or timezone-naive. If a team spans multiple timezones (common for online universities), does "72 hours before deadline" use the server's timezone, the Team Leader's timezone, or the assigned member's timezone? A 72-hour reminder sent at the wrong time defeats its purpose.

### Clarifying Question
**How should deadlines and scheduled notifications handle timezones?**
- **(A)** All deadlines stored in UTC; displayed in the user's local timezone (detected from browser)
- **(B)** Deadlines stored with an explicit timezone set by the Team Leader during workspace creation
- **(C)** Deadlines are date-only (no time component), notifications sent at a fixed time (e.g., 9 AM in the recipient's local timezone)

### Suggested Default
**(A) Store in UTC, display in local timezone.** The Team Leader sets a deadline with a date and time; the frontend converts to UTC before sending to the backend. All scheduled email logic runs against UTC. The frontend renders deadlines in the viewer's local timezone using the browser's `Intl` API. This is the standard pattern and requires no timezone selection UI.

---

## 14. Workspace Deletion — Is It Supported?

### Quote
> E-007.7: "A Workspace is deleted while scheduled emails are pending — All pending scheduled emails for that Workspace are cancelled"

### Why It's Ambiguous
The edge case references Workspace deletion, but no feature spec describes **how** a Workspace is deleted, **who** can delete it, or **what** happens to all associated data (tasks, chat history, assignment summaries, member associations). It's mentioned as an edge case without being a specified capability.

### Clarifying Question
**In the MVP, can Workspaces be deleted?**
- **(A)** Yes — Team Leader can delete; all data is soft-deleted (recoverable for 30 days)
- **(B)** Yes — Team Leader can delete; all data is hard-deleted immediately
- **(C)** No — Workspaces can only be archived (hidden from dashboard, data retained)
- **(D)** Not in MVP — defer to Phase 2

### Suggested Default
**(C) Archive only.** The Team Leader can "archive" a Workspace, hiding it from the active dashboard for all members. Data is retained. This avoids data loss scenarios and the complexity of cascading deletes in the MVP. Full deletion with cascading cleanup can be added in Phase 2.

---

## 15. Rate Limiting — No Specific Limits Defined

### Quote
> Constitution, Security & Privacy: "API endpoints must enforce rate limits to prevent abuse, especially on AI-consuming routes (chat, analysis, task distribution)"

### Why It's Ambiguous
The constitution mandates rate limiting but specifies no numbers. What are the limits? Per user? Per IP? Per endpoint? Without defined limits, a developer will either pick arbitrary numbers or skip implementation entirely.

### Clarifying Question
**What rate limits should be enforced on AI-consuming endpoints?**

### Suggested Default

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| Assignment upload & analysis | 5 requests | per user per hour |
| AI task distribution | 3 requests | per user per hour |
| AI chat message (Phase 2) | 30 requests | per user per hour |
| Lemon Squeezy webhook | 100 requests | per IP per minute |
| General API (non-AI) | 200 requests | per user per minute |
| OTP SMS request | 3 requests | per phone per 10 min |

---

## 16. The Team Supervisor Agent in MVP — AI or Rule-Based?

### Quote
> SRS §4.5: "Team Supervisor Agent — receives updates from all Personal Agents, automatically updates the shared Kanban board, posts progress notifications to group chat"  
> MVP Scope: "Group chat + Team Supervisor Agent ✓"

### Why It's Ambiguous
The SRS describes the Supervisor Agent as part of a "Multi-Agent AI System" that "receives updates from Personal Agents." But Personal Agents are Phase 2. In the MVP, what is the Supervisor Agent actually doing? Is it:
- A true AI agent making Claude API calls?
- A rule-based automation that listens to task status changes and posts formatted messages?

If it's just rule-based (task moved to Done → post message), it doesn't need AI calls at all, which changes the credit model (should it still cost 1 credit if no AI is involved?).

### Clarifying Question
**In the MVP (without Personal Agents), is the Team Supervisor Agent:**
- **(A)** An AI-powered agent that calls Claude to generate contextual progress messages (costs 1 credit per update)
- **(B)** A rule-based automation that posts template messages when task statuses change (e.g., "{member} completed {task} — {time_ago}") — no AI call, no credit cost
- **(C)** Rule-based for status posts (free), but AI-powered for deadline alerts sent to the Team Leader (costs 1 credit)

### Suggested Default
**(B) Rule-based in the MVP.** Without Personal Agents to feed it context, there's nothing for an AI to reason about. The Supervisor Agent should be a simple event listener: when a task status changes, post a formatted template message to group chat. **No AI call, no credit cost.** This simplifies the MVP significantly. The 1-credit "automated agent background update" cost activates in Phase 2 when Personal Agents exist and the Supervisor Agent uses AI to synthesize multi-member progress.

---

## Summary of Open Decisions

| # | Topic | Suggested Default | Priority |
|---|-------|-------------------|----------|
| 1 | Credit deduction pattern | Reserve-then-commit | 🔴 High |
| 2 | Automated agent credit billing | Triggering user pays | 🔴 High |
| 3 | "AI chat" in MVP scope | Phase 2 only; note in spec | 🟡 Medium |
| 4 | Structured summary format | JSON object in `jsonb` column | 🔴 High |
| 5 | Polling interval for MVP | Chat: 30s polling; Kanban: refresh only | 🟡 Medium |
| 6 | Assignment upload permissions | Team Leader only | 🟡 Medium |
| 7 | Account deletion cascade | Anonymize messages, 14-day grace period | 🟡 Medium |
| 8 | Team Leader transfer | Allow voluntary transfer | 🟢 Low |
| 9 | Workspace member limit | Max 10 members | 🟡 Medium |
| 10 | Constraints input method | Both auto-extracted + manual | 🟡 Medium |
| 11 | AI response validation mechanism | Prompt engineering + keyword check | 🔴 High |
| 12 | Invitation acceptance flow | Accept/decline for existing users | 🟡 Medium |
| 13 | Timezone handling | Store UTC, display local | 🔴 High |
| 14 | Workspace deletion | Archive only in MVP | 🟢 Low |
| 15 | Rate limits | Defined limits per endpoint | 🟡 Medium |
| 16 | Supervisor Agent: AI or rule-based? | Rule-based in MVP (no credit cost) | 🔴 High |

---

**Next Step:** Answer each question (or accept the suggested defaults), and I'll update the specification with the finalized decisions.
