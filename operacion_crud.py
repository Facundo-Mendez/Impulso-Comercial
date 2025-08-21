from dbimpulso import db, Usuario

def crear_usuario(nombre, correo, password):
    nuevo_usuario = Usuario(nombre=nombre, correo=correo, password=password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return nuevo_usuario

def obtener_usuarios():
    return Usuario.query.all()

def obtener_usuario_por_id(id_usuario):
    return Usuario.query.get(id_usuario)

def actualizar_usuario(id_usuario, nuevo_nombre=None, nuevo_correo=None):
    usuario = obtener_usuario_por_id(id_usuario)
    if usuario:
        if nuevo_nombre:
            usuario.nombre = nuevo_nombre
        if nuevo_correo:
            usuario.correo = nuevo_correo
        db.session.commit()
        return usuario
    return None
def eliminar_usuario(id_usuario):
    usuario = obtener_usuario_por_id(id_usuario)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return True
    return False

