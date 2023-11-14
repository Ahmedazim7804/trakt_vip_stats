import requests
from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from Model.list_model import Trakt250Movies, Imdb250Movies, Reddit250Movies, MostPlayedMovies
from Model.list_model import Trakt250Shows, Imdb250Shows, RollingStone100Shows, MostPlayedShows
from tqdm import tqdm

def get_list(list_name):
    all_data = []

    page = 1

    while True:
        url = urljoin(BASE_URL, f"lists/{list_name}/items?limit=250&page={page}")
        data = CORE._handle_request(method='get', url=url)

        if not data:
            break

        all_data.extend(data)
        page += 1
    
    return all_data

def top_shows_and_movies_lists(placeholder_pipe, pbar_pipe):

    imdb_top_250_shows = Imdb250Shows.add_list_to_db(get_list("imdb-top-rated-tv-shows"))
    pbar_pipe.send(True)

    trakt_top_250_shows = Trakt250Shows.add_list_to_db(get_list("trakt-popular-tv-shows"))
    pbar_pipe.send(True)

    rollingstone_top_100_shows = RollingStone100Shows.add_list_to_db(get_list("rolling-stone-s-100-greatest-tv-shows-of-all-time"))
    pbar_pipe.send(True)

    imdb_top_250_movies = Imdb250Movies.add_list_to_db(get_list("imdb-top-rated-movies"))
    pbar_pipe.send(True)

    trakt_top_250_movies = Trakt250Movies.add_list_to_db(get_list("trakt-popular-movies"))
    pbar_pipe.send(True)

    reddit_top_250_movies = Reddit250Movies.add_list_to_db(get_list("reddit-top-250-2019-edition"))
    pbar_pipe.send(True)

    most_played_show_trakt = MostPlayedShows.add_list_to_db(CORE._handle_request(method='get', url="https://api.trakt.tv/shows/played/all"))
    pbar_pipe.send(True)

    most_played_movies_trakt = MostPlayedMovies.add_list_to_db(CORE._handle_request(method='get', url="https://api.trakt.tv/movies/played/all"))
    pbar_pipe.send(True)

    pbar_pipe.send(False)

def progress_bar(conn):
    movies_pbar = tqdm(total=8)

    while True:
        try:
            bool = conn.recv()
            if bool:
                movies_pbar.update(1)
            else:
                movies_pbar.close()
                break
        except:
            break

def placeholder_add_data(conn):
    return

if  __name__ == '__main__':
    username = "***REMOVED***"
    client_id ='***REMOVED***'
    client_secret = '***REMOVED***'
    main.authenticate(username, client_id=client_id, client_secret=client_secret)

    top_shows_and_movies_lists()