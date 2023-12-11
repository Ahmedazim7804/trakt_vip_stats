from trakt.core import BASE_URL, CORE
from urllib.parse import urljoin
from sqlmodel import Session, create_engine, select, col
from sqlalchemy import desc
from Models.episode_model import Episode
from Models.shows_model import TV, Network
from Models.list_model import Trakt250Shows, Imdb250Shows, RollingStone100Shows
from datetime import datetime, timezone
import collections
import calendar


engine = create_engine("sqlite:///database.db")

def time_of_oldest_watched_episode():
    earliest = datetime.now(tz=timezone.utc)

    with Session(engine) as session:

        '''
        Check all episodes time to find the episode which was watched earliest in time.
        '''

        for watched_ats in session.exec(select(Episode.watched_at)).fetchall():
            for watched_at in watched_ats:
                watched_at = datetime.fromisoformat(watched_at)
                if watched_at < earliest:
                    earliest = watched_at
    
    return earliest


def time_since_first_play():
    earliest = time_of_oldest_watched_episode()
    
    days : float = (datetime.now(tz=timezone.utc) - earliest).days
    months : float = (days / 30.4375)
    years : float = (months / 12)
    
    return years, months, days


def tv_stats():

    url = urljoin(BASE_URL, 'users/ahmedazim7804/stats')
    data = CORE._handle_request(url=url, method='get')

    hours = round((data['episodes']['minutes'] / 60), 0)
    plays = data['episodes']['plays']
    
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
        for watched_ats in session.exec(select(Episode.watched_at)).fetchall():
            for watched_at in watched_ats:
                time = datetime.fromisoformat(watched_at)

                year = time.year
                month = time.strftime("%b")
                day = time.strftime("%a")
                hour = time.hour

                by_year[year] = by_year.get(year, 0) + 1    
                by_month[month] = by_month.get(month, 0) + 1   
                by_day_of_week[day] = by_day_of_week.get(day, 0) + 1
                by_hour[hour] = by_hour.get(hour, 0) + 1
    
    # Adding years where no Show has watched
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


def users_top_10_watched_shows():

    def prettify_minutes(minutes):
        days = minutes // (24 * 60)
        hours = (minutes % (24 * 60)) // 60
        remaining_minutes = minutes % 60

        return f"{days}D {hours}H {remaining_minutes}M"

    shows = {}

    with Session(engine) as session:
        shows_id = session.exec(select(TV.tmdb_id)).fetchall()
        
        for show_id in shows_id:
            runtimes = session.exec(select(Episode.runtime).where(Episode.tmdb_show_id == show_id)).fetchall()
            watched_time = sum(runtimes)

            shows[show_id] = watched_time

        shows = dict(collections.Counter(shows).most_common(10)) # Highest watched 10 shows

        for id, runtime in shows.items():
            runtime = prettify_minutes(runtime)
            poster = session.exec(select(TV.poster).where(TV.tmdb_id == id)).first()
            shows[id] = {'runtime': runtime, 'poster': poster}

    return shows

def shows_by_genre():
    shows = {}

    with Session(engine) as session:
        for genres in session.exec(select(TV.genres)).fetchall():
            for genre in genres:
                shows[genre] = shows.get(genre, 0) + 1

    # Sorting Dictionary
    shows = dict(sorted(shows.items(), key=lambda item: item[1], reverse=True))
    
    return shows

def shows_by_released_year():
    shows = {}

    with Session(engine) as session:
        for released_year in session.exec(select(TV.released_year)).fetchall():
            shows[released_year] = shows.get(released_year, 0) + 1
    
    for year in range(min(shows.keys()), max(shows.keys())):
        if year not in shows.keys():
            shows[year] = 0

    return shows

def shows_by_country():
    shows = {}

    with Session(engine) as session:
        for countries in session.exec(select(TV.countries)).fetchall():
            for country in countries:
                shows[country] = shows.get(country, 0) + 1

    return shows

def shows_by_networks():
    networks_list = {}

    with Session(engine) as session:
        for newtorks in session.exec(select(TV.networks)).fetchall():
            for network_id in newtorks:
                network, image = session.exec(select(Network.name, Network.image).where(Network.id == network_id)).first()
                if network in networks_list.keys():
                    networks_list[network]['shows'] = networks_list[network]['shows'] + 1
                else:
                    networks_list[network] = {'shows': 1, 'logo': image}
    
    return networks_list

def list_progress():
    with Session(engine) as session:
        
        trakt_list = session.exec(select(Trakt250Shows.tmdb_id)).fetchall()
        imdb_list = session.exec(select(Imdb250Shows.tmdb_id)).fetchall()
        rolling_list = session.exec(select(RollingStone100Shows.tmdb_id)).fetchall()

        watched_trakt_shows = session.exec(select(TV.tmdb_id).where(TV.tmdb_id.in_(trakt_list))).fetchall()
        watched_imdb_shows = session.exec(select(TV.tmdb_id).where(TV.tmdb_id.in_(imdb_list))).fetchall()
        watched_rolling_shows = session.exec(select(TV.tmdb_id).where(TV.tmdb_id.in_(rolling_list))).fetchall()

        watched_trakt_shows = len(watched_trakt_shows)
        watched_imdb_shows = len(watched_imdb_shows)
        watched_rolling_shows = len(watched_rolling_shows)

        total_trakt_shows = len(trakt_list)
        total_imdb_shows = len(imdb_list)
        total_rolling_shows = len(rolling_list)

    
    return {
        'trakt': {'total': total_trakt_shows, 'watched': watched_trakt_shows},
        'imdb': {'total': total_imdb_shows, 'watched': watched_imdb_shows},
        'rollingstone' : {'total': total_rolling_shows, 'watched': watched_rolling_shows}
    }
        
        

def highest_rated_shows():
    
    with Session(engine) as session:
        rated_shows = session.exec(select(TV.tmdb_id, TV.rating, TV.poster).order_by(desc(TV.rating)).limit(10)).fetchall()
        rated_shows = {item[0] : {'rating': item[1], 'poster': item[2]} for item in rated_shows}

    return rated_shows

def all_ratings():

    ratings = {}
    with Session(engine) as session:
        for rating in range(1,11):
            ratings[rating] = len(session.exec(select(True).where(TV.rating == rating)).fetchall())
    
    return ratings