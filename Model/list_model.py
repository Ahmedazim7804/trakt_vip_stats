from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from operator import itemgetter
from loguru import logger
from sqlmodel import create_engine, Session, select
from Model.movies_model import Movie
from tqdm import tqdm

#TODO: If rank of a movie changed or new movie took its place

class ListItem(SQLModel):
    trakt_id : str = Field(primary_key=True)
    imdb_id : str
    tmdb_id : str
    title : str
    year : str
    rank : str

class Imdb250Movies(ListItem, table=True, arbitrary_types_allowed=True):

    @staticmethod
    def add_list_to_db(list):
        with tqdm(total=len(list)) as pbar:
            with Session(engine) as session:
                for item in list:
                    rank = item['rank']
                    title, year = itemgetter('title', 'year')(item['movie'])
                    trakt, imdb, tmdb = itemgetter('trakt', 'imdb', 'tmdb')(item['movie']['ids'])

                    existed = session.exec(select(Imdb250Movies).where(Imdb250Movies.trakt_id == trakt)).first()

                    if not existed:
                        movie = Imdb250Movies(
                            rank=rank,
                            title=title,
                            year=year,
                            trakt_id=trakt,
                            imdb_id=imdb,
                            tmdb_id=tmdb
                        )

                        session.add(movie)
                    
                    pbar.update(1)

                else:
                    session.commit()
                    pbar.close()

class RollingStone100Shows(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with tqdm(total=len(list)) as pbar:
            with Session(engine) as session:
                for item in list:
                    rank = item['rank']
                    title, year = itemgetter('title', 'year')(item['show'])
                    trakt, imdb, tmdb = itemgetter('trakt', 'imdb', 'tmdb')(item['show']['ids'])

                    existed = session.exec(select(RollingStone100Shows).where(RollingStone100Shows.trakt_id == trakt)).first()

                    if not existed:
                        movie = RollingStone100Shows(
                            rank=rank,
                            title=title,
                            year=year,
                            trakt_id=trakt,
                            imdb_id=imdb,
                            tmdb_id=tmdb
                        )

                        session.add(movie)

                    pbar.update(1)
                else:
                    session.commit()
                    pbar.close()


class Imdb250Shows(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with tqdm(total=len(list)) as pbar:
            with Session(engine) as session:
                for item in list:
                    rank = item['rank']
                    title, year = itemgetter('title', 'year')(item['show'])
                    trakt, imdb, tmdb = itemgetter('trakt', 'imdb', 'tmdb')(item['show']['ids'])

                    existed = session.exec(select(Imdb250Shows).where(Imdb250Shows.trakt_id == trakt)).first()

                    if not existed:
                        movie = Imdb250Shows(
                            rank=rank,
                            title=title,
                            year=year,
                            trakt_id=trakt,
                            imdb_id=imdb,
                            tmdb_id=tmdb
                        )

                        session.add(movie)
                        
                    pbar.update(1)
                else:
                    session.commit()
                    pbar.close()


class Trakt250Movies(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with tqdm(total=len(list)) as pbar:
            with Session(engine) as session:
                for item in list:
                    rank = item['rank']
                    title, year = itemgetter('title', 'year')(item['movie'])
                    trakt, imdb, tmdb = itemgetter('trakt', 'imdb', 'tmdb')(item['movie']['ids'])

                    existed = session.exec(select(Trakt250Movies).where(Trakt250Movies.trakt_id == trakt)).first()

                    if not existed:
                        movie = Trakt250Movies(
                            rank=rank,
                            title=title,
                            year=year,
                            trakt_id=trakt,
                            imdb_id=imdb,
                            tmdb_id=tmdb
                        )

                        session.add(movie)

                    pbar.update(1)
                else:
                    session.commit()
                    pbar.close()


class Trakt250Shows(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with tqdm(total=len(list)) as pbar:
            with Session(engine) as session:
                for item in list:
                    rank = item['rank']
                    title, year = itemgetter('title', 'year')(item['show'])
                    trakt, imdb, tmdb = itemgetter('trakt', 'imdb', 'tmdb')(item['show']['ids'])

                    existed = session.exec(select(Trakt250Shows).where(Trakt250Shows.trakt_id == trakt)).first()

                    if not existed:
                        movie = Trakt250Shows(
                            rank=rank,
                            title=title,
                            year=year,
                            trakt_id=trakt,
                            imdb_id=imdb,
                            tmdb_id=tmdb
                        )

                        session.add(movie)

                    pbar.update(1)
                else:
                    session.commit()
                    pbar.close()


class Reddit250Movies(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with tqdm(total=len(list)) as pbar:
            with Session(engine) as session:
                for item in list:
                    rank = item['rank']
                    title, year = itemgetter('title', 'year')(item['movie'])
                    trakt, imdb, tmdb = itemgetter('trakt', 'imdb', 'tmdb')(item['movie']['ids'])

                    existed = session.exec(select(Reddit250Movies).where(Reddit250Movies.trakt_id == trakt)).first()
                    
                    if not existed:
                        movie = Reddit250Movies(
                            rank=rank,
                            title=title,
                            year=year,
                            trakt_id=trakt,
                            imdb_id=imdb,
                            tmdb_id=tmdb
                        )

                        session.add(movie)

                    pbar.update(1)
                else:
                    session.commit()
                    pbar.close()

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)