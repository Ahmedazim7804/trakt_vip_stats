from trakt_engine import BASE_URL, CORE
from urllib.parse import urljoin
from sqlmodel import Session, create_engine, select
from sqlalchemy import desc
from Models.movies_model import Movie
from Models.list_model import Trakt250Movies, Imdb250Movies, Reddit250Movies
from datetime import datetime, timezone
import collections
import calendar
import os

engine = create_engine("sqlite:///database.db")

def time_of_oldest_watched_movie():

    earliest = datetime.now(tz=timezone.utc)

    with Session(engine) as session:

        '''
        Check all Movies time to find the Movie which was watched earliest in time.
        '''

        for watched_ats in session.exec(select(Movie.watched_at)).fetchall():
            for watched_at in watched_ats:
                # watched_at = datetime.fromisoformat(watched_at)
                watched_at = datetime.strptime(watched_at, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
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

    url = urljoin(BASE_URL, f'users/{os.environ["username"]}/stats')
    data = CORE._handle_request(url=url, method='get')

    hours = round((data['movies']['minutes'] / 60), 0)
    plays = data['movies']['plays']
    
    years, months , days = time_since_first_play()
    
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
        'hours' : {'total': int(hours), 'per_year': hours_per_year, 'per_month': hours_per_month, 'per_day': hours_day_day},
        'plays' : {'total': int(plays), 'per_year': plays_per_year, 'per_month': plays_per_month, 'per_day': plays_day_day},
    }


def plays_by_time():

    by_year = {}
    by_month = {}
    by_day_of_week = {}
    by_hour = {}

    with Session(engine) as session:
        for watched_ats in session.exec(select(Movie.watched_at)).fetchall():
            for watched_at in watched_ats:
                time = datetime.strptime(watched_at, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                # time = datetime.fromisoformat(watched_at)

                year = time.year
                month = time.strftime("%b")
                day = time.strftime("%a")
                hour = time.hour

                by_year[year] = by_year.get(year, 0) + 1 
                by_month[month] = by_month.get(month, 0) + 1   
                by_day_of_week[day] = by_day_of_week.get(day, 0) + 1
                by_hour[hour] = by_hour.get(hour, 0) + 1
    
    # Adding years where no Movie has been watched
    max_year = max(by_year.keys())
    min_year = min(by_year.keys())
    for year in range(min_year, max_year):
        if year not in by_year.keys():
            by_year[year] = 0
    
    # Sort by_month by month name
    sorted_months = calendar.month_abbr[1:]
    by_month = dict(sorted(by_month.items(), key=lambda item: sorted_months.index(item[0])))

    # Sort by_day_of_week by day name
    sorted_days = calendar.day_abbr[:]
    
    by_day_of_week = dict(sorted(by_day_of_week.items(), key=lambda item: sorted_days.index(item[0])))

    # Sort by_year
    by_year = dict(sorted(by_year.items(), key=lambda item: item[0]))

    # Sort by_hour
    by_hour = dict(sorted(by_hour.items(), key=lambda item: item[0]))

    return {
        'by_year': by_year,
        'by_month': by_month,
        'by_day_of_week': by_day_of_week,
        'by_hour': by_hour
    }


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
        
        for id, runtime, plays in session.exec(select(Movie.tmdb_id, Movie.runtime, Movie.plays)).fetchall():
            movies[id] = movies.get(id, 0) + (runtime * plays)

    movies = dict(collections.Counter(movies).most_common(10)) # Highest watched 10 movies

    for id, runtime in movies.items():
        runtime = prettify_minutes(runtime)
        poster = session.exec(select(Movie.poster).where(Movie.tmdb_id == id)).first()
        movies[id] = {'runtime': runtime, 'poster': poster}

    return movies

def movies_by_genre():
    movies = {}

    with Session(engine) as session:
        for genres in session.exec(select(Movie.genres)).fetchall():
            for genre in genres:
                movies[genre] = movies.get(genre, 0) + 1

    movies = dict(sorted(movies.items(), key=lambda item: item[1], reverse=True))
    
    return movies


def movies_by_released_year():
    movies = {}

    with Session(engine) as session:
        for released_year in session.exec(select(Movie.released_year)).fetchall():
            if type(released_year) != int:
                continue
            movies[released_year] = movies.get(released_year, 0) + 1

    for year in range(min(movies.keys()), max(movies.keys())):
        if year not in movies.keys():
            movies[year] = 0

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
        rated_movies = session.exec(select(Movie.tmdb_id, Movie.rating, Movie.poster).order_by(desc(Movie.rating)).limit(10)).fetchall()
        rated_movies = {item[0] : {'rating': item[1], 'poster': item[2]} for item in rated_movies}


    return rated_movies


def all_ratings():

    ratings = {}
    with Session(engine) as session:
        for rating in range(1,11):
            ratings[rating] = len(session.exec(select(True).where(Movie.rating == rating)).fetchall())
    
    return ratings