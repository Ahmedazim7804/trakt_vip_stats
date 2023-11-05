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
TMDbTV = tmdbv3api.TV()


class Network(SQLModel, table=True, arbitrary_types_allowed=True):
    id : int = Field(primary_key=True)
    name: str
    image: Optional[str]


class TV(SQLModel, table=True, arbitrary_types_allowed=True):
    trakt_id : int = Field(primary_key=True)
    title : str
    episode_plays : int
    released_year : int
    rating: int #FIXME:
    poster: str
    networks: List[int] = Field(sa_column=Column(JSON))
    genres: List[int] = Field(sa_column=Column(JSON))
    countries: List[str] = Field(sa_column=Column(JSON))

class GetTvData:

    @staticmethod
    def get_genres(tmdb_id):
        genres = []

        try:
            item_info = TMDbTV.details(tmdb_id)['genres']

            for genre in item_info:
                genre = genre['name']
                if ' & ' in genre:
                    genres.extend(genre.split(' & '))
                else:
                    genres.append(genre)

        except TMDbException:
            logger.warning(f"TMDb Show Id : '{tmdb_id}' failed to get Genres")

        if not genres:
            logger.debug(f"TMDb Show Id : '{tmdb_id}' Genres are empty")

        return genres


    @staticmethod
    def get_network(tmdb_id):
        networks = []

        try:
            all_networks = TMDbTV.details(tmdb_id)['networks']

            for network in all_networks:
                id, name, image = itemgetter('id', 'name', 'logo_path')(network)

                networks.append(
                    Network(id=id, name=name, image=image)
                )
        except TMDbException:
            logger.warning(f"TMDb Show Id : '{tmdb_id}' failed to get Networks")

        if not networks:
            logger.debug(f"TMDb Show Id : '{tmdb_id}' Networks are empty")

        return networks
    

    @staticmethod
    def get_poster(tmdb_id):
        poster = None

        try:
            poster = TMDbTV.details(tmdb_id).poster_path
        except TMDbException:
            logger.warning(f"TMDb Show Id : '{tmdb_id}' failed to get Poster")

        if not poster:
            logger.debug(f"TMDb Show Id : '{tmdb_id}' Poster are empty")

        return poster

    
    @staticmethod
    def get_countries(tmdb_id):
        try:
            countries = []

            item_countries = TMDbTV.details(tmdb_id)["production_countries"]

            for item_country in item_countries:
                country = item_country['iso_3166_1']
                countries.append(country)

        except (TMDbException, KeyError):
            logger.warning(f"TMDb Show Id : '{tmdb_id}' failed to get Production Countries")

        if not countries:
            logger.debug(f"TMDb Show Id : '{tmdb_id}' Production Countries List is Empty")

        return countries