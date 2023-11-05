from sqlmodel import SQLModel, Field, Column, JSON
from typing import List, Optional
from tmdbv3api import TMDb
import tmdbv3api
from operator import itemgetter
from tmdbv3api.exceptions import TMDbException
from loguru import logger
from movies_model import Cast, Crew

tmdb = TMDb()
tmdb.api_key = "***REMOVED***"
trakt_CLIENT_ID = "***REMOVED***"
TMDbEpisode = tmdbv3api.Episode()


class Episode(SQLModel, table=True, arbitrary_types_allowed=True):
    tmdb_id : str = Field(primary_key=True)
    episode_title : str
    show_title : str
    season : int
    episode : int
    plays : int = Field(default=1)
    rating : Optional[int] = Field(default=0)
    tmdb_show_id : int
    watched_at : List[str] = Field(sa_column=Column(JSON)) 
    runtime : int
    cast : List[int] = Field(sa_column=Column(JSON))
    crew : List[int] = Field(sa_column=Column(JSON))

class GetEpisode:
    
    @staticmethod
    def format(season, episode):
        return f"S{str(season).zfill(2)}E{str(season).zfill(2)}"

    @staticmethod
    def runtime(tmdb_show_id, season, episode):
        runtime = 0

        try:
            runtime = TMDbEpisode.details(tmdb_show_id, season, episode)['runtime']
        except TMDbException:
            logger.warning(f"TMDb Show Id : '{tmdb_show_id}', {GetEpisode.format(season, episode)} failed to get runtime")

        if not runtime:
            logger.debug(f"TMDb Show Id : '{tmdb_show_id}', {GetEpisode.format(season, episode)} runtime is 0")
        
        return runtime

    
    @staticmethod
    def cast(tmdb_show_id, season, episode):
        cast_list = []
        try:
            item_cast = TMDbEpisode.credits(tmdb_show_id, season, episode)['cast']

            for actor in item_cast:
                name, id, gender, image = itemgetter('name', 'id', 'gender', 'profile_path')(actor)
                if (gender and image):
                    cast = Cast(
                        id=id,
                        name=name,
                        gender=gender,
                        image=image,
                    )
                    cast_list.append(cast)
        except TMDbException:
            logger.warning(f"TMDb Movie Id : '{tmdb_show_id}' {GetEpisode.format(season, episode)} failed to get Cast")

        return cast_list

    @staticmethod
    def crew(tmdb_show_id, season, episode):
        directors = []
        writers = []
        try:
            all_crew = TMDbEpisode.credits(tmdb_show_id, season, episode)['crew']

            for person in all_crew:
                id, name, dept, job, image = itemgetter('id', 'name', 'department', 'job', 'profile_path')(person)

                if person['job'] == 'Director':
                    directors.append(
                        Crew(id=id, name=name, dept=dept, job=job, image=image)
                    )
            
                if person['department'] == 'Writing':
                    writers.append(
                        Crew(id=id, name=name, dept=dept, job=job, image=image)
                    )

        except (TMDbException, KeyError):
            logger.warning(f"TMDb Movie Id : '{tmdb_show_id}' {GetEpisode.format(season, episode)} failed to get Crew")

        if not directors:
            logger.debug(f"TMDb Movie Id : '{tmdb_show_id}' {GetEpisode.format(season, episode)} Directors List is Empty")
        if not writers:
            logger.debug(f"TMDb Movie Id : '{tmdb_show_id}' {GetEpisode.format(season, episode)} Writers List is Empty")
        
        return [*directors, *writers]

#print(GetEpisode.crew('70523', 2, 1))