# UML diagrams
Diagrams use [Mermaid](https://mermaid.js.org/) and render natively on GitHub, GitLab and in
PyCharm (Markdown preview with the Mermaid plugin).

## 1. Use case diagram
```mermaid
flowchart LR
    Admin([Admin])
    Officer([Officer])
    Auditor([Auditor])
    subgraph TaxWatch
        UC1(Login)
        UC2(Manage users)
        UC3(Register / update taxpayer)
        UC4(Deactivate taxpayer)
        UC5(Record transaction)
        UC6(View dashboard)
        UC7(Review and clear flagged transaction)
        UC8(View audit trail)
    end
    Admin --> UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8
    Officer --> UC1 & UC3 & UC5 & UC6
    Auditor --> UC1 & UC6 & UC7 & UC8
```

## 2. Class diagram (domain and business rules)
```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string full_name
        +string password_hash
        +string role
        +bool is_active
    }
    class Taxpayer {
        +int id
        +string npwpd
        +string name
        +string address
        +string category
        +bool is_active
    }
    class Transaction {
        +int id
        +int taxpayer_id
        +date trx_date
        +int amount
        +int tax_amount
        +string source
        +bool is_flagged
        +string flag_reason
        +int created_by
    }
    class AuditLog {
        +int id
        +string actor
        +string action
        +string entity
        +int entity_id
        +string detail
        +datetime created_at
    }
    class Services {
        <<module>>
        +calculate_tax(category, amount) int
        +detect_anomaly(amount, threshold, history) string
        +log_action(db, actor, action, entity, entity_id, detail)
    }
    class Security {
        <<module>>
        +hash_password(password) string
        +verify_password(password, stored) bool
        +create_access_token(username, role) string
        +decode_token(token) dict
    }
    Taxpayer "1" --> "0..*" Transaction : has
    User "1" --> "0..*" Transaction : records
    Services ..> Transaction : computes tax and flags
    Services ..> AuditLog : writes
    Security ..> User : authenticates
```

## 3. Entity-relationship diagram (PostgreSQL)
```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : creates
    TAXPAYERS ||--o{ TRANSACTIONS : has
    USERS {
        int id PK
        string username UK
        string full_name
        string password_hash
        string role
        boolean is_active
        datetime created_at
    }
    TAXPAYERS {
        int id PK
        string npwpd UK
        string name
        string address
        string category
        boolean is_active
        datetime created_at
    }
    TRANSACTIONS {
        int id PK
        int taxpayer_id FK
        date trx_date
        bigint amount
        bigint tax_amount
        string source
        boolean is_flagged
        string flag_reason
        int created_by FK
        datetime created_at
    }
    AUDIT_LOGS {
        int id PK
        string actor
        string action
        string entity
        int entity_id
        string detail
        datetime created_at
    }
```

## 4. Sequence: login
```mermaid
sequenceDiagram
    actor U as User
    participant FE as Next.js
    participant API as FastAPI
    participant DB as PostgreSQL
    U->>FE: Enter username and password
    FE->>API: POST /api/auth/login (form)
    API->>DB: SELECT user by username
    DB-->>API: user row
    API->>API: verify_password (constant time)
    API->>DB: INSERT audit_logs (login)
    API-->>FE: 200 {access_token, role, full_name}
    FE->>FE: store session, redirect to /dashboard
```

## 5. Sequence: record a transaction
```mermaid
sequenceDiagram
    actor O as Officer
    participant FE as Next.js
    participant API as FastAPI
    participant SVC as Services
    participant DB as PostgreSQL
    O->>FE: Submit taxpayer, amount, date
    FE->>API: POST /api/transactions (Bearer token)
    API->>API: validate token, require role admin or officer
    API->>DB: load taxpayer and last 20 amounts
    API->>SVC: calculate_tax(category, amount)
    API->>SVC: detect_anomaly(amount, threshold, history)
    API->>DB: INSERT transaction and audit_log (one DB transaction)
    DB-->>API: committed
    API-->>FE: 201 transaction (tax_amount, is_flagged)
    FE-->>O: Table refreshed, flag badge if flagged
```

## 6. State diagram: transaction review
```mermaid
stateDiagram-v2
    [*] --> Normal: amount within rules
    [*] --> Flagged: above_threshold or spike_vs_average
    Flagged --> Cleared: auditor or admin clears flag
    Normal --> [*]
    Cleared --> [*]
```

## 7. Deployment diagram
```mermaid
flowchart LR
    Browser[Browser] -->|HTTPS| FE[Next.js container :3000]
    Browser -->|HTTPS REST + JWT| API[FastAPI container :8000]
    API -->|SQLAlchemy / psycopg2| PG[(PostgreSQL 16)]
    CI[GitHub Actions] -.->|lint, tests, migrate, smoke| API
```
