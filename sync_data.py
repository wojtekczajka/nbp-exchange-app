import requests
from database import SessionLocal, CurrencyAB, CurrencyC
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

def sync_currency_data():
    db = SessionLocal()

    start_date = datetime(2002, 1, 1)
    end_date = datetime.now()
    delta = timedelta(days=30)  # Fetch data in 30-day increments
    
    tables = ['A', 'B', 'C']
    
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + delta
        if next_date > end_date:
            next_date = end_date
            
        for table in tables:
            url = f"http://api.nbp.pl/api/exchangerates/tables/{table.lower()}/{current_date.strftime('%Y-%m-%d')}/{next_date.strftime('%Y-%m-%d')}/?format=json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    rates = entry['rates']
                    effective_date = entry['effectiveDate']
                    effective_date = datetime.strptime(effective_date, "%Y-%m-%d").date()
                    
                    if table in ['A', 'B']:
                        for rate in rates:
                            currency_entry = CurrencyAB(
                                table=table,
                                currency=rate["code"],
                                date=effective_date,
                                mid=rate.get("mid")
                            )
                            db.merge(currency_entry)
                    elif table == 'C':
                        for rate in rates:
                            currency_entry = CurrencyC(
                                table=table,
                                currency=rate["code"],
                                date=effective_date,
                                bid=rate.get("bid"),
                                ask=rate.get("ask")
                            )
                            db.merge(currency_entry)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
        
        current_date = next_date
    
    db.close()

if __name__ == "__main__":
    sync_currency_data()
