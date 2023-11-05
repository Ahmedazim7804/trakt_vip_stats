from sqlmodel import SQLModel, Field, ARRAY, Column, JSON, ForeignKey, Relationship
from typing import List, Optional
from tmdbv3api import TV
from tmdbv3api import TMDb
import tmdbv3api
from tmdbv3api import Season
from tmdbv3api import Episode
from operator import itemgetter
import json
from tmdbv3api.exceptions import TMDbException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Mapped


tmdb = TMDb()
tmdb.api_key = "***REMOVED***"
trakt_CLIENT_ID = "***REMOVED***"
TMDbMovie = tmdbv3api.Movie()

class Cast(BaseModel):
    id : int = Field(primary_key=True)
    name : Optional[str]
    gender : Optional[str]
    image: Optional[str]

class Movie(SQLModel, table=True, arbitrary_types_allowed=True, orm_mode = True):
    id: int
    title: str
    trakt_id: str = Field(primary_key=True)
    imdb_id: str = None
    tmdb_id: str = None
    watched_at: List[str] = Field(sa_column=Column(JSON))
    watched_ids: List[str] = Field(sa_column=Column(JSON))
    plays: int
    released_year: int
    cast: Mapped
        
    #cast_relation: List[cast] = Relationship(back_populates='movie_relation')
    # rating: Optional[int]
    # runtime: Optional[int]
    # genres: List[str] = Field(sa_column=Column(JSON))
    # poster: Optional[str]
    # countries: Optional[str]
    # studios: List[str] = Field(sa_column=Column(JSON))
    # crew: List[str] = Field(sa_column=Column(JSON))


class MovieGetData:
    @staticmethod
    def get_genres(tmdb_id):
        genres = []

        try:
            item_info = TMDbMovie.details(tmdb_id)["genres"]

            for genre in item_info:
                genre = genre["name"]
                if " & " in genre:
                    genres.extend(genre.split(" & "))
                else:
                    genres.append(genre)

        except TMDbException:
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Genres")
            return genres

        if not genres:
            logger.debug(f"TMDb Movie Id : '{tmdb_id}' Genres are empty")

        return genres
    
    @staticmethod
    def get_runtime(tmdb_id):
        runtime = 0

        try:
            runtime = TMDbMovie.details(tmdb_id)['runtime']
        except TMDbException:
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Runtime")
            return runtime

        if not runtime:
            logger.debug(f"TMDB Movie Id: '{tmdb_id}' runtime is 0")
        
        return runtime

    def get_poster(tmdb_id):
        poster = None

        try:
            poster = TMDbMovie.details(tmdb_id).poster_path
        except TMDbException:
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Poster")

        return poster

    def get_cast(tmdb_id):
        castlist = []
        try:
            item_cast = TMDbMovie.credits(tmdb_id)['cast']
            for actor in item_cast:
                name, id, gender, image = itemgetter('name', 'id', 'gender', 'profile_path')(actor)
                cast = Cast(
                    id=id,
                    name=name,
                    gender=gender,
                    image=image
                )
                castlist.append(cast)
        except TMDbException:
            pass

        return castlist