import trakt
from os import environ, path, makedirs
import platform
import trakt.core
from trakt.core import CORE
import get_movie_history
import get_tv_history
import get_episode_history
import get_ratings_data
import get_other_data
from multiprocessing import Process, Pipe
from sqlmodel import SQLModel, create_engine
from loguru import logger


def check_config():
    if "XDG_DATA_HOME" in environ:
        data_dir = environ["XDG_DATA_HOME"]
    elif platform.system() == "Windows":
        data_dir = path.expanduser("~/.traktexport")
    else:
        data_dir = path.expanduser("~/.local/share")
    makedirs(data_dir, exist_ok=True)

    default_cfg_path = path.join(data_dir, "traktexport.json")
    traktexport_cfg = environ.get("TRAKTEXPORT_CFG", default_cfg_path)
    trakt.core.CONFIG_PATH = traktexport_cfg

    if not path.exists(default_cfg_path):
        return False

    return True


def authenticate(username: str, client_id: str, client_secret: str):
    trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH

    if check_config():
        CORE._bootstrap()
    else:
        trakt.init(
            username, client_id=client_id, client_secret=client_secret, store=True
        )


def Multiprocess(fxn, add_to_db_fxn, progressBar):
    pipe, conn = Pipe()
    pbar_pipe, pbar_conn = Pipe()

    process1 = Process(target=fxn, args=(pipe, pbar_pipe))
    process2 = Process(target=add_to_db_fxn, args=(conn,))
    process3 = Process(target=progressBar, args=(pbar_conn,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()


if __name__ == "__main__":
    import time

    aa = time.time()
    username = "***REMOVED***"
    client_id = "***REMOVED***"
    client_secret = "***REMOVED***"
    authenticate(username, client_id=client_id, client_secret=client_secret)

    engine = create_engine("sqlite:///database.db")
    SQLModel.metadata.create_all(engine)

    '''
    To only disable info logs, use these lines.
        # logger.disable("get_movie_history")
        # logger.disable("get_episode_history")
        # logger.disable("get_tv_history")
    '''

    # Disable all logs.
    logger.remove()

    Multiprocess(
        fxn=get_movie_history.process_get_history,
        add_to_db_fxn=get_movie_history.process_add_data,
        progressBar=get_movie_history.progress_bar,
    )

    Multiprocess(
        fxn=get_tv_history.process_get_history,
        add_to_db_fxn=get_tv_history.process_add_data,
        progressBar=get_tv_history.progress_bar,
    )

    Multiprocess(
        fxn=get_episode_history.process_get_history,
        add_to_db_fxn=get_episode_history.process_add_data,
        progressBar=get_episode_history.progress_bar,
    )

    Multiprocess(
        fxn=get_ratings_data.process_get_ratings,
        add_to_db_fxn=get_ratings_data.process_add_data,
        progressBar=get_ratings_data.progress_bar,
    )

    Multiprocess(
        fxn=get_other_data.top_shows_and_movies_lists,
        add_to_db_fxn=get_other_data.placeholder_add_data,  # Placeholder function
        progressBar=get_other_data.progress_bar,
    )

    print(time.time() - aa)
    