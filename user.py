import sqlite3 as lite
from contextlib import closing


def init() -> None:
    with closing(lite.connect("users.db")) as u:
        u.executescript(
            """
CREATE TABLE IF NOT EXISTS "user" (
    "id"            INTEGER UNIQUE,
    "username"      TEXT NOT NULL,
    PRIMARY KEY("id")
)
"""
        )
        u.commit()


def add_user(user_id: int, username: str) -> None:
    with closing(lite.connect("users.db")) as u:
        u.execute(
            "INSERT OR IGNORE INTO user (id, username) VALUES (?, ?)",
            (
                user_id,
                username,
            ),
        )
        u.execute(
            "UPDATE user SET username = ? WHERE id = ?",
            (
                username,
                user_id,
            )
        )
        u.commit()


def get_username(user_id: int) -> str:
    with closing(lite.connect("users.db")) as u:
        try:
            name = u.execute(
                'SELECT username FROM "user" WHERE id = ?', (user_id,)).fetchone()[0]
        except TypeError:
            name = "[Error]"
    return name


def get_id(username: str) -> int:
    with closing(lite.connect("users.db")) as u:
        try:
            id = u.execute(
                'SELECT id FROM "user" WHERE username = ?', (username,)).fetchone()[0]
        except:
            id = -1
    return id
