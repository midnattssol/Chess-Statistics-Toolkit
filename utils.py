"""Defines functions for getting data for user groups.

Functions
---------
get_user_data_lichess : Gets data for a list of users from lichess.
get_user_data_chesscom : Gets data for a list of users from chess.com.
get_users_from_country_chesscom : Gets all users from a country on chess.com.

get_game_data_lichess : Gets selected game data from a Lichess database file.
dump_jsonbz2 : Dumps data into a .json.bz2 file.
load_jsonbz2 : Loads data from a .json.bz2 file.
"""

import urllib.request
import json
import concurrent.futures as cf
import bz2
import math


def dump_jsonbz2(obj: object, file_path: str) -> None:
    """BZ2-compresses and dumps a JSON-serializable object."""
    with open(file_path, "wb") as file:
        file.write(bz2.compress(json.dumps(obj).encode("utf-8")))


def load_jsonbz2(file_path: str) -> object:
    """Loads and decompresses a BZ2-compressed JSON file."""
    with open(file_path, "rb") as file:
        return json.loads(bz2.decompress(file.read()))


def get_game_data_lichess(file_path: str, tags: set, max_games: int = math.inf):
    """Returns a generator generating dictionaries of game data from a
    BZ2-compressed PGN-formatted file.

    These files are available here for Lichess:
    https://database.lichess.org

    Parameters
    ----------
    file_path : str
    tags : set
        A set of tags that will be saved for each current_game. Possible tags
        are Event, Site, White, Black, Result, UTCDate, UTCTime, WhiteElo,
        BlackElo, WhiteRatingDiff, BlackRatingDiff, ECO, Opening, TimeControl,
        and Terminator.
    max_games : int, optional
        A maximum number of games to analyze. Defaults to math.inf, which will
        analyze the whole file.

    Example
    -------
    >>> file_path = "lichess_db_standard_rated_2013-01.pgn.bz2"
    >>> tags = {"Event", "Result", "UTCDate"}
    >>> for i in get_game_data_lichess(file_path, tags, 4):
    ...     print(i)
    {'Event': 'Rated Classical game', 'Result': '1-0', 'UTCDate': '2012.12.31'}
    {'Event': 'Rated Classical game', 'Result': '1-0', 'UTCDate': '2012.12.31'}
    {'Event': 'Rated Classical game', 'Result': '1-0', 'UTCDate': '2012.12.31'}
    {'Event': 'Rated Bullet game', 'Result': '0-1', 'UTCDate': '2012.12.31'}

    """

    games_analyzed = 0
    l = 0

    for line in (lichess_file := bz2.BZ2File(file_path, "rb")):
        l += 1
        if line == b"\n":
            continue

        # Checks if line is the movetext.
        if not line.startswith(b"["):
            if "Movetext" in tags:
                current_game["Movetext"] = line.rstrip().decode("utf-8")
            continue

        # Identifies data enclosed by quotation marks.
        line = line[1:].decode("utf-8")
        quote_indices = [i for i, x in enumerate(line) if x == "\""]
        tag_name = line[:quote_indices[0]].rstrip()
        tag_value = line[quote_indices[0] + 1: quote_indices[1]]

        # Checks if a new game is being parsed.
        if tag_name == "Event":
            if games_analyzed > 0:
                yield current_game

            current_game = {}
            if (games_analyzed := games_analyzed + 1) > max_games:
                break

        # Fetches relevant tags.
        if tag_name in tags:
            current_game[tag_name] = tag_value
    print(l)

    lichess_file.close()


def get_user_data_lichess(usernames: list) -> list:
    """Fetches the stats of the usernames in `usernames` from Lichess. Note
    that usernames that are invalid Lichess accounts are silently ignored.

    The JSON formatting for each user can be found on this page:
    https://lichess.org/api#operation/apiUsers
    """

    @_concurrent_function
    def fetch_300(usernames: list) -> list:
        # Gets up to 300 user's data, ignoring invalid/empty/duplicate users.

        url = "https://lichess.org/api/users"
        data = ",".join(usernames).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as connection:
            data = json.load(connection)

        return data

    # List of chunks small enough for `fetch` to handle
    chunked_usernames = list(_chunks(list(set(usernames)), 300))
    output = []
    for i in fetch_300(chunked_usernames):
        output += i

    return output


def get_user_data_chesscom(usernames: list) -> list:
    """Fetches the stats of the usernames in `usernames` from chess.com. Note
    that usernames that are invalid chess.com accounts are silently ignored.

    The JSON is a dictionary with keys "profile" and "stats", with corresponding
    data stored for each value. The JSON formatting for the profile and stats
    data can be found on these documentation pages:

    https://www.chess.com/news/view/published-data-api#pubapi-endpoint-player-stats
    https://www.chess.com/news/view/published-data-api#pubapi-endpoint-player
    """

    @_concurrent_function
    def fetch(username: str) -> dict:
        data = {}

        profile_url = "https://api.chess.com/pub/player/" + username
        stats_url = "https://api.chess.com/pub/player/" + username + "/stats"

        with urllib.request.urlopen(profile_url) as connection:
            data["profile"] = json.load(connection)
        with urllib.request.urlopen(stats_url) as connection:
            data["stats"] = json.load(connection)

        return data

    return fetch(usernames)


def get_users_from_country_chesscom(iso_alpha_2: str) -> list:
    """Gets a list of all Chess.com players from a country. It is not
    recommended to use this for countries with a large amount of Chess.com
    accounts, as it will likely lead to a connection timeout.

    The relevant Chess.com API documentation can be found on this page:
    https://www.chess.com/news/view/published-data-api#pubapi-endpoint-country-players
    """

    url = "https://api.chess.com/pub/country/" + iso_alpha_2 + "/players"
    with urllib.request.urlopen(url) as connection:
        return json.load(connection)["players"]


def _chunks(input_list: list, chunk_size: int):
    """Yields successive `chunk_size`-sized chunks from `input_list`."""

    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]


def _concurrent_function(func, max_workers: int = 100):
    """
    Decorates a function taking in a value, turning it into a function taking
    in a list of values for that input to compute the function for. Useful for
    speeding up I/O-bound functions.

    Note that the output is NOT guaranteed to be in the same order as the input,
    and that urllib.error.HTTPErrors with code 404 are silently ignored.

    Example
    -------
    >>> @_concurrent_function
    >>> def get_req_length(url: str) -> int:
    ...     with urllib.request.urlopen(url) as conn:
    ...         return len(conn.read())
    >>>
    >>> get_req_length(["https://www.google.com/", "https://www.bing.com/"])
    69869, 13343
    >>> # The values are correct, but not in order.

    """

    def thread(data: list) -> list:
        def thread_attempt_get(data: list) -> tuple:
            # Returns results and requests that failed due to rate limiting
            results, failed_requests = [], []

            with cf.ThreadPoolExecutor(max_workers=max_workers) as exc:
                for chunk in _chunks(data, max_workers):
                    future_to_username = {
                        exc.submit(func, i): i for i in chunk}
                    completed_futures = cf.wait(future_to_username)[0]

                    for completed_future in completed_futures:
                        try:
                            results.append(completed_future.result())
                        except urllib.error.HTTPError as exc:
                            # Too many requests
                            if exc.code == 429:
                                username = future_to_username[completed_future]
                                failed_requests.append(username)
                            # User not found
                            elif exc.code != 404:
                                raise exc

            return results, failed_requests

        # Makes rate limited requests again until all results are retrieved
        results, failed_requests = thread_attempt_get(data)
        while failed_requests:
            new_results, failed_requests = thread_attempt_get(failed_requests)
            results += new_results

        return results

    return thread
