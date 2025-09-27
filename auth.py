from database import check_user, user_exists, create_user

def login_user(username, password):
    return check_user(username, password)

def register_user(username, password):
    # retorna (ok: bool, message: str)
    if username == "" or password == "":
        return False, "Usuario o contraseña vacíos"
    if user_exists(username):
        return False, "Ese nombre de usuario ya existe."
    ok, err = create_user(username, password)
    if ok:
        return True, f"Usuario '{username}' registrado correctamente."
    else:
        if err == "IntegrityError":
            return False, "Error: nombre ya existe."
        return False, f"Error interno: {err}"
