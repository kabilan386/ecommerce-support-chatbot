# AI-Based E-Commerce Customer Support Chatbot

An intelligent, full-stack customer support system for e-commerce platforms featuring an AI chatbot, voice input, sentiment analysis, automatic ticket management, and an admin analytics dashboard.

---

## Features

| Feature | Description |
|---|---|
| AI Chatbot | GPT-4o powered responses with SSE streaming and 10-turn context window |
| Voice Bot | Browser-native Web Speech API for STT input and TTS output |
| Sentiment Analysis | Per-message VADER scoring with green/yellow/red badge display |
| Ticket Management | Auto-creation on unresolved queries with sentiment-based escalation |
| Customer Portal | View and track personal support tickets |
| Admin Dashboard | Real-time KPIs and Chart.js bar/line visualizations |
| JWT Auth | Stateless authentication with customer / agent / admin roles |

---

## Architecture

```
┌─────────────────────────────────┐
│         Browser (Next.js 14)    │
│  Login · Chat · Tickets · Dash  │
└────────────┬────────────────────┘
             │ HTTP / SSE
┌────────────▼────────────────────┐
│       FastAPI Backend           │
│  /auth  /chat  /tickets  /analytics │
│  ChatService · SentimentService │
│  TicketService · AuthService    │
└────────────┬────────────────────┘
             │ SQLAlchemy async
┌────────────▼────────────────────┐
│       PostgreSQL 15             │
│  users · conversations          │
│  messages · tickets             │
│  analytics_events               │
└─────────────────────────────────┘
```

---

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Chart.js, Axios
- **Backend**: FastAPI, Python 3.11, SQLAlchemy 2 (async), Pydantic v2
- **AI/NLP**: OpenAI GPT-4o, VADER Sentiment
- **Database**: PostgreSQL 15
- **Auth**: JWT (python-jose), bcrypt (passlib)
- **DevOps**: Docker, Docker Compose

---

## Project Structure

```
ecommerce-support-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, lifespan
│   │   ├── config.py        # Settings from env
│   │   ├── database.py      # Async SQLAlchemy engine
│   │   ├── dependencies.py  # get_current_user, require_admin
│   │   ├── models/          # ORM: User, Conversation, Message, Ticket, AnalyticsEvent
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── routers/         # auth, chat, tickets, analytics
│   │   └── services/        # auth_service, chat_service, sentiment_service, ticket_service
│   ├── tests/               # pytest tests (auth, chat, tickets)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # ChatWindow, VoiceButton, TicketCard, KPICard
│   │   ├── lib/             # api.ts (Axios), auth.ts (localStorage)
│   │   └── types/           # Shared TypeScript interfaces
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Setup & Running

### Prerequisites
- Docker and Docker Compose installed
- An OpenAI API key

### 1. Configure environment

```bash
cd backend
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY and SECRET_KEY
```

### 2. Start all services

```bash
docker-compose up --build
```

Services will start on:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Run without Docker (development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection URL | `postgresql+asyncpg://postgres:postgres@db:5432/ecommerce_support` |
| `SECRET_KEY` | JWT signing secret | `change-me-in-production` |
| `OPENAI_API_KEY` | Your OpenAI API key | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry in minutes | `1440` (24h) |

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create account, returns JWT |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Get current user profile |

### Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat/conversations` | Create new conversation |
| GET | `/chat/conversations` | List user's conversations |
| POST | `/chat/message` | Send message, SSE streaming response |

### Tickets
| Method | Endpoint | Description |
|---|---|---|
| GET | `/tickets` | List tickets (own for customer, all for admin) |
| POST | `/tickets` | Create ticket manually |
| GET | `/tickets/{id}` | Get single ticket |
| PATCH | `/tickets/{id}` | Update ticket status/priority |

### Analytics (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/kpi` | Total/open/resolved tickets, avg sentiment |
| GET | `/analytics/trends` | Daily ticket counts + sentiment trend (30 days) |

---

## Running Tests

```bash
cd backend
pip install aiosqlite pytest-asyncio
pytest tests/ -v
```

Expected: 11 tests pass across auth, chat, and ticket flows.

---

## Automatic Ticket Creation

When the AI cannot resolve a query, it appends `[UNRESOLVED]` to its response. The backend then:
1. Detects the flag in the streamed response
2. Auto-categorizes the issue (order/return/refund/shipping/payment/general) via keyword matching
3. Sets priority to **HIGH** if the last 3 user messages all have sentiment score < -0.3
4. Creates and persists the ticket linked to the conversation

---

## User Roles

| Role | Access |
|---|---|
| `customer` | Chat, own tickets |
| `agent` | Chat, all tickets |
| `admin` | Chat, all tickets, analytics dashboard |

New registrations default to `customer`. Role can be updated directly in the database.
