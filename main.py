import trakt
from os import environ, path, makedirs
import platform
from trakt_engine import CORE
import get_data.get_movie_history as get_movie_history
import get_data.get_tv_history as get_tv_history
import get_data.get_episode_history as get_episode_history
import get_data.get_ratings_data as get_ratings_data
import get_data.get_lists_data as get_lists_data
from multiprocessing import Process, Pipe
from sqlmodel import SQLModel, create_engine
from loguru import logger
from parseData import parse_other_data
from parseData import parse_tv_data
from dotenv import load_dotenv

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
    start_time = time.time()

    load_dotenv()

    CORE.authenticate()

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
        fxn=get_lists_data.top_shows_and_movies_lists,
        add_to_db_fxn=get_lists_data.placeholder_add_data,  # Placeholder function
        progressBar=get_lists_data.progress_bar,
    )
    
    time_taken = time.time() - start_time
    print(time_taken)
    