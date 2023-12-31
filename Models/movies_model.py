from Models.cast_model import Cast
from Models.crew_model import Crew
from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from tmdbv3api import TMDb
import tmdbv3api
from operator import itemgetter
from loguru import logger
from sqlmodel import create_engine, Session, select
import os

engine = create_engine("sqlite:///database.db")

tmdb = TMDb()
tmdb.api_key = os.environ["tmdb_api_key"]
TMDbMovie = tmdbv3api.Movie()


class Studio(SQLModel, table=True, arbitrary_types_allowed=True):
    id: int = Field(primary_key=True)
    name: Optional[str]
    country: Optional[str]
    movies: int = Field(default=1)
    image: Optional[str]

    def add_to_db(self):
        with Session(engine) as session:
            existed_studio = session.exec(
                select(Studio).where(Studio.id == self.id)
            ).first()
            if not existed_studio:
                session.add(self)
            else:
                existed_studio.movies = existed_studio.movies + 1
                session.add(existed_studio)

            session.commit()


class Movie(SQLModel, table=True, arbitrary_types_allowed=True, orm_mode=True):
    id: int
    title: str
    trakt_id: str = Field(primary_key=True)
    imdb_id: str = Field(nullable=True, default='')
    tmdb_id: str = Field(nullable=True, default='')
    watched_at: List[str] = Field(sa_column=Column(JSON))
    watched_ids: List[str] = Field(sa_column=Column(JSON))
    plays: int
    released_year: int = Field(nullable=True)
    cast: List[int] = Field(sa_column=Column(JSON))
    studios: List[int] = Field(sa_column=Column(JSON))
    genres: List[str] = Field(sa_column=Column(JSON))
    crew: List[int] = Field(sa_column=Column(JSON))
    countries: List[str] = Field(sa_column=Column(JSON))
    runtime: Optional[int]
    poster: Optional[str]
    rating: Optional[int] = Field(default=0)

    def add_to_db(self):
        try:
            with Session(engine) as session:
                existed = session.exec(
                    select(Movie).where(Movie.tmdb_id == self.tmdb_id)
                ).first()
                if not existed:
                    session.add(self)
                    session.commit()
                else:
                    existed.watched_ids = [*existed.watched_ids, *self.watched_ids]
                    existed.watched_at = [*existed.watched_at, *self.watched_at]
                    existed.plays = existed.plays + 1

                session.commit()
        except Exception as e:
            logger.error(f"Failed to add Movie Trakt Id: {self.trakt_id} to database due to error {e}")

    def update(self, watched_id, watched_at):
        with Session(engine) as session:
            self.watched_at = [*self.watched_at, watched_at]
            self.watched_ids = [*self.watched_ids, watched_id]
            self.plays = self.plays + 1
            session.add(self)
            session.commit()

    def set_rating(self, rating):
        with Session(engine) as session:
            self.rating = int(rating)
            session.add(self)
            session.commit()


class MovieData:
    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id
        self.has_data = True

        try:
            self.movieDetails = TMDbMovie.details(self.tmdb_id)
            self.movieCredits = TMDbMovie.credits(self.tmdb_id)
        except Exception as e:
            logger.error(
                f"TMDb Movie Id : '{self.tmdb_id}', failed to get INFO because {e}"
            )
            self.has_data = False

    def genres(self):
        genres = []

        try:
            item_info = self.movieDetails["genres"]

            for genre in item_info:
                genre = genre["name"]
                if " & " in genre:
                    genres.extend(genre.split(" & "))
                else:
                    genres.append(genre)

        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Genres")

        if not genres:
            logger.debug(f"TMDb Movie Id : '{self.tmdb_id}' Genres are empty")

        return genres

    def runtime(self):
        runtime = 0

        try:
            runtime = self.movieDetails["runtime"]
        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Runtime")
            return runtime

        if not (KeyError, AttributeError):
            logger.debug(f"TMDB Movie Id: '{self.tmdb_id}' runtime is 0")

        return runtime

    def poster(self):
        poster = None

        try:
            poster = self.movieDetails.poster_path
        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Poster")

        return poster

    def cast(self):
        cast_list = []
        try:
            item_cast = self.movieCredits["cast"]
            for actor in item_cast:
                name, id, gender, image = itemgetter(
                    "name", "id", "gender", "profile_path"
                )(actor)
                if gender and image:
                    cast = Cast(id=id, name=name, gender=gender, image=image)
                    cast_list.append(cast)
        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Cast")

        return cast_list

    def studios(self):
        studios = []
        try:
            studios_data = self.movieDetails.production_companies

            for studio in studios_data:
                id, name, url, country = itemgetter(
                    "id", "name", "logo_path", "origin_country"
                )(studio)

                if url:  # Only add Companies which have valid image
                    studios.append(Studio(id=id, name=name, image=url, country=country))

        except (KeyError, AttributeError):
            logger.warning(
                f"TMDb Movie Id : '{self.tmdb_id}' failed to get Production Companies"
            )

        return studios

    def crew(self):
        directors = []
        writers = []
        try:
            all_crew = self.movieCredits["crew"]

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

        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Crew")

        if not directors:
            logger.debug(f"TMDb Movie Id : '{self.tmdb_id}' Directors List is Empty")
        if not writers:
            logger.debug(f"TMDb Movie Id : '{self.tmdb_id}' Writers List is Empty")

        return [*directors, *writers]

    def countries(self):
        try:
            countries = []

            item_countries = self.movieDetails["production_countries"]

            for item_country in item_countries:
                country = item_country["name"]
                countries.append(country)

        except (KeyError, AttributeError):
            logger.warning(
                f"TMDb Movie Id : '{self.tmdb_id}' failed to get Production Countries"
            )

        if not countries:
            logger.debug(
                f"TMDb Movie Id : '{self.tmdb_id}' Production Countries List is Empty"
            )

        return countries


# print(MovieData('754').runtime())
