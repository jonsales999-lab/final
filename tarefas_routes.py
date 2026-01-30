
"""
Módulo de rotas relacionadas às tarefas do sistema EcoPlay.
Inclui endpoints para listar, iniciar, executar e consultar o status de tarefas.
Regras de negócio envolvem validações de papéis de usuários, aprovações por fiscais e controle de pontuação das equipes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from models import Tarefa, Equipe, ExecucaoTarefa, ExecucaoTarefaAprovacao, MembroEquipe, PapelMembro
from dependencies import pegar_sesssao, verificar_token



tarefas_router = APIRouter(prefix="/tarefas", tags=["tarefas"])


# Mapeia IDs da unidade para slugs amigáveis usados no frontend
UNIDADE_SLUG = {
    1: "kg",
    2: "litros",
    3: "metro_cubico",
    4: "unidade",
    5: "acao",
}



@tarefas_router.get("/")
def listar_tarefas(session: Session = Depends(pegar_sesssao)):
    """
    Lista todas as tarefas cadastradas no sistema.
    Retorna id, título, descrição e pontuação de cada tarefa.
    """
    tarefas = session.query(Tarefa).all()
    tarefas_json = [
        {
            "id": t.id,
            "titulo": t.titulo,
            "descricao": t.descricao,
            "pontuacao": t.pontuacao,
            "unidade": UNIDADE_SLUG.get(t.unidade_id),
            "unidade_id": t.unidade_id,
            "material": t.material.nome if t.material else t.material_id
        }
        for t in tarefas
    ]
    # print('Tarefas retornadas:', tarefas_json)
    return tarefas_json


# cria tarefas de exemplo se a tabela estiver vazia


@tarefas_router.post("/{tarefa_id}/executar")
def executar_tarefa(tarefa_id: int, payload: dict, usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    """
    Executa uma tarefa para uma equipe, após validações de permissão e aprovações.
    - Admin pode executar diretamente.
    - Fiscais precisam aprovar (dupla aprovação: fiscal interno e externo).
    - Só pode executar se iniciada pelo líder.
    """
    payload = payload or {}
    equipe_id = payload.get("equipe_id")
    try:
        equipe_id = int(equipe_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe equipe_id válido")

    equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

    tarefa = session.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")

    # Permissões e ordem de aprovação:
    # - Fiscal interno pode registrar a primeira aprovação diretamente (sem exigir início prévio).
    # - Fiscal externo só pode aprovar após existir aprovação do fiscal interno.
    # - Admin sempre pode.
    membro_fiscal_interno = session.query(MembroEquipe).filter(
        MembroEquipe.usuario_id == usuario_logado.id,
        MembroEquipe.equipe_id == equipe_id,
        MembroEquipe.papel == PapelMembro.FISCAL_EQUIPE
    ).first()

    autorizado_externo = equipe.fiscal_externo_id == usuario_logado.id

    if not usuario_logado.is_admin and not membro_fiscal_interno and not autorizado_externo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o fiscal da equipe ou o fiscal externo autorizado podem concluir tarefas")

    if autorizado_externo and not usuario_logado.is_admin:
        iniciou_interno = session.query(ExecucaoTarefaAprovacao).filter(
            ExecucaoTarefaAprovacao.equipe_id == equipe_id,
            ExecucaoTarefaAprovacao.tarefa_id == tarefa_id,
            ExecucaoTarefaAprovacao.papel == PapelMembro.FISCAL_EQUIPE,
        ).first()
        if not iniciou_interno:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aguardando validação do fiscal da equipe")

    existe = session.query(ExecucaoTarefa).filter(
        ExecucaoTarefa.equipe_id == equipe_id,
        ExecucaoTarefa.tarefa_id == tarefa_id
    ).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tarefa já executada por esta equipe")

    if usuario_logado.is_admin:
        execucao = ExecucaoTarefa(
            equipe_id=equipe_id,
            tarefa_id=tarefa_id,
            pontos=tarefa.pontuacao
        )
        equipe.pontuacao = (equipe.pontuacao or 0) + tarefa.pontuacao
        session.add(execucao)
        session.commit()
        session.refresh(equipe)
        return {
            "mensagem": "Tarefa executada (admin)",
            "equipe_id": equipe_id,
            "tarefa_id": tarefa_id,
            "pontos_adicionados": tarefa.pontuacao,
            "pontuacao_total": equipe.pontuacao,
            "unidade": tarefa.unidade.nome if tarefa.unidade else None,
            "material": tarefa.material.nome if tarefa.material else tarefa.material_id
        }

    papel_fiscal = PapelMembro.FISCAL_EXTERNO if (equipe.fiscal_externo_id == usuario_logado.id) else PapelMembro.FISCAL_EQUIPE

    aprov_existente = session.query(ExecucaoTarefaAprovacao).filter(
        ExecucaoTarefaAprovacao.equipe_id == equipe_id,
        ExecucaoTarefaAprovacao.tarefa_id == tarefa_id,
        ExecucaoTarefaAprovacao.papel == papel_fiscal
    ).first()
    if not aprov_existente:
        aprov = ExecucaoTarefaAprovacao(
            equipe_id=equipe_id,
            tarefa_id=tarefa_id,
            fiscal_id=usuario_logado.id,
            papel=papel_fiscal
        )
        session.add(aprov)
        session.flush()

    aprovacoes = session.query(ExecucaoTarefaAprovacao).filter(
        ExecucaoTarefaAprovacao.equipe_id == equipe_id,
        ExecucaoTarefaAprovacao.tarefa_id == tarefa_id
    ).all()

    # Fiscal externo só pode registrar aprovação se a validação interna já existir.
    if not usuario_logado.is_admin and equipe.fiscal_externo_id == usuario_logado.id:
        tem_interno = any(a.papel == PapelMembro.FISCAL_EQUIPE for a in aprovacoes)
        if not tem_interno:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Aguardando validação do fiscal da equipe")

    tem_fiscal_eq = any(a.papel == PapelMembro.FISCAL_EQUIPE for a in aprovacoes)
    tem_fiscal_ext = any(a.papel == PapelMembro.FISCAL_EXTERNO for a in aprovacoes)

    if tem_fiscal_eq and tem_fiscal_ext:
        execucao = ExecucaoTarefa(
            equipe_id=equipe_id,
            tarefa_id=tarefa_id,
            pontos=tarefa.pontuacao
        )
        equipe.pontuacao = (equipe.pontuacao or 0) + tarefa.pontuacao
        session.add(execucao)
        session.query(ExecucaoTarefaAprovacao).filter(
            ExecucaoTarefaAprovacao.equipe_id == equipe_id,
            ExecucaoTarefaAprovacao.tarefa_id == tarefa_id
        ).delete()
        session.commit()
        session.refresh(equipe)
        return {
            "mensagem": "Tarefa executada após dupla aprovação dos fiscais",
            "equipe_id": equipe_id,
            "tarefa_id": tarefa_id,
            "pontos_adicionados": tarefa.pontuacao,
            "pontuacao_total": equipe.pontuacao,
            "unidade": tarefa.unidade.nome if tarefa.unidade else None,
            "material": tarefa.material.nome if tarefa.material else tarefa.material_id
        }

    session.commit()
    return {
        "mensagem": "Aguardando aprovação do outro fiscal para concluir a tarefa",
        "aprovacoes_registradas": [a.papel.value for a in aprovacoes],
        "tarefa_id": tarefa_id,
        "equipe_id": equipe_id,
    }



@tarefas_router.post("/{tarefa_id}/iniciar")
def iniciar_tarefa(tarefa_id: int, payload: dict, usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    """
    Inicia uma tarefa para uma equipe.
    Visível para todos, mas apenas o fiscal da equipe (ou admin) pode iniciar.
    Registra a aprovação inicial do fiscal interno.
    """
    payload = payload or {}
    equipe_id = payload.get("equipe_id")
    try:
        equipe_id = int(equipe_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe equipe_id válido")

    equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

    tarefa = session.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")

    # Apenas fiscal interno (ou admin) pode iniciar
    if not usuario_logado.is_admin:
        fiscal = session.query(MembroEquipe).filter(
            MembroEquipe.equipe_id == equipe_id,
            MembroEquipe.usuario_id == usuario_logado.id,
            MembroEquipe.papel == PapelMembro.FISCAL_EQUIPE,
        ).first()
        if not fiscal:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas o fiscal da equipe pode iniciar a tarefa")

    ja_executada = session.query(ExecucaoTarefa).filter(
        ExecucaoTarefa.equipe_id == equipe_id,
        ExecucaoTarefa.tarefa_id == tarefa_id,
    ).first()
    if ja_executada:
        # Permite refazer: limpa execução concluída e aprovações anteriores para reiniciar o fluxo.
        session.query(ExecucaoTarefaAprovacao).filter(
            ExecucaoTarefaAprovacao.equipe_id == equipe_id,
            ExecucaoTarefaAprovacao.tarefa_id == tarefa_id,
        ).delete()
        session.delete(ja_executada)
        session.flush()

    inicio = session.query(ExecucaoTarefaAprovacao).filter(
        ExecucaoTarefaAprovacao.equipe_id == equipe_id,
        ExecucaoTarefaAprovacao.tarefa_id == tarefa_id,
        ExecucaoTarefaAprovacao.papel == PapelMembro.LIDER,
    ).first()

    if not inicio:
        inicio = ExecucaoTarefaAprovacao(
            equipe_id=equipe_id,
            tarefa_id=tarefa_id,
            fiscal_id=usuario_logado.id,
            papel=PapelMembro.LIDER,
        )
        session.add(inicio)
    else:
        inicio.fiscal_id = usuario_logado.id

    session.commit()
    return {
        "mensagem": "Tarefa iniciada pelo fiscal da equipe. Aguarde validação dos dois fiscais.",
        "equipe_id": equipe_id,
        "tarefa_id": tarefa_id,
    }



@tarefas_router.get("/{tarefa_id}/status")
def status_tarefa(tarefa_id: int, equipe_id: int | None = None, usuario_logado=Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    """
    Consulta o status de execução de uma tarefa para uma equipe.
    Retorna se foi executada, pontos, se foi iniciada pelo fiscal interno, data de início e aprovações registradas.
    """
    if not equipe_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe equipe_id")

    equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipe não encontrada")

    if not usuario_logado.is_admin:
        membro = session.query(MembroEquipe).filter(
            MembroEquipe.usuario_id == usuario_logado.id,
            MembroEquipe.equipe_id == equipe_id
        ).first()
        autorizado_externo = equipe.fiscal_externo_id == usuario_logado.id
        if not membro and not autorizado_externo:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para esta equipe")

    tarefa = session.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")

    execucao = session.query(ExecucaoTarefa).filter(
        ExecucaoTarefa.equipe_id == equipe_id,
        ExecucaoTarefa.tarefa_id == tarefa_id
    ).first()

    aprovacoes = session.query(ExecucaoTarefaAprovacao).filter(
        ExecucaoTarefaAprovacao.equipe_id == equipe_id,
        ExecucaoTarefaAprovacao.tarefa_id == tarefa_id
    ).all()

    # Fiscal externo só enxerga status se já houver aprovação interna ou se a execução já foi concluída.
    if not usuario_logado.is_admin and equipe.fiscal_externo_id == usuario_logado.id:
        if not execucao:
            tem_interno = any(a.papel == PapelMembro.FISCAL_EQUIPE for a in aprovacoes)
            if not tem_interno:
                return Response(status_code=status.HTTP_204_NO_CONTENT)

    iniciou = next((a for a in aprovacoes if a.papel == PapelMembro.LIDER), None)

    return {
        "executada": bool(execucao),
        "pontos": execucao.pontos if execucao else None,
        "iniciada_por_lider": bool(iniciou),
        "iniciada_em": iniciou.criado_em.isoformat() if iniciou and iniciou.criado_em else None,
        "aprovacoes": [
            {
                "papel": a.papel.value,
                "fiscal_id": a.fiscal_id,
                "criado_em": a.criado_em.isoformat() if a.criado_em else None,
            }
            for a in aprovacoes
        ],
    }
