from trakt_engine import BASE_URL, CORE
from urllib.parse import urljoin
from sqlmodel import Session, create_engine, select
from Models.movies_model import Movie
from datetime import datetime, timezone


def first_play():
    engine = create_engine("sqlite:///database.db")

    movie_name = ''
    earliest = datetime.now(tz=timezone.utc)

    with Session(engine) as session:
        movies = session.exec(select(Movie.title, Movie.watched_at)).all()

        for movie in movies:
            title, watched_ats = movie
            for watched_at in watched_ats:
                watched_at = datetime.fromisoformat(watched_at)
                if watched_at < earliest:
                    earliest = watched_at
                    movie_name = title
    
    return movie_name, earliest

def oldest_play():
    
    '''
    I checked many users trakt all-time-stats, and first play were always a movie, now it could be that anyone is more likely to watch older movies rather than older show or trakt only shows a movie in first_play.
    Therefore i have excluded episodes here.
    '''

    engine = create_engine("sqlite:///database.db")

    with Session(engine) as session:
        title = session.exec(select(Movie.title).order_by(Movie.released_year)).first()

    return title