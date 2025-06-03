from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server-side default timestamp
from geoalchemy2 import Geometry # For PostGIS geometry types

# Import Base and engine from database.py
# The '.' indicates a relative import from the current package 'app'
from .database import Base, engine

class Store(Base):
    __tablename__ = "stores"

    id = Column("StoreID", Integer, primary_key=True, index=True, autoincrement=True)
    name = Column("Name", String(255), index=True, nullable=False)
    address = Column("Address", Text, nullable=False)
    latitude = Column("Latitude", Float, nullable=False)
    longitude = Column("Longitude", Float, nullable=False)
    chain_name = Column("ChainName", String(100))

    # PostGIS geometry column for geospatial queries
    # SRID 4326 is for WGS84 (latitude/longitude)
    geom = Column("geom", Geometry(geometry_type='POINT', srid=4326), nullable=True)

    promotions = relationship("Promotion", back_populates="store")

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column("PromotionID", Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column("StoreID", Integer, ForeignKey("stores.StoreID"), nullable=False)
    product_name = Column("ProductName", String(255), nullable=False)
    sale_price = Column("SalePrice", Numeric(10, 2), nullable=False)
    original_price = Column("OriginalPrice", Numeric(10, 2), nullable=True)
    valid_until = Column("ValidUntil", Date, nullable=True)
    description = Column("Description", Text, nullable=True)
    image_url = Column("ImageURL", Text, nullable=True)

    # Timestamp for when the promotion was last updated
    # server_default and onupdate are handled by the database
    last_updated = Column(
        "LastUpdated",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    store = relationship("Store", back_populates="promotions")

# Function to create tables in the database
# This can be called from main.py or a separate script
def create_db_tables():
    # Make sure all tables are created
    # In a production app, you'd likely use Alembic for migrations
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # This will create the tables in the database specified by SQLALCHEMY_DATABASE_URL
    # Make sure your database server is running and the database exists.
    print("Creating database tables...")
    create_db_tables()
    print("Database tables created (if they didn't exist).")
