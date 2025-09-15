"""
SQLite database setup and operations.
- Call init_db() once on startup to create tables, indexes, triggers.
- Includes basic insert/update functions for user profile and user record.
"""

import sqlite3
from pathlib import Path

# Always point to main.db in the same folder as this file
DB_PATH = Path(__file__).with_name("main.db")


def _connect() -> sqlite3.Connection:
    """Open a database connection with some default settings."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")      # Enforce foreign key constraints
    conn.execute("PRAGMA journal_mode = WAL;")     # Better read/write concurrency
    conn.execute("PRAGMA synchronous = NORMAL;")   # Balance between safety and speed
    return conn


def init_db() -> None:
    """Create tables, indexes, and triggers if they do not exist."""
    schema = """
    -- User profile table
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_birthday TEXT,          -- YYYY-MM-DD
        user_gender TEXT,            -- male, female
        user_height REAL CHECK(user_height IS NULL OR user_height > 0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- User record table
    CREATE TABLE IF NOT EXISTS user_record (
        user_id INTEGER NOT NULL,
        record_id INTEGER NOT NULL,            -- per-user increasing id
        user_weight REAL,
        user_bmi REAL,
        user_bmr REAL,
        user_activity_level INTEGER,
        user_tdee REAL, 
        user_goal TEXT,                        -- "cut", "maintain", "bulk"
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, record_id),
        FOREIGN KEY (user_id) REFERENCES user_profile(user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );

    -- helpful index for queries
    CREATE INDEX IF NOT EXISTS idx_user_record_user ON user_record(user_id, created_at DESC);


    -- Trigger: auto-update updated_at on user_profile
    CREATE TRIGGER IF NOT EXISTS trg_user_profile_touch_updated
    AFTER UPDATE ON user_profile
    BEGIN
        UPDATE user_profile
        SET updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id;
    END;

    -- Trigger: auto-update updated_at on user_record
    CREATE TRIGGER IF NOT EXISTS trg_user_record_touch_updated
    AFTER UPDATE ON user_record
    BEGIN
        UPDATE user_record
        SET updated_at = CURRENT_TIMESTAMP
        WHERE record_id = NEW.record_id;
    END;
    """
    with _connect() as conn:
        conn.executescript(schema)


# ===== Basic insert/update functions =====

def insert_user_profile(user_name, user_birthday, user_gender, user_height):
    with _connect() as conn:
        return conn.execute("""
            INSERT INTO user_profile (user_name, user_birthday, user_gender, user_height)
            VALUES (?, ?, ?, ?)
        """, (user_name, user_birthday, user_gender, user_height)).lastrowid


def insert_user_record(user_id, user_weight, user_bmi, user_bmr, user_activity_level, user_tdee, user_goal):
    """Insert a new record with per-user increasing record_id."""
    with _connect() as conn:
        # 1) get next record_id for this user (inside the same transaction)
        next_id = conn.execute(
            "SELECT COALESCE(MAX(record_id), 0) + 1 FROM user_record WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        # 2) insert with computed record_id
        conn.execute("""
            INSERT INTO user_record (
                user_id, record_id, user_weight, user_bmi, user_bmr, user_activity_level, user_tdee, user_goal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, next_id, user_weight, user_bmi, user_bmr, user_activity_level, user_tdee, user_goal))
        return next_id  # optional: so caller knows the per-user record number



def update_user_profile(user_id, user_name, user_birthday, user_gender, user_height):
    """Update all fields of user_profile for a given user_id."""
    with _connect() as conn:
        conn.execute("""
            UPDATE user_profile
            SET user_name = ?,
                user_birthday = ?,
                user_gender = ?,
                user_height = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_name, user_birthday, user_gender, user_height, user_id))


if __name__ == "__main__":
    # This allows you to run `python database.py` to initialize the DB
    init_db()
    print("Database initialized or verified.")


def get_profile_core(user_id: int):
    """Return (birthday_str, gender, height_m) for calculations."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT user_birthday, user_gender, user_height FROM user_profile WHERE user_id=?",
            (user_id,)
        ).fetchone()
        if not row:
            return None
        return row[0], row[1], row[2]


