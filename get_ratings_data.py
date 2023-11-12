from urllib.parse import urljoin
from trakt.core import CORE, BASE_URL
from movies_model import Movie
from shows_model import TV, GetTvData, Network
from episode_model import Episode, EpisodeData
from sqlmodel import SQLModel, create_engine, Session, select
import main
from loguru import logger
from mpire import WorkerPool
from mpire.utils import make_single_arguments
import time
from multiprocessing import Process
import multiprocessing
from tqdm import tqdm

def process_get_ratings():
    for page in range(1,10):
        url = urljoin(BASE_URL, f"users/ahmedazim7804/ratings?limit=50&page={page}")
        data = CORE._handle_request(method='get', url=url)
        pass

if __name__ == '__main__':
    username = "***REMOVED***"
    client_id ='***REMOVED***'
    client_secret = '***REMOVED***'
    main.authenticate(username, client_id=client_id, client_secret=client_secret)


    process_get_ratings()