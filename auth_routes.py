
# Endpoint de resumo para painel admin
from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import pegar_sesssao, require_admin, verificar_token, require_criacao_equipe
from sqlalchemy.orm import Session
from schemas import UsuarioCreate, LoginSchema
from app.main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from jose import jwt, JWTError
from models import Usuario, Equipe, MembroEquipe, PapelMembro
from sqlalchemy import or_
from datetime import datetime, timedelta,timezone
from fastapi.security import OAuth2PasswordRequestForm
import base64

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/verificar-duplicidade", tags=["auth"])
def verificar_duplicidade(email: str | None = None, cpf: str | None = None, session: Session = Depends(pegar_sesssao)):
    """Valida se email ou CPF já existem para evitar 409 antes do cadastro."""
    duplicados = []
    if email:
        existe_email = session.query(Usuario.id).filter(Usuario.email == email).first()
        if existe_email:
            duplicados.append("email")
    if cpf:
        existe_cpf = session.query(Usuario.id).filter(Usuario.cpf == cpf).first()
        if existe_cpf:
            duplicados.append("cpf")
    return {"ok": len(duplicados) == 0, "duplicados": duplicados}


@auth_router.get("/admin/resumo")
def admin_resumo(session: Session = Depends(pegar_sesssao), usuario=Depends(require_admin)):
    pendentes = session.query(Usuario).filter(Usuario.pode_criar_equipe == False).count()
    lideres_ativos = session.query(Usuario).filter(Usuario.pode_criar_equipe == True).count()
    escolas = session.query(Usuario.escola_id).distinct().count()
    return {
        "pendentes": pendentes,
        "lideres_ativos": lideres_ativos,
        "escolas": escolas
    }



def _criar_equipe_para_lider(session: Session, usuario: Usuario) -> Equipe:
    """Cria (ou recupera) equipe exclusiva do líder sem efetuar commit.

    Chamadores devem fazer `session.commit()` após usar esta função para manter a operação
    atômica junto de outras escritas (ex.: cadastro de novo membro).
    """
    # Verifica se já existe vínculo de liderança
    vinculo = (
        session.query(MembroEquipe)
        .filter(MembroEquipe.usuario_id == usuario.id, MembroEquipe.papel == PapelMembro.LIDER)
        .first()
    )
    if vinculo:
        equipe = session.get(Equipe, vinculo.equipe_id)
        if equipe:
            lideres = (
                session.query(MembroEquipe)
                .filter(MembroEquipe.equipe_id == equipe.id, MembroEquipe.papel == PapelMembro.LIDER)
                .all()
            )
            # Só é válido se o único líder da equipe for o próprio usuário
            if len(lideres) == 1 and lideres[0].usuario_id == usuario.id:
                return equipe

            # Remove vínculo errado para criar uma equipe exclusiva para este líder
            session.delete(vinculo)
            session.flush()

        # Vínculo órfão: remove e cria uma nova equipe para garantir consistência
        session.delete(vinculo)
        session.flush()

    equipe = Equipe(
        nome=f"Equipe de {usuario.nome_completo}",
        escola_id=usuario.escola_id,
        total_components=1,
        pontuacao=0,
    )
    session.add(equipe)
    session.flush()  # garante equipe.id para o relacionamento

    membro = MembroEquipe(equipe_id=equipe.id, usuario_id=usuario.id, papel=PapelMembro.LIDER)
    session.add(membro)
    session.flush()
    return equipe


def _mapear_funcao_para_papel(funcao: str) -> PapelMembro:
    f = (funcao or "").lower()
    if "fiscal" in f:
        return PapelMembro.FISCAL_EQUIPE
    return PapelMembro.PARTICIPANTE


def _carregar_membros_da_equipe(session: Session, equipe_id: int):
    return (
        session.query(MembroEquipe, Usuario)
        .join(Usuario, Usuario.id == MembroEquipe.usuario_id)
        .filter(MembroEquipe.equipe_id == equipe_id)
        .all()
    )


def _equipe_por_usuario(session: Session, usuario_id: int):
    """Retorna a equipe do usuário priorizando o papel de fiscal interno.

    Se o usuário tiver vários vínculos, escolhe primeiro `FISCAL_EQUIPE`,
    depois qualquer outro vínculo disponível.
    """
    vinculos = session.query(MembroEquipe).filter(MembroEquipe.usuario_id == usuario_id).all()
    if not vinculos:
        return None

    alvo = next((v for v in vinculos if v.papel == PapelMembro.FISCAL_EQUIPE), None)
    if not alvo:
        alvo = vinculos[0]

    equipe = session.get(Equipe, alvo.equipe_id)
    return equipe, alvo.papel if equipe else None


def _resumo_membros(membros):
    resumo = {}
    for membro, _usuario in membros:
        chave = membro.papel.value
        resumo[chave] = resumo.get(chave, 0) + 1
    return resumo
#Cricao do tokent jwt
def criar_token(usuario: Usuario, duracao_token = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {
        "sub": str(usuario.id),
        "exp": data_expiracao,
        "is_admin": bool(usuario.is_admin),
        "pode_criar_equipe": bool(usuario.pode_criar_equipe),
        "funcao": usuario.funcao,
        "escola_id": usuario.escola_id,
    }
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado



#Verificacao de USUARIO
def autenticar_usuario(email,senha,session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not usuario.senha_hash or not bcrypt_context.verify(senha, usuario.senha_hash):
        return False
    return usuario


@auth_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_usuario(user: UsuarioCreate, session = Depends(pegar_sesssao)):
    # Verifica duplicidade de email, CPF ou nome completo antes de salvar
    duplicatas = session.query(Usuario).filter(
        or_(
            Usuario.email == user.email,
            Usuario.cpf == user.cpf,
        )
    ).all()

    if duplicatas:
        campos = set()
        for usuario in duplicatas:
            if user.email and usuario.email == user.email:
                campos.add("email")
            if user.cpf and usuario.cpf == user.cpf:
                campos.add("cpf")
            # nomes podem repetir; não bloqueia por nome

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Dados ja cadastrados",
                "fields": sorted(list(campos)),
            },
        )
    
    # Função interna simples para tratar o Base64
    def converter_base64_para_binario(string_b64: str):
        if not string_b64:
            return None
        try:
            # Se o front enviar com o prefixo "data:image/jpeg;base64,", nós removemos
            if "," in string_b64:
                string_b64 = string_b64.split(",")[1]
            return base64.b64decode(string_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de imagem inválido")
    
    
    
    senha_hash = bcrypt_context.hash(user.senha)
    # Cria o usuário
    novo_usuario = Usuario(
        escola_id=user.escola_id,
        nome_completo=user.nome_completo,
        sexo=user.sexo,
        data_nascimento=user.data_nascimento,
        funcao=user.funcao,
        telefone_pessoal=user.telefone_pessoal,
        email=user.email,
        rg_path=converter_base64_para_binario(user.rg_path),
        cpf =user.cpf,
        senha_hash=senha_hash,
        cursando=user.cursando,
        manequim=user.manequim,
        tipo_sanguineo=user.tipo_sanguineo,
        medicamento_controlado=user.medicamento_controlado,
        nome_medicamento_1=user.nome_medicamento_1,
        declaracao_lida=user.declaracao_lida,
    )

    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return {"mensagem": "Usuário cadastrado com sucesso", "id": novo_usuario.id}


@auth_router.post("/lider/cadastrar", status_code=status.HTTP_201_CREATED)
async def lider_cadastrar_usuario(user: UsuarioCreate, lider: Usuario = Depends(require_criacao_equipe), session: Session = Depends(pegar_sesssao)):
    if user.funcao.lower() == 'lider':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível criar um novo líder a partir deste formulário. O cadastro de líderes é feito em outra tela e requer aprovação de um administrador."
        )
    # Forca o cadastro na mesma escola do lider (ignora o que vier do payload)
    escola_id = lider.escola_id
    if not escola_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lider sem escola definida")

    duplicatas = session.query(Usuario).filter(
        or_(
            Usuario.email == user.email,
            Usuario.cpf == user.cpf,
        )
    ).all()

    if duplicatas:
        campos = set()
        for usuario in duplicatas:
            if user.email and usuario.email == user.email:
                campos.add("email")
            if user.cpf and usuario.cpf == user.cpf:
                campos.add("cpf")
            # nomes podem repetir; não bloqueia por nome
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Dados ja cadastrados",
                "fields": sorted(list(campos)),
            },
        )

    def converter_base64_para_binario(string_b64: str):
        if not string_b64:
            return None
        try:
            if "," in string_b64:
                string_b64 = string_b64.split(",")[1]
            return base64.b64decode(string_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de imagem inválido")

    senha_hash = bcrypt_context.hash(user.cpf)  # senha inicial = CPF

    # Ignora escola_id que veio no payload e usa a do líder
    novo_usuario = Usuario(
        escola_id=escola_id,
        nome_completo=user.nome_completo,
        sexo=user.sexo,
        data_nascimento=user.data_nascimento,
        funcao=user.funcao,
        telefone_pessoal=user.telefone_pessoal,
        email=user.email,
        rg_path=converter_base64_para_binario(user.rg_path),
        cpf=user.cpf,
        senha_hash=senha_hash,
        cursando=user.cursando,
        manequim=user.manequim,
        tipo_sanguineo=user.tipo_sanguineo,
        medicamento_controlado=user.medicamento_controlado,
        nome_medicamento_1=user.nome_medicamento_1,
        declaracao_lida=user.declaracao_lida,
    )

    session.add(novo_usuario)
    session.flush()

    equipe = _criar_equipe_para_lider(session, lider)
    papel = _mapear_funcao_para_papel(user.funcao)

    existe = session.query(MembroEquipe).filter(MembroEquipe.usuario_id == novo_usuario.id).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ja esta vinculado a uma equipe")

    membro = MembroEquipe(equipe_id=equipe.id, usuario_id=novo_usuario.id, papel=papel)
    session.add(membro)

    # Atualiza total de integrantes
    equipe.total_components = session.query(MembroEquipe).filter(MembroEquipe.equipe_id == equipe.id).count()

    session.commit()
    session.refresh(novo_usuario)
    session.refresh(equipe)

    return {
        "mensagem": "Usuario cadastrado e adicionado na equipe do lider",
        "usuario_id": novo_usuario.id,
        "equipe_id": equipe.id,
        "papel": papel.value,
        "total_integrantes": equipe.total_components,
    }


@auth_router.get("/lider/equipe", tags=["auth"])
async def obter_equipe_do_lider(lider: Usuario = Depends(require_criacao_equipe), session: Session = Depends(pegar_sesssao)):
    equipe = _criar_equipe_para_lider(session, lider)
    membros = _carregar_membros_da_equipe(session, equipe.id)
    equipe.total_components = len(membros)
    session.commit()

    return {
        "equipe_id": equipe.id,
        "equipe_nome": equipe.nome,
        "escola_id": equipe.escola_id,
        "pontuacao": equipe.pontuacao,
        "total_integrantes": equipe.total_components,
        "fiscal_externo_id": equipe.fiscal_externo_id,
        "totais_por_papel": _resumo_membros(membros),
        "membros": [
            {
                "usuario_id": usuario.id,
                "nome": usuario.nome_completo,
                "funcao": usuario.funcao,
                "email": usuario.email,
                "papel": membro.papel.value,
            }
            for membro, usuario in membros
        ],
    }


@auth_router.get("/me/equipe", tags=["auth"])
async def obter_equipe_do_usuario(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sesssao)):
    resultado = _equipe_por_usuario(session, usuario.id)
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario sem equipe")

    equipe, papel_escolhido = resultado
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario sem equipe")

    membros = _carregar_membros_da_equipe(session, equipe.id)
    equipe.total_components = len(membros)
    session.commit()

    meu_papel = papel_escolhido.value if papel_escolhido else None

    return {
        "equipe_id": equipe.id,
        "equipe_nome": equipe.nome,
        "escola_id": equipe.escola_id,
        "pontuacao": equipe.pontuacao,
        "total_integrantes": equipe.total_components,
        "fiscal_externo_id": equipe.fiscal_externo_id,
        "totais_por_papel": _resumo_membros(membros),
        "meu_papel": meu_papel,
    }


@auth_router.post("/login")
async def login(login : LoginSchema, session = Depends(pegar_sesssao)):
    usuario = autenticar_usuario(login.email, login.senha, session)  # lembrar de validar com a senha
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Usuario não encontrado credenciais invalidas")
    
    else:
        access_token = criar_token(usuario)
        refresh_token = criar_token(usuario, duracao_token = timedelta(days=7))
        return{
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "token_type":"Bearer",
            "user": {
                "id": usuario.id,
                "nome_completo": usuario.nome_completo,
                "email": usuario.email,
                "funcao": usuario.funcao,
                "escola_id": usuario.escola_id,
                "escola_nome": getattr(usuario.escola, "nome", None),
                "is_admin": usuario.is_admin,
                "pode_criar_equipe": usuario.pode_criar_equipe,
            }
            
            }
#
@auth_router.post("/login-form")
async def login_form(dados_formulario : OAuth2PasswordRequestForm = Depends(), session : Session = Depends(pegar_sesssao)):
    usuario = autenticar_usuario(dados_formulario.username,dados_formulario.password,session)  # lembrar de validar com a senha
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "Usuario não encontrado credenciais invalidas")
    
    else:
        access_token = criar_token(usuario)
        refresh_token = criar_token(usuario, duracao_token = timedelta(days=7))
        return{
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "token_type":"Bearer",
            "user": {
                "id": usuario.id,
                "nome_completo": usuario.nome_completo,
                "email": usuario.email,
                "funcao": usuario.funcao,
                "escola_id": usuario.escola_id,
                "escola_nome": getattr(usuario.escola, "nome", None),
                "is_admin": usuario.is_admin,
                "pode_criar_equipe": usuario.pode_criar_equipe,
            }
            
            }


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario)
    return{
        "access_token" : access_token,
        "token_type" : "Bearer",
        "user": {
            "id": usuario.id,
            "nome_completo": usuario.nome_completo,
            "email": usuario.email,
            "funcao": usuario.funcao,
            "escola_id": usuario.escola_id,
            "escola_nome": getattr(usuario.escola, "nome", None),
            "is_admin": usuario.is_admin,
            "pode_criar_equipe": usuario.pode_criar_equipe,
        }
    }


@auth_router.post("/admin/liberar-criacao/{usuario_id}", tags=["admin"])
async def liberar_criacao(usuario_id: int, admin: Usuario = Depends(require_admin), session: Session = Depends(pegar_sesssao)):
    usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    usuario.pode_criar_equipe = True
    # Ao liberar, garante que ele lidera uma equipe própria
    equipe = _criar_equipe_para_lider(session, usuario)
    session.commit()
    return {
        "mensagem": "Permissão concedida e equipe criada/associada",
        "usuario_id": usuario_id,
        # equipe_id removido a pedido; ID já é gerado no banco e não é necessário aqui
    }


@auth_router.post("/admin/revogar-criacao/{usuario_id}", tags=["admin"])
async def revogar_criacao(usuario_id: int, admin: Usuario = Depends(require_admin), session: Session = Depends(pegar_sesssao)):
    usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    usuario.pode_criar_equipe = False
    session.commit()
    return {"mensagem": "Permissão revogada", "usuario_id": usuario_id}


@auth_router.get("/admin/pendentes", tags=["admin"])
async def listar_pendentes(admin: Usuario = Depends(require_admin), session: Session = Depends(pegar_sesssao)):
    """Lista usuários sem permissão de criar equipe (exclui admins)."""
    pendentes = (
        session.query(Usuario)
        .filter(Usuario.is_admin == False)  # noqa: E712
        .filter(
            or_(
                Usuario.pode_criar_equipe == False,  # noqa: E712
                Usuario.pode_criar_equipe.is_(None),
            )
        )
        .filter(
            or_(
                Usuario.funcao.ilike("%lid%"),
                Usuario.funcao.ilike("%líder%"),
            )
        )
        .all()
    )
    return [
        {
            "id": u.id,
            "nome_completo": u.nome_completo,
            "email": u.email,
            "funcao": u.funcao,
            "escola_id": u.escola_id,
        }
        for u in pendentes
    ]
