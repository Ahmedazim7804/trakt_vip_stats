from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from shows_model import TV, TvData
from sqlmodel import SQLModel, create_engine, Session, select
import main
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from multiprocessing import Process
import multiprocessing
from tqdm import tqdm


def get_tv(item):

    global pipe

    trakt_id = item['show']['ids']['trakt']

    with Session(engine) as session:
        existed = session.exec(select(TV).where(TV.trakt_id == trakt_id)).first()
    
    if not existed:

        logger.info(f"Getting SHOW trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item['show']['ids']['tmdb']
        title = item['show']['title']
        episode_plays = item['plays']
        released_year = item['show']['year']
        rating = 0 #FIXME:

        tvData = TvData(tmdb_id=tmdb_id)

        networks = tvData.network()
        networs_ids = [network.id for network in networks]

        poster = tvData.poster()
        genres = tvData.genres()
        countries = tvData.countries()

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

        show.add_to_db()
            
        for network in networks:
            network.add_to_db()
    
    pipe.send(True)

def process_get_history():

    #TODO: with pebble but limit=50 or higher

    with WorkerPool(n_jobs=10) as pool:
        url = urljoin(BASE_URL, f"users/ahmedazim7804/watched/shows")
        data = CORE._handle_request(method='get', url=url)

        data = make_single_arguments(data, generator=False)

        pool.map(get_tv, data)

        pipe.send(False)

def process_progress_bar(conn):
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: ^12}</level>] <level>{message}</level>"
    logger.configure(handlers=[dict(sink=lambda msg: tqdm.write(msg, end=''), format=logger_format, colorize=True)])

    url = urljoin(BASE_URL, f"users/ahmedazim7804/stats")
    data = CORE._handle_request(method='get', url=url)

    total_shows = data['shows']['watched']
    shows_pbar = tqdm(total=total_shows)
    while True:
        try:
            bool = conn.recv()
            if bool:
                shows_pbar.update(1)
            else:
                shows_pbar.close()
                break
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
    p2 = Process(target=process_progress_bar, args=(child_conn,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(time.time()-start_time)