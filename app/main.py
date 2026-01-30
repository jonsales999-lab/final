from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite TUDO (apenas para teste!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router  # Importa depois de criar o FastAPI
from catalog_routes import catalog_router
from equipes import equipes_router
from tarefas_routes import tarefas_router

# Inclui os routers
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(equipes_router)
app.include_router(tarefas_router)
