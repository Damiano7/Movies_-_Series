from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

casts = Table("cast", meta, 
            Column("idShow", Integer), 
            Column("cast", String(100)))

genres = Table("genre", meta, 
            Column("idShow", Integer), 
            Column("listed_in", String(30)))

movieTVShows = Table("movieTVShow", meta, 
            Column("idShow", Integer),
            Column("type", String(10)),
            Column("title", String(120)),
            Column("director", String(280)),
            Column("country", String(140)),
            Column("date_added", String(20)),
            Column("release_year", Integer),
            Column("rating", String(20)),
            Column("duration", Integer),
            Column("description", String(1900)),
            Column("platform", String(8)))

meta.create_all(engine)
