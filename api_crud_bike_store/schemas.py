# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductResponse(BaseModel):
    ProductID: int
    Name: str

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
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
    ModifiedDate: datetime = datetime.now()

    class Config:
        orm_mode = True
