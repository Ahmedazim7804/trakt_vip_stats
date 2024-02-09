from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv, set_key, dotenv_values
from os import environ
import json
import requests
from datetime import datetime, timedelta, timezone

# Core class is used to authenticate to trakt and get data from trakt api
# More or less copied from pytrakt [1].
# [1]: https://github.com/moogar0880/PyTrakt/tree/master 


class Core():
    def __init__(self, client_id, client_secret, username):
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {'Content-Type': 'application/json', 'trakt-api-version': '2'}
        self.base_url = "https://api.trakt.tv/"
        self.session = requests.Session()

        self.load_config()

    def fix_config(self):
        config = dotenv_values(dotenv_path='.env')
        
        if ('trakt_oauth_token' not in config.keys() or
            'trakt_oauth_refresh' not in config.keys() or
            'trakt_oauth_expires_at' not in config.keys()):
            self.store(
            {
                'trakt_oauth_token': '',
                'trakt_oauth_refresh': '',
                'trakt_oauth_expires_at': ''
            }
        )
    
    def load_config(self):
        load_dotenv(dotenv_path='.env', override=True)

        try:
            self.oauth_token = environ['trakt_oauth_token']
            self.oauth_refresh = environ['trakt_oauth_refresh']
            self.oauth_expires_at = environ['trakt_oauth_expires_at']
            self.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        except KeyError:
            self.fix_config()
            self.load_config()
            

    def authenticate(self):

        if self.is_user_authenticated():
            return
        
        authorization_base_url = "https://api.trakt.tv/oauth/authorize"
        token_url = "https://api.trakt.tv/oauth/token"

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

        self.load_config()
    
    def store(self, data):
        for key, value in data.items():
            set_key(dotenv_path='.env',
                    key_to_set=key,
                    value_to_set=value)
    
    def token_expired(self):

        current = datetime.now(tz=timezone.utc)
        expires_at = datetime.fromtimestamp(int(self.oauth_expires_at), tz=timezone.utc)

        if expires_at - current > timedelta(days=2):
            return False
        else:
            return True

    def refresh_token(self):
        url = "https://api.trakt.tv/oauth/token"

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
        
        self.headers['trakt-api-key'] = self.client_id
        self.headers['Authorization'] = 'Bearer {0}'.format(self.oauth_token)

        response = self.session.request(method, url, headers=self.headers, params=None)

        if response.status_code == 200:
            try:
                json_data = json.loads(response.content.decode('UTF-8', 'ignore'))
            except JSONDecodeError as e:
                raise BadResponseException(response, f"Unable to parse JSON: {e}")
                json_data = {}

        return json_data
        

load_dotenv(override=True)

BASE_URL = 'https://api.trakt.tv/'

CORE = Core(
    client_id=environ['trakt_client_id'],
    client_secret=environ['trakt_client_secret'],
    username=environ['username']
)