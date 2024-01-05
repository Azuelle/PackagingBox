import sqlite3 as lite
import json
from enum import IntEnum
from contextlib import closing

# CONSTS


class STATUS(IntEnum):
    OPEN = 0
    INGAME = 1


# LIST


def init() -> None:
    with closing(lite.connect("lobby.db")) as lobby:
        lobby.execute(
            """
CREATE TABLE IF NOT EXISTS lobby (
    "id"            INTEGER UNIQUE,
    "owner"         INTEGER NOT NULL,
    "players"       TEXT NOT NULL,
    "status"        INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
)
"""
            # TODO utilize index & use a new table for storing [players]
        )


def get_lobby_list() -> list:
    with closing(lite.connect("lobby.db")) as lobby:
        lobby_list = lobby.execute("SELECT * FROM lobby").fetchall()
    return lobby_list


# LOBBY


def create_lobby(owner_id: int) -> int:
    with closing(lite.connect("lobby.db")) as lobby:
        lobby.execute(
            "INSERT INTO lobby (owner, players, status) VALUES (?, ?, ?)",
            (
                owner_id,
                json.dumps([owner_id]),
                STATUS.OPEN,
            ),
        )
        lobby.commit()
        id = lobby.execute("SELECT MAX(id) FROM lobby").fetchone()[0]
    return id


def remove_lobby(id: int) -> None:
    with closing(lite.connect("lobby.db")) as lobby:
        lobby.execute("DELETE FROM lobby WHERE id = ?", (id,))
        lobby.commit()


# STATUS


def get_lobby_status(id: int) -> STATUS:
    with closing(lite.connect("lobby.db")) as lobby:
        status = lobby.execute(
            "SELECT status FROM lobby WHERE id = ?", (id,)
        ).fetchone()[0]
    return status


def set_lobby_status(id: int, status: STATUS) -> None:
    with closing(lite.connect("lobby.db")) as lobby:
        lobby.execute("UPDATE lobby SET status = ? WHERE id = ?", (status, id))
        lobby.commit()


# PLAYER


def add_player(lobby_id: int, player_id: int) -> None:
    with closing(lite.connect("lobby.db")) as lobby:
        l = lobby.execute("SELECT * FROM lobby WHERE id = ?", (id,)).fetchone()[0]
        if l is not None:
            print(l)


def remove_player(lobby_id: int, player_id: int) -> None:
    with closing(lite.connect("lobby.db")) as lobby:
        l = lobby.execute("SELECT * FROM lobby WHERE id = ?", (id,)).fetchone()[0]
        players = l


# FOR TESTING

if __name__ == "__main__":
    init()
    print(get_lobby_list())
    print(id := create_lobby(23333))
    print(get_lobby_list())
    print(get_lobby_status(id))
    set_lobby_status(id, STATUS.INGAME)
    print(get_lobby_status(id))
    print(get_lobby_list())
    add_player(id, 2048)
    remove_player(id, 2048)
    remove_lobby(id)
