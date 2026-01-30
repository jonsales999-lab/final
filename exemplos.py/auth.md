from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from passlib.context import CryptContext

from models import Usuario
from dependencies import pegar_sesssao  # pega a sessao de conexao do banco de dados

app = FastAPI()

# Cria o router
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioCreate(BaseModel):
    nome_completo: str
    sexo: str
    data_nascimento: date
    funcao: str
    telefone_pessoal: str
    rg_path: str
    cpf_path: str
    email: EmailStr
    senha: str
    cursando: Optional[str] = None
    manequim: Optional[str] = None
    tipo_sanguineo: Optional[str] = None
    medicamento_controlado: Optional[bool] = False
    nome_medicamento_1: Optional[str] = None
    declaracao_lida: Optional[bool] = False
    equipe_id: Optional[int] = None



@auth_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_usuario(user: UsuarioCreate, session = Depends(pegar_sesssao)):
    # Verifica se já existe usuário com o email
    usuario = session.query(Usuario).filter(Usuario.email == user.email).first()
    if usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um usuário com esse email")

    # Hash da senha
    senha_hash = pwd_context.hash(user.senha)

    # Cria o usuário com todos os campos
    novo_usuario = Usuario(
        user.nome_completo,
        user.sexo,
        user.data_nascimento,
        user.funcao,
        user.telefone_pessoal,
        user.rg_path,
        user.cpf_path,
        user.email,
        senha_hash=senha_hash,
        cursando=user.cursando,
        manequim=user.manequim,
        tipo_sanguineo=user.tipo_sanguineo,
        medicamento_controlado=user.medicamento_controlado,
        nome_medicamento_1=user.nome_medicamento_1,
        declaracao_lida=user.declaracao_lida,
        equipe_id=user.equipe_id,
    )

    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return {"mensagem": "Usuário cadastrado com sucesso", "id": novo_usuario.id}

# Inclui o router no app
app.include_router(auth_router)