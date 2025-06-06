from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar clases desde el archivo de modelos
from genera_tablas import Usuario, Publicacion, Reaccion
from configuracion import cadena_base_datos

# Crear engine y sesión
engine = create_engine(cadena_base_datos)
Session = sessionmaker(bind=engine)
session = Session()

# --------------------
# Cargar usuarios desde DATA/usuarios_red_x.csv
# --------------------
with open('DATA/usuarios_red_x.csv', 'r', encoding='utf-8') as archivo:
    next(archivo)  # Saltar encabezado
    for linea in archivo:
        nombre = linea.strip()
        if not session.query(Usuario).filter_by(nombre=nombre).first():
            nuevo_usuario = Usuario(nombre=nombre)
            session.add(nuevo_usuario)
session.commit()

# --------------------
# Cargar publicaciones desde DATA/usuarios_publicaciones.csv
# --------------------
with open('DATA/usuarios_publicaciones.csv', 'r', encoding='utf-8') as archivo:
    next(archivo)  # Saltar encabezado
    for linea in archivo:
        partes = linea.strip().split('|')
        if len(partes) == 2:
            nombre_usuario, texto_publicacion = partes

            usuario = session.query(Usuario).filter_by(nombre=nombre_usuario).first()
            if not usuario:
                usuario = Usuario(nombre=nombre_usuario)
                session.add(usuario)
                session.commit()

            existe = session.query(Publicacion).filter_by(contenido=texto_publicacion, usuario_id=usuario.id).first()
            if not existe:
                nueva_publicacion = Publicacion(contenido=texto_publicacion, usuario=usuario)
                session.add(nueva_publicacion)
session.commit()

# --------------------
# Cargar reacciones desde DATA/usuario_publicacion_emocion.csv
# --------------------
with open('DATA/usuario_publicacion_emocion.csv', 'r', encoding='utf-8') as archivo:
    next(archivo)  # Saltar encabezado
    for linea in archivo:
        partes = linea.strip().split('|')
        if len(partes) == 3:
            nombre_usuario, comentario, tipo_emocion = partes

            usuario = session.query(Usuario).filter_by(nombre=nombre_usuario).first()
            if not usuario:
                usuario = Usuario(nombre=nombre_usuario)
                session.add(usuario)
                session.commit()

            publicacion = session.query(Publicacion).filter_by(contenido=comentario).first()
            if publicacion:
                ya_existe = session.query(Reaccion).filter_by(usuario_id=usuario.id, publicacion_id=publicacion.id).first()
                if not ya_existe:
                    nueva_reaccion = Reaccion(tipo_emocion=tipo_emocion, usuario=usuario, publicacion=publicacion)
                    session.add(nueva_reaccion)
session.commit()
