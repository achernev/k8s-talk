from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# noinspection PyPackageRequirements
from scrooge.models import Base

engine = create_engine(current_app.config['SQL_URI'], echo=True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = session.query_property()
