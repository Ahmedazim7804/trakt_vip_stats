from urllib.parse import urljoin
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv, set_key
from os import path, environ
import json
import requests
from datetime import datetime, timedelta, timezone

class Core():
    def __init__(self, client_id, client_secret, username):
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {'Content-Type': 'application/json', 'trakt-api-version': '2'}
        self.base_url = "https://api-v2launch.trakt.tv/"
        self.session = requests.Session()

        self.load_config()
    
    def load_config(self):
        load_dotenv()

        self.oauth_token = environ['trakt_oauth_token']
        self.oauth_refresh = environ['trakt_oauth_refresh']
        self.oauth_expires_at = environ['trakt_oauth_expires_at']
        self.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

    def authenticate(self):

        if self.is_user_authenticated():
            return
        
        authorization_base_url = "https://api-v2launch.trakt.tv/oauth/authorize"
        token_url = "https://api-v2launch.trakt.tv/oauth/token"

        oauth = OAuth2Session(client_id=self.client_id,
                            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
                            )

        authorization_url, _ = oauth.authorization_url(authorization_base_url, username=self.username)

        print('Please go here and authorize,', authorization_url)
        oauth_pin = input('Paste the Code returned here: ')

        oauth.fetch_token(token_url, client_secret=self.client_secret, code=oauth_pin)
        
        oauth_token = oauth.token['access_token']
        oauth_refresh = oauth.token['refresh_token']
        oauth_expires_at = oauth.token["created_at"] + oauth.token["expires_in"]

        self.store(
            {
                'trakt_oauth_token': str(oauth_token),
                'trakt_oauth_refresh': str(oauth_refresh),
                'trakt_oauth_expires_at': str(oauth_expires_at)
            }
        )
    
    def store(self, data):
        for key, value in data.items():
            set_key(dotenv_path='.env',
                    key_to_set=key,
                    value_to_set=value)
    
    def token_expired(self):
        current = datetime.now(tz=timezone.utc)
        expires_at = datetime.fromtimestamp(int(self.oauth_expires_at), tz=timezone.utc)

        if expires_at - current > timedelta(days=2):
            return True
        else:
            return False

    def refresh_token(self):
        url = "https://api-v2launch.trakt.tv/oauth/token"

        post_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.oauth_refresh,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'refresh_token'
            }

        response = self.session.post(url, json=post_data, headers=self.headers)

        if response.status_code == 200:
            data = response.json()

            oauth_token = data.get("access_token")
            oauth_refresh = data.get("refresh_token")
            oauth_expires_at = data.get("created_at") + data.get("expires_in")

            self.store(
                {
                'trakt_oauth_token': str(oauth_token),
                'trakt_oauth_refresh': str(oauth_refresh),
                'trakt_oauth_expires_at': str(oauth_expires_at)
                }
            )
        

    def is_user_authenticated(self):
    
        if (not self.oauth_token or not self.oauth_expires_at):
            return False
        
        if self.token_expired():
            self.refresh_token()
        
        return True
    
    def _handle_request(self, method, url):
        print(url)
        self.headers['trakt-api-key'] = self.client_id
        self.headers['Authorization'] = 'Bearer {0}'.format(self.oauth_refresh)

        response = self.session.request(method, url, headers=self.headers, params=None)

        if response.status_code == 200:
            try:
                json_data = json.loads(response.content.decode('UTF-8', 'ignore'))
            except JSONDecodeError as e:
                raise BadResponseException(response, f"Unable to parse JSON: {e}")
        
        return json_data
        

load_dotenv()

BASE_URL = 'https://api-v2launch.trakt.tv/'

CORE = Core(
    client_id=environ['trakt_client_id'],
    client_secret=environ['trakt_client_secret'],
    username=environ['username']
)

CORE.authenticate()
CORE._handle_request('get', 'https://api-v2launch.trakt.tv/users/Ahmedazim7804/history/movies')