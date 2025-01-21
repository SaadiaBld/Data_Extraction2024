from pydantic import BaseModel
from typing import List
from sqlmodel import Field, Session, create_engine, SQLModel
from sqlalchemy.sql import text
from sqlalchemy.exc import ProgrammingError
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Table, MetaData
from sqlmodel import select
import traceback, logging, uuid


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

@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product_data: ProductResponse, session: Session = Depends(get_session)):
    """
    Crée un nouveau produit dans la base de données avec ProductNumber.
    :param product_data: Données JSON du produit à créer.
    :param session: Session de base de données injectée via Depends.
    :return: JSON contenant les informations du produit créé.
    """
    try:
        # Générer un ProductNumber unique si ce n'est pas fourni
        if not product_data.ProductNumber:
            product_data.ProductNumber = str(uuid.uuid4())  # Générer un UUID comme ProductNumber
        
        # Créer une nouvelle instance du modèle Product à partir des données entrantes
        new_product = Product(Name=product_data.Name, ProductNumber=product_data.ProductNumber)

        # Ajouter le produit dans la session
        session.add(new_product)
        session.commit()  # Confirmer les changements dans la base de données
        session.refresh(new_product)  # Recharger l'objet pour obtenir l'ID généré

        logging.debug(f"Product created: {new_product}")
        return new_product  # Retourner les données du produit créé
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
