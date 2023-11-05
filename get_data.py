from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from sqlitedict import SqliteDict
import json
from movies_model import Movie, MovieGetData, Cast
from sqlmodel import SQLModel, create_engine, Session, select

from tmdbv3api import TV
from tmdbv3api import TMDb
from tmdbv3api import Season
from tmdbv3api import Episode
from tmdbv3api.exceptions import TMDbException

tmdb = TMDb()
tmdb.api_key = '***REMOVED***'
trakt_CLIENT_ID = '***REMOVED***'


username = "***REMOVED***"
client_id ='***REMOVED***'
client_secret = '***REMOVED***'
#main.authenticate(username, client_id=client_id, client_secret=client_secret)

def get_movies():
    file = open('data.json', 'r')
    data = json.load(file)
    file.close()

    engine = create_engine("sqlite:///database.db")
    SQLModel.metadata.create_all(engine)
            
    for item in data['history']:
        if item['type'] == 'movie':

            MovieGetData.get_genres(item['movie']['ids']['tmdb'])

            watched_id = str(item['id']) # Unique Watched id, unique for any item
            trakt_id = item['movie']['ids']['trakt'] # Unique movie trakt id

            with Session(engine) as session:
                existed = session.exec(select(Movie).where(Movie.id == trakt_id)).first()

            if not existed:
                title = item['movie']['title']
                released_year = item['movie']['year']
                imdb_id = item['movie']['ids']['imdb']
                tmdb_id = item['movie']['ids']['tmdb']
                watched_ids = [watched_id]
                watched_at = item['watched_at']
                plays = 1
                rating = 0
                genres = []
                studios = []
                cast = MovieGetData.get_cast(tmdb_id=tmdb_id)
                crew = []

                movie = Movie(
                    id=trakt_id,
                    title=title,
                    trakt_id=trakt_id,
                    imdb_id=imdb_id,
                    tmdb_id=tmdb_id,
                    watched_at=[watched_at],
                    watched_ids=watched_ids,
                    plays=plays,
                    cast=cast,
                    released_year=released_year,
                )

                with Session(engine) as session:
                    session.add(movie)
                    session.commit()

            elif watched_id not in existed.watched_ids:
                existed.watched_ids = [*existed.watched_ids, watched_id]
                existed.watched_at = [*existed.watched_at, item['watched_at']]
                existed.plays += 1

                with Session(engine) as session:
                    session.add(existed)
                    session.commit()

    # for page in range(4,5):
    #     url = urljoin(BASE_URL, f"users/ahmedazim7804/history?page={page}")
    #     data = CORE._handle_request(method='get', url=url)
    #     for j in data:
    #         if j['type'] == 'movie':
    #             print(j)

get_movies()