from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from typing import List, Optional
from sqlalchemy.orm import Session

from dependencies import pegar_sesssao, require_criacao_equipe, verificar_token
from models import Equipe, Usuario, MembroEquipe, PapelMembro, ConviteFiscalExterno, StatusConvite


equipes_router = APIRouter(prefix="/equipes", tags=["equipes"])


class EquipeCreate(BaseModel):
    nome: str
    escola_id: Optional[int] = None
    fiscal_equipe_id: int
    fiscal_externo_id: Optional[int] = None
    participantes: List[int]

    @field_validator('participantes')
    @classmethod
    def validar_participantes(cls, v):
        if len(v) != 5:
            raise ValueError("Informe exatamente 5 participantes")
        return v


class FiscalExternoUpdate(BaseModel):
    usuario_id: int


    @equipes_router.get("/minha/detalhes")
    def minha_equipe_detalhes(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
        # Prioriza a equipe onde o usuário é líder para evitar misturar equipes ao ter outros vínculos
        vinculo = (
            session.query(MembroEquipe)
            .filter(MembroEquipe.usuario_id == usuario.id, MembroEquipe.papel == PapelMembro.LIDER)
            .first()
        )
        if not vinculo:
            vinculo = session.query(MembroEquipe).filter(MembroEquipe.usuario_id == usuario.id).first()
        if not vinculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não está em nenhuma equipe")

        equipe = session.query(Equipe).filter(Equipe.id == vinculo.equipe_id).first()
        if not equipe:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

        membros = (
            session.query(MembroEquipe, Usuario)
            .join(Usuario, Usuario.id == MembroEquipe.usuario_id)
            .filter(MembroEquipe.equipe_id == equipe.id)
            .all()
        )

        totais_por_papel: dict[str, int] = {}
        for m, _u in membros:
            key = m.papel.value
            totais_por_papel[key] = totais_por_papel.get(key, 0) + 1

        return {
            "equipe_id": equipe.id,
            "equipe_nome": equipe.nome,
            "escola_id": equipe.escola_id,
            "pontuacao": equipe.pontuacao,
            "total_integrantes": len(membros),
            "fiscal_externo_id": equipe.fiscal_externo_id,
            "totais_por_papel": totais_por_papel,
            "membros": [
                {
                    "usuario_id": u.id,
                    "nome": u.nome_completo,
                    "funcao": u.funcao,
                    "email": u.email,
                    "papel": m.papel.value,
                }
                for m, u in membros
            ],
        }


class ConviteFiscalResponse(BaseModel):
    id: int
    equipe_id: int
    equipe_nome: str | None
    convidado_id: int
    status: str

    class Config:
        from_attributes = True


def _buscar_usuario(session: Session, user_id: int) -> Usuario:
    usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario {user_id} não encontrado")
    return usuario


@equipes_router.post("/", status_code=status.HTTP_201_CREATED)
def criar_equipe(payload: EquipeCreate, usuario_logado: Usuario = Depends(require_criacao_equipe), session: Session = Depends(pegar_sesssao)):
    # Líder é o usuário logado
    lider = usuario_logado

    fiscal_eq = _buscar_usuario(session, payload.fiscal_equipe_id)
    fiscal_ext = _buscar_usuario(session, payload.fiscal_externo_id) if payload.fiscal_externo_id else None
    participantes = [_buscar_usuario(session, pid) for pid in payload.participantes]

    # Define escola: se não veio no payload, assume a do líder; senão, valida consistência
    escola_id = payload.escola_id or lider.escola_id
    if escola_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escola não informada e não definida no líder")

    if lider.escola_id and lider.escola_id != escola_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Líder não pertence à escola informada")

    envolvidos = [fiscal_eq] + participantes
    if fiscal_ext:
        envolvidos.append(fiscal_ext)

    for u in envolvidos:
        if u.escola_id != escola_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Usuario {u.id} não pertence à escola {escola_id}")

    # Valida unicidade de membros (líder + fiscais + participantes)
    ids_set = {lider.id, payload.fiscal_equipe_id, *payload.participantes}
    if payload.fiscal_externo_id:
        ids_set.add(payload.fiscal_externo_id)
    if len(ids_set) != 1 + 1 + len(payload.participantes) + (1 if payload.fiscal_externo_id else 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não repita usuários entre líder/fiscais/participantes")

    if fiscal_ext:
        vinculo_ext = session.query(MembroEquipe).filter(MembroEquipe.usuario_id == fiscal_ext.id).first()
        if not vinculo_ext:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fiscal externo precisa estar vinculado a outra equipe")
        if vinculo_ext.equipe_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fiscal externo inválido")

    total_components = 1 + 1 + len(payload.participantes)  # líder + fiscal interno + participantes
    equipe = Equipe(
        nome=payload.nome,
        escola_id=escola_id,
        total_components=total_components,
        fiscal_externo_id=payload.fiscal_externo_id,
    )
    session.add(equipe)
    session.flush()  # para obter id

    membros = [
        MembroEquipe(equipe_id=equipe.id, usuario_id=lider.id, papel=PapelMembro.LIDER),
        MembroEquipe(equipe_id=equipe.id, usuario_id=payload.fiscal_equipe_id, papel=PapelMembro.FISCAL_EQUIPE),
    ]
    membros.extend([
        MembroEquipe(equipe_id=equipe.id, usuario_id=pid, papel=PapelMembro.PARTICIPANTE)
        for pid in payload.participantes
    ])

    session.add_all(membros)
    session.commit()
    session.refresh(equipe)

    return {
        "id": equipe.id,
        "nome": equipe.nome,
        "escola_id": equipe.escola_id,
        "total_components": equipe.total_components,
        "fiscal_externo_id": equipe.fiscal_externo_id,
        "membros": [
            {"usuario_id": m.usuario_id, "papel": m.papel.value}
            for m in membros
        ],
    }


@equipes_router.post("/{equipe_id}/fiscal-externo/convite")
def convidar_fiscal_externo(equipe_id: int, payload: FiscalExternoUpdate, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

    if not usuario.is_admin:
        lider = session.query(MembroEquipe).filter(
            MembroEquipe.equipe_id == equipe_id,
            MembroEquipe.usuario_id == usuario.id,
            MembroEquipe.papel == PapelMembro.LIDER,
        ).first()
        if not lider:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o líder da equipe ou admin pode convidar fiscal externo")

    fiscal = _buscar_usuario(session, payload.usuario_id)
    vinculo_fiscal = session.query(MembroEquipe).filter(MembroEquipe.usuario_id == fiscal.id).first()
    if not vinculo_fiscal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fiscal externo deve pertencer a outra equipe")
    if vinculo_fiscal.equipe_id == equipe_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escolha um fiscal de outra equipe")
    if vinculo_fiscal.papel not in (PapelMembro.FISCAL_EQUIPE, PapelMembro.FISCAL_EXTERNO):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escolha alguém que seja fiscal em sua equipe")

    convite = session.query(ConviteFiscalExterno).filter(
        ConviteFiscalExterno.equipe_solicitante_id == equipe_id,
        ConviteFiscalExterno.convidado_id == fiscal.id,
    ).first()
    if convite:
        convite.status = StatusConvite.PENDENTE
    else:
        convite = ConviteFiscalExterno(
            equipe_solicitante_id=equipe_id,
            convidado_id=fiscal.id,
            status=StatusConvite.PENDENTE,
        )
        session.add(convite)

    session.commit()
    session.refresh(convite)

    return {
        "mensagem": "Convite enviado. Aguarde o fiscal aceitar.",
        "convite_id": convite.id,
        "status": convite.status.value,
    }


@equipes_router.get("/fiscal-externo/minhas")
def minhas_equipes_como_fiscal_externo(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    equipes = session.query(Equipe).filter(Equipe.fiscal_externo_id == usuario.id).all()
    return [
        {
            "equipe_id": e.id,
            "equipe_nome": e.nome,
            "escola_id": e.escola_id,
        }
        for e in equipes
    ]


@equipes_router.delete("/{equipe_id}/membros/{usuario_id}", status_code=status.HTTP_200_OK)
def remover_membro(equipe_id: int, usuario_id: int, usuario_logado: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

    # Apenas admin ou líder da equipe pode remover
    if not usuario_logado.is_admin:
        lider = session.query(MembroEquipe).filter(
            MembroEquipe.equipe_id == equipe_id,
            MembroEquipe.usuario_id == usuario_logado.id,
            MembroEquipe.papel == PapelMembro.LIDER,
        ).first()
        if not lider:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o líder da equipe ou admin pode remover membros")

    vinculo = session.query(MembroEquipe).filter(
        MembroEquipe.equipe_id == equipe_id,
        MembroEquipe.usuario_id == usuario_id,
    ).first()

    if not vinculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membro não encontrado na equipe")

    if vinculo.papel == PapelMembro.LIDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido remover o líder")

    # Se o removido for o fiscal externo registrado na equipe, limpa o campo
    if equipe.fiscal_externo_id == usuario_id:
        equipe.fiscal_externo_id = None

    session.delete(vinculo)

    # Atualiza total de integrantes
    equipe.total_components = session.query(MembroEquipe).filter(MembroEquipe.equipe_id == equipe_id).count()

    session.commit()
    return {"mensagem": "Membro removido com sucesso", "usuario_id": usuario_id, "equipe_id": equipe_id}


@equipes_router.get("/convites/pendentes", response_model=list[ConviteFiscalResponse])
def convites_pendentes(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    convites = session.query(ConviteFiscalExterno).join(Equipe, ConviteFiscalExterno.equipe_solicitante_id == Equipe.id).filter(
        ConviteFiscalExterno.convidado_id == usuario.id,
        ConviteFiscalExterno.status == StatusConvite.PENDENTE,
    ).all()
    return [
        ConviteFiscalResponse(
            id=c.id,
            equipe_id=c.equipe_solicitante_id,
            equipe_nome=getattr(session.query(Equipe).filter(Equipe.id == c.equipe_solicitante_id).first(), 'nome', None),
            convidado_id=c.convidado_id,
            status=c.status.value,
        )
        for c in convites
    ]


@equipes_router.post("/convites/{convite_id}/aceitar")
def aceitar_convite(convite_id: int, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    convite = session.query(ConviteFiscalExterno).filter(ConviteFiscalExterno.id == convite_id).first()
    if not convite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite não encontrado")
    if not usuario.is_admin and convite.convidado_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o convidado ou admin pode aceitar")

    equipe_solicitante = session.query(Equipe).filter(Equipe.id == convite.equipe_solicitante_id).first()
    if not equipe_solicitante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe solicitante não encontrada")

    equipe_do_convidado = session.query(MembroEquipe).filter(
        MembroEquipe.usuario_id == convite.convidado_id,
        MembroEquipe.papel == PapelMembro.FISCAL_EQUIPE
    ).first()
    if not equipe_do_convidado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Convidado precisa ser fiscal de alguma equipe")

    equipe_convidado = session.query(Equipe).filter(Equipe.id == equipe_do_convidado.equipe_id).first()
    if not equipe_convidado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe do convidado não encontrada")

    fiscal_solicitante = session.query(MembroEquipe).filter(
        MembroEquipe.equipe_id == convite.equipe_solicitante_id,
        MembroEquipe.papel == PapelMembro.FISCAL_EQUIPE
    ).first()

    # Pareamento: o convidado vira fiscal externo da equipe solicitante e, se existir fiscal interno, ele vira fiscal externo da equipe do convidado.
    equipe_solicitante.fiscal_externo_id = convite.convidado_id
    if fiscal_solicitante:
        equipe_convidado.fiscal_externo_id = fiscal_solicitante.usuario_id

    # Garante vínculo formal como membro das duas equipes, evitando duplicidade.
    vinculo_convidado_solicitante = session.query(MembroEquipe).filter(
        MembroEquipe.equipe_id == convite.equipe_solicitante_id,
        MembroEquipe.usuario_id == convite.convidado_id,
    ).first()
    if vinculo_convidado_solicitante:
        # Garante que o convidado passe a atuar como fiscal externo nesta equipe.
        vinculo_convidado_solicitante.papel = PapelMembro.FISCAL_EXTERNO
    else:
        session.add(MembroEquipe(
            equipe_id=convite.equipe_solicitante_id,
            usuario_id=convite.convidado_id,
            papel=PapelMembro.FISCAL_EXTERNO,
        ))

    if fiscal_solicitante:
        vinculo_fiscal_na_equipe_convidado = session.query(MembroEquipe).filter(
            MembroEquipe.equipe_id == equipe_convidado.id,
            MembroEquipe.usuario_id == fiscal_solicitante.usuario_id,
        ).first()
        if vinculo_fiscal_na_equipe_convidado:
            # Se já está vinculado, atualiza o papel para fiscal externo.
            vinculo_fiscal_na_equipe_convidado.papel = PapelMembro.FISCAL_EXTERNO
        else:
            session.add(MembroEquipe(
                equipe_id=equipe_convidado.id,
                usuario_id=fiscal_solicitante.usuario_id,
                papel=PapelMembro.FISCAL_EXTERNO,
            ))

    # Recalcula totais para refletir o novo integrante externo
    equipe_solicitante.total_components = session.query(MembroEquipe).filter(MembroEquipe.equipe_id == equipe_solicitante.id).count()
    equipe_convidado.total_components = session.query(MembroEquipe).filter(MembroEquipe.equipe_id == equipe_convidado.id).count()

    convite.status = StatusConvite.ACEITO
    session.commit()
    return {
        "mensagem": "Convite aceito e pareamento de fiscais realizado",
        "equipe_solicitante": equipe_solicitante.id,
        "fiscal_externo_da_solicitante": convite.convidado_id,
        "equipe_convidado": equipe_convidado.id,
        "fiscal_externo_da_equipe_convidado": getattr(fiscal_solicitante, "usuario_id", None),
    }


@equipes_router.get("/fiscais/elegiveis")
def listar_fiscais_elegiveis(
    equipe_id: int,
    usuario: Usuario = Depends(verificar_token),
    session: Session = Depends(pegar_sesssao),
):
    # precisa existir a equipe solicitante para que o filtro faça sentido
    equipe_solicitante = session.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe_solicitante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe solicitante não encontrada")

    # bloqueia usuários que já atuam como fiscal externo em qualquer outra equipe (exceto a própria solicitante)
    subq_externos = (
        session.query(Equipe.fiscal_externo_id)
        .filter(Equipe.fiscal_externo_id.isnot(None), Equipe.id != equipe_id)
        .subquery()
    )

    # evita listar membros da própria equipe solicitante
    subq_membros_solicitante = (
        session.query(MembroEquipe.usuario_id)
        .filter(MembroEquipe.equipe_id == equipe_id)
        .subquery()
    )

    candidatos = (
        session.query(MembroEquipe, Usuario, Equipe)
        .join(Usuario, Usuario.id == MembroEquipe.usuario_id)
        .join(Equipe, Equipe.id == MembroEquipe.equipe_id)
        .filter(MembroEquipe.papel == PapelMembro.FISCAL_EQUIPE)
        .filter(MembroEquipe.equipe_id != equipe_id)
        .filter(~MembroEquipe.usuario_id.in_(subq_externos))
        .filter(~MembroEquipe.usuario_id.in_(subq_membros_solicitante))
    ).all()

    vistos = set()
    resposta = []
    for m, u, eq in candidatos:
        if u.id in vistos:
            continue
        vistos.add(u.id)
        resposta.append({
            "id": u.id,
            "nome_completo": u.nome_completo,
            "funcao": u.funcao,
            "escola_id": u.escola_id,
            "escola_nome": getattr(u.escola, "nome", None),
            "equipe_origem_id": eq.id,
            "equipe_origem_nome": eq.nome,
        })

    return resposta


@equipes_router.get("/ranking")
def ranking(session: Session = Depends(pegar_sesssao)):
    equipes = (
        session.query(Equipe)
        .order_by(Equipe.pontuacao.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "nome": e.nome,
            "escola_id": e.escola_id,
            "pontuacao": e.pontuacao,
            "total_components": e.total_components,
        }
        for e in equipes
    ]


@equipes_router.get("/minha")
def minha_equipe(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    vinculo = (
        session.query(MembroEquipe)
        .filter(MembroEquipe.usuario_id == usuario.id, MembroEquipe.papel == PapelMembro.LIDER)
        .first()
    )
    if not vinculo:
        vinculo = session.query(MembroEquipe).filter(MembroEquipe.usuario_id == usuario.id).first()
    if not vinculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não está em nenhuma equipe")

    equipe = session.query(Equipe).filter(Equipe.id == vinculo.equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

    return {
        "equipe_id": equipe.id,
        "equipe_nome": equipe.nome,
        "papel": vinculo.papel.value,
        "pontuacao": equipe.pontuacao,
    }

