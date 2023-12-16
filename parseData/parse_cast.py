from sqlmodel import Session, create_engine, select
from Models.cast_model import Cast
from Models.movies_model import Movie
from Models.shows_model import TV

engine = create_engine("sqlite:///database.db")

def most_watched_actors():
    actors = []

    with Session(engine) as session:
        count = 0
        
        for cast_data in session.exec(select(Cast.id, Cast.name, Cast.movies, Cast.shows, Cast.episode, Cast.image).where(Cast.gender == 2).order_by((Cast.movies_count + Cast.shows_count).desc()).order_by(Cast.episode)):
            id, name, movies, shows, episode_count, image = cast_data

            movies = [session.exec(select(Movie.title).where(Movie.tmdb_id == id)).first() for id in movies]
            shows = [session.exec(select(TV.title).where(TV.tmdb_id == id)).first() for id in shows]

            actors.append({
                'name': name,
                'movies': movies,
                'shows': shows,
                'episode': episode_count,
                'image': image
            })

            count += 1

            if count >= 100:
                break

    return actors

def most_watched_actresses():
    actresses = []

    with Session(engine) as session:
        count = 0
        
        for cast_data in session.exec(select(Cast.id, Cast.name, Cast.movies, Cast.shows, Cast.episode, Cast.image).where(Cast.gender == 1).order_by((Cast.movies_count + Cast.shows_count).desc()).order_by(Cast.episode)):
            id, name, movies, shows, episode_count, image = cast_data

            movies = [session.exec(select(Movie.title).where(Movie.tmdb_id == id)).first() for id in movies]
            shows = [session.exec(select(TV.title).where(TV.tmdb_id == id)).first() for id in shows]

            actresses.append({
                'name': name,
                'movies': movies,
                'shows': shows,
                'episode': episode_count,
                'image': image
            })

            count += 1

            if count >= 100:
                break

    return actresses
