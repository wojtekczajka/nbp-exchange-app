from sqlalchemy.orm import Session
from sqlalchemy import extract, func, asc, desc
from datetime import datetime

from database import CurrencyAB, CurrencyC

def get_distinct_currencies(db: Session, table: str):
    if table in ['A', 'B']:
        return db.query(CurrencyAB.currency).filter(CurrencyAB.table == table).distinct().all()
    elif table == 'C':
        return db.query(CurrencyC.currency).distinct().all()

def get_date_range(db: Session, table: str, currency: str = 'USD'):
    if table in ['A', 'B']:
        return db.query(func.min(CurrencyAB.date), func.max(CurrencyAB.date))\
                 .filter(CurrencyAB.table == table)\
                 .filter(CurrencyAB.currency == currency)\
                 .first()
    elif table == 'C':
        return db.query(func.min(CurrencyC.date), func.max(CurrencyC.date))\
                 .filter(CurrencyC.currency == currency)\
                 .first()

def get_available_dates(db: Session, table: str, year: int, month: int, currency: str):
    if table in ['A', 'B']:
        return db.query(CurrencyAB.date).filter(
            CurrencyAB.table == table,
            CurrencyAB.currency == currency,
            extract('year', CurrencyAB.date) == year,
            extract('month', CurrencyAB.date) == month
        ).distinct().all()
    elif table == 'C':
        return db.query(CurrencyC.date).filter(
            CurrencyC.table == table,
            CurrencyC.currency == currency,
            extract('year', CurrencyC.date) == year,
            extract('month', CurrencyC.date) == month
        ).distinct().all()

def get_currency_rate(db: Session, table: str, currency: str, date_obj: datetime.date):
    if table in ['A', 'B']:
        return db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date == date_obj).first()
    elif table == 'C':
        return db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date == date_obj).first()

def get_nearest_currency_rate(db: Session, table: str, currency: str, date_obj: datetime.date):
    if table in ['A', 'B']:
        result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date <= date_obj).order_by(desc(CurrencyAB.date)).first()
        if not result:
            result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date >= date_obj).order_by(asc(CurrencyAB.date)).first()
    elif table == 'C':
        result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date <= date_obj).order_by(desc(CurrencyC.date)).first()
        if not result:
            result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date >= date_obj).order_by(asc(CurrencyC.date)).first()
    return result

def get_plot_data(db: Session, table: str, currency: str, start_date_obj: datetime.date, end_date_obj: datetime.date):
    if table in ['A', 'B']:
        return db.query(CurrencyAB.date, CurrencyAB.mid).filter(
            CurrencyAB.table == table,
            CurrencyAB.currency == currency,
            CurrencyAB.date >= start_date_obj,
            CurrencyAB.date <= end_date_obj
        ).order_by(asc(CurrencyAB.date)).all()
    elif table == 'C':
        return db.query(CurrencyC.date, CurrencyC.bid, CurrencyC.ask).filter(
            CurrencyC.table == table,
            CurrencyC.currency == currency,
            CurrencyC.date >= start_date_obj,
            CurrencyC.date <= end_date_obj
        ).order_by(asc(CurrencyC.date)).all()
