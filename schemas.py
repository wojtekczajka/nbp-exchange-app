from pydantic import BaseModel
from datetime import date

class CurrencyBaseSchema(BaseModel):
    table: str
    currency: str
    date: date

class CurrencyABSchema(CurrencyBaseSchema):
    mid: float

    class Config:
        orm_mode = True

class CurrencyCSchema(CurrencyBaseSchema):
    bid: float
    ask: float

    class Config:
        orm_mode = True

class DateRangeSchema(BaseModel):
    min: date
    max: date
