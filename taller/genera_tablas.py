from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

# Importar cadena de conexión
from configuracion import cadena_base_datos

# Crear motor
engine = create_engine(cadena_base_datos)

# Base de datos
Base = declarative_base()

# Tabla Usuario
class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)

    publicaciones = relationship("Publicacion", back_populates="usuario")
    reacciones = relationship("Reaccion", back_populates="usuario")

    def __repr__(self):
        return f"Usuario: {self.nombre}"

# Tabla Publicacion
class Publicacion(Base):
    __tablename__ = 'publicacion'
    id = Column(Integer, primary_key=True)
    contenido = Column(String, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))

    usuario = relationship("Usuario", back_populates="publicaciones")
    reacciones = relationship("Reaccion", back_populates="publicacion")

    def __repr__(self):
        return f"Publicación: {self.contenido[:30]}... (Autor ID: {self.usuario_id})"

# Tabla Reaccion
class Reaccion(Base):
    __tablename__ = 'reaccion'
    id = Column(Integer, primary_key=True)
    tipo_emocion = Column(String(50), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    publicacion_id = Column(Integer, ForeignKey('publicacion.id'), nullable=False)

    usuario = relationship("Usuario", back_populates="reacciones")
    publicacion = relationship("Publicacion", back_populates="reacciones")

    # Solo una reacción por usuario por publicación
    __table_args__ = (
        UniqueConstraint('usuario_id', 'publicacion_id', name='uq_usuario_publicacion'),
    )

    def __repr__(self):
        return f"Reacción: {self.tipo_emocion} (Usuario ID: {self.usuario_id}, Publicación ID: {self.publicacion_id})"

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)
