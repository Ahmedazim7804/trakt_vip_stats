# Trakt All Time Stats
Trakt [all-time-stats](https://blog.trakt.tv/all-time-year-in-review-f6f931e4461d) without Trakt VIP.

# Prerequisite
* [Trakt Client ID](https://trakt.tv/oauth/applications)
* [TMDB API key](https://www.themoviedb.org/settings/api)

# Installation
- 1. Clone the repository:
     ```sh
     git clone https://github.com/Ahmedazim7804/trakt_vip_stats
     ```
- 2. Change to project directory:
     ```sh
     cd trakt_vip_stats
     ```
- 3. Install the dependencies:
     ```sh
     pip install -r requirements.txt
     ```

## Usage
Basic Usage:
- Populate .env file in repo directory. 
    ```sh
    username = "your trakt username"
    trakt_client_id = "your trakt client id"
    trakt_client_secret = "your trakt client secret"
    tmdb_api_key = "your tmdb api key"
    ```

```sh 
python main.py run --save
```
It will authenticate and get all neccessary data from trakt and tmdb api, and then generate `all-time-stats.json`

#### Command `run`
Create `database.db` with required all data from trakt to ``database.db``.
```sh
usage: TraktVipStats run [-h] [--save] [--log-level {ERROR,INFO,DEBUG,WARNING}] [--print-time]

options:
  -h, --help            show this help message and exit
  --save
  --log-level {ERROR,INFO,DEBUG,WARNING}
  --print-time
```

#### Command `update`
Updates specified data from trakt to `database.db`
```sh
usage: TraktVipStats update [-h] [--save] [--log-level {ERROR,INFO,DEBUG,WARNING}] {movies,tv,ratings,lists}

positional arguments:
  {movies,tv,ratings,lists}

options:
  -h, --help            show this help message and exit
  --save
  --log-level {ERROR,INFO,DEBUG,WARNING}
```
Example:
Let's say you tracked some new movie in trakt, now you want to update it here then
```sh
python main.py update movies --save
```

#### Command `save`
Generate the `all-time-stats.json` from existing `database.db`, equivalent to --save flag.
```sh
python main.py save
```

#### Command `server`
Start a basic flask server to serve the all-time-stats via basic http api.</br>
Used for app.
```sh
usage: TraktVipStats server [-h] [--port PORT] [--debug]

options:
  -h, --help   show this help message and exit
  --port PORT
  --debug
```
Available Endpoints are
 - ```/all_time_stats```
 - ```/first_play```
 - ```/pfp```
 - ```/username```
 - ```/actors```
 - ```/actresses```
 - ```/directors```
 - ```/writers```
 - ```/trakt/most_watched_shows```
 - ```/trakt/most_watched_movies```
 - ```/tv/stats```
 - ```/tv/plays```
 - ```/tv/users_top_10```
 - ```/tv/by_genre```
 - ```/tv/by_country```
 - ```/tv/list_progress```
 - ```/tv/highest_rated```
 - ```/tv/all_ratings```
 - ```/movies/stats```
 - ```/movies/plays```
 - ```/movies/users_top_10```
 - ```/movies/by_genre```
 - ```/movies/by_released_year```
 - ```/movies/by_country```
 - ```/movies/list_progress```
 - ```/movies/highest_rated```
 - ```/movies/all_ratings```


# Note
This program only generates [all-time-stats](https://blog.trakt.tv/all-time-year-in-review-f6f931e4461d) equivalent data. To see this data in graphical interface use this app.