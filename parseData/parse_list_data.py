from sqlmodel import Session, create_engine, select
from Models.movies_model import Movie
from Models.episode_model import Episode
from Models.shows_model import TV
from Models.list_model import MostPlayedShows, MostPlayedMovies
from datetime import datetime
from datetime import timezone
from urllib.parse import urljoin
from trakt_engine import CORE, BASE_URL
from sqlalchemy import ARRAY

engine = create_engine("sqlite:///database.db")

def trakt_most_watched_shows():

    def prettify_play_count(count):
        count = '{:.3g}'.format(int(count) / 1000000)

        return f"{count}M PLAYS "

    shows = {}

    with Session(engine) as session:
        items = session.exec(select(MostPlayedShows.tmdb_id, MostPlayedShows.title, MostPlayedShows.play_count)).fetchall()

        for index, item in enumerate(items, 1):
            tmdb_id, title, play_count = item
            
            watched : bool = True if session.exec(select(TV.tmdb_id).where(TV.tmdb_id == tmdb_id)).first() else False 
            play_count = prettify_play_count(play_count)

            shows[index] = {'title': title, 'play_count': play_count, 'watched': watched}
        
    return shows


def trakt_most_watched_movies():

    def prettify_play_count(count):
        count = '{:.3g}'.format(int(count) / 1000000)

        return f"{count}M PLAYS "

    movies = {}

    with Session(engine) as session:
        items = session.exec(select(MostPlayedMovies.tmdb_id, MostPlayedMovies.title, MostPlayedMovies.play_count)).fetchall()

        for index, item in enumerate(items, 1):
            tmdb_id, title, play_count = item
            
            watched : bool = True if session.exec(select(Movie.tmdb_id).where(Movie.tmdb_id == tmdb_id)).first() else False 
            play_count = prettify_play_count(play_count)

            movies[index] = {'title': title, 'play_count': play_count, 'watched': watched}
        
    return movies