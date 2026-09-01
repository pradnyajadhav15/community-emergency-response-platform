# CERP API Reference

Base URL: `http://127.0.0.1:8000/api`

All endpoints except register and login require:
`Authorization: Bearer <access_token>`

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register/` | Create account. Body: username, email, password, password2, first_name, role, phone |
| POST | `/auth/login/` | Returns `access`, `refresh`, and `user` object |
| POST | `/auth/refresh/` | Body: `{"refresh": "..."}` |
| POST | `/auth/token-verify/` | Validate a token |
| GET/PATCH | `/auth/me/` | Current user profile |
| POST | `/auth/push-token/` | Save Expo push token |
| POST | `/auth/availability/` | Body: `{"is_available": true}` |
| GET | `/auth/directory/` | Security, volunteers and admins in your society |

Roles: `RESIDENT`, `GUARDIAN`, `VOLUNTEER`, `SECURITY`, `ADMIN`

## Emergency Contacts

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/auth/emergency-contacts/` | List or create |
| GET/PUT/DELETE | `/auth/emergency-contacts/{id}/` | Detail operations |
| POST | `/auth/emergency-contacts/{id}/send_code/` | Send verification code |
| POST | `/auth/emergency-contacts/{id}/verify/` | Body: `{"code": "123456"}` |

Escalation levels: `1` primary guardian, `2` secondary guardian, `3` emergency contact.

## Society Management

| Method | Endpoint | Description |
|---|---|---|
| CRUD | `/societies/` | Society records. Write requires admin |
| CRUD | `/blocks/` | Filter with `?society={id}` |
| CRUD | `/flats/` | Filter with `?block={id}` |
| CRUD | `/residents/` | Resident profiles |
| GET/POST | `/residents/my-profile/` | Own profile shortcut |

## SOS Alerts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/sos/` | Raise an alert. Triggers full notification fan-out |
| GET | `/sos/` | List alerts visible to the caller's role |
| GET | `/sos/active/` | Unresolved alerts only |
| GET | `/sos/{id}/` | Alert detail |
| GET | `/sos/{id}/notifications/` | Delivery log for this alert |
| POST | `/sos/{id}/acknowledge/` | Mark as seen |
| POST | `/sos/{id}/accept/` | Claim as responder. 409 if already claimed |
| POST | `/sos/{id}/escalate/` | Manually move to the next tier |
| POST | `/sos/{id}/resolve/` | Body: `{"resolution_notes": "..."}` |
| POST | `/sos/{id}/close/` | Final closure |
| GET | `/notifications/` | Caller's in-app notifications |
| POST | `/notifications/{id}/mark-read/` | Mark read |

Categories: `MEDICAL`, `FIRE`, `SECURITY`, `ACCIDENT`, `FALL`, `OTHER`

Statuses: `OPEN`, `ACKNOWLEDGED`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`, `CLOSED`, `CANCELLED`

### Visibility rules

- Admin and staff see all alerts
- Security and volunteers see alerts in their society
- Residents see their own alerts plus those of anyone who listed them as a linked guardian

## Incident Response

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/incidents/messages/` | Chat thread. Filter with `?alert={id}` |
| GET/POST | `/incidents/assignments/` | Responder assignments |
| POST | `/incidents/assignments/{id}/set-status/` | Body: `{"status": "ON_SITE"}` |

Assignment statuses: `INVITED`, `ACCEPTED`, `DECLINED`, `ON_SITE`, `COMPLETED`

## Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/stats/` | Totals, breakdown by category and status, average resolution time, notification delivery counts |

## Notification Channels

Every alert generates one `AlertNotification` row per recipient per channel:

- `PUSH` - Expo Push API. Fails gracefully when no token is registered
- `SMS` - console output in development, Twilio-ready in production
- `EMAIL` - console backend in development, SMTP in production
- `IN_APP` - stored for retrieval via `/notifications/`
