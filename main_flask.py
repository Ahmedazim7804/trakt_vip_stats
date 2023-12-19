from flask import Flask
from flask import jsonify
from parseData import parse_tv_data
from parseData import parse_movie_data
from parseData import parse_other_data
from parseData import parse_list_data
from parseData import parse_cast
from parseData import parse_crew
from get_data import get_other_data
from main import authenticate

load_dotenv()

username = os.environ['username']
client_id = os.environ['trakt_client_id']
client_secret = os.environ['trakt_client_secret']

authenticate(username, client_id=client_id, client_secret=client_secret)

app = Flask(__name__)
app.json.sort_keys = False

@app.route('/all_time_stats', methods=['GET'])
def all_time_stats():
    return jsonify(get_other_data.all_time_stats())

@app.route('/first_play', methods=['GET'])
def first_play():
    return jsonify(parse_other_data.first_play())

@app.route('/pfp', methods=['GET'])
def profile_picture():
    return parse_other_data.profile_picture()

@app.route('/username', methods=['GET'])
def username_route():
    return username

@app.route('/tv/stats', methods=['GET'])
def tv_stats():
    return jsonify(parse_tv_data.tv_stats())

@app.route('/tv/plays', methods=['GET'])
def tv_plays_by_time():
    return jsonify(parse_tv_data.plays_by_time())

@app.route('/tv/users_top_10', methods=['GET'])
def users_top_10_watched_shows():
    return jsonify(parse_tv_data.users_top_10_watched_shows())

@app.route('/trakt/most_watched_shows', methods=['GET'])
def trakt_most_watched_shows(): 
    return jsonify(parse_list_data.trakt_most_watched_shows())

@app.route('/tv/by_genre', methods=['GET'])
def shows_by_genre():
    return jsonify(parse_tv_data.shows_by_genre())

@app.route('/tv/by_released_year', methods=['GET'])
def shows_by_released_year():
    return jsonify(parse_tv_data.shows_by_released_year())

@app.route('/tv/by_country', methods=['GET'])
def shows_by_country():
    return jsonify(parse_tv_data.shows_by_country())

@app.route('/tv/by_networks', methods=['GET'])
def shows_by_networks():
    return jsonify(parse_tv_data.shows_by_networks())

@app.route('/tv/list_progress', methods=['GET'])
def tv_list_progress():
    return jsonify(parse_tv_data.list_progress())

@app.route('/tv/highest_rated', methods=['GET'])
def highest_rated_shows():
    return parse_tv_data.highest_rated_shows()

@app.route('/tv/all_ratings', methods=['GET'])
def tv_all_ratings():
    return jsonify(parse_tv_data.all_ratings())

@app.route('/actors', methods=['GET'])
def actors():
    return jsonify(parse_cast.most_watched_actors())

@app.route('/actresses', methods=['GET'])
def actresses():
    return jsonify(parse_cast.most_watched_actresses())

@app.route('/directors', methods=['GET'])
def directors():
    return jsonify(parse_crew.most_watched_directors())

@app.route('/writers', methods=['GET'])
def writers():
    return jsonify(parse_crew.most_watched_writers())

@app.route('/movies/stats', methods=['GET'])
def movie_stats():
    return jsonify(parse_movie_data.movie_stats())

@app.route('/movies/plays', methods=['GET'])
def movies_plays_by_time():
    return jsonify(parse_movie_data.plays_by_time())

@app.route('/movies/users_top_10', methods=['GET'])
def users_top_10_watched_movies():
    return jsonify(parse_movie_data.users_top_10_watched_movies())

@app.route('/trakt/most_watched_movies', methods=['GET'])
def trakt_most_watched_movies(): 
    return jsonify(parse_list_data.trakt_most_watched_movies())

@app.route('/movies/by_genre', methods=['GET'])
def movies_by_genre():
    return jsonify(parse_movie_data.movies_by_genre())

@app.route('/movies/by_released_year', methods=['GET'])
def movies_by_released_year():
    return jsonify(parse_movie_data.movies_by_released_year())

@app.route('/movies/by_country', methods=['GET'])
def movies_by_country():
    return jsonify(parse_movie_data.movies_by_country())

@app.route('/movies/list_progress', methods=['GET'])
def movies_list_progress():
    return jsonify(parse_movie_data.list_progress())

@app.route('/movies/highest_rated', methods=['GET'])
def highest_rated_movies():
    return parse_movie_data.highest_rated_movies()

@app.route('/movies/all_ratings', methods=['GET'])
def movies_all_ratings():
    return jsonify(parse_movie_data.all_ratings())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8455, debug=True)