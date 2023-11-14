from sqlmodel import SQLModel, Field
from typing import Optional
from operator import itemgetter
from sqlmodel import create_engine, Session, select

# TODO: If rank of a movie changed or new movie took its place


class ListItem(SQLModel):
    trakt_id: str = Field(primary_key=True)
    imdb_id: Optional[str]
    tmdb_id: Optional[str]
    title: Optional[str]
    year: Optional[str]
    rank: Optional[str]


class Imdb250Movies(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                rank = item["rank"]
                title, year = itemgetter("title", "year")(item["movie"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["movie"]["ids"]
                )

                existed = session.exec(
                    select(Imdb250Movies).where(Imdb250Movies.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = Imdb250Movies(
                        rank=rank,
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                    )

                    session.add(movie)

            else:
                session.commit()


class RollingStone100Shows(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                rank = item["rank"]
                title, year = itemgetter("title", "year")(item["show"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["show"]["ids"]
                )

                existed = session.exec(
                    select(RollingStone100Shows).where(
                        RollingStone100Shows.trakt_id == trakt
                    )
                ).first()

                if not existed:
                    movie = RollingStone100Shows(
                        rank=rank,
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                    )

                    session.add(movie)
            else:
                session.commit()


class Imdb250Shows(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                rank = item["rank"]
                title, year = itemgetter("title", "year")(item["show"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["show"]["ids"]
                )

                existed = session.exec(
                    select(Imdb250Shows).where(Imdb250Shows.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = Imdb250Shows(
                        rank=rank,
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                    )

                    session.add(movie)
            else:
                session.commit()


class Trakt250Movies(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                rank = item["rank"]
                title, year = itemgetter("title", "year")(item["movie"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["movie"]["ids"]
                )

                existed = session.exec(
                    select(Trakt250Movies).where(Trakt250Movies.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = Trakt250Movies(
                        rank=rank,
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                    )

                    session.add(movie)
            else:
                session.commit()


class Trakt250Shows(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                rank = item["rank"]
                title, year = itemgetter("title", "year")(item["show"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["show"]["ids"]
                )

                existed = session.exec(
                    select(Trakt250Shows).where(Trakt250Shows.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = Trakt250Shows(
                        rank=rank,
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                    )

                    session.add(movie)
            else:
                session.commit()


class Reddit250Movies(ListItem, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                rank = item["rank"]
                title, year = itemgetter("title", "year")(item["movie"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["movie"]["ids"]
                )

                existed = session.exec(
                    select(Reddit250Movies).where(Reddit250Movies.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = Reddit250Movies(
                        rank=rank,
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                    )

                    session.add(movie)
            else:
                session.commit()


class ListItem2(SQLModel):
    trakt_id: str = Field(primary_key=True)
    imdb_id: Optional[str]
    tmdb_id: Optional[str]
    title: Optional[str]
    year: Optional[str]
    watcher_count: Optional[str] = None
    play_count: Optional[str] = None
    collected_count: Optional[str] = None
    collecter_count: Optional[str] = None


class MostPlayedShows(ListItem2, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                title, year = itemgetter("title", "year")(item["show"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["show"]["ids"]
                )
                (
                    watcher_count,
                    play_count,
                    collected_count,
                    collector_count,
                ) = itemgetter(
                    "watcher_count", "play_count", "collected_count", "collector_count"
                )(item)

                existed = session.exec(
                    select(MostPlayedShows).where(MostPlayedShows.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = MostPlayedShows(
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                        watcher_count=watcher_count,
                        play_count=play_count,
                        collected_count=collected_count,
                        collector_count=collector_count,
                    )

                    session.add(movie)

                else:
                    if (
                        existed.watcher_count != str(watcher_count)
                        or existed.play_count != str(play_count)
                        or existed.collected_count != str(collected_count)
                        or existed.collecter_count != str(collector_count)
                    ):
                        existed.watcher_count = watcher_count
                        existed.play_count = play_count
                        existed.collected_count = collected_count
                        existed.collecter_count = collector_count

                        session.add(existed)

            else:
                session.commit()


class MostPlayedMovies(ListItem2, table=True, arbitrary_types_allowed=True):
    @staticmethod
    def add_list_to_db(list):
        with Session(engine) as session:
            for item in list:
                title, year = itemgetter("title", "year")(item["movie"])
                trakt, imdb, tmdb = itemgetter("trakt", "imdb", "tmdb")(
                    item["movie"]["ids"]
                )
                watcher_count, play_count, collected_count = itemgetter(
                    "watcher_count", "play_count", "collected_count"
                )(item)

                existed = session.exec(
                    select(MostPlayedMovies).where(MostPlayedMovies.trakt_id == trakt)
                ).first()

                if not existed:
                    movie = MostPlayedMovies(
                        title=title,
                        year=year,
                        trakt_id=trakt,
                        imdb_id=imdb,
                        tmdb_id=tmdb,
                        watcher_count=watcher_count,
                        play_count=play_count,
                        collected_count=collected_count,
                    )

                    session.add(movie)

                else:
                    if (
                        existed.watcher_count != str(watcher_count)
                        or existed.play_count != str(play_count)
                        or existed.collected_count != str(collected_count)
                    ):
                        existed.watcher_count = watcher_count
                        existed.play_count = play_count
                        existed.collected_count = collected_count

                        session.add(existed)

            else:
                session.commit()


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
