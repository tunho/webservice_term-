# Database Schema (ERD)

## Entity Relationship Diagram

```
┌──────────────────┐
│      users       │
├──────────────────┤
│ id (PK)          │───┐
│ email (UQ)       │   │
│ password         │   │
│ display_name     │   │
│ role (ENUM)      │   │
│ is_active        │   │
│ is_banned        │   │
│ created_at       │   │
│ updated_at       │   │
└──────────────────┘   │
                       │ 1
                       │
                       │ N
┌──────────────────┐   │
│    calendars     │   │
├──────────────────┤   │
│ id (PK)          │   │
│ user_id (FK) ────┼───┘
│ title            │
│ description      │
│ color            │
│ created_at       │
│ updated_at       │
└──────────────────┘
        │
        │ 1
        │
    ┌───┴───┐
    │       │ N
    │       │
┌───▼───────────┐     ┌──────────────────┐
│    events     │     │      tasks       │
├───────────────┤     ├──────────────────┤
│ id (PK)       │     │ id (PK)          │
│ calendar_id   │     │ calendar_id (FK) │
│ title         │     │ title            │
│ description   │     │ description      │
│ start_at      │     │ due_date         │
│ end_at        │     │ priority (ENUM)  │
│ location      │     │ status (ENUM)    │
│ created_at    │     │ completed_at     │
│ updated_at    │     │ created_at       │
└───────────────┘     │ updated_at       │
                      └──────────────────┘
```

---

## Table Definitions (DDL)

### users
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);
```

### calendars
```sql
CREATE TABLE calendars (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);
```

### events
```sql
CREATE TABLE events (
    id VARCHAR(36) PRIMARY KEY,
    calendar_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_at DATETIME NOT NULL,
    end_at DATETIME NOT NULL,
    location VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE,
    INDEX idx_calendar_id (calendar_id),
    INDEX idx_start_at (start_at)
);
```

### tasks
```sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    calendar_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATETIME,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    status ENUM('todo', 'in_progress', 'completed', 'cancelled') DEFAULT 'todo',
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE,
    INDEX idx_calendar_id (calendar_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);
```

---

## Indexes for Performance

| Table | Column(s) | Purpose |
|-------|-----------|---------|
| users | email | Login lookup |
| users | role | Admin queries |
| calendars | user_id | User's calendars |
| events | calendar_id | Events per calendar |
| events | start_at | Date range queries |
| tasks | calendar_id | Tasks per calendar |
| tasks | status | Status filtering |
| tasks | due_date | Due date sorting |
