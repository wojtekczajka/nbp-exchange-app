from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, CurrencyAB, CurrencyC
from datetime import datetime

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
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/check-currency", response_class=HTMLResponse)
async def check_currency(request: Request, table: str, currency: str, date: str, db: Session = Depends(get_db)):
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    if table in ['A', 'B']:
        result = db.query(CurrencyAB).filter(CurrencyAB.table == table, CurrencyAB.currency == currency, CurrencyAB.date == date_obj).first()
        if result:
            rate_info = f"Kurs środkowy: {result.mid}"
        else:
            raise HTTPException(status_code=404, detail="Brak danych dla podanej waluty lub daty.")
    elif table == 'C':
        result = db.query(CurrencyC).filter(CurrencyC.table == table, CurrencyC.currency == currency, CurrencyC.date == date_obj).first()
        if result:
            rate_info = f"Kurs kupna: {result.bid}, Kurs sprzedaży: {result.ask}"
        else:
            raise HTTPException(status_code=404, detail="Brak danych dla podanej waluty lub daty.")
    
    return templates.TemplateResponse("currency_rate.html", {"request": request, "table": table, "currency": currency, "date": date, "rate_info": rate_info})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
