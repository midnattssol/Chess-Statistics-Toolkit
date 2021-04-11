"""An example script showing the functionality of
get_users_from_country_chesscom. Plots length of usernames by country as
percentage of total number of names."""

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from utils import get_users_from_country_chesscom


ISO_CODES = {"XW": ("Wales", "#eb6746"), "XS": ("Scotland", "#95a4f0")}


def main() -> None:
    """The main function."""

    axes = plt.subplots()[1]
    width = 0.35
    offset = - (width / 1.8)

    longest_name_length = 0

    for iso_a2 in ISO_CODES:
        # Gets lengths for each country.
        users = get_users_from_country_chesscom(iso_a2)
        count_dict = dict(Counter([len(user) for user in users]))

        keys = np.array(list(count_dict.keys()))
        keys.sort()

        values = np.array([count_dict[k] for k in keys])
        values = 100 * values / np.sum(values)

        # Plots the data.
        axes.bar(
            keys + offset,
            values,
            width,
            label=ISO_CODES[iso_a2][0],
            color=ISO_CODES[iso_a2][1]
        )

        offset *= -1
        longest_name_length = max(longest_name_length, max(keys))

    axes.set_xlabel("Number of characters in name")
    axes.set_ylabel("Percentage of total names")
    axes.set_title("Chess.com username length by country")
    axes.set_xticks(range(longest_name_length + 2))
    axes.legend()

    plt.show()


if __name__ == "__main__":
    main()
