from models import db, Usuario, Base
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=db)
session = Session()

# Apaga todos os registros da tabela usuarios
deleted = session.query(Usuario).delete()
session.commit()
print(f"Registros apagados: {deleted}")
