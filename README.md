# Community Emergency Response Platform (CERP)

Infosys Springboard Virtual Internship, Batch 3

Residents of gated societies raise an SOS with one tap. Alerts reach guardians, security staff, volunteers, and neighbours through a configurable escalation workflow, with every notification and response tracked.

## Live deployment

| Component | URL |
|---|---|
| Admin portal | https://community-emergency-response-platfo.vercel.app |
| REST API | https://community-emergency-response-platform.onrender.com |
| Django admin | https://community-emergency-response-platform.onrender.com/admin/ |

The API runs on a free tier and may take up to a minute to respond after a long idle period.

### Demo accounts (mobile app)

| Username | Role | Password |
|---|---|---|
| resident1 | Resident | Cerp@2026Pass |
| guard1 | Guardian | Cerp@2026Pass |
| secure1 | Security | Cerp@2026Pass |
| volun1 | Volunteer | Cerp@2026Pass |

Demo data only. Administrator credentials are shared separately.

## Features

- Five roles: resident, guardian, volunteer, security, administrator
- Society, block, flat, and resident mapping
- Three-tier emergency contacts with verification
- One-tap SOS with category, message, and GPS location
- Notification engine: push, SMS, email, in-app, each delivery logged
- Routing to guardians, security, available volunteers, and the community
- Automatic escalation on a configurable window, scheduled every 15 minutes
- First-responder lock, incident chat, responder assignment, full lifecycle
- Analytics: totals, resolution time, category and status breakdown, delivery rate
- Admin portal for monitoring alerts and managing societies and users

## Tech stack

| Layer | Technology |
|---|---|
| API | Django 6.1, Django REST Framework, SimpleJWT |
| Database | PostgreSQL (Neon in production) |
| Mobile | React Native, Expo SDK 57, Expo Router |
| Admin portal | Next.js (App Router) |
| Hosting | Render (API), Vercel (portal), EAS Build (APK) |
| Scheduler | GitHub Actions |

## Repository layout
backend/ Django API (accounts, societies, alerts, incidents)
mobile/ Expo mobile app
admin/ Next.js admin portal
docs/ Architecture, database, API, mobile, user manual, Postman collection
.github/ Scheduled escalation workflow

## Documentation

- [System architecture](docs/ARCHITECTURE.md)
- [Database design](docs/DATABASE.md)
- [API reference](docs/API.md) and [Postman collection](docs/CERP.postman_collection.json)
- [Mobile app](docs/MOBILE_APP.md)
- [User manual](docs/USER_MANUAL.md)
- [Test plan](docs/TEST_PLAN.md) and [test report](docs/TEST_REPORT.md)

## Local setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:
DEBUG=True
SECRET_KEY=any-long-random-string
DB_NAME=cerp_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
ESCALATION_WINDOW_MINUTES=2
CRON_TOKEN=local-dev-token

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000
```

### Admin portal

```powershell
cd admin
npm install
npm run dev
```

Opens on http://localhost:3000. Set `NEXT_PUBLIC_API_URL` to point at a non-local API.

### Mobile app

```powershell
cd mobile
npm install
npx expo start --clear
```

Set `BASE_URL` in `mobile/src/api.js` to your API address.

## Tests

45 automated API tests (86% coverage), including a dedicated security suite. See [Test plan](docs/TEST_PLAN.md) and [Test report](docs/TEST_REPORT.md).

```powershell
cd backend
python manage.py test
```

## Escalation scheduling

Locally: `python manage.py run_escalations`

Production: `.github/workflows/escalations.yml` calls `POST /api/internal/run-escalations/` every 15 minutes with the `X-Cron-Token` header. Requires repository secrets `CERP_API_URL` and `CRON_TOKEN`.