import json
from dotenv import load_dotenv
import os
from parseData import parse_tv_data
from parseData import parse_movie_data
from parseData import parse_other_data
from parseData import parse_list_data
from parseData import parse_cast
from parseData import parse_crew
from get_data import get_other_data

def save():
    load_dotenv()

    username = os.environ['username']
    os.environ['trakt_client_id']
    os.environ['trakt_client_secret']

    json_data = {}

    json_data['all_time_stats'] = get_other_data.all_time_stats()
    json_data['first_play'] = parse_other_data.first_play()
    json_data['pfp'] = parse_other_data.profile_picture()
    json_data['username'] = username

    tv = {}
    tv['stats'] = parse_tv_data.tv_stats()
    tv['plays'] = parse_tv_data.plays_by_time()
    tv['users_top_10'] = parse_tv_data.users_top_10_watched_shows()
    tv['most_watched_shows'] = parse_list_data.trakt_most_watched_shows()
    tv['by_genre'] = parse_tv_data.shows_by_genre()
    tv['by_released_year'] = parse_tv_data.shows_by_released_year()
    tv['by_country'] = parse_tv_data.shows_by_country()
    tv['list_progress'] = parse_tv_data.list_progress()
    tv['highest_rated'] = parse_tv_data.highest_rated_shows()
    tv['all_ratings'] = parse_tv_data.all_ratings()
    json_data['tv'] = tv

    movies = {}
    movies['stats'] = parse_movie_data.movie_stats()
    movies['plays'] = parse_movie_data.plays_by_time()
    movies['users_top_10'] = parse_movie_data.users_top_10_watched_movies()
    movies['most_watched_movies'] = parse_list_data.trakt_most_watched_movies()
    movies['by_genre'] = parse_movie_data.movies_by_genre()
    movies['by_released_year'] = parse_movie_data.movies_by_released_year()
    movies['by_country'] = parse_movie_data.movies_by_country()
    movies['list_progress'] = parse_movie_data.list_progress()
    movies['highest_rated'] = parse_movie_data.highest_rated_movies()
    movies['all_ratings'] = parse_movie_data.all_ratings()
    json_data['movies'] = movies

    json_data['actors'] = parse_cast.most_watched_actors()
    json_data['actresses'] = parse_cast.most_watched_actresses()
    json_data['directors'] = parse_crew.most_watched_directors()
    json_data['writers'] = parse_crew.most_watched_writers()

    with open('trakt-all-time-stats.json', 'w') as file:
        json.dump(json_data, file, indent=4)