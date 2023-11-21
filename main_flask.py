from flask import Flask
from flask import jsonify
from parseData import parse_tv_data
from main import authenticate


username = "***REMOVED***"
client_id = "***REMOVED***"
client_secret = "***REMOVED***"
authenticate(username, client_id=client_id, client_secret=client_secret)

app = Flask(__name__)


@app.route('/tv/stats', methods=['GET'])
def tv_stats():
    return jsonify(parse_tv_data.tv_stats())


@app.route('/tv/plays', methods=['GET'])
def plays_by_time():
    return jsonify(parse_tv_data.plays_by_time())


@app.route('/tv/users_top_10', methods=['GET'])
def users_top_10_watched_shows():
    return jsonify(parse_tv_data.users_top_10_watched_shows())


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
def list_progress():
    return jsonify(parse_tv_data.list_progress())


@app.route('/tv/highest_rated', methods=['GET'])
def highest_rated_shows():
    return jsonify(parse_tv_data.highest_rated_shows())


@app.route('/tv/all_ratings', methods=['GET'])
def all_ratings():
    return jsonify(parse_tv_data.all_ratings())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8455)