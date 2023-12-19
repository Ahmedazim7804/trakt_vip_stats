from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from Models.movies_model import Movie, MovieData, Cast, Studio, Crew
from sqlmodel import create_engine, Session, select
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from tqdm import tqdm
import os


engine = create_engine("sqlite:///database.db")


def get_movie(pipes, item):
    pipe, pbar_pipe = pipes

    watched_id = str(item["id"])  # Unique Watched id, unique for any item
    trakt_id = item["movie"]["ids"]["trakt"]  # Unique movie trakt id
    watched_at = str(item["watched_at"])

    with Session(engine) as session:
        existed = session.exec(select(Movie).where(Movie.id == trakt_id)).first()

    if not existed:
        logger.info(f"Getting Movie trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item["movie"]["ids"]["tmdb"]
        title = item["movie"]["title"]
        released_year = item["movie"]["year"]
        imdb_id = item["movie"]["ids"]["imdb"]
        watched_ids = [watched_id]
        watched_at = [watched_at]
        rating = item["rating"] if "rating" in item.keys() else 0
        plays = 1  # TODO: make plays=1 default in model.

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
            pipe.send([person.add_to_db, [tmdb_id, "movie"]])

        for person in crew:
            pipe.send([person.add_to_db, [tmdb_id, "movie"]])

        for studio in studios:
            pipe.send([studio.add_to_db, []])

    elif watched_id not in existed.watched_ids:
        pipe.send([existed.update, [watched_id, watched_at]])

    pbar_pipe.send(True)


def process_get_history(pipe, pbar):
    # TODO: with pebble but limit=50 or higher

    with WorkerPool(n_jobs=10, shared_objects=(pipe, pbar)) as pool:
        page = 1
        while True:
            url = urljoin(
                BASE_URL, f"users/{os.environ['username']}/history/movies?limit=50&page={page}"
            )
            data = CORE._handle_request(method="get", url=url)

            if page % 5 == 0:
                logger.warning(f"Sleeping for 1 second : Page {page}")
                time.sleep(1)

            data = make_single_arguments(data, generator=False)

            if not data:
                logger.error(f"COMPLETED")
                pipe.send(["stop"])
                pbar.send(False)
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
    url = urljoin(BASE_URL, f"users/{os.environ['username']}/stats")
    data = CORE._handle_request(method="get", url=url)
    total_movies = data["movies"]["plays"]
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
