from trakt.core import BASE_URL, CORE
from urllib.parse import urljoin
from sqlmodel import Session, create_engine, select
from Models.movies_model import Movie
from Models.list_model import Trakt250Movies, Imdb250Movies, Reddit250Movies
from datetime import datetime, timezone
import collections

engine = create_engine("sqlite:///database.db")

def time_of_oldest_watched_movie():

    earliest = datetime.now(tz=timezone.utc)

    with Session(engine) as session:

        '''
        Check all Movies time to find the Movie which was watched earliest in time.
        '''

        for watched_ats in session.exec(select(Movie.watched_at)).fetchall():
            for watched_at in watched_ats:
                watched_at = datetime.fromisoformat(watched_at)
                if watched_at < earliest:
                    earliest = watched_at
    
    return earliest


def time_since_first_play():
    
    earliest = time_of_oldest_watched_movie()
    
    days : float = (datetime.now(tz=timezone.utc) - earliest).days
    months : float = (days / 30.4375)
    years : float = (months / 12)
    
    return years, months, days

def movie_stats():

    url = urljoin(BASE_URL, 'users/ahmedazim7804/stats')
    data = CORE._handle_request(url=url, method='get')

    hours = round((data['movies']['minutes'] / 60), 0)
    plays = data['movies']['plays']
    
    years, months , days = time_since_first_play()
    print(hours, plays)
    if hours:
        hours_per_year : float = round(hours / years, 1)
        hours_per_month : float = round(hours / months, 1)
        hours_day_day : float = round(hours / days, 1)
    else:
        hours_per_year = 0
        hours_per_month = 0
        hours_day_day = 0
    
    if plays:
        plays_per_year : float = round(plays / years, 1)
        plays_per_month : float = round(plays / months, 1)
        plays_day_day : float = round(plays / days, 1)
    else:
        plays_per_year = 0
        plays_per_month = 0
        plays_day_day = 0
    
    return {
        'hours' : (hours, hours_per_year, hours_per_month, hours_day_day),
        'plays' : (plays, plays_per_year, plays_per_month, plays_day_day)
    }


def plays_by_time():

    by_year = {}
    by_month = {}
    by_day_of_week = {}
    by_hour = {}

    with Session(engine) as session:
        for watched_ats in session.exec(select(Movie.watched_at)).fetchall():
            for watched_at in watched_ats:
                time = datetime.fromisoformat(watched_at)

                year = time.year
                month = time.strftime("%b")
                day = time.strftime("%b")
                hour = time.hour

                by_year[year] = by_year.get(year, 0) + 1 
                by_month[month] = by_month.get(month, 0) + 1   
                by_day_of_week[day] = by_day_of_week.get(day, 0) + 1
                by_hour[hour] = by_hour.get(hour, 0) + 1
    

    return (by_year, by_month, by_day_of_week, by_hour)


def users_top_10_watched_movies():

    def prettify_minutes(minutes):
        days = minutes // (24 * 60)
        hours = (minutes % (24 * 60)) // 60
        remaining_minutes = minutes % 60

        if days == 0:
            return f"{hours}H {remaining_minutes}M"
        else:
            return f"{days}D {hours}H {remaining_minutes}M"
        
    movies = {}

    with Session(engine) as session:
        
        for id, runtime in session.exec(select(Movie.trakt_id, Movie.runtime)).fetchall():
            movies[id] = movies.get(id, 0) + runtime

    movies = dict(collections.Counter(movies).most_common(10)) # Highest watched 10 movies

    for id, runtime in movies.items():
        runtime = prettify_minutes(runtime)

        movies[id] = runtime

    return movies

def movies_by_genre():
    movies = {}

    with Session(engine) as session:
        for genres in session.exec(select(Movie.genres)).fetchall():
            for genre in genres:
                movies[genre] = movies.get(genre, 0) + 1

    
    return movies


def movies_by_released_year():
    movies = {}

    with Session(engine) as session:
        for released_year in session.exec(select(Movie.released_year)).fetchall():
            movies[released_year] = movies.get(released_year, 0) + 1

    return movies

def movies_by_country():
    movies = {}

    with Session(engine) as session:
        for countries in session.exec(select(Movie.countries)).fetchall():
            for country in countries:
                movies[country] = movies.get(country, 0) + 1

    return movies

def movies_by_studios():
    movies = {}

    with Session(engine) as session:
        for studios in session.exec(select(Movie.studios)).fetchall():
            for studio in studios:
                movies[studio] = movies.get(studio, 0) + 1
    
    return movies

def list_progress():
    with Session(engine) as session:
        
        trakt_list = session.exec(select(Trakt250Movies.tmdb_id)).fetchall()
        imdb_list = session.exec(select(Imdb250Movies.tmdb_id)).fetchall()
        reddit_list = session.exec(select(Reddit250Movies.tmdb_id)).fetchall()

        watched_trakt_shows = session.exec(select(Movie.tmdb_id).where(Movie.tmdb_id.in_(trakt_list))).fetchall()
        watched_imdb_shows = session.exec(select(Movie.tmdb_id).where(Movie.tmdb_id.in_(imdb_list))).fetchall()
        watched_reddit_list = session.exec(select(Movie.tmdb_id).where(Movie.tmdb_id.in_(reddit_list))).fetchall()

        watched_trakt_shows = len(watched_trakt_shows)
        watched_imdb_shows = len(watched_imdb_shows)
        watched_reddit_list = len(watched_reddit_list)

        total_trakt_shows = len(trakt_list)
        total_imdb_shows = len(imdb_list)
        total_reddit_list = len(reddit_list)

    
    return {
        'trakt': {'total': total_trakt_shows, 'watched': watched_trakt_shows},
        'imdb': {'total': total_imdb_shows, 'watched': watched_imdb_shows},
        'reddit' : {'total': total_reddit_list, 'watched': watched_reddit_list}
    }

def highest_rated_movies():
    
    with Session(engine) as session:
        rated_movies = session.exec(select(Movie.tmdb_id, Movie.rating)).fetchall()
        rated_movies = sorted(rated_movies, key=lambda x: x[1], reverse=True)[:10]
        rated_movies = dict(rated_movies)


    return rated_movies


def all_ratings():

    ratings = {}
    with Session(engine) as session:
        for rating in range(1,11):
            ratings[rating] = len(session.exec(select(True).where(Movie.rating == rating)).fetchall())
    
    return ratings