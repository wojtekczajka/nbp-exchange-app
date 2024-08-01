from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func, extract, asc, desc
from database import SessionLocal, CurrencyAB, CurrencyC
from schemas import CurrencyABSchema, CurrencyCSchema, DateRangeSchema
from datetime import datetime, timedelta

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    pass  # Database connection setup is handled by SQLAlchemy

@app.on_event("shutdown")
async def shutdown():
    pass  # Database connection teardown is handled by SQLAlchemy

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    currencies_a = db.query(distinct(CurrencyAB.currency)).filter(CurrencyAB.table == 'A').all()
    currencies_b = db.query(distinct(CurrencyAB.currency)).filter(CurrencyAB.table == 'B').all()
    currencies_c = db.query(distinct(CurrencyC.currency)).all()

    date_range_a = db.query(func.min(CurrencyAB.date), func.max(CurrencyAB.date)).filter(CurrencyAB.table == 'A').first()
    date_range_b = db.query(func.min(CurrencyAB.date), func.max(CurrencyAB.date)).filter(CurrencyAB.table == 'B').first()
    date_range_c = db.query(func.min(CurrencyC.date), func.max(CurrencyC.date)).first()

    currencies_list_a = [{"code": currency, "name": currency} for currency, in currencies_a]
    currencies_list_b = [{"code": currency, "name": currency} for currency, in currencies_b]
    currencies_list_c = [{"code": currency, "name": currency} for currency, in currencies_c]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "currencies_a": currencies_list_a,
        "currencies_b": currencies_list_b,
        "currencies_c": currencies_list_c,
        "date_range_a": DateRangeSchema(min=date_range_a[0], max=date_range_a[1]),
        "date_range_b": DateRangeSchema(min=date_range_b[0], max=date_range_b[1]),
        "date_range_c": DateRangeSchema(min=date_range_c[0], max=date_range_c[1])
    })

@app.get("/check-currency", response_class=HTMLResponse)
async def check_currency(request: Request, table: str, currency: str, date: str, db: Session = Depends(get_db)):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    if table in ['A', 'B']:
        result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date == date_obj).first()
        if not result:
            # If no exact match, find nearest date
            result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date <= date_obj).order_by(desc(CurrencyAB.date)).first()
            if not result:
                result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date >= date_obj).order_by(asc(CurrencyAB.date)).first()
        if result:
            rate_info = f"Kurs środkowy: {result.mid}"
        else:
            raise HTTPException(status_code=404, detail="Brak danych dla podanej waluty lub daty.")
    elif table == 'C':
        result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date == date_obj).first()
        if not result:
            # If no exact match, find nearest date
            result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date <= date_obj).order_by(desc(CurrencyC.date)).first()
            if not result:
                result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date >= date_obj).order_by(asc(CurrencyC.date)).first()
        if result:
            rate_info = f"Kurs kupna: {result.bid}, Kurs sprzedaży: {result.ask}"
        else:
            raise HTTPException(status_code=404, detail="Brak danych dla podanej waluty lub daty.")
    
    return templates.TemplateResponse("currency_rate.html", {"request": request, "table": table, "currency": currency, "date": date, "rate_info": rate_info})

@app.get("/date-ranges/{table}", response_model=DateRangeSchema)
async def get_date_ranges(table: str, db: Session = Depends(get_db)):
    if table == 'A':
        date_range = db.query(func.min(CurrencyAB.date), func.max(CurrencyAB.date)).filter(CurrencyAB.table == 'A').first()
    elif table == 'B':
        date_range = db.query(func.min(CurrencyAB.date), func.max(CurrencyAB.date)).filter(CurrencyAB.table == 'B').first()
    elif table == 'C':
        date_range = db.query(func.min(CurrencyC.date), func.max(CurrencyC.date)).first()
    else:
        raise HTTPException(status_code=404, detail="Invalid table specified")
    
    return DateRangeSchema(min=date_range[0], max=date_range[1])

@app.get("/available-dates/{table}/{year}/{month}")
async def get_available_dates(table: str, year: int, month: int, currency: str, db: Session = Depends(get_db)):
    if table in ['A', 'B']:
        dates = db.query(CurrencyAB.date).filter(
            CurrencyAB.table == table,
            CurrencyAB.currency == currency,
            extract('year', CurrencyAB.date) == year,
            extract('month', CurrencyAB.date) == month
        ).distinct().all()
    elif table == 'C':
        dates = db.query(CurrencyC.date).filter(
            CurrencyC.table == table,
            CurrencyC.currency == currency,
            extract('year', CurrencyC.date) == year,
            extract('month', CurrencyC.date) == month
        ).distinct().all()
    else:
        raise HTTPException(status_code=404, detail="Invalid table specified")
    
    return [date[0] for date in dates]

@app.get("/plot-data/{table}/{currency}")
async def get_plot_data(table: str, currency: str, range: str = '1m', db: Session = Depends(get_db)):
    end_date = datetime.now().date()
    if range == '1m':
        start_date = end_date - timedelta(days=30)
    elif range == '3m':
        start_date = end_date - timedelta(days=90)
    elif range == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid date range specified")
    
    if table in ['A', 'B']:
        data = db.query(CurrencyAB.date, CurrencyAB.mid).filter(
            CurrencyAB.table == table,
            CurrencyAB.currency == currency,
            CurrencyAB.date >= start_date,
            CurrencyAB.date <= end_date
        ).order_by(asc(CurrencyAB.date)).all()
    elif table == 'C':
        data = db.query(CurrencyC.date, CurrencyC.bid, CurrencyC.ask).filter(
            CurrencyC.table == table,
            CurrencyC.currency == currency,
            CurrencyC.date >= start_date,
            CurrencyC.date <= end_date
        ).order_by(asc(CurrencyC.date)).all()
    else:
        raise HTTPException(status_code=404, detail="Invalid table specified")
    
    if table in ['A', 'B']:
        return [{"date": str(record[0]), "value": {"mid": record[1]}} for record in data]
    elif table == 'C':
        return [{"date": str(record[0]), "value": {"bid": record[1], "ask": record[2]}} for record in data]

@app.get("/nearest-date/{table}/{currency}/{date}")
async def get_nearest_date(table: str, currency: str, date: str, db: Session = Depends(get_db)):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    if table in ['A', 'B']:
        result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date <= date_obj).order_by(desc(CurrencyAB.date)).first()
        if not result:
            result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date >= date_obj).order_by(asc(CurrencyAB.date)).first()
    elif table == 'C':
        result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date <= date_obj).order_by(desc(CurrencyC.date)).first()
        if not result:
            result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date >= date_obj).order_by(asc(CurrencyC.date)).first()
    else:
        raise HTTPException(status_code=404, detail="Invalid table specified")
    
    if result:
        return {"date": str(result.date), "value": {"mid": result.mid} if table in ['A', 'B'] else {"bid": result.bid, "ask": result.ask}}
    else:
        raise HTTPException(status_code=404, detail="No available date found")
