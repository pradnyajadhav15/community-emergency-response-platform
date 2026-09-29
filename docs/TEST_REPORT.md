# Test Report

**Project:** Community Emergency Response Platform (CERP)
**Date:** 29 September 2026
**Build:** `main` branch, deployed to Render, Vercel, and EAS

## Summary

| Area | Result |
|---|---|
| Automated API tests | **45 / 45 passed** |
| Code coverage | **86%** of application code (979 statements, 139 missed) |
| Security findings | **7 found, 7 fixed**, each covered by a regression test |
| Load test | **1,000 requests, 0 errors** at 10 concurrent users |
| SOS creation latency | **172 ms average**, 206 ms p95, including notification fan-out |
| Production end-to-end | SOS from phone on mobile data appears on the live admin portal |

---

## 1. Automated tests
Ran 45 tests in 110.897s
OK

| Suite | Tests | Covers |
|---|---|---|
| `accounts` | 10 | Registration, JWT login, contact rules and privacy, availability, admin user management |
| `societies` | 4 | Society hierarchy, resident mapping, admin-only writes |
| `alerts` | 12 | SOS creation, notification routing, responder conflict, escalation tiers, analytics, scheduler endpoint |
| `alerts.test_security` | 15 | Authentication, authorization, registration abuse, workflow integrity, malformed input |
| `incidents` | 4 | Thread posting and privacy, system messages, status validation |

## 2. Code coverage

| Module | Coverage | Note |
|---|---|---|
| accounts | 71 to 100% | `views.py` 71%: contact verification codes, push-token save, directory endpoint not yet tested |
| alerts | 62 to 100% | `notifications.py` 62%: live push and email calls to external services are not exercised in tests |
| incidents | 87 to 100% | |
| societies | 72 to 100% | `views.py` 72%: resident profile self-service not yet tested |
| `seed_demo` command | 0% | Demo-data utility; runs on every production deploy but has no test |
| **Total** | **86%** | |

## 3. Security testing

Findings from code review, each fixed and then locked in by a test in `alerts/test_security.py`.

| ID | Finding | Severity | Fix | Status |
|---|---|---|---|---|
| S1 | Any visitor could self-register with the Administrator role | Critical | Registration accepts only Resident, Guardian, Volunteer, Security | Fixed |
| S2 | Any signed-in user could post into any incident thread by alert ID | High | Messages and assignments checked against alert visibility; 403 otherwise | Fixed |
| S3 | Any user who could see an alert could resolve, escalate, or close it | High | Resolve: resident, responder, or coordinator. Escalate/close: security or admin only | Fixed |
| S4 | A resident could accept their own SOS | Medium | Rejected with 400 | Fixed |
| S5 | Two simultaneous accepts could both succeed (race condition) | Medium | Row lock with `select_for_update` inside a transaction | Fixed |
| S6 | Malformed filter values (e.g. `?society=1 OR 1=1`) caused a 500 error | Low | Non-numeric filters return an empty result | Fixed |
| S7 | Accepting an alert did not create a responder assignment record | Functional | Accept creates the assignment; resolve marks it completed | Fixed |

Additional controls verified by tests:

- All protected endpoints return 401 without a token
- A forged JWT is rejected
- Weak passwords are rejected by Django's password validators
- Volunteers cannot see alerts from other societies
- Incidents must be resolved before they can be closed
- The scheduler endpoint returns 503 when unconfigured and 403 for a wrong token

Not tested: SQL injection beyond filter parameters (the Django ORM parameterises all queries), rate limiting (not implemented), and third-party penetration testing.

## 4. Performance testing

Local run: Django development server, local PostgreSQL, 10 concurrent users x 20 rounds x 5 read endpoints.

| Endpoint | Requests | Errors | Avg ms | p50 ms | p95 ms | Max ms |
|---|---|---|---|---|---|---|
| `/api/sos/` | 200 | 0 | 748 | 727 | 925 | 1423 |
| `/api/sos/active/` | 200 | 0 | 721 | 705 | 892 | 1228 |
| `/api/dashboard/stats/` | 200 | 0 | 754 | 740 | 972 | 1149 |
| `/api/auth/me/` | 200 | 0 | 758 | 736 | 953 | 1127 |
| `/api/auth/emergency-contacts/` | 200 | 0 | 746 | 736 | 909 | 984 |
| **All reads** | **1000** | **0** | **746** | **727** | **932** | **1423** |

Throughput: **13.3 requests/second**.
SOS creation with full notification fan-out, 10 sequential alerts: **avg 172 ms, p95 206 ms**.

### Analysis

- Zero errors under concurrent load.
- Latency under load is dominated by queueing. At 13.3 requests/second, each request takes roughly 75 ms of server work; with 10 users waiting, observed latency rises to about 750 ms.
- The local setup is a pessimistic baseline: the development server and a new database connection per request. Production uses gunicorn with persistent database connections.
- The time-critical path, raising an SOS, completes in under a quarter of a second.

### Improvement opportunities

| Finding | Impact | Recommendation |
|---|---|---|
| `notification_count` runs one query per alert in list responses (N+1) | List endpoints slow down as history grows | Annotate the count in the queryset |
| `/api/sos/active/` is not paginated | Large payloads in a busy society | Paginate the active list |
| Free hosting tier sleeps after idle periods | First request after a pause can take up to a minute | Scheduler pings every 15 minutes; a paid tier removes it |

## 5. Mobile app testing

Physical Android device.

| ID | Case | Result |
|---|---|---|
| M-01 | Valid login | Pass |
| M-06 | Send SOS | Pass |
| M-13 | Volunteer sees incident list | Pass |
| M-14 | Accept incident | Pass |
| M-16 | Chat between roles | Pass |
| M-20 | SOS over mobile data via production API | Pass |
| M-02 to M-05, M-07 to M-12, M-15, M-17 to M-19, M-21, M-22 | Remaining cases | Not run |

## 6. Admin portal testing

| ID | Case | Result |
|---|---|---|
| W-01 | Administrator login (production) | Pass |
| W-03 | Phone SOS appears on live dashboard | Pass |
| W-02, W-04 to W-12 | Remaining cases | Not run |

## 7. User acceptance testing

| Scenario | Result | Tester | Date |
|---|---|---|---|
| UAT-1 Medical emergency, volunteer responds | Not run | | |
| UAT-2 Escalation without response | Not run | | |
| UAT-3 Society onboarding | Not run | | |
| UAT-4 Unauthorised actions blocked | Pass (automated, `test_security.py`) | Automated | 29 Sep 2026 |

## 8. Known limitations

- SMS delivery is a console stub; no gateway is connected
- Device push on the APK requires Firebase Cloud Messaging credentials, not yet configured; alerts still arrive via in-app inbox, SMS stub, and email
- Escalation granularity in production is 15 minutes, set by the scheduler interval
- No rate limiting on authentication endpoints