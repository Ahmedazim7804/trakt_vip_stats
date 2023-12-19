from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
import os
from Models.movies_model import Cast, Crew
from Models.episode_model import Episode, EpisodeData
from sqlmodel import create_engine, Session, select
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from tqdm import tqdm


engine = create_engine("sqlite:///database.db")


def get_episode(pipes, item):
    pipe, pbar_pipe = pipes

    trakt_id = item["episode"]["ids"]["trakt"]
    watched_id = str(item["id"])  # Unique Watched id, unique for any item
    watched_at = str(item["watched_at"])

    with Session(engine) as session:
        existed = session.exec(
            select(Episode).where(Episode.trakt_id == trakt_id)
        ).first()

    if not existed:
        logger.info(f"Getting Episode trakt_id={trakt_id} Data and adding to Database")

        tmdb_id = item["episode"]["ids"]["tmdb"]
        tmdb_show_id = item["show"]["ids"]["tmdb"]
        show_title = item["show"]["title"]
        season = item["episode"]["season"]
        episode = item["episode"]["number"]
        episode_title = item["episode"]["title"]

        episodeData = EpisodeData(
            tmdb_show_id=tmdb_show_id, season=season, episode=episode
        )

        runtime = episodeData.runtime() #FIXME: Some episode do not have runtime in tmdb, use standard or avg. runtime of their show for them

        cast = episodeData.cast()
        cast_ids = [person.id for person in cast]

        crew = episodeData.crew()
        crew_ids = [person.id for person in crew]
        rating = 0  # FIXME:

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
            crew=crew_ids,
        )

        pipe.send([episode.add_to_db, []])

        for person in cast:
            pipe.send([person.add_to_db, [tmdb_show_id, "episode"]])

        for person in crew:
            pipe.send([person.add_to_db, [tmdb_show_id, "episode"]])

    elif watched_id not in existed.watched_ids:
        pipe.send([existed.update, [watched_id, watched_at]])

    pbar_pipe.send(True)


def process_get_history(pipe, pbar):
    # TODO: with pebble but limit=50 or higher

    with WorkerPool(n_jobs=10, shared_objects=(pipe, pbar)) as pool:
        page = 1
        while True:
            url = urljoin(
                BASE_URL, f"users/{os.environ['username']}/history/episodes?limit=50&page={page}"
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

            pool.map(get_episode, data)

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
    total_episodes = data["episodes"]["plays"]
    movies_pbar = tqdm(total=total_episodes)

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
