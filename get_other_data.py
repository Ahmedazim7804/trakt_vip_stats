import requests
import main
from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from Model.list_model import Trakt250Movies, Imdb250Movies, Reddit250Movies
from Model.list_model import Trakt250Shows, Imdb250Shows, RollingStone100Shows

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

def get_top_shows_and_movies_lists():
    import time

    aa = time.time()

    imdb_top_250_shows = Imdb250Shows.add_list_to_db(get_list("imdb-top-rated-tv-shows"))
    trakt_top_250_shows = Trakt250Shows.add_list_to_db(get_list("trakt-popular-tv-shows"))
    rollingstone_top_100_shows = RollingStone100Shows.add_list_to_db(get_list("rolling-stone-s-100-greatest-tv-shows-of-all-time"))

    imdb_top_250_movies = Imdb250Movies.add_list_to_db(get_list("imdb-top-rated-movies"))
    trakt_top_250_movies = Trakt250Movies.add_list_to_db(get_list("trakt-popular-movies"))
    reddit_top_250_movies = Reddit250Movies.add_list_to_db(get_list("reddit-top-250-2019-edition"))

    most_played_show_trakt = CORE._handle_request(method='get', url="https://api.trakt.tv/shows/played/all")
    most_played_movies_trakt = CORE._handle_request(method='get', url="https://api.trakt.tv/movies/played/all")

    print(time.time()-aa)

if  __name__ == '__main__':
    username = "***REMOVED***"
    client_id ='***REMOVED***'
    client_secret = '***REMOVED***'
    main.authenticate(username, client_id=client_id, client_secret=client_secret)

    get_top_shows_and_movies_lists()