from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database URL in a production environment
# For local development, this might point to a local PostgreSQL instance
# Example: SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host:port/database"
SQLALCHEMY_DATABASE_URL = "postgresql://swiss_grocery_user:swiss_grocery_password@localhost:5432/swiss_grocery_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session in FastAPI path operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
