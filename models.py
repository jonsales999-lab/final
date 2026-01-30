from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean, Enum, UniqueConstraint, DateTime
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import declarative_base, relationship
from datetime import date
import enum
from datetime import datetime

db = create_engine(
    'mysql+mysqlconnector://root:GUvNdigPYtfgtcbGdCfTgTqRlwLZoNoT@trolley.proxy.rlwy.net:46075/railway'
)

Base = declarative_base()


class PapelMembro(str, enum.Enum):
    LIDER = "LIDER"
    FISCAL_EQUIPE = "FISCAL_EQUIPE"
    FISCAL_EXTERNO = "FISCAL_EXTERNO"
    PARTICIPANTE = "PARTICIPANTE"

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    escola_id = Column(Integer, ForeignKey('escolas.id'), nullable=True)
    nome_completo = Column(String(255), nullable=False)
    sexo = Column(String(1), nullable=False)  # 'M' ou 'F'
    data_nascimento = Column(Date, nullable=False)
    funcao = Column(String(50), nullable=False)  # Atuante, Líder, Vice, Fiscal, Suplente
    telefone_pessoal = Column(String(20), nullable=False)
    rg_path = Column(LONGBLOB)
    cpf = Column(String(255))
    email = Column(String(100), nullable=False)
    senha_hash = Column(String(255), nullable=True)
    cursando = Column(String(50), nullable=False)  # Fundamental 1, Fundamental 2, Universitário
    manequim = Column(String(10), nullable=False)  # PP, P, M, G, GG
    tipo_sanguineo = Column(String(5), nullable=False)  # A+, O-, etc.
    medicamento_controlado = Column(Boolean, nullable=False, default=False)
    nome_medicamento_1 = Column(String(100), nullable=True)
    declaracao_lida = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    pode_criar_equipe = Column(Boolean, nullable=False, default=False)
    escola = relationship("Escola", back_populates="usuarios")
    membros = relationship("MembroEquipe", back_populates="usuario", cascade="all, delete-orphan")

    def __init__(self, nome_completo, sexo, data_nascimento, funcao, telefone_pessoal, 
                 rg_path, cpf, email, senha_hash=None, cursando=None, manequim=None, tipo_sanguineo=None, 
                 medicamento_controlado=False, nome_medicamento_1=None, 
                 declaracao_lida=False, escola_id=None, is_admin=False, pode_criar_equipe=False):
        """
        Construtor da classe Usuario
        """

        self.nome_completo = nome_completo
        self.sexo = sexo
        self.data_nascimento = data_nascimento
        self.funcao = funcao
        self.telefone_pessoal = telefone_pessoal
        self.rg_path = rg_path
        self.cpf = cpf
        self.email = email
        self.senha_hash = senha_hash
        self.cursando = cursando
        self.manequim = manequim
        self.tipo_sanguineo = tipo_sanguineo
        self.medicamento_controlado = medicamento_controlado
        self.nome_medicamento_1 = nome_medicamento_1
        self.declaracao_lida = declaracao_lida
        self.escola_id = escola_id
        self.is_admin = is_admin
        self.pode_criar_equipe = pode_criar_equipe
        # self.equipe_id = equipe_id  # Comentado para testes sem equipe id

    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome_completo}')>"

class Escola(Base):
    __tablename__ = 'escolas'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    endereco = Column(String(255), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    cep = Column(String(20), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    usuarios = relationship("Usuario", back_populates="escola", cascade="all, delete-orphan")
    
    def __init__(self, nome, endereco, cidade, estado, cep, telefone, email):
        """
        Construtor da classe Escola
        """
        self.nome = nome
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        self.telefone = telefone
        self.email = email
    
    def __repr__(self):
        return f"<Escola(id={self.id}, nome='{self.nome}')>"



#Classe para criacao de equipe
class Equipe(Base):
    __tablename__ = 'equipes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=True)  # Opcional
    aceito = Column(Boolean, nullable=False, default=False)
    total_components = Column(Integer, nullable=False, default=0)
    pontuacao = Column(Integer, nullable=False, default=0)
    fiscal_externo_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    escola_id = Column(Integer, ForeignKey('escolas.id'), nullable=True)
    escola = relationship("Escola")
    membros = relationship("MembroEquipe", back_populates="equipe", cascade="all, delete-orphan")

    
    def __init__(self, nome=None, aceito=False, total_components=0, pontuacao=0, escola_id=None, fiscal_externo_id=None):
        """
        Construtor da classe Equipe
        """
        self.nome = nome
        self.aceito = aceito
        self.total_components = total_components
        self.pontuacao = pontuacao
        self.escola_id = escola_id
        self.fiscal_externo_id = fiscal_externo_id
    
    def __repr__(self):
        return f"<Equipe(id={self.id}, nome='{self.nome}', aceito={self.aceito})>"


class MembroEquipe(Base):
    __tablename__ = 'membros_equipes'

    id = Column(Integer, primary_key=True)
    equipe_id = Column(Integer, ForeignKey('equipes.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    papel = Column(Enum(PapelMembro), nullable=False)

    equipe = relationship("Equipe", back_populates="membros")
    usuario = relationship("Usuario", back_populates="membros")

    __table_args__ = (
        UniqueConstraint('equipe_id', 'usuario_id', name='uq_membro_unico'),
    )



# Novas tabelas para materiais e unidades de medida
class UnidadeMedida(Base):
    __tablename__ = 'unidade_medida'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    tarefas = relationship("Tarefa", back_populates="unidade")

class Material(Base):
    __tablename__ = 'material'
    # Usa slug textual (ex.: "garrafa_pet") como chave primária para alinhar com o script de carga
    id = Column(String(100), primary_key=True)
    nome = Column(String(255), nullable=False)
    tarefas = relationship("Tarefa", back_populates="material")

class Tarefa(Base):
    __tablename__ = 'tarefas'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(String(1024), nullable=True)
    pontuacao = Column(Integer, nullable=False, default=0)
    unidade_id = Column(Integer, ForeignKey('unidade_medida.id'))
    material_id = Column(String(100), ForeignKey('material.id'))

    unidade = relationship("UnidadeMedida", back_populates="tarefas")
    material = relationship("Material", back_populates="tarefas")

    def __repr__(self):
        return f"<Tarefa(id={self.id}, titulo='{self.titulo}', pontuacao={self.pontuacao}, unidade_id={self.unidade_id}, material_id={self.material_id})>"


class ExecucaoTarefa(Base):
    __tablename__ = 'execucoes_tarefas'

    id = Column(Integer, primary_key=True)
    equipe_id = Column(Integer, ForeignKey('equipes.id'), nullable=False)
    tarefa_id = Column(Integer, ForeignKey('tarefas.id'), nullable=False)
    pontos = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    equipe = relationship("Equipe")
    tarefa = relationship("Tarefa")

    __table_args__ = (
        UniqueConstraint('equipe_id', 'tarefa_id', name='uq_execucao_unica'),
    )

    def __repr__(self):
        return f"<ExecucaoTarefa(equipe={self.equipe_id}, tarefa={self.tarefa_id}, pontos={self.pontos})>"


class ExecucaoTarefaAprovacao(Base):
    __tablename__ = 'execucoes_tarefas_aprovacoes'

    id = Column(Integer, primary_key=True)
    equipe_id = Column(Integer, ForeignKey('equipes.id'), nullable=False)
    tarefa_id = Column(Integer, ForeignKey('tarefas.id'), nullable=False)
    fiscal_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    papel = Column(Enum(PapelMembro), nullable=False)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('equipe_id', 'tarefa_id', 'papel', name='uq_aprovacao_papel'),
    )

    def __repr__(self):
        return f"<Aprovacao(equipe={self.equipe_id}, tarefa={self.tarefa_id}, fiscal={self.fiscal_id}, papel={self.papel})>"


class StatusConvite(str, enum.Enum):
    PENDENTE = "PENDENTE"
    ACEITO = "ACEITO"
    RECUSADO = "RECUSADO"


class ConviteFiscalExterno(Base):
    __tablename__ = 'convites_fiscal_externo'

    id = Column(Integer, primary_key=True)
    equipe_solicitante_id = Column(Integer, ForeignKey('equipes.id'), nullable=False)
    convidado_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    status = Column(Enum(StatusConvite), nullable=False, default=StatusConvite.PENDENTE)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('equipe_solicitante_id', 'convidado_id', name='uq_convite_unico'),
    )

    def __repr__(self):
        return f"<Convite(equipe={self.equipe_solicitante_id}, convidado={self.convidado_id}, status={self.status})>"


Base.metadata.create_all(db)




