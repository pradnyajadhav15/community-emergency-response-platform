# Database Design

PostgreSQL 16. Ten models across four Django apps.

## Entity relationship diagram

```mermaid
erDiagram
    SOCIETY ||--o{ BLOCK : contains
    BLOCK ||--o{ FLAT : contains
    FLAT ||--o{ RESIDENT_PROFILE : houses
    USER ||--o| RESIDENT_PROFILE : has
    SOCIETY ||--o{ USER : "has members"
    USER ||--o{ EMERGENCY_CONTACT : configures
    USER |o--o{ EMERGENCY_CONTACT : "linked as"
    USER ||--o{ SOS_ALERT : raises
    USER |o--o{ SOS_ALERT : "responds to"
    SOS_ALERT ||--o{ ALERT_NOTIFICATION : generates
    SOS_ALERT ||--o{ INCIDENT_MESSAGE : "has thread"
    SOS_ALERT ||--o{ RESPONDER_ASSIGNMENT : assigns
    USER ||--o{ RESPONDER_ASSIGNMENT : "assigned in"

    USER {
        bigint id PK
        string username
        string role "RESIDENT GUARDIAN VOLUNTEER SECURITY ADMIN"
        bigint society_id FK
        string phone
        string expo_push_token
        bool is_available
    }
    SOCIETY {
        bigint id PK
        string name
        string code UK
        string city
        float latitude
        float longitude
    }
    BLOCK {
        bigint id PK
        bigint society_id FK
        string name
        int total_floors
    }
    FLAT {
        bigint id PK
        bigint block_id FK
        string flat_number
        int floor
    }
    RESIDENT_PROFILE {
        bigint id PK
        bigint user_id FK
        bigint flat_id FK
        bool is_senior_citizen
    }
    EMERGENCY_CONTACT {
        bigint id PK
        bigint resident_id FK
        bigint linked_user_id FK
        string full_name
        string phone
        int escalation_level "1 2 3"
        int order
        bool is_verified
    }
    SOS_ALERT {
        bigint id PK
        bigint resident_id FK
        bigint society_id FK
        bigint flat_id FK
        bigint responder_id FK
        string category
        string status
        int escalation_level
        float latitude
        float longitude
    }
    ALERT_NOTIFICATION {
        bigint id PK
        bigint alert_id FK
        string audience
        string channel "PUSH SMS EMAIL IN_APP"
        string status "PENDING SENT FAILED READ"
        text error
    }
    INCIDENT_MESSAGE {
        bigint id PK
        bigint alert_id FK
        bigint sender_id FK
        text body
        bool is_system
    }
    RESPONDER_ASSIGNMENT {
        bigint id PK
        bigint alert_id FK
        bigint responder_id FK
        string status
    }
```

## Tables

| Model | Purpose |
|---|---|
| `User` | Custom user (extends `AbstractUser`) with one of five roles, society link, push token, availability |
| `Society` | A residential community, identified by a unique join code |
| `Block` | Tower or wing within a society |
| `Flat` | Individual dwelling within a block |
| `ResidentProfile` | Binds a user to a flat so every alert carries an exact address |
| `EmergencyContact` | A contact at escalation tier 1, 2, or 3; optionally a registered user |
| `SOSAlert` | One emergency event with category, location, status, and tier |
| `AlertNotification` | One delivery attempt per recipient per channel, with status and error text |
| `IncidentMessage` | A message on an alert's thread; system messages flagged |
| `ResponderAssignment` | A responder's engagement state for an alert |

## Constraints

| Name | Columns | Purpose |
|---|---|---|
| `uniq_contact_slot` | resident, escalation_level, order | No two contacts in the same escalation slot |
| `uniq_block_per_society` | society, name | Block names unique within a society |
| `uniq_flat_per_block` | block, flat_number | Flat numbers unique within a block |
| `uniq_assignment` | alert, responder | A responder is assigned to an alert at most once |
| `Society.code` | code | Unique join code |

## Design notes

- **Custom user model from the first migration.** Django makes swapping it later very difficult.
- **Every notification is a row.** Failures (for example, a user with no push token) stay visible instead of silently disappearing.
- **Timestamps per lifecycle stage** (`acknowledged_at`, `escalated_at`, `resolved_at`, `closed_at`) power the average-resolution-time metric.
- **`SET_NULL` on optional links** (flat, society, responder) so deleting a flat or user never deletes alert history.