# AssignMind — Software Requirements Specification
**Version:** 1.0 | **Status:** Draft | **Date:** March 2026

---

## 1. Product Overview

**AssignMind** is an AI-powered academic team collaboration platform. It acts as an intelligent bridge between university students and AI tools.

**Core Philosophy:** The AI must never provide direct answers. It guides students through structured thinking, helping them understand problems and develop solutions themselves.

**Target Audience:** University students worldwide working on group assignments and projects.

---

## 2. The Problem

Students face these recurring challenges:
- Cannot properly decompose or understand assignment requirements
- Use AI tools with vague prompts, getting shallow and unstructured responses
- Unfair or constraint-ignoring task distribution within teams
- No real-time visibility into each team member's progress
- Communication breakdown leading to late submissions

---

## 3. Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 + Tailwind CSS (PWA-enabled) |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL via Supabase |
| Real-time | Supabase Realtime (WebSocket) |
| AI Provider | Anthropic Claude API (primary) |
| Email | Resend + React Email |
| Payments | Lemon Squeezy (Merchant of Record) |
| Auth | Supabase Auth (Google OAuth + GitHub OAuth + Phone verification) |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## 4. Core Features

### 4.1 Prompt Engine
- Maintains an internal library of structured prompt templates
- User inputs are automatically enriched with context-specific templates before being sent to the AI API
- Users never need to write complex prompts
- AI responses always include: requirements breakdown, step-by-step plan, recommended tools, illustrative scenarios, and expected deliverable criteria
- Assignment documents (PDF or text) are parsed ONCE, converted to a structured summary, and stored — never re-sent on every request (saves ~70% token cost)
- Auto-detects user language (Arabic or English) and responds accordingly

### 4.2 Workspace System
- Team Leader creates a Workspace for a single assignment or project
- Members are invited via email
- Each member must have an individual AssignMind account
- Each Workspace contains: assignment details, Kanban board, group chat, individual member chats
- One Workspace = one assignment or project

### 4.3 Intelligent Task Distribution
- AI analyzes assignment requirements and proposes a fair, constraint-aware task distribution
- Respects explicit project constraints (e.g., all members must contribute to both frontend and backend)
- Team Leader reviews and modifies the proposed distribution before finalizing
- Each task has: assigned member, deadline, and status

### 4.4 Kanban Board
- Columns: To Do / In Progress / Done
- Tasks are automatically assigned to correct columns by the Team Supervisor Agent
- Team members can manually update task status
- Real-time updates for all Workspace members (Phase 2)

### 4.5 Multi-Agent AI System

**Personal Agent (one per member per Workspace):**
- Aware only of the assigned member's tasks
- Assists via a private chat interface
- Automatically reports task completions to the Team Supervisor Agent
- Private — not visible to other team members

**Team Supervisor Agent (one per Workspace):**
- Receives updates from all Personal Agents
- Automatically updates the shared Kanban board
- Posts progress notifications to group chat (e.g., "Ahmed completed Task 1.3 — UI Mockups — 10 minutes ago.")
- Sends alert emails to Team Leader when a member misses a deadline

### 4.6 Automated Email Notifications
All emails sent via Resend + React Email.

| Trigger | Recipient |
|---------|-----------|
| Account registration | User (verification email) |
| Account activation | User (welcome email) |
| Credits purchase | User (payment confirmation) |
| Added to Workspace | Member (invitation email) |
| 72 hours before task deadline | Assigned member (reminder) |
| 24 hours before task deadline | Assigned member (final reminder) |
| Task deadline missed | Team Leader (alert with member name, task name, delay duration) |

---

## 5. Business Model — Credit-Based

- Each user has a **personal** Credit balance (not shared with team)
- New accounts receive **30 free Credits** on registration (tied to phone number, non-renewable)
- When Credits are depleted, user purchases more via Lemon Squeezy

### Credit Consumption
| Action | Credits |
|--------|---------|
| Upload and analyze new assignment | 10 |
| Send a message in AI chat | 2 |
| Generate AI task distribution for team | 5 |
| Automated Agent background update | 1 |

### Top-Up Packages
| Package | Credits | Price |
|---------|---------|-------|
| Starter | 100 | $2.00 |
| Standard | 300 | $5.00 |
| Pro | 700 | $10.00 |

**Gross margin per Credit: >96%**

---

## 6. Security & Privacy Requirements
- No API keys in client-side code
- All inputs sanitized (XSS and SQL injection prevention)
- All endpoints require authentication
- Phone number verification to prevent duplicate accounts
- GDPR-like compliance: data minimization, right to erasure, transparent data usage
- Users informed in Terms of Service that assignment content is sent to third-party AI API (Anthropic)
- No assignment data retained by AI provider beyond the API request scope

---

## 7. MVP Scope (Phase 1 — Weeks 1–3)

| Feature | Status |
|---------|--------|
| Assignment upload & AI analysis | MVP ✓ |
| Prompt Engine (internal templates) | MVP ✓ |
| Workspace creation + member invitation | MVP ✓ |
| Intelligent task distribution | MVP ✓ |
| Basic Kanban board (manual updates) | MVP ✓ |
| Group chat + Team Supervisor Agent | MVP ✓ |
| Automated email notifications | MVP ✓ |
| Credit system + Lemon Squeezy integration | MVP ✓ |
| Private chat + Personal Agent | Phase 2 |
| Real-time Kanban auto-updates (Multi-Agent) | Phase 2 |
| Full PWA + push notifications | Phase 3 |
| Third-party integrations (Notion, GitHub) | Phase 3 |

---

## 8. Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Document processing | One-time structured summary (no RAG in MVP) | Saves ~70% token cost; RAG evaluated in Phase 2 |
| Payment processing | Lemon Squeezy (MoR) | No registered business entity required |
| Mobile strategy | PWA first | Single codebase for web + mobile |
| Credit scope | Per-user (not per-team) | Prevents team conflicts over shared balance |
| Auth method | Google + GitHub OAuth + Phone verification | Prevents duplicate accounts |

---

## 9. Open Questions

| # | Question | Notes |
|---|----------|-------|
| OQ-1 | Privacy Policy details for third-party AI API data transmission | Legal review before launch |
| OQ-2 | How to handle a member who consistently misses deadlines | Options: warnings, alerts, task reassignment |
| OQ-3 | iOS PWA push notification limitations | Evaluate React Native wrapper as fallback |
| OQ-4 | Minimum Credit threshold for low-balance warning | Suggested: notify at 10 Credits remaining |
