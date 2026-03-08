# AssignMind — Deployment Guide

## Table of Contents

1. [Backend — Railway](#backend--railway)
2. [Frontend — Cloudflare Pages](#frontend--cloudflare-pages)
3. [Database — Supabase](#database--supabase)
4. [Post-Deployment Verification](#post-deployment-verification)

---

## Backend — Railway

### Prerequisites

- [Railway account](https://railway.app)
- GitHub repository connected to Railway

### Step 1: Create Railway Project

1. Go to Railway dashboard → **New Project** → **Deploy from GitHub Repo**
2. Select the `AssignMind` repository
3. Set the **Root Directory** to `backend/`

### Step 2: Configure Build

Railway will auto-detect the `Dockerfile` and `railway.toml`. The config uses:

- **Builder**: Dockerfile
- **Health check**: `GET /api/health`
- **Start command**: `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

Go to **Variables** tab and add all required variables:

```
# App
APP_ENV=production
FRONTEND_URL=https://your-frontend.pages.dev
BACKEND_URL=https://your-backend.up.railway.app

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/assignmind
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret

# AI
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4096
ANTHROPIC_TIMEOUT_SECONDS=60

# Email
RESEND_API_KEY=re_...
EMAIL_FROM=noreply@assignmind.com
EMAIL_FROM_NAME=AssignMind

# Payments
LEMON_SQUEEZY_API_KEY=ls_...
LEMON_SQUEEZY_WEBHOOK_SECRET=whsec_...
LEMON_SQUEEZY_STORE_ID=12345
LEMON_SQUEEZY_STARTER_VARIANT_ID=67890
LEMON_SQUEEZY_STANDARD_VARIANT_ID=67891
LEMON_SQUEEZY_PRO_VARIANT_ID=67892

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Step 4: Deploy

Railway will automatically deploy on push to `main`. Manual deploy:

1. Go to **Deployments** tab → **Deploy**
2. Watch the build logs for successful migration output
3. Wait for the health check to pass (green status)

### Step 5: Verify

```bash
curl https://your-backend.up.railway.app/api/health
# Expected: {"status": "ok"}
```

---

## Frontend — Cloudflare Pages

### Prerequisites

- [Cloudflare account](https://dash.cloudflare.com)
- GitHub repository connected

### Step 1: Create Pages Project

1. Go to **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
2. Select the `AssignMind` repository
3. Configure build settings:
   - **Root directory**: `frontend/`
   - **Build command**: `npm run pages:build`
   - **Build output directory**: `.vercel/output/static`
   - **Node.js version**: `20`

### Step 2: Set Environment Variables

Go to **Settings** → **Environment Variables** and add:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

> **Important**: Only `NEXT_PUBLIC_*` variables — never put secrets here (Constitution §II).

### Step 3: Deploy

Cloudflare Pages deploys automatically on push to `main`.

For manual deployment:
```bash
cd frontend
npm run pages:build
npx wrangler pages deploy .vercel/output/static --project-name=assignmind-frontend
```

### Step 4: Custom Domain (Optional)

1. Go to **Custom Domains** → **Set up a custom domain**
2. Add your domain (e.g., `app.assignmind.com`)
3. Follow DNS configuration instructions
4. Update `FRONTEND_URL` in Railway backend variables to match

---

## Database — Supabase

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) → **New Project**
2. Note down:
   - Project URL (`SUPABASE_URL`)
   - Anon key (`NEXT_PUBLIC_SUPABASE_ANON_KEY`)
   - Service role key (`SUPABASE_SERVICE_ROLE_KEY`)
   - JWT secret (`SUPABASE_JWT_SECRET`)
   - Connection string (`DATABASE_URL`)

### Step 2: Auth Configuration

1. Go to **Authentication** → **Providers**
2. Enable **Google OAuth** with your credentials
3. Set redirect URL: `https://your-frontend.pages.dev/auth/callback`

### Step 3: Phone Verification

1. Go to **Authentication** → **Phone Auth**
2. Enable and configure Twilio or Vonage for OTP

### Step 4: Run Migrations

The Railway deployment runs `alembic upgrade head` automatically on each deploy.

For manual migration:
```bash
cd backend
alembic upgrade head
```

---

## Post-Deployment Verification

### Backend Health Check

```bash
curl https://your-backend.up.railway.app/api/health
```

### Webhook Configuration

1. Go to [Lemon Squeezy Dashboard](https://app.lemonsqueezy.com)
2. **Settings** → **Webhooks** → **Create Webhook**
3. URL: `https://your-backend.up.railway.app/api/webhooks/lemon-squeezy`
4. Secret: Same value as `LEMON_SQUEEZY_WEBHOOK_SECRET`
5. Events: `order_created`, `order_refunded`

### CORS Verification

Ensure `FRONTEND_URL` in Railway matches your actual frontend domain exactly. The backend CORS middleware only allows this specific origin.

### Checklist

- [ ] Backend health check returns `{"status": "ok"}`
- [ ] Frontend loads login page
- [ ] Google OAuth redirect works
- [ ] Phone verification sends OTP
- [ ] Lemon Squeezy webhook configured
- [ ] Email sending works (test invitation)
- [ ] AI analysis works (test assignment upload)
- [ ] CORS allows frontend → backend requests

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 on Railway | Check build logs; likely missing env var or migration failure |
| CORS errors | Verify `FRONTEND_URL` matches the exact deployed frontend URL |
| Auth redirect fails | Check Supabase redirect URL includes `/auth/callback` |
| Webhook signature fails | Ensure `LEMON_SQUEEZY_WEBHOOK_SECRET` matches Lemon Squeezy dashboard |
| Emails not sending | Verify `RESEND_API_KEY` and sender domain is verified in Resend |
