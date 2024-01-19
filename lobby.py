import sqlite3 as lite
import json
from enum import IntEnum
from contextlib import closing
import user

MAX_PLAYERS = 6

# UTILS


class Lobby:
    # * Update this every time the `lobby` database structure is changed
    def __init__(self, row):
        self.id = row[0]
        self.owner = row[1]
        self.player_count = row[2]
        self.max_players = row[3]
        self.game_state = row[4]

    def __str__(self) -> str:
        status = f"#{self.id} — Owner {user.get_username(self.owner)} — "

        with closing(lite.connect("lobbies.db")) as lobby:
            players = lobby.execute(
                "SELECT player_id FROM player WHERE lobby_id = ?", (id,)
            ).fetchall()
        players = [user.get_username(p[0]) for p in players]
        status += f"{self.player_count} / {self.max_players} player{'s' if self.player_count >
                                                                    1 else ''}" + f"[{", ".join([p for p in players])}] — "

        status += "Waiting" if check_ingame(id) else "In Game"
        return status


# DB


def init() -> None:
    with closing(lite.connect("lobbies.db")) as lobby:
        lobby.executescript(
            """
CREATE TABLE IF NOT EXISTS "lobby" (
    "id"            INTEGER UNIQUE,
    "owner_id"      INTEGER NOT NULL,
    "player_count"  INTEGER NOT NULL,
    "max_players"   INTEGER NOT NULL,
    "game_state"    TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "player" (
    "lobby_id"	INTEGER NOT NULL,
    "player_id"	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "session" (
    "player_id"	INTEGER UNIQUE NOT NULL,
    "session"	INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS "lobby_id" ON "lobby" (
    "id"	DESC
);
CREATE INDEX IF NOT EXISTS "lobby_player" ON "player" (
    "lobby_id"	DESC,
    "player_id"
);
"""
        )
        lobby.commit()


# LOBBY

def get_lobby_list() -> list[Lobby]:
    with closing(lite.connect("lobbies.db")) as lobby:
        lobby_list = lobby.execute("SELECT * FROM lobby").fetchall()
    return [Lobby(l) for l in lobby_list]


def get_lobby_list_str() -> list[str]:
    return [str(l) for l in get_lobby_list()]


def create_lobby(owner_id: int) -> int:
    with closing(lite.connect("lobbies.db")) as lobby:
        id = lobby.execute(
            'INSERT INTO "lobby" (owner_id, player_count, max_players) VALUES (?, ?, ?)',
            (
                owner_id,
                1,
                MAX_PLAYERS,
            ),
        ).lastrowid  # Yes this should be the Auto Incremented ID (somehow)
        lobby.execute(
            'INSERT INTO "player" (lobby_id, player_id) VALUES (?, ?)',
            (
                id,
                owner_id,
            ),
        )
        lobby.commit()
    return id


def remove_lobby(id: int) -> None:
    with closing(lite.connect("lobbies.db")) as lobby:
        lobby.execute("DELETE FROM lobby WHERE id = ?", (id,))
        lobby.execute("DELETE FROM player WHERE lobby_id = ?", (id,))
        lobby.commit()


# STATUS


def check_ingame(id: int) -> bool:
    return get_game_state(id) is None


def get_lobby_status(id: int) -> str:
    with closing(lite.connect("lobbies.db")) as lobby:
        l = lobby.execute("SELECT * FROM lobby WHERE id = ?", (id,)).fetchone()
        if l is not None:
            status = str(Lobby(l))
        else:
            status = "Lobby not found"
    return status


def get_game_state(lobby_id: int) -> dict:
    with closing(lite.connect("lobbies.db")) as lobby:
        state = lobby.execute(
            "SELECT game_state FROM lobby WHERE id = ?", (lobby_id,)
        ).fetchone()[0]
    return state


def set_game_state(lobby_id: int, state: dict) -> None:
    with closing(lite.connect("lobbies.db")) as lobby:
        lobby.execute(
            "UPDATE lobby SET game_state = ? WHERE id = ?",
            (json.dumps(state), lobby_id),
        )
        lobby.commit()


# PLAYER


def change_owner(lobby_id: int, owner_id: int) -> None:
    with closing(lite.connect("lobbies.db")) as lobby:
        lobby.execute(
            "UPDATE lobby SET owner_id = ? WHERE id = ?", (owner_id, lobby_id)
        )
        lobby.commit()


def add_player(lobby_id: int, player_id: int) -> None:
    with closing(lite.connect("lobbies.db")) as lobby:
        # Update lobby table
        count = lobby.execute(
            "SELECT player_count FROM lobby WHERE id = ?", (id,)
        ).fetchone()[0]
        lobby.execute(
            "UPDATE lobby SET player_count = ? WHERE id = ?", (count + 1, id))

        # Update player table
        lobby.execute(
            "INSERT INTO player (lobby_id, player_id) VALUES (?, ?)",
            (lobby_id, player_id),
        )

        lobby.commit()


def remove_player(lobby_id: int, player_id: int) -> None:
    with closing(lite.connect("lobbies.db")) as lobby:
        l = lobby.execute("SELECT * FROM lobby WHERE id = ?",
                          (lobby_id,)).fetchone()
        if l is not None:
            l = Lobby(l)
            # Check if owner
            if l.owner == player_id:
                print("is owner")
                if l.player_count == 1:
                    # Sole player in lobby, simply delete lobby
                    remove_lobby(lobby_id)
                    return
                else:
                    # Fetch one player from lobby
                    next_owner = lobby.execute(
                        "SELECT player_id FROM player WHERE lobby_id = ? AND player_id != ?",
                        (lobby_id, player_id),
                    ).fetchone()[0]
                    # Exchange owner of the lobby and proceed as normal
                    change_owner(lobby_id, next_owner)

            # Update lobby table
            lobby.execute(
                "UPDATE lobby SET player_count = ? WHERE id = ?",
                (l.player_count - 1, lobby_id),
            )

            # Update player table
            lobby.execute(
                "DELETE FROM player WHERE lobby_id = ? AND player_id = ?",
                (lobby_id, player_id),
            )

            lobby.commit()
        else:
            print("Lobby not found")


# FOR TESTING

if __name__ == "__main__":
    print("=== TESTING LOBBY.PY ===")

    print("\n>>> Init & print lobby list")
    init()
    user.init()
    user.add_user(23333, "owo")
    user.add_user(2048, "qwq")
    print(get_lobby_list())

    print("\n>>> Create new lobby owned by owo(23333)")
    print("ID:", id := create_lobby(23333))
    print(get_lobby_list())
    print(get_lobby_status(id))

    print("\n>>> Update lobby gamestate")
    set_game_state(id, {})
    print(get_game_state(id))
    print(get_lobby_list())
    print(get_lobby_status(id))

    print("\n>>> Add player qwq(2048)")
    add_player(id, 2048)
    print(get_lobby_list())
    print(get_lobby_status(id))

    print("\n>>> Remove player owo(23333) by ID")
    remove_player(id, 23333)
    print(get_lobby_list())
    print(get_lobby_status(id))

    print("\n>>> Remove player qwq(2048) by name")
    remove_player(id, user.get_id("qwq"))
    print(get_lobby_list())
    print(get_lobby_status(id))

    print("\n>>> Recreate lobby owned by owo(23333)")
    print("ID:", id := create_lobby(23333))
    print(get_lobby_list())
    print(get_lobby_status(id))

    print("\n>>> Remove lobby")
    remove_lobby(id)
    print(get_lobby_list())
