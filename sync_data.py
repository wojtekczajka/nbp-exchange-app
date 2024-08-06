import requests
from database import SessionLocal, CurrencyAB, CurrencyC
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from crud import get_date_range, get_distinct_currencies


def sync_currency_data():
    db = SessionLocal()

    tables = ['A', 'B', 'C']

    for table in tables:
        currencies = get_distinct_currencies(db, table)
        for currency in currencies:
            currency_code = currency[0]
            min_date, max_date = get_date_range(db, table, currency_code)
            current_date = max_date + \
                timedelta(days=1) if max_date else datetime(2002, 1, 1).date()

            end_date = datetime.now().date()
            delta = timedelta(days=30)

            while current_date < end_date:
                next_date = current_date + delta
                if next_date > end_date:
                    next_date = end_date

                url = f"http://api.nbp.pl/api/exchangerates/rates/{table.lower()}/{currency_code}/{current_date.strftime('%Y-%m-%d')}/{next_date.strftime('%Y-%m-%d')}/?format=json"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    for entry in data['rates']:
                        effective_date = entry['effectiveDate']
                        effective_date = datetime.strptime(
                            effective_date, "%Y-%m-%d").date()

                        if table in ['A', 'B']:
                            currency_entry = CurrencyAB(
                                table=table,
                                currency=currency_code,
                                date=effective_date,
                                mid=entry.get("mid")
                            )
                            db.merge(currency_entry)
                        elif table == 'C':
                            currency_entry = CurrencyC(
                                table=table,
                                currency=currency_code,
                                date=effective_date,
                                bid=entry.get("bid"),
                                ask=entry.get("ask")
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
