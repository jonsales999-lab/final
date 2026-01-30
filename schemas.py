from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, Literal
from datetime import date


class UsuarioCreate(BaseModel):
    escola_id: int
    nome_completo: str
    sexo: Literal["M", "F"]
    data_nascimento: date
    funcao: str
    telefone_pessoal: str
    rg_path: str
    cpf: str
    email: EmailStr
    senha: str
    cursando: Literal["Fundamental 1", "Fundamental 2", "Universitário"]
    manequim: Literal["PP", "P", "M", "G", "GG"]
    tipo_sanguineo: Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    medicamento_controlado: bool
    nome_medicamento_1: Optional[str] = None
    declaracao_lida: bool

    class Config:
        from_attributes = True

    @field_validator("escola_id", mode="before")
    @classmethod
    def _escola_obrigatoria(cls, v):
        try:
            v_int = int(v)
        except (TypeError, ValueError):
            raise ValueError("Escolha uma escola válida")
        if v_int <= 0:
            raise ValueError("Escolha uma escola válida")
        return v_int

    @field_validator(
        "nome_completo",
        "funcao",
        "telefone_pessoal",
        "rg_path",
        "cpf",
        "senha",
        mode="before",
    )
    @classmethod
    def _nao_vazio(cls, v: Optional[str]):
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("Campo obrigatório não pode ser vazio")
        return v

    @model_validator(mode="after")
    def _validar_medicamentos_e_declaracao(self):
        if self.medicamento_controlado and not (self.nome_medicamento_1 and self.nome_medicamento_1.strip()):
            raise ValueError("Informe o nome do medicamento controlado")
        if not self.declaracao_lida:
            raise ValueError("A declaração deve ser lida e aceita")
        return self


class LoginSchema(BaseModel):
    email: Optional[str] = None
    senha: Optional[str] = None