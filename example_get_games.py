"""An example script showing the functionality of get_game_data_lichess. Plots
the results of 25 000 rated Lichess games played in December 2012 (ignoring
games that aren"t Blitz, Bullet or Classical)."""


import matplotlib.pyplot as plt
import numpy as np

from utils import get_game_data_lichess


# Globals
FILE_PATH = "lichess_db_standard_rated_2013-01.pgn.bz2"
TAGS = {"Event", "Result"}
TIME_FORMATS = ["Bullet", "Blitz", "Classical"]
GAME_RESULTS = ["1-0", "1/2-1/2", "0-1"]
GAME_RESULTS_LABELS = ["White win", "Draw", "Black win"]
COLORS = ["#fffa9e", "#eb6746", "#a6174c"]
GAMES_N = 25000


def main() -> None:
    """The main function."""

    data = np.zeros([3, 3])
    game_generator = get_game_data_lichess(FILE_PATH, TAGS, max_games=GAMES_N)

    # Goes through the games and tallies their results.
    for game in game_generator:
        time_format = game["Event"].split()[1]
        if time_format not in TIME_FORMATS:
            continue
        time_index = TIME_FORMATS.index(time_format)
        result_index = GAME_RESULTS.index(game["Result"])
        data[result_index][time_index] += 1

    # Scales results for each time format.
    for i in range(len(data)):
        data[:, i] *= 100 / np.sum(data[:, i])

    # Displays the plot.
    axes = plt.subplots()[1]
    cumulative_sum = np.zeros(data.shape[0])

    for i, value in enumerate(data):
        axes.bar(
            TIME_FORMATS,
            value,
            0.35,
            bottom=cumulative_sum,
            label=GAME_RESULTS_LABELS[i],
            color=COLORS[i]
        )
        cumulative_sum += data[i]

    axes.set_ylabel("Results (percentage)")
    axes.set_title("Lichess game results by time format")
    axes.legend()

    plt.show()


if __name__ == "__main__":
    main()
