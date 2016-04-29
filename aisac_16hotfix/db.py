from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, String, Date, Time, Integer


def generate_engine(db_connect_string):
    return create_engine(db_connect_string)


def generate_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def generate_table_announce2GISAC(Base):
    return Base.classes.announce2GISAC


def generate_automap_base_with_metadata(engine):
    metadata = MetaData()
    metadata.reflect(engine, only=['announce2GISAC'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    return Base, metadata


def generate_automap_base(engine):
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    return Base


def generate_declarative_base(engine):
    Base = declarative_base()

    class announce2GISAC(Base):
        __tablename__ = 'announce2GISAC'
        publishID = Column(String(25), nullable=False, primary_key=True)
        acceptId = Column(String(25), nullable=False)
        date = Column(Date, nullable=False)
        time = Column(Time, nullable=False)
        type = Column(Integer, nullable=False)
        typeId = Column(Integer, nullable=False)
        toUnitId = Column(Integer, nullable=False)
        responseNumber = Column(String(4), nullable=False)
        responseID = Column(String(25), nullable=False)

        def __repr__(self):
            return '<announce2GISAC(publishID=\'%s\'>' % self.publishID
