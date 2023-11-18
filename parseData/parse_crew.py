from sqlmodel import Session, create_engine, select
from Models.crew_model import Crew

engine = create_engine("sqlite:///database.db")

def most_watched_directors():
    directors = []

    with Session(engine) as session:
        for cast_data in session.exec(select(Crew.id, Crew.name, Crew.movies, Crew.shows, Crew.episode).where(Crew.dept == 'Directing').order_by((Crew.movies_count + Crew.shows_count).desc()).order_by(Crew.episode)):
            id, name, movies, shows, episode_count = cast_data
            directors.append({id: {
                'name': name,
                'movies': movies,
                'shows': shows,
                'episode': episode_count
            }})
    
    directors = directors[:100]

    return directors

def most_watched_writers():
    writers = []

    with Session(engine) as session:
        for cast_data in session.exec(select(Crew.id, Crew.name, Crew.movies, Crew.shows, Crew.episode).where(Crew.dept == "Writing").order_by((Crew.movies_count + Crew.shows_count).desc()).order_by(Crew.episode)):
            id, name, movies, shows, episode_count = cast_data
            writers.append({id: {
                'name': name,
                'movies': movies,
                'shows': shows,
                'episode': episode_count
            }})
    
    writers = writers[:100]

    return writers