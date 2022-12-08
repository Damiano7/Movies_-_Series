from fastapi import FastAPI
from sqlalchemy import select, func, text
from config.db import conn, meta
from models.user import movieTVShows, genres, casts

app = FastAPI(
    title= "Movies & TV Shows",
    description= "Netflix, Hulu, Amazon and Disney",
    version="1.0.2",
    openapi_tags=[{
        "name": "Consultas",
        "description": "Movies & TV Shows"
    }]
)

# Nos pasan por parametro las variables: year, platform, [min or season]
@app.get('/get_max_duration/', tags=["Consultas"])
def get_max_duration(year: int, platform: str, type:str):
    platform = platform.lower()
    type = type.lower()
    tipo = type
    if (type == "min"): type = "Movie"
    else: type = "Tv Show"
    s = select(movieTVShows.c.title, func.concat(movieTVShows.c.duration, ' ', tipo).label("duracion")).where(movieTVShows.c.release_year == year).where(movieTVShows.c.platform == platform).where(movieTVShows.c.type == type).order_by(movieTVShows.c.duration.desc())
    return (conn.execute(s).first())

# Nos pasan por parametro la variable: platform
@app.get('/get_count_plataform/', tags=["Consultas"])
def get_count_plataform(platform: str):
    platform = platform.lower()
    s = select(movieTVShows.c.type, func.count(movieTVShows.c.type).label("cantidad")).where(movieTVShows.c.platform == platform).group_by(movieTVShows.c.type)
    return (conn.execute(s).fetchall())

# Nos pasan por parametro la variable: genre
@app.get('/get_listedin/', tags=["Consultas"])
def get_listedin(genre: str):
    genre = genre.lower()
    s = select(movieTVShows.c.platform, func.count(movieTVShows.c.platform).label("cantidad")).join(genres, genres.c.idShow==movieTVShows.c.idShow).where(genres.c.listed_in == genre).group_by(movieTVShows.c.platform).order_by(func.count(movieTVShows.c.platform).desc())
    return (conn.execute(s).first())

# Nos pasan por parametro las variables: year, platform
@app.get('/get_actor/', tags=["Consultas"])
def get_actor(year: int, platform: str):
    platform = platform.lower()
    s = select(func.count(casts.c.cast).label("cantidad"), casts.c.cast).join(movieTVShows, casts.c.idShow==movieTVShows.c.idShow).where(movieTVShows.c.platform == platform).where(movieTVShows.c.release_year == year).where(casts.c.cast != "Sin Datos").group_by(casts.c.cast).order_by(func.count(casts.c.cast).desc())
    return (conn.execute(s).first())    