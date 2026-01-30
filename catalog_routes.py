from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from models import Escola, Usuario
from dependencies import pegar_sesssao

catalog_router = APIRouter(prefix="/catalog", tags=["catalogo"])


@catalog_router.get("/escolas")
def listar_escolas(session: Session = Depends(pegar_sesssao)) -> List[dict]:
    escolas = session.query(Escola).all()
    return [
        {"id": escola.id, "nome": escola.nome}
        for escola in escolas
    ]


@catalog_router.get("/usuarios")
def listar_usuarios(
    escola_id: Optional[int] = None,
    somente_fiscais: bool = False,
    session: Session = Depends(pegar_sesssao),
) -> List[dict]:
    query = session.query(Usuario)
    if escola_id is not None:
        query = query.filter(Usuario.escola_id == escola_id)
    if somente_fiscais:
        query = query.filter(Usuario.funcao.ilike("%fiscal%"))

    usuarios = query.all()
    return [
        {
            "id": u.id,
            "nome_completo": u.nome_completo,
            "escola_id": u.escola_id,
            "funcao": u.funcao,
            "escola_nome": getattr(u.escola, "nome", None),
        }
        for u in usuarios
    ]
