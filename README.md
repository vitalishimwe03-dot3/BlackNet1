# BlackNet // NEXUS

A private-network-inspired social and file-sharing platform with a dark cyberpunk aesthetic, built with Django + React + TypeScript.

> **A legitimate platform running on the normal internet.** No Tor routing, no anonymous marketplaces, no malware. Standard moderation and community rules apply.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Django 5, Django REST Framework, Channels, PostgreSQL, Redis, Celery |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Zustand, React Query |
| Realtime | Django Channels WebSocket (messaging + notifications) |
| Storage | Local filesystem (or S3-compatible via django-storages) |
| Infra | Docker Compose |

---

## Quick Start (Docker)

```bash
# Clone and enter the repo
cd blacknet

# Create your env
cp .env.example .env
# Edit .env and set a strong DJANGO_SECRET_KEY

# Start everything
docker compose up --build
```

First boot will:
1. Build all containers
2. Run Django migrations (auto-generated via `makemigrations`)
3. Seed demo data
4. Start the backend on `http://localhost:8000`
5. Start the frontend on `http://localhost:5173`

**Demo login:** `admin / BlackNet-Demo-2026`

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Start PostgreSQL + Redis locally or use SQLite:
export USE_SQLITE=1

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # optional demo data
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173.

---

## Project Structure

```
blacknet/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── config/              # settings, urls, asgi/wsgi, celery
│   ├── users/               # User model, auth, 2FA, sessions
│   ├── posts/               # Feed posts, comments, likes, follows
│   ├── messaging/           # Conversations, messages, WebSocket consumers
│   ├── files/               # File upload, quota, thumbnails, share links
│   ├── communities/         # Communities, channels, membership
│   ├── notifications/       # Notifications + realtime consumer
│   ├── moderation/          # Reports, audit logs
│   ├── security/            # Security events + center
│   ├── api/                 # URL routing, pagination, errors, search
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/      # Reusable UI: Avatar, NeonButton, ProgressBar...
    │   ├── pages/           # All routes: Dashboard, Feed, Messages...
    │   ├── layouts/         # AppLayout with sidebar + bottom nav
    │   ├── hooks/           # useNotificationsSocket
    │   ├── services/        # Axios API client, WebSocket helpers
    │   ├── stores/          # Zustand auth + UI stores
    │   ├── types/           # TypeScript interfaces
    │   └── utils/           # formatBytes, timeAgo, etc.
    ├── Dockerfile
    └── package.json
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register a new account |
| POST | `/api/auth/login` | Login (JWT) |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Blacklist refresh token |
| GET | `/api/users/me` | Current user profile |
| PATCH | `/api/users/me/profile` | Update profile settings |
| GET | `/api/users/{username}` | Public profile |
| POST | `/api/users/{username}/follow` | Follow/unfollow |
| GET | `/api/posts/feed` | Social feed |
| POST | `/api/posts/` | Create post |
| POST | `/api/posts/{id}/like` | Like/unlike |
| POST | `/api/posts/{id}/comments` | Add comment |
| GET | `/api/messages/` | List conversations |
| POST | `/api/messages/direct` | Open DM |
| POST | `/api/messages/{id}/send` | Send message |
| GET | `/api/files/` | List files |
| POST | `/api/files/upload` | Upload file |
| DELETE | `/api/files/{id}` | Delete file |
| POST | `/api/files/{id}/share` | Create share link |
| GET | `/api/files/usage` | Storage usage stats |
| GET | `/api/communities/` | List communities |
| POST | `/api/communities/` | Create community |
| POST | `/api/communities/{id}/join` | Join community |
| GET | `/api/notifications/` | List notifications |
| POST | `/api/notifications/read-all` | Mark all read |
| GET | `/api/search?q=` | Global search |
| GET | `/api/security/overview` | Security center data |
| POST | `/api/moderation/reports` | File a report |

Interactive API docs available at `/api/schema/docs`.

---

## Frontend Routes

| Path | Page |
|------|------|
| `/` | Landing page |
| `/login` | Login |
| `/register` | Registration |
| `/dashboard` | Main dashboard |
| `/feed` | Social feed |
| `/messages` | Conversations list |
| `/messages/:id` | Conversation (realtime) |
| `/files` | File explorer |
| `/vault` | Digital vault (protected) |
| `/communities` | Community discovery |
| `/communities/:id` | Community detail |
| `/notifications` | Notification center |
| `/security` | Security center |
| `/settings` | Account settings |
| `/profile/:username` | User profile |
| `/search` | Global search |
| `/admin` | Admin dashboard |

Press **Ctrl+K** anywhere to open the Command Palette.

---

## Features

- **5 GB personal storage** with quota enforcement and storage intelligence
- **Real-time messaging** via WebSockets with typing indicators and read receipts
- **Social feed** with posts, comments, likes, follows, bookmarks, and polls
- **Communities** with channels, roles, and moderation
- **Digital vault** with extra authentication gate
- **Security center** with active sessions, 2FA, login history, threat metrics
- **Share links** with expiration, download limits, and password protection
- **Notifications** delivered in real-time over WebSocket
- **Global search** across users, posts, communities, and files
- **Moderation** system with reports and audit trail
- **Admin dashboard** with Django admin + platform health overview
- **Responsive design** with sidebar + bottom navigation on mobile
- **Cyberpunk terminal aesthetic** without compromising usability

---

## Security

- JWT authentication with refresh token rotation and blacklisting
- Password validation (min 10 chars, complexity checks)
- TOTP-based two-factor authentication
- CSRF protection on all state-changing requests
- CORS configuration with credential support
- File type validation via MIME sniffing (blocks executables)
- Per-user 5 GB storage quota with accounting
- Rate limiting on auth, uploads, and messaging
- Secure WebSocket authentication
- Audit logging for security events
- Session management with revocation
- Content Security headers

---

## Environment Variables

See `.env.example` for all configuration. Key variables:

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Cryptographic secret (change in production) |
| `DJANGO_DEBUG` | Enable debug mode |
| `POSTGRES_*` | Database connection settings |
| `REDIS_URL` | Redis connection URL |
| `DEFAULT_USER_STORAGE_GB` | Default per-user storage (default: 5) |
| `USE_S3` | Enable S3-compatible storage |

---

## License

MIT