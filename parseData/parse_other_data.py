from sqlmodel import Session, create_engine, select
from Models.movies_model import Movie
from Models.episode_model import Episode
from datetime import datetime
from datetime import timezone
from urllib.parse import urljoin
from trakt_engine import CORE, BASE_URL
import os

engine = create_engine("sqlite:///database.db")

def profile_picture():
    url = urljoin(BASE_URL, f'users/{os.environ["username"]}?extended=full')
    data = CORE._handle_request(url=url, method='get')

    pfp = data['images']['avatar']['full']

    return pfp

def first_play():

    """
    I have excluded TV Shows here, because in every all-time-stats page i have seen in trakt, oldest play is always a movie, it can be because of people have likely watched old movies rather than old tv show, or trakt may exclude tv show in 'first play'
    """

    first_play = datetime.now(tz=timezone.utc)
    movie_title = None
    tmdb_id = None

    with Session(engine) as session:

        for watched_ats, title, tmdb_id_ in session.exec(select(Movie.watched_at, Movie.title, Movie.tmdb_id)).fetchall():
            for watched_at in watched_ats:
                watched_at = datetime.fromisoformat(watched_at)
                if watched_at < first_play:
                    first_play = watched_at
                    movie_title = title
                    tmdb_id = tmdb_id_


    date = first_play.strftime("%d %B %Y")
    time = first_play.strftime("%H:%M")

    import requests
    response = requests.get(f'http://webservice.fanart.tv/v3/movies/{tmdb_id}?api_key=eb712f1a7ba8ef0fe678c4399ae2edea').json()
    try:
        movie_logo = response['hdmovielogo'][0]['url']
    except:
        movie_logo = None

    return {'movie': movie_title, 'date': date, 'time': time, 'movie_logo': movie_logo}


def most_recent_play():

    def most_recent_movie():

        min_time = datetime.min
        recent_play = min_time.replace(tzinfo=timezone.utc)
        
        movie_title = None

        with Session(engine) as session:

            for watched_ats, title in session.exec(select(Movie.watched_at, Movie.title)).fetchall():
                for watched_at in watched_ats:
                    watched_at = datetime.fromisoformat(watched_at)
                    if watched_at > recent_play:
                        recent_play = watched_at
                        movie_title = title

        return recent_play, movie_title

    def most_recent_episode():

        min_time = datetime.min
        recent_play = min_time.replace(tzinfo=timezone.utc)

        episode_title = None
        show_title = None
        episode = None
        season = None

        with Session(engine) as session:

            for watched_ats, show_title_, season_, episode_, episode_title_ in session.exec(select(Episode.watched_at, Episode.show_title, Episode.season, Episode.episode, Episode.episode_title)).fetchall():
                for watched_at in watched_ats:
                    watched_at = datetime.fromisoformat(watched_at)
                    if watched_at > recent_play:
                        recent_play = watched_at
                        show_title = show_title_
                        episode_title = episode_title_
                        season = season_
                        episode = episode_
        
            return recent_play, show_title, season, episode, episode_title

    recent_movie = most_recent_movie()
    recent_episode = most_recent_episode()

    if recent_movie[0] > recent_episode[0]:
        return recent_movie
    else:
        return recent_episode