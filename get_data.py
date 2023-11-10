from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from movies_model import Movie, MovieData, Cast, Studio, Crew
from shows_model import TV, GetTvData, Network
from episode_model import Episode, EpisodeData
from sqlmodel import SQLModel, create_engine, Session, select
import main
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments

from tmdbv3api import TMDb
from multiprocessing import Lock


def get_movie(item):

    watched_id = str(item['id']) # Unique Watched id, unique for any item
    trakt_id = item['movie']['ids']['trakt'] # Unique movie trakt id

    with Session(engine) as session:
        existed = session.exec(select(Movie).where(Movie.id == trakt_id)).first()
        
    if not existed:

        logger.info(f"Getting Movie trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item['movie']['ids']['tmdb']
        title = item['movie']['title']
        released_year = item['movie']['year']
        imdb_id = item['movie']['ids']['imdb']
        watched_ids = [watched_id]
        watched_at = item['watched_at']
        rating = item['rating'] if 'rating' in item.keys() else 0 #FIXME:
        plays = 1 #TODO: make plays=1 default in model.

        movieData = MovieData(tmdb_id=tmdb_id)

        countries = movieData.countries()
        poster = movieData.poster()
        runtime = movieData.runtime()
        genres = movieData.genres()

        studios = movieData.studios()
        studios_ids = [studio.id for studio in studios]

        cast = movieData.cast()
        cast_ids = [person.id for person in cast]

        crew = movieData.crew()
        crew_ids = [person.id for person in crew]

        movie = Movie(
            id=trakt_id,
            title=title,
            trakt_id=trakt_id,
            imdb_id=imdb_id,
            tmdb_id=tmdb_id,
            watched_at=[watched_at],
            watched_ids=watched_ids,
            plays=plays,
            genres=genres,
            cast=cast_ids,
            crew=crew_ids,
            runtime=runtime,
            poster=poster,
            studios=studios_ids,
            countries=countries,
            rating=rating,
            released_year=released_year,
        )

        lock.acquire()

        movie.add_to_db()

        for person in cast:
            person.add_to_db(tmdb_id, type='movie')
            
        for person in crew:
            person.add_to_db(tmdb_id, type='movie')

        for studio in studios:
            studio.add_to_db()
        
        lock.release()

    elif watched_id not in existed.watched_ids:
        lock.acquire()
        existed.add_to_db()
        lock.release()


def get_tv(item):

    for item in data['watched'][385:400]:
        if 'show' in item.keys():

            trakt_id = item['show']['ids']['trakt']

            with Session(engine) as session:
                existed = session.exec(select(TV).where(TV.trakt_id == trakt_id)).first()
            
            if not existed:
                tmdb_id = item['show']['ids']['tmdb']
                title = item['show']['title']
                episode_plays = item['plays']
                released_year = item['show']['year']
                rating = 0 #FIXME:

                networks = GetTvData.get_network(tmdb_id=tmdb_id)
                networs_ids = [network.id for network in networks]

                poster = GetTvData.get_poster(tmdb_id=tmdb_id)
                genres = GetTvData.get_genres(tmdb_id=tmdb_id)
                countries = GetTvData.get_countries(tmdb_id=tmdb_id)

                show = TV(
                    trakt_id=trakt_id,
                    title=title,
                    episode_plays=episode_plays,
                    released_year=released_year,
                    rating=rating,
                    poster=poster,
                    genres=genres,
                    countries=countries,
                    networks=networs_ids
                )

                with Session(engine) as session:
                    session.add(show)
                    
                    for network in networks:
                        existed_network = session.exec(select(Network).where(Network.id == network.id)).first()
                        if not existed_network:
                            session.add(network)
                        else:
                            existed_network.shows = existed_network.shows + 1
                    
                    session.commit()


def get_episode(item):

    tmdb_id = item['episode']['ids']['tmdb']

    with Session(engine) as session:
        existed = session.exec(select(Episode).where(Episode.tmdb_id == tmdb_id)).first()
    
    if not existed:

        logger.info(f"Getting Episode tmdb_id={tmdb_id} Data and adding to Database")

        watched_id = str(item['id'])

        tmdb_show_id = item['show']['ids']['tmdb']
        show_title = item['show']['title']
        season = item['episode']['season']
        episode = item['episode']['number']
        episode_title = item['episode']['title']

        episodeData = EpisodeData(tmdb_show_id=tmdb_show_id, season=season, episode=episode)

        runtime = episodeData.runtime()

        cast = episodeData.cast()
        cast_ids = [person.id for person in cast]

        crew = episodeData.crew()
        crew_ids = [person.id for person in crew]
        rating = 0 #FIXME:

        episode = Episode(
            tmdb_id=tmdb_id,
            tmdb_show_id=tmdb_show_id,
            show_title=show_title,
            season=season,
            episode=episode,
            episode_title=episode_title,
            watched_at=[watched_id],
            runtime=runtime,
            cast=cast_ids,
            crew=crew_ids
        )

        lock.acquire()
        episode.add_to_db()

        for person in cast:
            person.add_to_db(tmdb_show_id, type='episode')
                
        for person in crew:
            person.add_to_db(tmdb_show_id, type='episode')
        
        lock.release()


def trakt_history_page(item):
    if item['type'] == 'movie':
        get_movie(item)
    if item['type'] == 'episode':
        get_episode(item)


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


tmdb = TMDb()
tmdb.api_key = '***REMOVED***'
trakt_CLIENT_ID = '***REMOVED***'

username = "***REMOVED***"
client_id ='***REMOVED***'
client_secret = '***REMOVED***'
main.authenticate(username, client_id=client_id, client_secret=client_secret)


import time 

aa = time.time()

lock = Lock()


with WorkerPool(n_jobs=10) as pool:
    for page in range(83, 100):
        url = urljoin(BASE_URL, f"users/ahmedazim7804/history?page={page}")
        data = CORE._handle_request(method='get', url=url)

        if (page % 5 == 0):
            logger.warning(f"Sleeping for 1 second : Page {page}")
            time.sleep(1)

        data = make_single_arguments(data, generator=False)

        pool.map(trakt_history_page, data)

print(time.time()-aa)