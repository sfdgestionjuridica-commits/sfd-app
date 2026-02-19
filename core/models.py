from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nit = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    nombre = Column(String, nullable=False)
    documento = Column(String)
    correo = Column(String)
    celular = Column(String)
    direccion = Column(String)


from datetime import datetime

class Proceso(Base):
    __tablename__ = "procesos"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    jurisdiccion = Column(String)
    tipo_proceso = Column(String)
    numero_rama = Column(String)
    juzgado = Column(String)
    ciudad = Column(String)
    estado_actual = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

