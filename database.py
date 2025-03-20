from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Create a new database
DATABASE_URL = "sqlite:///fitzone.db"
engine = create_engine(DATABASE_URL, echo=False)

# Create a session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
