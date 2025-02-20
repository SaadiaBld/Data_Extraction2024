from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Field, Session, create_engine, SQLModel
from sqlalchemy.sql import text
from sqlalchemy.exc import ProgrammingError
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Table, MetaData
from sqlmodel import select
import traceback, logging, uuid
from datetime import datetime


app = FastAPI()

# URL de la base de données SQL Server sur Azure
DATABASE_URL = "mssql+pyodbc://jvcb:cbjv592023!@adventureworks-server-hdf.database.windows.net:1433/adventureworks?driver=ODBC+Driver+18+for+SQL+Server"

# Définir la configuration des logs
logging.basicConfig(level=logging.DEBUG)

# Modèle SQLAlchemy pour la table 'product'
class Product(SQLModel, table=True):
    __tablename__ = "Product"
    __table_args__ = {"schema": "Production"}

    ProductID: int = Field(default=None, primary_key=True)
    Name: str

# Modèle Pydantic pour les produits
class ProductResponse(BaseModel):
    ProductID: int = None # Seulement la colonne 'ProductID'
    Name: str  # Seulement la colonne 'Name'

    class Config:
        orm_mode = True  # Permet la conversion des résultats de la base de données en réponse JSON

# Créer une instance de l'engine
engine = create_engine(DATABASE_URL)

#modele pour creer produit

class ProductCreate(BaseModel):
    Name: str  # Colonne 'Name' de type nvarchar (non nullable)
    ProductNumber: str  # Colonne 'ProductNumber' de type nvarchar (non nullable)
    MakeFlag: bool  # Colonne 'MakeFlag' de type bit (non nullable)
    FinishedGoodsFlag: bool  # Colonne 'FinishedGoodsFlag' de type bit (non nullable)
    SafetyStockLevel: int  # Colonne 'SafetyStockLevel' de type smallint (non nullable)
    ReorderPoint: int  # Colonne 'ReorderPoint' de type smallint (non nullable)
    StandardCost: float  # Colonne 'StandardCost' de type money (non nullable)
    ListPrice: float  # Colonne 'ListPrice' de type money (non nullable)
    DaysToManufacture: int  # Colonne 'DaysToManufacture' de type int (non nullable)
    SellStartDate: datetime  # Colonne 'SellStartDate' de type datetime (non nullable)
    rowguid: Optional[str] = None  # Colonne 'rowguid' de type uniqueidentifier (nullable)
    ModifiedDate: datetime = datetime.now()  # Colonne 'ModifiedDate' de type datetime (non nullable)

    class Config:
        orm_mode = True

# Fonction de session pour interagir avec la base de données
def get_session():
    logging.debug("Creating new session")
    with Session(engine) as session:
        yield session

#### route pour avoir nom des produits
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

#### route pour ajouter un produit
# @app.post("/products", response_model=ProductResponse, status_code=201)
# def create_product(product_data: ProductResponse, session: Session = Depends(get_session)):
#     """
#     Crée un nouveau produit dans la base de données.
#     Retourne un JSON contenant les informations du produit créé.
#     """
#     try:
#         # Crée une nouvelle instance du modèle Product à partir des données entrantes
#         new_product = Product(Name=product_data.Name)

#         # Ajoute le produit dans la session
#         session.add(new_product)
#         session.commit()  # Confirme les changements dans la base de données
#         session.refresh(new_product)  # Recharge l'objet pour obtenir l'ID généré

#         logging.debug(f"Product created: {new_product}")
#         return new_product  # Retourne les données du produit créé
#     except Exception as e:
#         logging.error(f"Error creating product: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

######################""
# @app.post("/products", response_model=ProductResponse, status_code=201)
# def create_product(product_data: ProductResponse, session: Session = Depends(get_session)):
#     """
#     Crée un nouveau produit dans la base de données avec ProductNumber.
#     :param product_data: Données JSON du produit à créer.
#     :param session: Session de base de données injectée via Depends.
#     :return: JSON contenant les informations du produit créé.
#     """
#     try:
#         # Générer un ProductNumber unique si ce n'est pas fourni
#         if not product_data.ProductNumber:
#             product_data.ProductNumber = str(uuid.uuid4())  # Générer un UUID comme ProductNumber
        
#         # Créer une nouvelle instance du modèle Product à partir des données entrantes
#         new_product = Product(Name=product_data.Name, ProductNumber=product_data.ProductNumber)

#         # Ajouter le produit dans la session
#         session.add(new_product)
#         session.commit()  # Confirmer les changements dans la base de données
#         session.refresh(new_product)  # Recharger l'objet pour obtenir l'ID généré

#         logging.debug(f"Product created: {new_product}")
#         return new_product  # Retourner les données du produit créé
#     except Exception as e:
#         logging.error(f"Error creating product: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

###############
# Route pour créer un produit
# @app.post("/products", response_model=ProductResponse)
# def create_product(product: ProductCreate, session: Session = Depends(get_session)):
#     try:
#         new_product = Product(
#             Name=product.Name,
#             ProductNumber=product.ProductNumber,
#             MakeFlag=product.MakeFlag,
#             FinishedGoodsFlag=product.FinishedGoodsFlag,
#             SafetyStockLevel=product.SafetyStockLevel,
#             ReorderPoint=product.ReorderPoint,
#             StandardCost=product.StandardCost,
#             ListPrice=product.ListPrice,
#             DaysToManufacture=product.DaysToManufacture,
#             SellStartDate=product.SellStartDate,
#             rowguid=product.rowguid,
#             ModifiedDate=product.ModifiedDate
#         )
#         session.add(new_product)
#         session.commit()
#         session.refresh(new_product)
#         return new_product
#     except Exception as e:
#         logging.error(f"Error creating product: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


###
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    try:
        # Générer un UUID pour 'rowguid'
        rowguid_value = str(uuid.uuid4())  # Génère un UUID valide
        
        # Si SafetyStockLevel est 0 ou moins, changer la valeur (par exemple 1)
        safety_stock = product.SafetyStockLevel if product.SafetyStockLevel > 0 else 1
        
        # Requête d'insertion avec des paramètres nommés
        query = text("""
            INSERT INTO [Production].[Product] 
            ([Name], [ProductNumber], [MakeFlag], [FinishedGoodsFlag], [SafetyStockLevel], 
            [ReorderPoint], [StandardCost], [ListPrice], [DaysToManufacture], [SellStartDate], 
            [rowguid], [ModifiedDate])
            OUTPUT inserted.ProductID 
            VALUES (:Name, :ProductNumber, :MakeFlag, :FinishedGoodsFlag, :SafetyStockLevel, 
                    :ReorderPoint, :StandardCost, :ListPrice, :DaysToManufacture, :SellStartDate, 
                    :rowguid, :ModifiedDate)
        """)

        params = {
            "Name": product.Name, 
            "ProductNumber": product.ProductNumber,
            "MakeFlag": product.MakeFlag,
            "FinishedGoodsFlag": product.FinishedGoodsFlag,
            "SafetyStockLevel": safety_stock,
            "ReorderPoint": product.ReorderPoint,
            "StandardCost": product.StandardCost,
            "ListPrice": product.ListPrice,
            "DaysToManufacture": product.DaysToManufacture,
            "SellStartDate": product.SellStartDate,
            "rowguid": rowguid_value,
            "ModifiedDate": product.ModifiedDate}

        
        result = session.execute(query, params)
        product_id = result.scalar()  # Récupère l'ID du produit inséré
        
        # Renvoyer le produit créé avec son ID
        return {**product.dict(), "ProductID": product_id}

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
