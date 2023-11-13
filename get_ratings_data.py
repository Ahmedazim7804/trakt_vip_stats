from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from sqlmodel import SQLModel, create_engine, Session, select
from Model.movies_model import Movie
from Model.shows_model import TV
from Model.episode_model import Episode
import main
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from multiprocessing import Process
import multiprocessing
from tqdm import tqdm


def set_rating(item):
    type = item['type']
    id = item[type]['ids']['trakt']
    rating = item['rating']

    with Session(engine) as session:
        if type == 'movie':
            existed = session.exec(select(Movie).where(Movie.trakt_id == id)).first()
        elif type == 'show':
            existed = session.exec(select(TV).where(TV.trakt_id == id)).first()
        elif type == 'episode':
            existed = session.exec(select(Episode).where(Episode.trakt_id == id)).first()
        else:
            pipe.send(True)
            return
        
        if existed:
            if not existed.rating == int(rating):
                existed.rating = int(rating)
                session.add(existed)
                session.commit()
        else:
            print(item)

    pipe.send(True)

def process_get_ratings():
    page = 0
    with WorkerPool(n_jobs=10) as pool:
        while True:
            url = urljoin(BASE_URL, f"users/ahmedazim7804/ratings?limit=50&page={page}")
            data = CORE._handle_request(method='get', url=url)

            if not data:
                pipe.send(False)
                break

            data = make_single_arguments(data, generator=False)

            pool.map(set_rating, data)

            page += 1


def process_progress_bar(conn):
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: ^12}</level>] <level>{message}</level>"
    logger.configure(handlers=[dict(sink=lambda msg: tqdm.write(msg, end=''), format=logger_format, colorize=True)])

    url = urljoin(BASE_URL, f"users/ahmedazim7804/stats")
    data = CORE._handle_request(method='get', url=url)

    total_ratings = data['ratings']['total']
    ratings_pbar = tqdm(total=total_ratings)
    while True:
        try:
            bool = conn.recv()
            if bool:
                ratings_pbar.update(1)
            else:
                ratings_pbar.close()
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

    p1 = Process(target=process_get_ratings)
    p2 = Process(target=process_progress_bar, args=(child_conn,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(time.time()-start_time)