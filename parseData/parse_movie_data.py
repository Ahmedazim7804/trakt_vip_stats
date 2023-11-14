import sys
sys.path.append('/home/ajeem/Development/projects/python/traktData')
from trakt.core import BASE_URL, CORE
from urllib.parse import urljoin
from sqlmodel import Session, create_engine, select
from Models.movies_model import Movie
from Models.shows_model import TV
from datetime import datetime, timezone


def time_since_first_play():
    engine = create_engine("sqlite:///database.db")

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



if __name__ == '__main__':
    import sys
    sys.path.append('/home/ajeem/Development/projects/python/traktData/main.py')
    from main import authenticate

    username = "***REMOVED***"
    client_id = "***REMOVED***"
    client_secret = "***REMOVED***"
    authenticate(username, client_id=client_id, client_secret=client_secret)
    print(movie_stats())