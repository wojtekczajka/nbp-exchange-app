from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal
from crud import get_distinct_currencies, get_date_range, get_currency_rate, get_available_dates, get_plot_data

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    currencies_a = get_distinct_currencies(db, 'A')
    currencies_b = get_distinct_currencies(db, 'B')
    currencies_c = get_distinct_currencies(db, 'C')

    date_range_a = get_date_range(db, 'A')
    date_range_b = get_date_range(db, 'B')
    date_range_c = get_date_range(db, 'C')

    currencies_list_a = [{"code": currency, "name": currency} for currency, in currencies_a]
    currencies_list_b = [{"code": currency, "name": currency} for currency, in currencies_b]
    currencies_list_c = [{"code": currency, "name": currency} for currency, in currencies_c]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "currencies_a": currencies_list_a,
        "currencies_b": currencies_list_b,
        "currencies_c": currencies_list_c,
        "date_range_a": {"min": date_range_a[0], "max": date_range_a[1]},
        "date_range_b": {"min": date_range_b[0], "max": date_range_b[1]},
        "date_range_c": {"min": date_range_c[0], "max": date_range_c[1]}
    })

@app.get("/date-ranges/{table}", response_model=dict)
async def get_date_ranges(table: str, db: Session = Depends(get_db)):
    date_range = get_date_range(db, table)
    if date_range:
        return {"min": date_range[0], "max": date_range[1]}
    else:
        raise HTTPException(status_code=404, detail="Invalid table specified")

@app.get("/available-dates/{table}/{year}/{month}")
async def get_available_dates_endpoint(table: str, year: int, month: int, currency: str, db: Session = Depends(get_db)):
    dates = get_available_dates(db, table, year, month, currency)
    return [date[0] for date in dates]

@app.get("/check-currency")
async def check_currency(table: str, currency: str, date: str, db: Session = Depends(get_db)):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    result = get_currency_rate(db, table, currency, date_obj)
    if result:
        if table in ['A', 'B']:
            return {"date": str(result.date), "value": {"mid": result.mid}}
        elif table == 'C':
            return {"date": str(result.date), "value": {"bid": result.bid, "ask": result.ask}}
    else:
        raise HTTPException(status_code=404, detail="Not found")

@app.get("/check-currency-range")
async def check_currency_range(table: str, currency: str, start_date: str, end_date: str, db: Session = Depends(get_db)):
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    data = get_plot_data(db, table, currency, start_date_obj, end_date_obj)
    if table in ['A', 'B']:
        return [{"date": str(record[0]), "value": {"mid": record[1]}} for record in data]
    elif table == 'C':
        return [{"date": str(record[0]), "value": {"bid": record[1], "ask": record[2]}} for record in data]
