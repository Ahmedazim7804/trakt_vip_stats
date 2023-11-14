from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from sqlmodel import create_engine, Session, select
from Model.movies_model import Movie
from Model.shows_model import TV
from Model.episode_model import Episode
from mpire import WorkerPool
from mpire.utils import make_single_arguments
from tqdm import tqdm

engine = create_engine("sqlite:///database.db")


def set_rating(pipes, item):
    pipe, pbar_pipe = pipes

    type = item["type"]
    id = item[type]["ids"]["trakt"]
    rating = item["rating"]

    with Session(engine) as session:
        if type == "movie":
            existed = session.exec(select(Movie).where(Movie.trakt_id == id)).first()
        elif type == "show":
            existed = session.exec(select(TV).where(TV.trakt_id == id)).first()
        elif type == "episode":
            existed = session.exec(
                select(Episode).where(Episode.trakt_id == id)
            ).first()
        else:
            pbar_pipe.send(True)
            return

        if existed:
            if not existed.rating == int(rating):
                pipe.send([existed.set_rating, [rating]])

    pbar_pipe.send(True)


def process_get_ratings(pipe, pbar):
    page = 0
    with WorkerPool(n_jobs=10, shared_objects=(pipe, pbar)) as pool:
        while True:
            url = urljoin(BASE_URL, f"users/ahmedazim7804/ratings?limit=50&page={page}")
            data = CORE._handle_request(method="get", url=url)

            if not data:
                pipe.send(["stop"])
                pbar.send(False)
                break

            data = make_single_arguments(data, generator=False)

            pool.map(set_rating, data)

            page += 1


def process_add_data(conn):
    while True:
        try:
            fxn, args = conn.recv()
            fxn(*args)
        except:
            break


def progress_bar(conn):
    url = urljoin(BASE_URL, f"users/ahmedazim7804/stats")
    data = CORE._handle_request(method="get", url=url)

    total_ratings = data["ratings"]["total"]
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
