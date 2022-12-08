from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+pymysql://root:Discoteca$7@host.docker.internal:3306/fasAPImovies")

meta = MetaData()

conn = engine.connect()