from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from Models.shows_model import TV, TvData
from sqlmodel import create_engine, Session, select
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
from tqdm import tqdm
import os

engine = create_engine("sqlite:///database.db")


def get_tv(pipes, item):
    pipe, pbar_pipe = pipes

    trakt_id = item["show"]["ids"]["trakt"]

    with Session(engine) as session:
        existed = session.exec(select(TV).where(TV.trakt_id == trakt_id)).first()

    if not existed:
        logger.info(f"Getting SHOW trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item["show"]["ids"]["tmdb"]
        title = item["show"]["title"]
        episode_plays = item["plays"]
        released_year = item["show"]["year"]
        rating = 0  # FIXME:

        tvData = TvData(tmdb_id=tmdb_id)

        networks = tvData.network()
        networs_ids = [network.id for network in networks]

        poster = tvData.poster()
        genres = tvData.genres()
        countries = tvData.countries()

        show = TV(
            trakt_id=trakt_id,
            tmdb_id=tmdb_id,
            title=title,
            episode_plays=episode_plays,
            released_year=released_year,
            rating=rating,
            poster=poster,
            genres=genres,
            countries=countries,
            networks=networs_ids,
        )

        pipe.send([show.add_to_db, []])

        for network in networks:
            pipe.send([network.add_to_db, []])

    pbar_pipe.send(True)


def process_get_history(pipe, pbar):
    # TODO: with pebble but limit=50 or higher

    with WorkerPool(n_jobs=10, shared_objects=(pipe, pbar)) as pool:
        url = urljoin(BASE_URL, f"users/{os.environ['username']}/watched/shows")
        data = CORE._handle_request(method="get", url=url)

        data = make_single_arguments(data, generator=False)

        pool.map(get_tv, data)

    pipe.send(False)
    pbar.send(False)


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
    total_shows = data["shows"]["watched"]
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
