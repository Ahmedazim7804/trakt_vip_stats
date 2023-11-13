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
TMDbTV = tmdbv3api.TV()

engine = create_engine("sqlite:///database.db")

class Network(SQLModel, table=True, arbitrary_types_allowed=True):
    id : int = Field(primary_key=True)
    name: str
    shows: int = Field(default=1)
    image: Optional[str]

    def add_to_db(self):
        with Session(engine) as session:
            existed_network = session.exec(select(Network).where(Network.id == self.id)).first()
            if not existed_network:
                session.add(self)
            else:
                existed_network.shows = existed_network.shows + 1
                session.add(existed_network)
            
            session.commit()


class TV(SQLModel, table=True, arbitrary_types_allowed=True):
    trakt_id : int = Field(primary_key=True)
    title : str
    episode_plays : int
    released_year : int
    rating: int #FIXME:
    poster: str
    networks: List[int] = Field(sa_column=Column(JSON))
    genres: List[str] = Field(sa_column=Column(JSON))
    countries: List[str] = Field(sa_column=Column(JSON))

    def add_to_db(self):
        with Session(engine) as session:
            existed = session.exec(select(TV).where(TV.trakt_id == self.trakt_id)).first()
            if not existed:
                session.add(self)
                session.commit()

    def set_rating(self, rating):
        with Session(engine) as session:
            self.rating = int(rating)
            session.add(self)
            session.commit()


class TvData:

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id

        try:
            self.tvDetails = TMDbTV.details(tmdb_id)
        except:
            pass

    def genres(self):
        genres = []

        try:
            item_info = self.tvDetails['genres']

            for genre in item_info:
                genre = genre['name']
                if ' & ' in genre:
                    genres.extend(genre.split(' & '))
                else:
                    genres.append(genre)

        except (KeyError, AttributeError):
            logger.warning(f"TMDb Show Id : '{self.tmdb_id}' failed to get Genres")

        return genres


    def network(self):
        networks = []

        try:
            all_networks = self.tvDetails['networks']

            for network in all_networks:
                id, name, image = itemgetter('id', 'name', 'logo_path')(network)

                networks.append(
                    Network(id=id, name=name, image=image)
                )
        except (KeyError, AttributeError):
            logger.warning(f"TMDb Show Id : '{self.tmdb_id}' failed to get Networks")

        return networks
    

    def poster(self):
        poster = None

        try:
            poster = self.tvDetails.poster_path
        except (KeyError, AttributeError):
            logger.warning(f"TMDb Show Id : '{self.tmdb_id}' failed to get Poster")

        return poster

    
    def countries(self):
        try:
            countries = []

            item_countries = self.tvDetails["production_countries"]

            for item_country in item_countries:
                country = item_country['iso_3166_1']
                countries.append(country)

        except (TMDbException, KeyError):
            logger.warning(f"TMDb Show Id : '{self.tmdb_id}' failed to get Production Countries")

        return countries