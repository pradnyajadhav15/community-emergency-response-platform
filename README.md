# Community Emergency Response Platform (CERP)

Infosys Springboard Virtual Internship - Batch 3

A platform that lets residents of gated societies raise emergency SOS alerts,
which are routed to guardians, security staff, volunteers and neighbours through
a configurable escalation workflow.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.1 + Django REST Framework |
| Database | PostgreSQL 16 |
| Auth | JWT (djangorestframework-simplejwt) |
| Push | Expo Push API |
| SMS | Console stub (Twilio-ready) |
| Email | Django SMTP backend |
| Mobile | React Native (Expo) - in progress |
| Admin portal | Next.js - in progress |

## Modules Implemented

1. Resident, Society and Emergency Contact Management
2. SOS Alert and Emergency Notification Engine
3. Community Response and Guardian Escalation
4. Incident Lifecycle and Chat
5. Reporting and Analytics

## Local Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:

```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=cerp_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
ESCALATION_WINDOW_MINUTES=15
```

Then:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

## Demo Accounts

| Username | Role | Password |
|---|---|---|
| resident1 | Resident | Resident@2026 |
| guard1 | Guardian | Cerp@2026Pass |
| secure1 | Security | Cerp@2026Pass |
| volun1 | Volunteer | Cerp@2026Pass |

## Escalation Workflow

1. Resident triggers SOS. Primary guardian, security, volunteers and the
   community are notified immediately.
2. If nobody accepts within `ESCALATION_WINDOW_MINUTES`, the alert escalates
   to the secondary guardian.
3. After a further window, it escalates to the emergency contact tier.
4. Any responder can accept, chat on the incident thread, and resolve.

Escalation runs via a management command, scheduled with Task Scheduler or cron:

```powershell
python manage.py run_escalations
```

## API

Import `docs/CERP.postman_collection.json` into Postman. Run **Login** first -
it stores the JWT automatically for all other requests.

Full endpoint reference: `docs/API.md`

## Database Schema

- **User** - custom model with 5 roles, society link, push token, availability
- **Society / Block / Flat / ResidentProfile** - physical structure and mapping
- **EmergencyContact** - 3 escalation tiers per resident
- **SOSAlert** - alert with category, location, status, escalation level
- **AlertNotification** - one row per recipient per channel, with delivery status
- **IncidentMessage** - chat thread per alert
- **ResponderAssignment** - responder status tracking
