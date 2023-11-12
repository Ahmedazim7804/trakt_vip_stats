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
import time
from multiprocessing import Process


def get_movie(item):

    global pipe

    watched_id = str(item['id']) # Unique Watched id, unique for any item
    trakt_id = item['movie']['ids']['trakt'] # Unique movie trakt id
    watched_at = str(item['watched_at'])

    with Session(engine) as session:
        existed = session.exec(select(Movie).where(Movie.id == trakt_id)).first()
        
    if not existed:

        logger.info(f"Getting Movie trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item['movie']['ids']['tmdb']
        title = item['movie']['title']
        released_year = item['movie']['year']
        imdb_id = item['movie']['ids']['imdb']
        watched_ids = [watched_id]
        watched_at = [watched_at]
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
            watched_at=watched_at,
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

        

        pipe.send([movie.add_to_db, []])

        for person in cast:
            pipe.send([person.add_to_db, [tmdb_id, 'movie']])
            
        for person in crew:
            pipe.send([person.add_to_db, [tmdb_id, 'movie']])
            
        for studio in studios:
            pipe.send([studio.add_to_db, []])
        

    elif watched_id not in existed.watched_ids:
        pipe.send([existed.update, [watched_id, watched_at]])
        


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
    global pipe

    trakt_id = item['episode']['ids']['trakt']
    watched_id = str(item['id']) # Unique Watched id, unique for any item
    watched_at = str(item['watched_at'])

    with Session(engine) as session:
        existed = session.exec(select(Episode).where(Episode.trakt_id == trakt_id)).first()
    
    if not existed:
        logger.info(f"Getting Episode trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item['episode']['ids']['tmdb']
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
            trakt_id=trakt_id,
            tmdb_id=tmdb_id,
            tmdb_show_id=tmdb_show_id,
            show_title=show_title,
            season=season,
            episode=episode,
            episode_title=episode_title,
            watched_ids=[watched_id],
            watched_at=[watched_at],
            runtime=runtime,
            cast=cast_ids,
            crew=crew_ids
        )

        
        pipe.send([episode.add_to_db, []])

        for person in cast:
            pipe.send([person.add_to_db, [tmdb_show_id, 'episode']])
                
        for person in crew:
            pipe.send([person.add_to_db, [tmdb_show_id, 'episode']])

    elif watched_id not in existed.watched_ids:
        pipe.send([existed.update, [watched_id, watched_at]])
        
        
def trakt_history_page(item):
    if item['type'] == 'movie':
        get_movie(item)
    if item['type'] == 'episode':
        get_episode(item)

def process_get_data():
    #TODO: with pebble but limit=50 or higher
    with WorkerPool(n_jobs=10) as pool:
        page = 1
        while True:
            url = urljoin(BASE_URL, f"users/ahmedazim7804/history?limit=50&page={page}")
            data = CORE._handle_request(method='get', url=url)

            if (page % 5 == 0):
                logger.warning(f"Sleeping for 1 second : Page {page}")
                time.sleep(1)

            data = make_single_arguments(data, generator=False)

            if not data:
                logger.error(f"COMPLETED")
                pipe.send(['stop'])
                break

            pool.map(trakt_history_page, data)

            page += 1

def process_add_data(conn):
    while True:
        try:
            fxn, args = conn.recv()
            fxn(*args)
        except:
            break


if __name__ == '__main__':

start_time = time.time()
    engine = create_engine("sqlite:///database.db")
    SQLModel.metadata.create_all(engine)
    
    username = "***REMOVED***"
    client_id ='***REMOVED***'
    client_secret = '***REMOVED***'
    main.authenticate(username, client_id=client_id, client_secret=client_secret)

    pipe, child_conn = multiprocessing.Pipe()

    url = urljoin(BASE_URL, f"users/ahmedazim7804/stats")
    data = CORE._handle_request(method='get', url=url)

    total_movies = data['movies']['plays']
    total_episodes = data['episodes']['plays']

    p1 = Process(target=process_get_data)
    p2 = Process(target=process_add_data, args=(child_conn,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(time.time()-start_time)