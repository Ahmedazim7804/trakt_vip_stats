from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData

engine = create_engine('sqlite:///college.db', echo = True)
meta = MetaData()

movies = Table(
    'Movies', meta,
    Column('id', String, primary_key=True),
    Column('title', String),
    Column('cast', list)
)