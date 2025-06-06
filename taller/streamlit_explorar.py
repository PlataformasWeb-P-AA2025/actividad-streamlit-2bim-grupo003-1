# streamlit_explorar.py

import streamlit as st  # Librería de streamlit
from sqlalchemy.orm import sessionmaker  # Para crear sesiones de base de datos
from sqlalchemy import create_engine  # Para conectar con la base de datos

# Importar las clases y configuración que definimos en otros archivos
from configuracion import cadena_base_datos  # String de conexión a la base de datos
from genera_tablas import Usuario, Publicacion, Reaccion  # Nuestras tablas/clases de SQLAlchemy

# Crear el motor de base de datos 
engine = create_engine(cadena_base_datos)
Session = sessionmaker(bind=engine)

def get_session():
    """
    Función helper que crea una nueva sesión de base de datos
    Es como abrir una nueva "conversación" con la base de datos
    """
    return Session()

# Configurar la página de Streamlit (título y diseño ancho)
st.set_page_config(page_title="Explorador de tablas SQLAlchemy", layout="wide")

def listar_usuarios():
    """
    Esta función muestra todos los usuarios de la base de datos
    Para cada usuario, muestra sus publicaciones y reacciones en un menú desplegable
    """
    st.header("Usuarios")  # Título grande en la página
    session = get_session()  # Abrir conexión con la base de datos
    
    # Hacer consulta: traer TODOS los usuarios de la tabla 'usuario'
    usuarios = session.query(Usuario).all()

    # Si no hay usuarios, mostrar mensaje y salir
    if not usuarios:
        st.info("No hay registros en 'usuario'.")
        session.close()  # Cerrar la conexión
        return

    # Para cada usuario encontrado, crear un menú desplegable
    for usuario in usuarios:
        # st.expander crea un menú que se puede abrir/cerrar
        # El título muestra ID y nombre del usuario
        with st.expander(f"ID {usuario.id} → {usuario.nombre}", expanded=False):
            
            # Mostrar información básica del usuario
            st.write(f"**ID:** {usuario.id}")
            st.write(f"**Nombre:** {usuario.nombre}")
            # len() cuenta cuántos elementos hay en la lista
            st.write(f"**Total Publicaciones:** {len(usuario.publicaciones)}")
            st.write(f"**Total Reacciones:** {len(usuario.reacciones)}")

            # Si el usuario tiene publicaciones, mostrarlas en una tabla
            if usuario.publicaciones:
                st.write("**Publicaciones del usuario:**")
                filas_pub = []  # Lista vacía para guardar los datos de la tabla
                
                # Recorrer cada publicación del usuario
                for pub in usuario.publicaciones:
                    # Crear un diccionario con los datos de cada fila
                    filas_pub.append({
                        "ID Publicación": pub.id,
                        # Si el contenido es muy largo, cortarlo y agregar "..."
                        "Contenido": pub.contenido[:50] + "..." if len(pub.contenido) > 50 else pub.contenido,
                        "Reacciones": len(pub.reacciones),  # Contar reacciones
                    })
                st.table(filas_pub)  # Mostrar la tabla con todas las filas
            else:
                st.write("_Este usuario no tiene publicaciones._")

            # Si el usuario tiene reacciones, mostrarlas
            if usuario.reacciones:
                st.write("**Reacciones del usuario:**")
                filas_reac = []  # Lista para los datos de reacciones
                
                # Recorrer cada reacción del usuario
                for reac in usuario.reacciones:
                    # Cortar el contenido de la publicación si es muy largo
                    contenido_pub = reac.publicacion.contenido[:30] + "..." if len(reac.publicacion.contenido) > 30 else reac.publicacion.contenido
                    
                    # Agregar fila con datos de la reacción
                    filas_reac.append({
                        "Tipo Emoción": reac.tipo_emocion,  # alaegre, me gusta, etc.
                        "Publicación": contenido_pub,  # A qué publicación reaccionó
                        "Autor Publicación": reac.publicacion.usuario.nombre,  # Quién escribió esa publicación
                    })
                st.table(filas_reac)
            else:
                st.write("_Este usuario no ha reaccionado a ninguna publicación._")
    
    session.close()  # Cerrar la conexión

def listar_publicaciones():
    """
    Esta función muestra todas las publicaciones
    Para cada publicación, muestra quién la escribió y qué reacciones tiene
    """
    st.header("Publicaciones")
    session = get_session()  # Abrir nueva conexión
    
    # Traer TODAS las publicaciones
    publicaciones = session.query(Publicacion).all()

    # Si no hay publicaciones, mostrar mensaje
    if not publicaciones:
        st.info("No hay registros en 'publicacion'.")
        session.close()
        return

    # Para cada publicación, crear un menú desplegable
    for pub in publicaciones:
        # Cortar el contenido para que el título no sea muy largo
        titulo_contenido = pub.contenido[:50] + "..." if len(pub.contenido) > 50 else pub.contenido
        
        with st.expander(f"ID {pub.id} → {titulo_contenido}", expanded=False):
            # Mostrar información de la publicación
            st.write(f"**ID:** {pub.id}")
            st.write(f"**Contenido completo:** {pub.contenido}")  # Contenido sin cortar
            st.write(f"**Autor:** {pub.usuario.nombre}")  # Quién la escribió
            st.write(f"**Total Reacciones:** {len(pub.reacciones)}")

            # Si tiene reacciones, analizarlas y mostrarlas
            if pub.reacciones:
                st.write("**Reacciones a esta publicación:**")
                
                # Contar cuántas reacciones de cada tipo hay
                conteo_reacciones = {}  # Diccionario vacío
                for reac in pub.reacciones:
                    # Si ya existe este tipo de emoción, sumar 1
                    if reac.tipo_emocion in conteo_reacciones:
                        conteo_reacciones[reac.tipo_emocion] += 1
                    else:
                        # Si es la primera vez que vemos esta emoción, empezar en 1
                        conteo_reacciones[reac.tipo_emocion] = 1
                
                # Mostrar el resumen
                st.write("**Resumen de reacciones:**")
                for tipo, cantidad in conteo_reacciones.items():
                    st.write(f"- {tipo}: {cantidad}")
                
                # Mostrar detalle: quién reaccionó y cómo
                st.write("**Detalle de reacciones:**")
                filas_reac = []
                for reac in pub.reacciones:
                    filas_reac.append({
                        "Usuario": reac.usuario.nombre,  # Quién reaccionó
                        "Tipo Emoción": reac.tipo_emocion,  # Cómo reaccionó
                    })
                st.table(filas_reac)
            else:
                st.write("_Esta publicación no tiene reacciones._")
    
    session.close()

def listar_reacciones():
    """
    Esta función muestra TODAS las reacciones en una sola tabla grande
    Cada fila muestra: quién reaccionó, cómo reaccionó, y a qué publicación
    """
    st.header("Reacciones")
    session = get_session()
    
    # Traer TODAS las reacciones
    reacciones = session.query(Reaccion).all()

    if not reacciones:
        st.info("No hay registros en 'reaccion'.")
        session.close()
        return

    filas = []  # Lista para todas las filas de la tabla
    
    # Recorrer cada reacción y crear una fila
    for reac in reacciones:
        # Cortar el contenido de la publicación para que no sea muy largo
        contenido_pub = reac.publicacion.contenido[:40] + "..." if len(reac.publicacion.contenido) > 40 else reac.publicacion.contenido
        
        # Agregar fila con toda la información
        filas.append({
            "ID Reacción": reac.id,
            "Usuario": reac.usuario.nombre,  # Quién reaccionó
            "Tipo Emoción": reac.tipo_emocion,  # like, love, etc.
            "Publicación": contenido_pub,  # A qué publicación
            "Autor Publicación": reac.publicacion.usuario.nombre,  # Quién escribió esa publicación
        })
    
    # Mostrar toda la tabla de una vez
    st.table(filas)
    session.close()

def estadisticas_generales():
    """
    Esta función muestra estadísticas y números generales de toda la red social
    Como un "dashboard" con métricas importantes
    """
    st.header("Estadísticas Generales")
    session = get_session()
    
    # Contar totales usando .count()
    total_usuarios = session.query(Usuario).count()
    total_publicaciones = session.query(Publicacion).count()
    total_reacciones = session.query(Reaccion).count()
    
    # Crear 3 columnas para mostrar las métricas lado a lado
    col1, col2, col3 = st.columns(3)
    
    # st.metric() crea las cajas con números grandes
    with col1:
        st.metric("Total Usuarios", total_usuarios)
    
    with col2:
        st.metric("Total Publicaciones", total_publicaciones)
    
    with col3:
        st.metric("Total Reacciones", total_reacciones)
    
    # Encontrar los usuarios más activos 
    if total_usuarios > 0:
        st.subheader("Usuarios más activos")
        
        # Traer todos los usuarios para analizarlos
        usuarios_con_pub = session.query(Usuario).all()
        
        if usuarios_con_pub:
            # max() encuentra el usuario con más publicaciones
            # key=lambda u: len(u.publicaciones) le dice cómo comparar
            usuario_mas_publicaciones = max(usuarios_con_pub, key=lambda u: len(u.publicaciones))
            st.write(f"**Usuario con más publicaciones:** {usuario_mas_publicaciones.nombre} ({len(usuario_mas_publicaciones.publicaciones)} publicaciones)")
        
        # Encontrar el usuario que más reacciona
        if usuarios_con_pub:
            usuario_mas_reacciones = max(usuarios_con_pub, key=lambda u: len(u.reacciones))
            st.write(f"**Usuario más reactivo:** {usuario_mas_reacciones.nombre} ({len(usuario_mas_reacciones.reacciones)} reacciones)")
    
    # Analizar qué tipos de emociones son más populares
    if total_reacciones > 0:
        st.subheader("Emociones más populares")
        reacciones = session.query(Reaccion).all()  # Traer todas las reacciones
        conteo_emociones = {}  # Diccionario para contar
        
        # Contar cada tipo de emoción
        for reac in reacciones:
            if reac.tipo_emocion in conteo_emociones:
                conteo_emociones[reac.tipo_emocion] += 1
            else:
                conteo_emociones[reac.tipo_emocion] = 1
        
        # Ordenar de mayor a menor popularidad
        # sorted() ordena, key=lambda x: x[1] ordena por el segundo elemento (la cantidad)
        # reverse=True pone los números más grandes primero
        emociones_ordenadas = sorted(conteo_emociones.items(), key=lambda x: x[1], reverse=True)
        
        # Mostrar cada emoción con su cantidad
        for emocion, cantidad in emociones_ordenadas:
            st.write(f"- **{emocion}:** {cantidad} veces")
    
    session.close()

def main():
    """
    Función principal que controla toda la aplicación
    Crea el menú lateral y decide qué mostrar según lo que elija el usuario
    """
    # Título principal de la aplicación
    st.title("Explorar tablas - SQLAlchemy")
    st.markdown("---")  # Línea horizontal para separar

    # st.sidebar.selectbox crea un menú desplegable en la barra lateral
    entidad = st.sidebar.selectbox(
        "Elija la sección que desea explorar:",
        (
            "Estadísticas Generales",  # Opción 1
            "Usuarios",               # Opción 2
            "Publicaciones",          # Opción 3
            "Reacciones",            # Opción 4
        ),
    )

    # Según lo que eligió el usuario, llamar a la función correspondiente
    if entidad == "Estadísticas Generales":
        estadisticas_generales()
    elif entidad == "Usuarios":
        listar_usuarios()
    elif entidad == "Publicaciones":
        listar_publicaciones()
    elif entidad == "Reacciones":
        listar_reacciones()

# Esta línea hace que el código se ejecute solo si corremos este archivo directamente
if __name__ == "__main__":
    main()
