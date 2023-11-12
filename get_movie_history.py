from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from movies_model import Movie, MovieData, Cast, Studio, Crew
from sqlmodel import SQLModel, create_engine, Session, select
import main
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from multiprocessing import Process
import multiprocessing
from tqdm import tqdm


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
    
    global pbar_pipe
    pbar_pipe.send(True)
                

def process_get_history():

    #TODO: with pebble but limit=50 or higher
    
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: ^12}</level>] <level>{message}</level>"
    logger.configure(handlers=[dict(sink=lambda msg: tqdm.write(msg, end=''), format=logger_format, colorize=True)])
    
    with WorkerPool(n_jobs=10) as pool:
        page = 1
        while True:
            url = urljoin(BASE_URL, f"users/ahmedazim7804/history/movies?limit=50&page={page}")
            data = CORE._handle_request(method='get', url=url)

            if (page % 5 == 0):
                logger.warning(f"Sleeping for 1 second : Page {page}")
                time.sleep(1)

            data = make_single_arguments(data, generator=False)

            if not data:
                logger.error(f"COMPLETED")
                pipe.send(['stop'])
                pbar_pipe.send(False)
                break

            pool.map(get_movie, data)

            page += 1


def process_add_data(conn):
    while True:
        try:
            fxn, args = conn.recv()
            fxn(*args)
        except:
            break

def progress_bar(conn):
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: ^12}</level>] <level>{message}</level>"
    logger.configure(handlers=[dict(sink=lambda msg: tqdm.write(msg, end=''), format=logger_format, colorize=True)])

    url = urljoin(BASE_URL, f"users/ahmedazim7804/stats")
    data = CORE._handle_request(method='get', url=url)
    total_movies = data['movies']['plays']
    movies_pbar = tqdm(total=total_movies)

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
    pbar_pipe, pbar_conn = multiprocessing.Pipe()

    p1 = Process(target=process_get_history)
    p2 = Process(target=process_add_data, args=(child_conn,))
    p3 = Process(target=progress_bar, args=(pbar_conn,))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

    print(time.time()-start_time)