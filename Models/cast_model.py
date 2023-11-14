from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from sqlmodel import Session, select, create_engine

engine = create_engine("sqlite:///database.db")

class Cast(SQLModel, table=True, arbitrary_types_allowed=True):
    id: int = Field(primary_key=True)
    name: Optional[str]
    gender: Optional[str]
    image: Optional[str]
    episode: int = Field(default=0)
    shows: List[int] = Field(sa_column=Column(JSON), default=[])
    shows_count: int = Field(default=0)
    movies: List[int] = Field(sa_column=Column(JSON), default=[])
    movies_count: int = Field(default=0)

    def add_to_db(self, tmdb_id, type):
        with Session(engine) as session:
            existed_person = session.exec(
                select(Cast).where(Cast.id == self.id)
            ).first()
            if not existed_person:
                if type == "episode":
                    self.add_show(tmdb_id)
                    self.add_episode()
                if type == "movie":
                    self.add_movie(tmdb_id)
                session.add(self)
            else:
                if type == "episode":
                    existed_person.add_show(tmdb_id)
                    existed_person.add_episode()
                if type == "movie":
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