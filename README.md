# Chess-Statistics-Toolkit
Get data from the Lichess and Chess.com public APIs easily without any 
dependencies outside Python's standard library.

## How do I use this?

Download or clone this repository into the repository you're working in. All
functions are in the `utils.py` file. No dependencies outside the standard
library are used, so you should be fine running the examples as soon as you
get them downloaded!

I have also included the smallest (and first) file in the Lichess database, so
I could include examples on the `get_game_data_lichess` function (see below).
If you want to torrent it from [here](https://database.lichess.org/) instead,
you can download everything else in the repository and then put that file in the
folder and it should run smoothly.

## Available functions

The `get_user_data_lichess` and `get_user_data_chesscom` functions are used to
get user data from Lichess and Chess.com respectively. They both take in a list
of users, ignoring invalid users/duplicates/empty usernames, and make a series
of multithreaded requests to the relevant API.

Since the Lichess API supports getting up to 300 users with a single call, it
can often be faster on orders of magnitude than Chess.com. Keep this in mind
when selecting what site to sample data from.

The Chess Statistics Toolkit also includes the `get_users_from_country_chesscom`
and `get_game_data_lichess` functions. `get_users_from_country_chesscom` does
exactly what it says on the tin, and returns a list of all usernames from the
selected country. It takes in the 2-letter capitalized ISO-3166 name for the
country. Note that this can take a lot of time for large countries, and will
most likely lead to a timeout error for countries like, for example, the
United States.

`get_game_data_lichess` takes in a file path, and returns a generator yielding
selected data from a Lichess .pgn.bz2 database file. Check out the documentation
for exactly what kinds of data can be extracted from a normal .pgn.bz2 file.
These files can be downloaded from the
[Lichess game database](https://database.lichess.org/). Keep in mind that the
number of games played on the website is massive and that using the (optional)
`max_games` keyword argument when using the function is heavily encouraged.

### Examples

There are examples of the functions in the Python files starting with
`examples_` - check them out! All of them depend on having `matplotlib` and
`numpy` installed - if you don't have them installed, do
`pip install matplotlib` from the command line.

Documentation is also included - use the `help()` command on any function you're
confused about, or take a peek at the docstrings themselves in the `utils.py`
file.

## Status

While the project is working, I feel like there are still some improvements that
could be made - for example, move compression that would improve performance
for using large Lichess data files, as well as potentially improving the
`get_game_data_lichess` function execution speed. I feel like the API access is
close to as good as it can get, though - please contact me if you have
improvements!

## License

The Chess Statistics Toolkit is released under the GNU General Public License
v3.0.

## Links

Here are links to Lichess's game database, as well as the API documentations.
There are also links in the documentation for each relevant function to the
relevant API documentation.

* [Lichess's game database](https://database.lichess.org/)
* [Chess.com's public API](https://www.chess.com/news/view/published-data-api)
* [Lichess's public API](https://lichess.org/api)
