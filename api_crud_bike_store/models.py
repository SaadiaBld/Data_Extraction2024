# modèle SQLAlchemy pour la table Product

from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class Product(SQLModel, table=True):
    __tablename__ = "Product"
    __table_args__ = {"schema": "Production"}

    ProductID: int = Field(default=None, primary_key=True)
    Name: str
    ProductNumber: str
    MakeFlag: bool
    FinishedGoodsFlag: bool
    SafetyStockLevel: Optional[int] = None
    ReorderPoint: Optional[int] = None
    StandardCost: float
    ListPrice: float
    DaysToManufacture: Optional[int] = None
    SellStartDate: datetime
    rowguid: Optional[str] = None
    ModifiedDate: datetime
