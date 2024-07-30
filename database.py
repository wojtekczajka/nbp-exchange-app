from sqlalchemy import create_engine, Column, String, Float, Date, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./currencies.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CurrencyBase(Base):
    __abstract__ = True
    table = Column(String, primary_key=True)
    currency = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)

class CurrencyAB(CurrencyBase):
    __tablename__ = "currencies_ab"
    mid = Column(Float, nullable=True)

class CurrencyC(CurrencyBase):
    __tablename__ = "currencies_c"
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)