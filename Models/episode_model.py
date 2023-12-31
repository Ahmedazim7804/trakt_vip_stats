from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from tmdbv3api import TMDb
import tmdbv3api
from operator import itemgetter
from loguru import logger
from Models.cast_model import Cast
from Models.crew_model import Crew
from sqlmodel import create_engine, Session, select
import os

tmdb = TMDb()
tmdb.api_key = os.environ["tmdb_api_key"]
TMDbEpisode = tmdbv3api.Episode()

engine = create_engine("sqlite:///database.db")


class Episode(SQLModel, table=True, arbitrary_types_allowed=True):
    trakt_id: str = Field(primary_key=True)
    tmdb_id: str
    episode_title: str
    show_title: str
    season: int
    episode: int
    plays: int = Field(default=1)
    rating: Optional[int] = Field(default=0)
    tmdb_show_id: int
    watched_at: List[str] = Field(sa_column=Column(JSON))
    watched_ids: List[str] = Field(sa_column=Column(JSON))
    runtime: int
    cast: List[int] = Field(sa_column=Column(JSON))
    crew: List[int] = Field(sa_column=Column(JSON))

    def add_to_db(self):
        try:
            with Session(engine) as session:
                existed = session.exec(
                    select(Episode).where(Episode.trakt_id == self.trakt_id)
                ).first()
                if not existed:
                    session.add(self)
                    session.commit()
                else:
                    existed.watched_at = [*existed.watched_at, *self.watched_at]
                    existed.watched_ids = [*existed.watched_ids, *self.watched_ids]
                    existed.plays = existed.plays + 1

                session.commit()
        except Exception as e:
            logger.error(f"Failed to add Episode Trakt Id: {self.trakt_id} to database due to Error {e}")

    def update(self, watched_id, watched_at):
        with Session(engine) as session:
            self.watched_ids = [*self.watched_ids, watched_id]
            self.watched_at = [*self.watched_at, watched_at]
            self.plays += 1
            session.add(self)
            session.commit()

    def set_rating(self, rating):
        with Session(engine) as session:
            self.rating = int(rating)
            session.add(self)
            session.commit()


class EpisodeData:
    def __init__(self, tmdb_show_id, season, episode):
        self.tmdb_show_id = tmdb_show_id
        self.season = season
        self.episode = episode
        self.has_data = True

        try:
            self.episodeDetails = TMDbEpisode.details(tmdb_show_id, season, episode)
            self.episodeCredits = TMDbEpisode.credits(tmdb_show_id, season, episode)
        except Exception as e:
            logger.error(
                f"TMDb Show Id : '{self.tmdb_show_id}', {self.format()} failed to get INFO because {e}"
            )
            self.episodeDetails = {}
            self.episodeCredits = {}
            self.has_data = False

    def format(self):
        return f"S{str(self.season).zfill(2)}E{str(self.episode).zfill(2)}"

    def runtime(self):
        runtime = 0

        try:
            runtime = self.episodeDetails["runtime"]
        except KeyError:
            logger.warning(
                f"TMDb Show Id : '{self.tmdb_show_id}', {self.format()} failed to get runtime"
            )

        if not runtime:
            logger.debug(
                f"TMDb Show Id : '{self.tmdb_show_id}', {self.format()} runtime is 0"
            )

        return runtime

    def cast(self):
        cast_list = []
        try:
            item_cast = self.episodeCredits["cast"]

            for actor in item_cast:
                name, id, gender, image = itemgetter(
                    "name", "id", "gender", "profile_path"
                )(actor)
                if gender and image:
                    cast = Cast(
                        id=id,
                        name=name,
                        gender=gender,
                        image=image,
                    )
                    cast_list.append(cast)
        except KeyError:
            logger.warning(
                f"TMDb Show Id : '{self.tmdb_show_id}' {self.format()} failed to get Cast"
            )

        return cast_list

    def crew(self):
        directors = []
        writers = []
        try:
            all_crew = self.episodeCredits["crew"]

            for person in all_crew:
                id, name, dept, job, image = itemgetter(
                    "id", "name", "department", "job", "profile_path"
                )(person)

                if person["job"] == "Director":
                    directors.append(
                        Crew(id=id, name=name, dept=dept, job=job, image=image)
                    )

                if person["department"] == "Writing":
                    writers.append(
                        Crew(id=id, name=name, dept=dept, job=job, image=image)
                    )

        except KeyError:
            logger.warning(
                f"TMDb Show Id : '{self.tmdb_show_id}' {self.format()} failed to get Crew"
            )

        if not directors:
            logger.debug(
                f"TMDb Show Id : '{self.tmdb_show_id}' {self.format()} Directors List is Empty"
            )
        if not writers:
            logger.debug(
                f"TMDb Show Id : '{self.tmdb_show_id}' {self.format()} Writers List is Empty"
            )

        return [*directors, *writers]


# print(GetEpisode.crew('70523', 2, 1))
