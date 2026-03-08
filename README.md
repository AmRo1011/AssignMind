# AssignMind

> AI-powered academic task management platform for university team assignments.

AssignMind helps student teams break down assignments, distribute tasks fairly using AI, track progress via Kanban boards, and communicate through group chat — all guided by a Supervisor Agent that never gives direct answers.

## Architecture

```
frontend/          → Next.js 16 (TypeScript, TailwindCSS 4)
backend/           → FastAPI (Python 3.13, SQLAlchemy, asyncpg)
```

| Service           | Provider           |
|-------------------|--------------------|
| Auth              | Supabase Auth      |
| Database          | Supabase PostgreSQL|
| AI                | Anthropic Claude   |
| Payments          | Lemon Squeezy      |
| Email             | Resend             |
| Backend Hosting   | Railway            |
| Frontend Hosting  | Cloudflare Pages   |

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (or Supabase project)

### 1. Clone & Setup Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required variables:
- `DATABASE_URL` — PostgreSQL connection string
- `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` / `SUPABASE_JWT_SECRET`
- `ANTHROPIC_API_KEY`
- `RESEND_API_KEY`
- `LEMON_SQUEEZY_WEBHOOK_SECRET`

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start Backend

```bash
uvicorn main:app --reload --port 8000
```

### 5. Setup Frontend

```bash
cd frontend
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 6. Start Frontend

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic layer
│   ├── routers/         # FastAPI route handlers
│   ├── prompts/         # AI prompt templates
│   └── utils/           # Shared utilities
├── alembic/             # Database migrations
├── tests/               # pytest test suite
├── main.py              # Application entry point
├── Dockerfile           # Production container
└── railway.toml         # Railway deployment config

frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # Reusable UI components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # API client, Supabase client
│   └── types/           # TypeScript interfaces
├── wrangler.toml        # Cloudflare Pages config
└── package.json
```

## Key Features

- **AI Assignment Analysis** — Upload PDF/TXT, get structured breakdown
- **Smart Task Distribution** — AI proposes fair task assignments
- **Kanban Board** — Drag-and-drop task management
- **Group Chat** — Team communication with Supervisor Agent
- **Credit System** — Reserve-commit pattern for AI usage
- **Email Notifications** — Deadline reminders, invitation alerts
- **Guided Learning** — AI never provides direct answers

## Testing

```bash
cd backend
pytest -v
```

All 16 tests pass covering AI service, assignments, credits, tasks, emails, and end-to-end flows.

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guides.

## Constitution

Development follows strict rules defined in `.specify/memory/constitution.md`:
- No direct answers from AI (P0)
- No secrets in client code
- Input sanitization everywhere
- All endpoints authenticated
- TypeScript strict mode, no `any`
- Functions ≤ 50 lines max

## License

Private — All rights reserved.
