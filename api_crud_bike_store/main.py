# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import text
from sqlmodel import Session, select, create_engine
from fastapi.responses import JSONResponse
from models import Product
from schemas import ProductResponse, ProductCreate
from typing import List
import logging

app = FastAPI()

# Database URL 
DATABASE_URL = "mssql+pyodbc://jvcb:cbjv592023!@adventureworks-server-hdf.database.windows.net:1433/adventureworks?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(DATABASE_URL)

# Définir la configuration des logs
logging.basicConfig(level=logging.DEBUG)

# Fonction de session pour interagir avec la base de données
def get_session():
    with Session(engine) as session:
        yield session

# Route pour obtenir la liste des produits
@app.get("/products", response_model=List[str])
def get_products(session: Session = Depends(get_session)):
    try:
        raw_query = text("SELECT Name FROM [Production].[Product]")
        results = session.exec(raw_query).all()
        return [row[0] for row in results]
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#### route pour avoir le nom des produits et l'id des produits
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product_details(product_id: int, session: Session = Depends(get_session)):
    """
    Retourne les détails d'un produit spécifique à partir de son product_id: ID du produit à rechercher.
    La réponse est stockée dans un objet JSON avec les détails du produit ou une erreur 404. {
    """
    try:
        # Recherche du produit par ID
        product = session.get(Product, product_id)
        if product is None:
            logging.warning(f"Product with ID {product_id} not found.")
            raise HTTPException(status_code=404, detail="Product not found in database")

        logging.debug(f"Product found: {product}")
        return product  # Automatiquement converti en JSON grâce à response_model
    except Exception as e:
        logging.error(f"Error fetching product details: {e}")
        raise HTTPException(status_code=404, detail="Product not found in database")


# Route pour créer un produit
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    try:
        new_product = Product(
            Name=product.Name,
            ProductNumber=product.ProductNumber,
            MakeFlag=product.MakeFlag,
            FinishedGoodsFlag=product.FinishedGoodsFlag,
            SafetyStockLevel=product.SafetyStockLevel,
            ReorderPoint=product.ReorderPoint,
            StandardCost=product.StandardCost,
            ListPrice=product.ListPrice,
            DaysToManufacture=product.DaysToManufacture,
            SellStartDate=product.SellStartDate,
            rowguid=product.rowguid,
            ModifiedDate=product.ModifiedDate
        )
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product
    except Exception as e:
        logging.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    # Cette fonction attrape toutes les exceptions non gérées
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "details": str(exc),
            "trace": traceback.format_exc()
        })

@app.exception_handler(ProgrammingError)
async def db_exception_handler(request: Request, exc: ProgrammingError):
    return JSONResponse(
        status_code=400,  # Ou un autre code pertinent pour l'erreur SQL
        content={
            "message": "Database error",
            "details": str(exc),
            "trace": traceback.format_exc()
        }
    ) 
