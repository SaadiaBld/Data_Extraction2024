from sqlmodel import SQLModel, Field
from datetime import date

class Product(SQLModel, table=True):
    ProductID: int = Field(primary_key=True)
    Name: str = Field(index=True)
    ProductNumber: int | None = Field(default=None, index=True)
    StandardCost: float | None = Field(default=None)
    ListPrice: float | None = Field(default=None)
    ProductSubcategoryID: int
    SellStartDate: date
