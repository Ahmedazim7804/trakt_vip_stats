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

    global queue

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

        

        queue.put([movie.add_to_db, []])

        for person in cast:
            queue.put([person.add_to_db, [tmdb_id, 'movie']])
            pass
            
        for person in crew:
            queue.put([person.add_to_db, [tmdb_id, 'movie']])
            pass

        for studio in studios:
            queue.put([studio.add_to_db, []])
            pass
        

    elif watched_id not in existed.watched_ids:
        pass
        queue.put([existed.add_to_db, []])
        


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
    global queue

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

        
        queue.put([episode.add_to_db, []])

        for person in cast:
            queue.put([person.add_to_db, [tmdb_show_id, 'episode']])
            pass
                
        for person in crew:
            queue.put([person.add_to_db, [tmdb_show_id, 'episode']])
            pass
        
        


def trakt_history_page(item):
    if item['type'] == 'movie':
        get_movie(item)
    if item['type'] == 'episode':
        get_episode(item)


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


# tmdb = TMDb()
# tmdb.api_key = '***REMOVED***'
# trakt_CLIENT_ID = '***REMOVED***'

username = "***REMOVED***"
client_id ='***REMOVED***'
client_secret = '***REMOVED***'
main.authenticate(username, client_id=client_id, client_secret=client_secret)


import time 

aa = time.time()

from multiprocessing import Process
import multiprocessing
from multiprocessing import Pool
from joblib import Parallel, delayed
from pebble import ProcessPool

def run_parallely(fn, items):
    return Parallel(n_jobs=10, backend='threading')(delayed(fn)(item) for item in items)

queue = multiprocessing.Queue()

def fxn1():
    with ProcessPool(max_workers=10) as pool:
        end = 500
        for page in range(1, end+1):
            url = urljoin(BASE_URL, f"users/ahmedazim7804/history?page={page}")
            data = CORE._handle_request(method='get', url=url)

            if not data:
                logger.error(f"COMPLETED")

            if (page % 5 == 0):
                logger.warning(f"Sleeping for 1 second : Page {page}")
                time.sleep(1)

            # with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
            #     executor.map(trakt_history_page, data)
            #data = make_single_arguments(data, generator=False)

            pool.map(trakt_history_page, data)

        # with ProcessPoolExecutor(max_workers=10) as executor:
        #     executor.map(trakt_history_page, data)
        #pool.map(trakt_history_page, data)

        #run_parallely(trakt_history_page, data)

def fxn2(queue):
    while True:
        try:
            fxn, args = queue.get()
            fxn(*args)
        except:
            break

p1 = Process(target=fxn1, )
p2 = Process(target=fxn2, args=(queue,))
p1.start()
p2.start()
p1.join()
p2.join()


print(time.time()-aa)