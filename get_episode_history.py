from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from movies_model import Movie, MovieData, Cast, Studio, Crew
from episode_model import Episode, EpisodeData
from sqlmodel import SQLModel, create_engine, Session, select
import main
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from multiprocessing import Process
import multiprocessing
from tqdm import tqdm


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


def process_get_history():

    url = urljoin(BASE_URL, f"users/ahmedazim7804/stats")
    data = CORE._handle_request(method='get', url=url)

    total_episodes = data['episodes']['plays']

    session = Session(engine)

    #TODO: with pebble but limit=50 or higher
    episode_pbar = tqdm(total=total_episodes)
    
    with WorkerPool(n_jobs=10) as pool:
        page = 1
        while True:
            url = urljoin(BASE_URL, f"users/ahmedazim7804/history/episodes?limit=50&page={page}")
            data = CORE._handle_request(method='get', url=url)

            if (page % 5 == 0):
                logger.warning(f"Sleeping for 1 second : Page {page}")
                time.sleep(1)

            data = make_single_arguments(data, generator=False)

            episode_count = sum(session.exec(select(Episode.plays)).all())

            episode_pbar.update(episode_count - episode_pbar.n)

            if not data:
                logger.error(f"COMPLETED")
                pipe.send(['stop'])
                episode_pbar.close()
                break

            pool.map(get_episode, data)

            page += 1


def process_add_data(conn):
    while True:
        try:
            fxn, args = conn.recv()
            fxn(*args)
        except:
            break


if __name__ == '__main__':


    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: ^12}</level>] <level>{message}</level>"
    logger.configure(handlers=[dict(sink=lambda msg: tqdm.write(msg, end=''), format=logger_format, colorize=True)])

    start_time = time.time()
    engine = create_engine("sqlite:///database.db")
    SQLModel.metadata.create_all(engine)
    
    username = "***REMOVED***"
    client_id ='***REMOVED***'
    client_secret = '***REMOVED***'
    main.authenticate(username, client_id=client_id, client_secret=client_secret)

    pipe, child_conn = multiprocessing.Pipe()

    p1 = Process(target=process_get_history)
    p2 = Process(target=process_add_data, args=(child_conn,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(time.time()-start_time)