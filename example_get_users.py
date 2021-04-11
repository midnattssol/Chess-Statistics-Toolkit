"""An example script showing the functionality of get_game_data_lichess together
with get_user_data_lichess. Plots Blitz rating against Bullet rating for users
fetched from 25000 games, provided their rating deviation is low enough."""


import matplotlib.pyplot as plt
import numpy as np

from utils import get_game_data_lichess, get_user_data_lichess

# Globals
FILE_PATH = "lichess_db_standard_rated_2013-01.pgn.bz2"
TAGS = {"Black", "White"}
GAMES_N = 25000
MAX_DEV = 75


def main() -> None:
    """The main function."""

    game_generator = get_game_data_lichess(FILE_PATH, TAGS, max_games=GAMES_N)

    # Samples usernames from games
    usernames = []
    for game in game_generator:
        usernames += list(game.values())

    data = [i["perfs"] for i in get_user_data_lichess(usernames)]
    data = [i for i in data if "blitz" in i and "bullet" in i]

    # Get rating and rating deviation for Blitz and Bullet
    data_btz = [(u["blitz"]["rating"], u["blitz"]["rd"]) for u in data]
    data_blt = [(u["bullet"]["rating"], u["bullet"]["rd"]) for u in data]

    # Only includes ratings with deviation below 75.
    volatile = set()

    for i in range(len(data)):
        if data_blt[i][1] >= MAX_DEV or data_btz[i][1] >= MAX_DEV:
            volatile.add(i)

    data_blt = [v[0] for i, v in enumerate(data_blt) if i not in volatile]
    data_btz = [v[0] for i, v in enumerate(data_btz) if i not in volatile]

    # Gets colors for each point.
    red = [0 for i in range(len(data_blt))]
    green = [data_blt[i] / max(data_blt) for i in range(len(data_blt))]
    blue = [data_btz[i] / max(data_btz) for i in range(len(data_btz))]

    colors = np.array([red, green, blue]).T
    axes = plt.subplots()[1]

    axes.scatter(data_blt, data_btz, c=colors, alpha=0.5)
    axes.set_xlabel("Bullet rating")
    axes.set_ylabel("Blitz rating")
    axes.set_title(f"Blitz rating compared to Bullet rating (n={len(data)})")

    plt.axis("square")
    plt.show()


if __name__ == "__main__":
    main()
