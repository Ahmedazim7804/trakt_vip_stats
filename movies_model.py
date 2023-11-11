from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from tmdbv3api import TMDb
import tmdbv3api
from operator import itemgetter
from tmdbv3api.exceptions import TMDbException
from loguru import logger
from sqlmodel import create_engine, Session, select


tmdb = TMDb()
tmdb.api_key = "***REMOVED***"
trakt_CLIENT_ID = "***REMOVED***"
TMDbMovie = tmdbv3api.Movie()


class Cast(SQLModel, table=True, arbitrary_types_allowed=True):
    id : int = Field(primary_key=True)
    name : Optional[str]
    gender : Optional[str]
    image: Optional[str]
    episode : int = Field(default=0)
    shows : List[int] = Field(sa_column=Column(JSON), default=[])
    shows_count : int = Field(default = 0)
    movies : List[int] = Field(sa_column=Column(JSON), default=[])
    movies_count : int = Field(default=0)

    def add_to_db(self, tmdb_id, type):
        engine = create_engine("sqlite:///database.db")
        with Session(engine) as session:
            existed_person = session.exec(select(Cast).where(Cast.id == self.id)).first()
            if not existed_person:
                if type == 'episode':
                    self.add_show(tmdb_id)
                    self.add_episode()
                if type =='movie':
                    self.add_movie(tmdb_id)
                session.add(self)
            else:
                if type == 'episode':
                    existed_person.add_show(tmdb_id)
                    existed_person.add_episode()
                if type == 'movie':
                    existed_person.add_movie(tmdb_id)
                session.add(existed_person)

            session.commit()


    def add_show(self, show):
        if show not in self.shows:
            self.shows = [*self.shows, show]
            self.shows_count = self.shows_count + 1

    
    def add_episode(self):
        self.episode = self.episode + 1


    def add_movie(self, movie):
        if movie not in self.movies:
            self.movies = [*self.movies, movie]
            self.movies_count = self.movies_count + 1


class Crew(SQLModel, table=True, arbitrary_types_allowed=True):
    id: int = Field(primary_key=True)
    name: str
    dept: str
    job : Optional[str]
    image : Optional[str]
    episode : int = Field(default=0)
    shows : List[int] = Field(sa_column=Column(JSON), default=[])
    shows_count : int = Field(default=0)
    movies : List[int] = Field(sa_column=Column(JSON), default=[])
    movies_count : int = Field(default=0)

    def add_to_db(self, tmdb_id, type):
        engine = create_engine("sqlite:///database.db")
        with Session(engine) as session:
            existed_person = session.exec(select(Crew).where(Crew.id == self.id)).first()
            if not existed_person:
                if type == 'episode':
                    self.add_show(tmdb_id)
                    self.add_episode()
                if type == 'movie':
                    self.add_movie(tmdb_id)
                session.add(self)
            else:
                if type == 'episode':
                    existed_person.add_show(tmdb_id)
                    existed_person.add_episode()
                if type == 'movie':
                    existed_person.add_movie(tmdb_id)
                session.add(existed_person)
            
            session.commit()

    def add_show(self, show):
        if show not in self.shows:
            self.shows = [*self.shows, show]
            self.shows_count = self.shows_count + 1
    
    def add_episode(self):
        self.episode = self.episode + 1

    def add_movie(self, movie):
        if movie not in self.movies:
            self.movies = [*self.movies, movie]
            self.movies_count = self.movies_count + 1


class Studio(SQLModel, table=True, arbitrary_types_allowed=True):
    id : int = Field(primary_key=True)
    name : Optional[str]
    country: Optional[str]
    movies: int = Field(default=1)
    image: Optional[str]

    def add_to_db(self):
        engine = create_engine("sqlite:///database.db")
        with Session(engine) as session:
            existed_studio = session.exec(select(Studio).where(Studio.id == self.id)).first()
            if not existed_studio:
                session.add(self)
            else:
                existed_studio.movies = existed_studio.movies + 1
                session.add(existed_studio)
            
            session.commit()
        


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

    def add_to_db(self):
        engine = create_engine("sqlite:///database.db")
        with Session(engine) as session:
            existed = session.exec(select(Movie).where(Movie.tmdb_id == self.tmdb_id)).first()
            if not existed:
                session.add(self)
                session.commit()
            else:
                existed.watched_ids = [*existed.watched_ids, *self.watched_ids]
                existed.watched_at = [*existed.watched_at, *self.watched_at]
                existed.plays = existed.plays + 1
            
            session.commit()
        


class MovieData:

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id

        try:
            self.movieDetails = TMDbMovie.details(self.tmdb_id)
            self.movieCredits = TMDbMovie.credits(self.tmdb_id)
        except Exception as e:
            logger.error(f"TMDb Movie Id : '{self.tmdb_id}', failed to get INFO because {e}")

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
            runtime = self.movieDetails['runtime']
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
            item_cast = self.movieCredits['cast']
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
        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Cast")

        return cast_list

    def studios(self):
        studios = []
        try:
            studios_data = self.movieDetails.production_companies

            for studio in studios_data:
                id, name, url, country = itemgetter('id', 'name', 'logo_path', 'origin_country')(studio)

                if url:  # Only add Companies which have valid image
                    studios.append(
                        Studio(id=id, name=name, image=url, country=country)
                    )

        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Production Companies")

        return studios

    def crew(self):
        directors = []
        writers = []
        try:
            all_crew = self.movieCredits['crew']

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
                country = item_country['iso_3166_1']
                countries.append(country)

        except (KeyError, AttributeError):
            logger.warning(f"TMDb Movie Id : '{self.tmdb_id}' failed to get Production Countries")

        if not countries:
            logger.debug(f"TMDb Movie Id : '{self.tmdb_id}' Production Countries List is Empty")

        return countries

print(MovieData('754').runtime())