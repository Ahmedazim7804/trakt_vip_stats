from tmdbv3api import TV
from tmdbv3api import TMDb
from tmdbv3api import Movie
from tmdbv3api import Season
from tmdbv3api import Episode
from tmdbv3api.exceptions import TMDbException


tmdb = TMDb()
tmdb.api_key = '***REMOVED***'
trakt_CLIENT_ID = '***REMOVED***'

def get_genres(tmdb_id, type_of_item):
    if tmdb_id not in info.keys():
        info[tmdb_id] = {}

    if 'genres' in info.get(tmdb_id, {}).keys() and not firstRun:
        genres = info[tmdb_id]['genres']
    else:
        genres = []
        try:
            if type_of_item == 'movie':
                item_info = TMDbMovie.details(tmdb_id)['genres']
            else:
                item_info = TMDbTV.details(tmdb_id)['genres']

            for genre in item_info:
                genre = genre['name']
                if ' & ' in genre:
                    genres.extend(genre.split(' & '))
                else:
                    genres.append(genre)
        except TMDbException:
            pass

        info[tmdb_id]['genres'] = genres

    return genres