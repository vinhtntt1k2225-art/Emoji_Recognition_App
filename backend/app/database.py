"""
Database setup with SQLite.
Tables: users, predictions
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "emoji.db")


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            predicted_emoji TEXT NOT NULL,
            predicted_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            top_predictions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"[OK] Database initialized at {DB_PATH}")


# User operations
def create_user(username: str, email: str, hashed_password: str):
    """Create a new user."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        user = conn.execute(
            "SELECT id, username, email, created_at FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(user)
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            raise ValueError("Username already exists")
        elif "email" in str(e):
            raise ValueError("Email already exists")
        raise
    finally:
        conn.close()


def get_user_by_username(username: str):
    """Get user by username."""
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id: int):
    """Get user by ID."""
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, email, created_at FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


# Prediction operations
def save_prediction(user_id: int, emoji: str, label: str, confidence: float, top_predictions: str):
    """Save a prediction to history."""
    conn = get_db()
    conn.execute(
        """INSERT INTO predictions (user_id, predicted_emoji, predicted_label, confidence, top_predictions)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, emoji, label, confidence, top_predictions)
    )
    conn.commit()
    conn.close()


def get_user_predictions(user_id: int, limit: int = 50):
    """Get prediction history for a user."""
    conn = get_db()
    predictions = conn.execute(
        """SELECT id, predicted_emoji, predicted_label, confidence, top_predictions, created_at
           FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(p) for p in predictions]
