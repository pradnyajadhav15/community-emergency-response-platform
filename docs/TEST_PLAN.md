# Test Plan

## Scope

| Level | Method | Where |
|---|---|---|
| API / unit | Automated, Django `APITestCase` | `backend/*/tests.py`, `backend/alerts/test_security.py` |
| Security | Automated tests + code review | `backend/alerts/test_security.py` |
| Performance | Concurrent load script | `backend/scripts/load_test.py` |
| Mobile app | Manual test cases on a physical Android device | This document |
| Admin portal | Manual test cases in Chrome | This document |
| User acceptance | Role-based scenarios run end to end | This document |

Results are recorded in [TEST_REPORT.md](TEST_REPORT.md).

## Running the automated tests

```powershell
cd backend
python manage.py test
coverage run --source=accounts,societies,alerts,incidents --omit="*/migrations/*,*/tests.py,*/test_*.py" manage.py test
coverage report
```

## Running the load test

```powershell
python manage.py runserver 0.0.0.0:8000          # terminal 1
python scripts/load_test.py --users 10 --rounds 20 --sos 10   # terminal 2
```

## Test environment

| Item | Value |
|---|---|
| Mobile device | Android phone, Expo Go and EAS preview APK |
| Browser | Google Chrome (Windows) |
| API | Render (production) and local Django dev server |
| Database | Neon PostgreSQL (production), PostgreSQL 16 (local) |
| Accounts | `resident1`, `guard1`, `secure1`, `volun1`, plus an administrator |

---

## Mobile app test cases

| ID | Area | Steps | Expected |
|---|---|---|---|
| M-01 | Login | Enter valid resident credentials, tap Sign In | SOS screen opens |
| M-02 | Login | Enter a wrong password | Error banner, stays on login |
| M-03 | Session | Close and reopen the app | Still signed in |
| M-04 | Register | Register a new volunteer | Account created, lands on incident list |
| M-05 | Register | Mismatched passwords | Error "Passwords do not match" |
| M-06 | SOS | Pick Medical, tap SOS, confirm | Alert sent dialog shows notification count |
| M-07 | SOS | Tap SOS, then Cancel in the dialog | Nothing is sent |
| M-08 | Location | Deny location permission, send SOS | Alert still sends, without GPS |
| M-09 | Location | Allow location, send SOS | GPS shown on incident detail |
| M-10 | Active alert | After sending, check SOS tab | Active alert card with status |
| M-11 | Contacts | Add a tier 1 contact | Appears under Primary Guardian |
| M-12 | Contacts | Remove a contact | Disappears after confirmation |
| M-13 | Responder | Sign in as volunteer | Incident list shown instead of SOS button |
| M-14 | Accept | Open an unclaimed incident, tap Accept & Respond | Status In Progress, system message in thread |
| M-15 | Accept | Second volunteer opens same incident | No Accept button; shows who is responding |
| M-16 | Chat | Send a message from the responder | Resident sees it within 8 seconds |
| M-17 | Resolve | Responder taps Mark Resolved | Status Resolved, removed from active list |
| M-18 | Availability | Volunteer switches availability off | Setting saved and persists after reload |
| M-19 | Inbox | Responder opens Inbox, taps an item | Opens the incident, item marked read |
| M-20 | Network | Turn off WiFi, use mobile data, send SOS | Works through the production API |
| M-21 | Network | Airplane mode, send SOS | Clear "cannot reach the server" error, no crash |
| M-22 | Sign out | Tap Sign Out in Profile | Returns to login, token cleared |

## Admin portal test cases

| ID | Area | Steps | Expected |
|---|---|---|---|
| W-01 | Login | Sign in as administrator | Dashboard loads |
| W-02 | Login | Sign in as a resident | Rejected: administrators only |
| W-03 | Dashboard | Raise an SOS from the phone | Active count increases within 15 seconds |
| W-04 | Alerts | Use the status filters | List narrows correctly |
| W-05 | Alert detail | Open an alert | Details, notification log, and thread shown |
| W-06 | Alert detail | Click the GPS link | Opens Google Maps at that point |
| W-07 | Actions | Acknowledge, then Escalate | Tier increases, new notifications in log |
| W-08 | Actions | Resolve with notes, then Close | Status Resolved, then Closed |
| W-09 | Societies | Add a society, block, and flat | Each appears in its column |
| W-10 | Users | Change a user's role | Persists after reload |
| W-11 | Users | Deactivate a user | That user can no longer sign in |
| W-12 | Users | Try to deactivate yourself | Button disabled |

---

## User acceptance scenarios

Each scenario is run with real accounts on real devices and signed off by the tester.

### UAT-1: Medical emergency, volunteer responds

1. `resident1` sends a Medical SOS with the message "Chest pain"
2. `volun1` sees it in the incident list and accepts
3. `volun1` posts "On my way" in the chat
4. `resident1` sees the responder name and the message
5. `volun1` resolves with notes
6. Administrator sees it as resolved on the dashboard and closes it

**Accept when:** every step works without errors and the dashboard totals update.

### UAT-2: Nobody responds, alert escalates

1. `resident1` sends a Fall SOS
2. Nobody accepts
3. After the response window, the scheduled job escalates to tier 2, then tier 3
4. The alert's notification log shows secondary guardian and emergency contact deliveries

**Accept when:** the tier reaches 3 and each tier's contacts appear in the log.

### UAT-3: Society onboarding by the administrator

1. Administrator creates a new society, block, and flat
2. A new user registers as a resident
3. Administrator assigns the user to the new society
4. The resident sends an SOS and it shows the correct flat and society

**Accept when:** the alert shows the new society's name and flat.

### UAT-4: Unauthorised actions are blocked

1. Try registering with the Administrator role through the API
2. As a resident, try to escalate or close an alert
3. As a volunteer from another society, try to open an alert by ID

**Accept when:** all three are refused.