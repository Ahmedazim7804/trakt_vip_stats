from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from tmdbv3api import TMDb
import tmdbv3api
from operator import itemgetter
from tmdbv3api.exceptions import TMDbException
from loguru import logger


tmdb = TMDb()
tmdb.api_key = "***REMOVED***"
trakt_CLIENT_ID = "***REMOVED***"
TMDbMovie = tmdbv3api.Movie()


class Cast(SQLModel, table=True, arbitrary_types_allowed=True):
    id : int = Field(primary_key=True)
    name : Optional[str]
    gender : Optional[str]
    image: Optional[str]


class Studio(SQLModel, table=True, arbitrary_types_allowed=True):
    id : int = Field(primary_key=True)
    name : Optional[str]
    country: Optional[str]
    movies: int = Field(default=1)
    image: Optional[str]


class Crew(SQLModel, table=True, arbitrary_types_allowed=True):
    id: int = Field(primary_key=True)
    name: str
    dept: str
    job : Optional[str]
    image : Optional[str]


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
    cast: List[int] = Field(sa_column=Column(JSON))
    studios: List[int] = Field(sa_column=Column(JSON))
    genres: List[str] = Field(sa_column=Column(JSON))
    crew: List[int] = Field(sa_column=Column(JSON))
    countries: List[str] = Field(sa_column=Column(JSON))
    runtime: Optional[int]
    poster: Optional[str]
    rating: Optional[int] = Field(default=0)
        


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

    @staticmethod
    def get_cast(tmdb_id):
        cast_list = []
        try:
            item_cast = TMDbMovie.credits(tmdb_id)
            item_cast = item_cast['cast']
            for actor in item_cast:
                name, id, gender, image = itemgetter('name', 'id', 'gender', 'profile_path')(actor)
                if (gender and image):
                    cast = Cast(
                        id=id,
                        name=name,
                        gender=gender,
                        image=image
                    )
                    cast_list.append(cast)
        except TMDbException:
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Cast")

        return cast_list

    @staticmethod
    def get_studios(tmdb_id):
        studios = []
        try:
            studios_data = TMDbMovie.details(tmdb_id).production_companies

            for studio in studios_data:
                id, name, url, country = itemgetter('id', 'name', 'logo_path', 'origin_country')(studio)

                if url:  # Only add Companies which have valid image
                    studios.append(
                        Studio(id=id, name=name, image=url, country=country)
                    )

        except TMDbException:
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Production Companies")

        return studios

    @staticmethod
    def get_crew(tmdb_id):
        directors = []
        writers = []
        try:
            all_crew = TMDbMovie.credits(tmdb_id)['crew']

            for person in all_crew:
                id, name, dept, job, image = itemgetter('id', 'name', 'department', 'job', 'profile_path')(person)

                if person['job'] == 'Director':
                    directors.append(
                        Crew(id=id, name=name, dept=dept, job=job, image=image)
                    )
            
                if person['department'] == 'Writing':
                    writers.append(
                        Crew(id=id, name=name, dept=dept, job=job, image=image)
                    )

        except (TMDbException, KeyError):
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Crew")

        if not directors:
            logger.debug(f"TMDb Movie Id : '{tmdb_id}' Directors List is Empty")
        if not writers:
            logger.debug(f"TMDb Movie Id : '{tmdb_id}' Writers List is Empty")
        
        return [*directors, *writers]
    

    @staticmethod
    def get_countries(tmdb_id):
        try:
            countries = []

            item_countries = TMDbMovie.details(tmdb_id)["production_countries"]

            for item_country in item_countries:
                country = item_country['iso_3166_1']
                countries.append(country)

        except (TMDbException, KeyError):
            logger.warning(f"TMDb Movie Id : '{tmdb_id}' failed to get Production Countries")

        if not countries:
            logger.debug(f"TMDb Movie Id : '{tmdb_id}' Production Countries List is Empty")

        return countries

#print(MovieGetData.get_genres(tmdb_id='550'))