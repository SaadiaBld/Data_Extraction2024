from pydantic import BaseModel
from typing import List
from sqlmodel import Field, Session, create_engine, SQLModel
from sqlalchemy.exc import ProgrammingError
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import select
import traceback
import logging

app = FastAPI()

# URL de la base de données SQL Server sur Azure
DATABASE_URL = "mssql+pyodbc://jvcb:cbjv592023!@adventureworks-server-hdf.database.windows.net:1433/adventureworks?driver=ODBC+Driver+18+for+SQL+Server"

# Définir la configuration des logs
logging.basicConfig(level=logging.DEBUG)

# Modèle SQLAlchemy pour la table 'product'
class Product(SQLModel, table=True):
    #__tablename__ = "Product"
    #__schema__ = "Production"

    ProductID: int = Field(default=None, primary_key=True)
    Name: str

# Modèle Pydantic pour les produits
class ProductResponse(BaseModel):
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

@app.get("/products", response_model=List[str])
def get_products(session: Session = Depends(get_session)):
    logging.debug("Fetching products")
    try:
        # Utilisation de select(Product) pour récupérer tous les objets Product
        statement = select(Product)

        # Récupérer les résultats sous forme de liste
        results = session.exec(statement).all()
        
        logging.debug(f"Number of results: {len(results)}")

        # Ajouter un log pour inspecter les premiers éléments des résultats
        if len(results) > 0:
            logging.debug(f"First result: {results[0]}")

        # Vérification de la structure des résultats avant de les traiter
        products_names = [result.Name for result in results]
        
        # Si products_names est vide, loguez un message d'avertissement
        if not products_names:
            logging.warning("No products found")
        
        logging.debug(f"Products fetched: {products_names}")
        return products_names  # Retourner une liste de noms
    except Exception as e:
        logging.error(f"Error occurred: {e}")
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
