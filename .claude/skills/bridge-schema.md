# Bridge Database Schema Skill

> Trigger: mentions of SQL, database, table names, column names, relationships, migrations

## Tables Overview

```
users ─────────────┬──── specialist_profiles ──┬── specialist_domains
                   │                           ├── specialist_languages
                   │                           ├── specialist_competencies
                   │                           └── reviews (specialist_id)
                   ├── reviews (client_id)
                   ├── chat_rooms (client_id / specialist_id)
                   └── messages (sender_id)
```

## Table: users
| Column        | Type                          | Constraints              |
|---------------|-------------------------------|--------------------------|
| id            | UUID                          | PK, default uuid4        |
| email         | VARCHAR                       | UNIQUE, NOT NULL, INDEX  |
| password_hash | VARCHAR                       | NOT NULL                 |
| role          | ENUM('client','specialist')   | NOT NULL                 |
| full_name     | VARCHAR                       | NOT NULL                 |
| avatar_url    | VARCHAR                       | NULLABLE                 |
| created_at    | TIMESTAMP WITH TZ             | DEFAULT now()            |
| updated_at    | TIMESTAMP WITH TZ             | DEFAULT now(), ON UPDATE |

## Table: specialist_profiles
| Column       | Type                                    | Constraints                  |
|--------------|-----------------------------------------|------------------------------|
| id           | UUID                                    | PK                           |
| user_id      | UUID FK → users(id)                     | UNIQUE                       |
| headline     | VARCHAR(200)                            | NULLABLE                     |
| bio          | TEXT                                    | NULLABLE                     |
| hourly_rate  | DECIMAL(10,2)                           | NULLABLE                     |
| availability | ENUM('available','busy','vacation')     | DEFAULT 'available'          |
| avg_rating   | FLOAT                                   | DEFAULT 0                    |
| review_count | INTEGER                                 | DEFAULT 0                    |

## Table: specialist_domains
| Column        | Type                        | Constraints             |
|---------------|-----------------------------|-------------------------|
| id            | UUID                        | PK                      |
| specialist_id | UUID FK → specialist_profiles(id) | CASCADE          |
| domain        | VARCHAR                     | NOT NULL                |

Domain values: 'AI/ML', 'Law', 'Finance', 'Data Science', 'Design', 'Technology', 'Cybersecurity', 'Biotech', 'Science', 'Business', 'Startups', 'Education', 'Writing', 'Cloud'

## Table: specialist_languages
| Column        | Type                                           | Constraints    |
|---------------|------------------------------------------------|----------------|
| id            | UUID                                           | PK             |
| specialist_id | UUID FK → specialist_profiles(id)              | CASCADE        |
| language      | VARCHAR                                        | NOT NULL       |
| proficiency   | ENUM('basic','conversational','fluent','native')| DEFAULT fluent |

## Table: specialist_competencies
| Column        | Type                        | Constraints             |
|---------------|-----------------------------|-------------------------|
| id            | UUID                        | PK                      |
| specialist_id | UUID FK → specialist_profiles(id) | CASCADE          |
| label         | VARCHAR                     | NOT NULL                |
| url           | VARCHAR                     | NOT NULL                |
| display_order | INTEGER                     | DEFAULT 0               |

## Table: reviews
| Column        | Type                        | Constraints                                  |
|---------------|-----------------------------|----------------------------------------------|
| id            | UUID                        | PK                                           |
| specialist_id | UUID FK → specialist_profiles(id) |                                        |
| client_id     | UUID FK → users(id)         |                                              |
| rating        | INTEGER                     | CHECK (1-5)                                  |
| comment       | TEXT                        | NULLABLE                                     |
| created_at    | TIMESTAMP WITH TZ           | DEFAULT now()                                |
| **UNIQUE**    | (specialist_id, client_id)  | One review per client/specialist pair        |

## Table: chat_rooms
| Column        | Type                        | Constraints                            |
|---------------|-----------------------------|----------------------------------------|
| id            | UUID                        | PK                                     |
| client_id     | UUID FK → users(id)         |                                        |
| specialist_id | UUID FK → users(id)         |                                        |
| created_at    | TIMESTAMP WITH TZ           | DEFAULT now()                          |
| **UNIQUE**    | (client_id, specialist_id)  | One room per pair                      |

## Table: messages
| Column     | Type                        | Constraints             |
|------------|-----------------------------|-------------------------|
| id         | UUID                        | PK                      |
| room_id    | UUID FK → chat_rooms(id)    | CASCADE                 |
| sender_id  | UUID FK → users(id)         |                         |
| content    | TEXT                        | NOT NULL                |
| is_read    | BOOLEAN                     | DEFAULT false           |
| created_at | TIMESTAMP WITH TZ           | DEFAULT now()           |

## SQLAlchemy Model Locations
- `app/models/user.py` — User, UserRole, Base
- `app/models/specialist.py` — SpecialistProfile, SpecialistDomain, SpecialistLanguage, SpecialistCompetency, Availability, LanguageProficiency
- `app/models/review.py` — Review
- `app/models/chat.py` — ChatRoom, Message

## Important Rules
- **ALWAYS use async** queries: `await db.execute(select(...))`
- **UUID primary keys** on all tables
- **Alembic migrations** for every schema change — never edit DB directly
- **One review per (specialist, client)** — enforced by UNIQUE constraint
- **One chat room per (client, specialist)** — enforced by UNIQUE constraint
- **Ratings 1-5 only** — enforced by CHECK constraint
