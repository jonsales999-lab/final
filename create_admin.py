from datetime import date
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from models import db, Usuario

SessionLocal = sessionmaker(bind=db)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    session = SessionLocal()
    try:
        email = "adm@gmail.com"
        user = session.query(Usuario).filter_by(email=email).first()
        if user:
            # Atualiza a senha do admin existente
            user.senha_hash = bcrypt_context.hash("123456")
            session.commit()
            print("Admin já existia. Senha redefinida para '123456'.")
            return

        admin = Usuario(
            nome_completo="Administrador",
            sexo="M",
            data_nascimento=date(2000, 1, 1),
            funcao="ADMIN",
            telefone_pessoal="000000000",
            rg_path=None,
            cpf="00000000000",
            email=email,
            senha_hash=bcrypt_context.hash("123456"),
            cursando="Fundamental 2",
            manequim="M",
            tipo_sanguineo="O+",
            medicamento_controlado=False,
            nome_medicamento_1=None,
            declaracao_lida=True,
            escola_id=None,
            is_admin=True,
            pode_criar_equipe=True,
        )
        session.add(admin)
        session.commit()
        print("Admin criado com sucesso.")
    except Exception as exc:
        session.rollback()
        print(f"Erro ao criar admin: {exc}")
    finally:
        session.close()

if __name__ == "__main__":
    create_admin()