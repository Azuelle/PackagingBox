import random as rand
from enum import Enum, IntEnum
import os

while True:
    player_count = int(input("Player Count: "))
    if 4 <= player_count <= 6:
        break
    print("Invalid player count.")

players = [input(f"Name of player {i}: ") for i in range(player_count)]
WORDBANK = ["猫", "狗", "鸟", "火", "车", "水", "博物馆", "太阳"]


class Team:
    def __init__(self, players, wordbank):
        self.players = players
        self.wordbank = wordbank
        self.intercepts = 0
        self.misses = 0

        self.hints = []
        self.passwords = []
        self.decode_attempts = []
        self.intercept_attempts = [[]]

    def get_score(self) -> int:
        return self.intercepts - self.misses

    def game_ended(self) -> bool:
        return self.misses >= 2 or self.intercepts >= 2


team = []
rand.shuffle(players)
rand.shuffle(WORDBANK)
team.append(Team(players[: player_count // 2], WORDBANK[:4]))
team.append(Team(players[player_count // 2 :], WORDBANK[4:8]))


def print_status(index: int, round: int):
    print(
        f"""[Team {index+1}]
Intercepts {team[index].intercepts} / Misses {team[index].misses}
Word bank {team[index].wordbank}\n"""
    )

    if round > 1:
        print("[Ally]\nPasswords / Hints / Decode Attempts / Enemy Intercept Attempts")
        for i in range(round - 1):
            print(
                team[index].passwords[i],
                team[index].hints[i],
                team[index].decode_attempts[i],
                team[1 - index].intercept_attempts[i],
            )
        print("————————")
        print("[Enemy]\nPasswords / Hints / Decode Attempts / Ally Intercept Attempts")
        for i in range(round - 1):
            print(
                team[1 - index].passwords[i],
                team[1 - index].hints[i],
                team[1 - index].decode_attempts[i],
                team[index].intercept_attempts[i],
            )
        print()


round = 1
while not (team[0].game_ended() or team[1].game_ended()):
    if round >= 9:
        break
    os.system("clear")

    # Hint
    for i in range(2):
        team[i].passwords.append(rand.sample(range(1, 5), 3))
        print_status(i, round)
        print(f"Password: {team[i].passwords[-1]}")
        team[i].hints.append(
            [
                input(f"Hint #{j} (for word {team[i].passwords[-1][j]}): ")
                for j in range(3)
            ]
        )
        os.system("clear")

    # Guess
    for i in range(2):
        print_status(i, round)
        print(f"Hints: {team[i].hints[-1]}")
        team[i].decode_attempts.append(
            list(map(int, input("Enter password (separate with spaces): ").split()))
        )
        os.system("clear")

    # Intercept
    if round > 1:
        for i in range(2):
            print_status(i, round)
            print(f"Their hints: {team[1-i].hints[-1]}")
            team[i].intercept_attempts.append(
                list(map(int, input("Enter password (separate with spaces): ").split()))
            )
            os.system("clear")

    # End of round
    for i in range(2):
        if round > 1 and team[i].intercept_attempts[-1] == team[1 - i].passwords[-1]:
            team[i].intercepts += 1
        if team[i].decode_attempts[-1] != team[i].passwords[-1]:
            team[i].misses += 1
    round += 1

# Game finished

os.system("clear")
if (
    (
        (team[0].intercepts == 2 and team[0].misses == 2)
        or (team[1].intercepts == 2 and team[1].misses == 2)
    )
    or team[0].intercepts == team[1].intercepts == 2
    or team[0].misses == team[1].misses == 2
    or round == 9
):
    diff = team[0].get_score() - team[1].get_score()
    if diff == 0:
        print("Tied")
    else:
        print(f"Team {1 if diff > 0 else 2} wins")
else:
    if team[0].intercepts == 2 or team[1].misses == 2:
        print("Team 1 wins")
    if team[1].intercepts == 2 or team[0].misses == 2:
        print("Team 2 wins")
print()
for i in range(2):
    print_status(i, round)
