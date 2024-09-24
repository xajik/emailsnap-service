from app.env import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import threading

class Database:
    _engine = None
    _SessionLocal = None
    _lock = threading.Lock()

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            with cls._lock:  # Thread-safe initialization
                if cls._engine is None:  # Double-check locking
                    cls._engine = create_engine(DATABASE_URL)
        return cls._engine

    @classmethod
    def get_session(cls):
        if cls._SessionLocal is None:
            cls._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.get_engine())
        return cls._SessionLocal

def get_db_session():
    db = Database.get_session()()
    try:
        return db
    except Exception as e:
        raise e
    finally:
        db.close()
