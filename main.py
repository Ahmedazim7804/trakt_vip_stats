from os import environ, path, makedirs
import platform
import sys
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
from save import save
from dotenv import load_dotenv
import argparse

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

def set_log_level(log_level):
    if log_level:
        logger.remove()
        logger.add(sys.stderr, level=log_level)
    else:
        logger.remove()

def run(args):
    set_log_level(args.log_level)

    if args.print_time:
        import time
        start_time = time.time()

    load_dotenv(override=True)

    CORE.authenticate()

    engine = create_engine("sqlite:///database.db")
    SQLModel.metadata.create_all(engine)

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
    
    if args.save:
        save()
        logger.info("Data saved to json file")

    if args.print_time:
        time_taken = time.time() - start_time
        print(time_taken)

def update(args):
    set_log_level(args.log_level)

    if args.data == 'movies':
        Multiprocess(
            fxn=get_movie_history.process_get_history,
            add_to_db_fxn=get_movie_history.process_add_data,
            progressBar=get_movie_history.progress_bar,
        )
    elif args.data == 'tv':
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
    elif args.data == 'ratings':
        Multiprocess(
            fxn=get_ratings_data.process_get_ratings,
            add_to_db_fxn=get_ratings_data.process_add_data,
            progressBar=get_ratings_data.progress_bar,
        )
    elif args.data == 'lists':
        Multiprocess(
            fxn=get_lists_data.top_shows_and_movies_lists,
            add_to_db_fxn=get_lists_data.placeholder_add_data,  # Placeholder function
            progressBar=get_lists_data.progress_bar,
        )
    
    if args.save:
        save()
        logger.info("Data saved to json file")


if __name__ == "__main__":
        
    parser = argparse.ArgumentParser(
        prog='TraktVipStats',
        description='Get the all-time-stats of trakt without trakt vip subscription',
    )

    subparsers = parser.add_subparsers(dest='command', help='Available Commands')

    run_subparser = subparsers.add_parser('run', help='save all necessary data to database.db')
    run_subparser.add_argument('--save', action='store_true')
    run_subparser.add_argument('--log-level', action='store', default=None, choices=['ERROR', 'INFO', 'DEBUG', 'WARNING'])
    run_subparser.add_argument('--print-time', action='store_true', default=False)
    run_subparser.set_defaults(func=run)

    update_subparser = subparsers.add_parser('update', help='update specific data in existing database.db from trakt')
    update_subparser.add_argument('data', type=str, default=None, choices=['movies', 'tv', 'ratings', 'lists'])
    update_subparser.add_argument('--save', action='store_true')
    update_subparser.add_argument('--log-level', action='store', default=None, choices=['ERROR', 'INFO', 'DEBUG', 'WARNING'])
    update_subparser.set_defaults(func=update)

    save_subparser = subparsers.add_parser('save', help='create trakt-all-time-stats.json from existing database.db file')
    save_subparser.set_defaults(func=lambda x: save())

    server_subparser = subparsers.add_parser('server', help='start api to serve all-time-stats data') 

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()