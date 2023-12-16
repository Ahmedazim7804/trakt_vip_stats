from sqlmodel import Session, create_engine, select
from Models.crew_model import Crew
from Models.movies_model import Movie
from Models.shows_model import TV

engine = create_engine("sqlite:///database.db")


def most_watched_directors():
    directors = []

    with Session(engine) as session:
        count = 0

        for cast_data in session.exec(select(Crew.id, Crew.name, Crew.movies, Crew.shows, Crew.episode, Crew.image).where(Crew.dept == 'Directing').order_by((Crew.movies_count + Crew.shows_count).desc()).order_by(Crew.episode)):
            id, name, movies, shows, episode_count, image = cast_data
            
            movies = [session.exec(select(Movie.title).where(Movie.tmdb_id == id)).first() for id in movies]
            shows = [session.exec(select(TV.title).where(TV.tmdb_id == id)).first() for id in shows]

            directors.append({
                'name': name,
                'movies': movies,
                'shows': shows,
                'episode': episode_count,
                'image': image
            })
    
            count += 1

            if count >= 100:
                break

    return directors

def most_watched_writers():
    writers = []

    with Session(engine) as session:
        count = 0

        for cast_data in session.exec(select(Crew.id, Crew.name, Crew.movies, Crew.shows, Crew.episode, Crew.image).where(Crew.dept == "Writing").order_by((Crew.movies_count + Crew.shows_count).desc()).order_by(Crew.episode)):
            id, name, movies, shows, episode_count, image = cast_data
            
            movies = [session.exec(select(Movie.title).where(Movie.tmdb_id == id)).first() for id in movies]
            shows = [session.exec(select(TV.title).where(TV.tmdb_id == id)).first() for id in shows]

            writers.append({
                'name': name,
                'movies': movies,
                'shows': shows,
                'episode': episode_count,
                'image': image
            })
    
            count += 1

            if count >= 100:
                break

    return writers